#!/bin/bash
#
# 脚本名称: wk-cpy
# 描述: 复制指定文件到目标目录，保持目录结构
# 用法: ./wk-cpy [OPTIONS]
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
    [file]="CONTCAR"
    [to_dir]="$(pwd)"
    [match]=""
    [command]="0"
)

# 日志记录
logging 1 "wk-cpy started"

# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]
Options:
    -d, -dir       Set source directory (default: current directory)
    -f, -file      Set file to copy (default: CONTCAR)
    -to            Set destination directory (default: current directory)
    -m, -match     Set pattern to match directories
    -c, -command   Set operation command (default: 0)
    -h, --help     Show this help message

Example:
    $(basename "$0") -d /source/dir -f CONTCAR -to /dest/dir -m pattern
EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -dir|-D|-d)
                CONFIG[root_dir]="$2"
                logging 1 "Source directory set to: ${CONFIG[root_dir]}"
                shift 2
                ;;
            -file|-F|-f)
                CONFIG[file]="$2"
                logging 1 "File to copy set to: ${CONFIG[file]}"
                shift 2
                ;;
            -to)
                CONFIG[to_dir]="$2"
                logging 1 "Destination directory set to: ${CONFIG[to_dir]}"
                shift 2
                ;;
            -match|-m|-M)
                CONFIG[match]="$2"
                logging 1 "Match pattern set to: ${CONFIG[match]}"
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

# 复制文件
copy_file() {
    local source_dir="$1"
    local rel_path="$2"
    local dest_dir="${CONFIG[to_dir]}/$rel_path"
    
    # 创建目标目录
    if ! mkdir -p "$dest_dir"; then
        logging 3 "Failed to create directory: $dest_dir"
        return 1
    fi
    
    # 使用rsync复制文件
    if rsync -av --include="${CONFIG[file]}" --exclude="*" "$source_dir/" "$dest_dir" 2>>"$work_dir/errors"; then
        logging 1 "Successfully copied ${CONFIG[file]} to $dest_dir"
    else
        logging 3 "Failed to copy ${CONFIG[file]} to $dest_dir"
        return 1
    fi
}

# 获取相对路径
get_relative_path() {
    local full_path="$1"
    echo "$(awk -F/ '{print $(NF-2)"/"$(NF-1)"/"$NF}' <<< "$full_path")"
}

# 主程序
main() {
    # 确保我们在工作目录中
    cd "$work_dir"
    
    case "${CONFIG[command]}" in
        0)
            find "${CONFIG[root_dir]}" -type d | while read -r target_dir; do
                # 检查是否是叶子目录
                if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
                    # 检查目录名是否匹配模式
                    if [[ -z "${CONFIG[match]}" || "$target_dir" == *"${CONFIG[match]}"* ]]; then
                        # 获取相对路径
                        rel_path="$(get_relative_path "$target_dir")"
                        logging 1 "Processing directory: $rel_path"
                        
                        # 复制文件
                        copy_file "$target_dir" "$rel_path"
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
result $? "wk-cpy"
