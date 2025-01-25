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
. functions

# 默认配置
declare -A CONFIG=(
    [root_dir]="$(pwd)"
    [file]="CHG"
    [command]="0"
)

# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Description:
    Delete specified files from VASP calculation directories.
    Can selectively remove specific files or clean up all files in target directories.

Options:
    -d|-D|-dir,         --dir       Set root directory (default: current directory): directory containing files to delete
    -f|-F|-file,        --file      Set file to delete (default: CHG): target file name
    -c|-C|-command,     --command   Set operation command (default: 0)
    -h|-help,           --help      Show this help message

Commands:
    0: Delete specified file from target directories
    1: Delete all files from target directories (use with caution)

Examples:
    # Delete CHG files from current directory
    $(basename "$0")

    # Delete specific file from target directory
    $(basename "$0") -d /path/to/calcs -f WAVECAR

    # Delete all files from target directory (use with caution)
    $(basename "$0") -d /path/to/calcs -c 1
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
        if rm "$target_file" 2>>"${PATHS[log_dir]}/errors"; then
            logging 1 "Successfully deleted: $target_file"
        else
            logging 1 "Failed to delete: $target_file"
            return 1
        fi
    else
        logging 1 "File not found: $target_file"
    fi
}

delete_all_file() {
    local target_dir="$1"
    if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
            rm "$target_dir"/* 2>>"${PATHS[log_dir]}/errors" || logging 1 "Failed to delete: $target_dir"
        logging 1 "Successfully deleted: $target_dir"
    else
        logging 1 " $target_dir is not mindepth 1"
    fi
}
# 主程序
main() {
    case "${CONFIG[command]}" in
        0)
            find "${CONFIG[root_dir]}" -mindepth 1 -type d | while read -r target_dir; do
                delete_file "$target_dir"
            done
            ;;
        1)
            find "${CONFIG[root_dir]}" -mindepth 1 -type d | while read -r target_dir; do
                delete_all_file "$target_dir"
            done
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

# 日志记录
logging 0 

# 启动脚本
parse_arguments "$@"

# 执行主程序
main

# 结果检查
result $? "wk-del"
