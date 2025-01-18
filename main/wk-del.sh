#!/bin/bash
#
# 脚本名称: wk-del
# 描述: 删除指定目录下的特定文件
# 用法: ./wk-del [OPTIONS]
# 作者: wukai
# 日期: 2024-01-18

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 加载配置和函数
source environment
source setting

# 默认配置
declare -A CONFIG=(
    [root_dir]="$(pwd)"
    [file]="CHG"
    [command]="0"
)

# 日志记录
logging 1 "wk-del started"

# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]
Options:
    -d, -dir       Set root directory (default: current directory)
    -f, -file      Set file to delete (default: CHG)
    -c, -command   Set operation command (default: 0)
    -h, --help     Show this help message

Example:
    $(basename "$0") -d /path/to/dir -f CHG
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
            -file|-F|-f)
                CONFIG[file]="$2"
                logging 1 "File to delete set to: ${CONFIG[file]}"
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

# 删除文件
delete_file() {
    local target_dir="$1"
    local target_file="$target_dir/${CONFIG[file]}"
    
    if [[ -f "$target_file" ]]; then
        if rm "$target_file" 2>>"$WORK_DIR/errors"; then
            logging 1 "Successfully deleted: $target_file"
        else
            logging 3 "Failed to delete: $target_file"
            return 1
        fi
    else
        logging 2 "File not found: $target_file"
    fi
}

# 主程序
main() {
    case "${CONFIG[command]}" in
        0)
            find "${CONFIG[root_dir]}" -type d | while read -r target_dir; do
                # 检查是否是叶子目录
                if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
                    delete_file "$target_dir"
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
result $? "wk-del"
