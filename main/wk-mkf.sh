#!/bin/bash
#
# 脚本名称: mkf-in-loop
# 描述: 在循环中将文件复制到子目录，支持多种复制模式
# 用法: ./mkf-in-loop [OPTIONS]
# 作者: wukai
# 日期: 2024-10-23

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 加载配置和函数
. functions

# 默认配置
declare -A CONFIG=(
    [root_dir]="$(pwd)"
    [file]="$SCRIPT_DIR/data/KPOINTS"
    [command]="0"
    [to_dir]="$(pwd)"
    [match]=""
)

# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Description:
    Copy files to multiple directories while maintaining structure.

Options:
    -d, -dir      Set root directory (default: current directory)
    -f, -file     Set file to copy (default: KPOINTS)
    -to           Set target directory
    -m, -match    Set match pattern for directories
    -c, -command  Set operation command (default: 0)
    -h, --help    Show this help message

Commands:
    0: Copy single file to matching directories
    1: Copy files maintaining directory structure

Examples:
    # Copy single file to matching directories
    $(basename "$0") -f KPOINTS -to /target/dir -m "pattern"

    # Copy files maintaining structure
    $(basename "$0") -d /source/dir -to /target/dir -m "pattern" -c 1
EOF
}

# 函数：解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -from)
                CONFIG[root_dir]="$2"
                logging 1 "ROOT_DIR set to: ${CONFIG[root_dir]}"
                shift 2
                ;;
            -file|-F|-f)
                CONFIG[file]="$2"
                logging 1 "File set to: ${CONFIG[file]}"
                shift 2
                ;;
            -to)
                CONFIG[to_dir]="$2"
                logging 1 "TO_DIR set to: ${CONFIG[to_dir]}"
                shift 2
                ;;
            -match|-M|-m)
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

# 函数：执行命令模式 0（单文件复制到多个目标目录）
copy_file_to_all() {
    local to_dir="${CONFIG[to_dir]}"
    local file="${CONFIG[file]}"
    local match="${CONFIG[match]}"

    find "$to_dir" -mindepth 1 -type d | while read -r target_dir; do
        if [ -z "$(find "$target_dir" -mindepth 1 -type d)" ] && [[ "$target_dir" == *"$match"* ]]; then
            cp "$file" "$target_dir" 2>> "${PATHS[log_dir]}/errors" 
            logging 1 "Copied $file to $target_dir"
        fi
    done
}

# 函数：执行命令模式 1（基于结构复制文件）
structured_copy() {
    local from_dir="${CONFIG[root_dir]}"
    local to_dir="${CONFIG[to_dir]}"
    local match="${CONFIG[match]}"

    find "$to_dir" -mindepth 1 -type d | while read -r target_dir; do
        if is_empty_dir "$target_dir" && [[ "$target_dir" == *"$match"* ]]; then
            # 提取相对路径
            local relative_path="${target_dir#$to_dir}"
            relative_path="${relative_path#/}"
            
            local source_file="$from_dir/$relative_path/CONTCAR"
            local target_file="$target_dir/POSCAR"
            
            # 执行复制
            if [[ -f "$source_file" ]]; then
                cp "$source_file" "$target_file" 2>> "${PATHS[log_dir]}/errors" 
                logging 1 "Copied $source_file to $target_file"
            else
                logging 1 "Warning: Source file $source_file not found"
            fi
        fi
    done
}

# 主程序
main() {
    local command="${CONFIG[command]}"
    
    # 检查目标目录是否存在
    if [[ ! -d "${CONFIG[to_dir]}" ]]; then
        error_exit "Target directory ${CONFIG[to_dir]} does not exist"
    fi

    case "$command" in
        0)  # 执行命令模式 0
            copy_file_to_all
            ;;
        1)  # 执行命令模式 1
            structured_copy
            ;;
        *)
            error_exit "Invalid command: ${command}"
            ;;
    esac
}

# 启动脚本
logging 0
logging 1 "Starting mkf-in-loop"

# 解析命令行参数
parse_arguments "$@"

# 执行主程序
main

# 记录结果
result $? "mkf-in-loop"