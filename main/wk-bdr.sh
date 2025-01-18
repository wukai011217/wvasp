#!/bin/bash
#
# 脚本名称: wk-bdr
# 描述: 执行Bader电荷分析，处理VASP的AECCAR文件并生成分析结果
# 用法: ./wk-bdr [OPTIONS]
# 作者: wukai
# 日期: 2024-01-18

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 加载配置和函数
. config_file
. functions

# 默认配置
declare -A CONFIG=(
    [root_dir]="$(pwd)"
    [command]="0"
)

# 日志记录
logging 1 "wk-bdr started"

# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]
Options:
    -d, -dir       Set root directory (default: current directory)
    -c, -command   Set operation command (default: 0)
    -h, --help     Show this help message

Commands:
    0: Process Bader analysis for directories without ACF.dat
    1: Reserved for future use
    help: Show this help message

Example:
    $(basename "$0") -d /path/to/dir -c 0
EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -dir|-D|-d)
                CONFIG[root_dir]="$2"
                logging 1 "Root directory set to: ${CONFIG[root_dir]}"
                shift 2
                ;;
            -command|-c|-C)
                CONFIG[command]="$2"
                logging 1 "Command set to: ${CONFIG[command]}"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            --)
                shift
                break
                ;;
            *)
                echo "Error: $1 is not a valid option" >&2
                show_help
                exit 1
                ;;
        esac
    done
}

# 执行Bader分析
run_bader_analysis() {
    local target_dir="$1"
    local current_dir="$(pwd)"
    
    cd "$target_dir"
    logging 1 "Running Bader analysis in: $target_dir"
    
    # 执行Bader分析
    if chgsum.pl AECCAR0 AECCAR2; then
        if bader CHGCAR -ref CHGCAR_sum; then
            logging 1 "Bader analysis completed successfully in: $target_dir"
        else
            logging 3 "Bader analysis failed in: $target_dir"
        fi
    else
        logging 3 "chgsum.pl failed in: $target_dir"
    fi
    
    cd "$current_dir"
}

# 检查必要的文件
check_files() {
    local dir="$1"
    local files=("$@")
    
    for file in "${files[@]:1}"; do
        if [[ ! -f "$dir/$file" ]]; then
            return 1
        fi
    done
    return 0
}

# 主程序
main() {
    case "${CONFIG[command]}" in
        0)
            find "${CONFIG[root_dir]}" -type d | while read -r target_dir; do
                # 检查是否是叶子目录
                if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
                    if [[ -f "$target_dir/ACF.dat" ]]; then
                        logging 1 "ACF.dat already exists in: $target_dir"
                    else
                        if check_files "$target_dir" "AECCAR0" "AECCAR2"; then
                            run_bader_analysis "$target_dir"
                        else
                            logging 2 "Missing AECCAR files in: $target_dir"
                        fi
                    fi
                fi
            done
            ;;
        1)
            logging 1 "Command 1 is reserved for future use"
            ;;
        help)
            show_help
            ;;
        *)
            echo "Error: ${CONFIG[command]} is not a valid command" >&2
            show_help
            exit 1
            ;;
    esac
}

# 启动脚本
parse_arguments "$@"

# 执行主程序
main

# 结果检查
result $? "wk-bdr"
