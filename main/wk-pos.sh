#!/bin/bash
#
# 脚本名称: pos-to-all
# 描述: 生成和修改 POSCAR 文件
# 用法: pos-to-all [OPTIONS]
# 作者: wukai
# 创建日期: 2024-10-23

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 加载配置和函数
. functions

# 默认配置
declare -A CONFIG=(
    [file]="POSCAR"
    [command]="0"
    [to_dir]="$(pwd)"
    [match]=""
    [start]="0"
    [end]="0"
)

# 函数：显示帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Description:
    This script handles POSCAR file operations for different structures.

Options:
    -f, -file     Set input file (default: POSCAR)
    -to           Set target directory (required)
    -m, -match    Set match pattern for elements
    -n, -number   Set line number (default: 0)  
    -c, -command  Set operation command (default: 0)
    -h, --help    Show this help message

Commands:
    0: Copy POSCAR to specified elements directories
    1: Generate M-2H structure from M structure
    2: Convert M-2H to 2H structure

Example:
    $(basename "$0") -f POSCAR -to /path/to/dir -m "pattern"
EOF
}

# 函数：解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -file|-F|-f)
                CONFIG[file]="$2"
                echo "file: ${CONFIG[file]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -to)
                CONFIG[to_dir]="$2"
                echo "TO_DIR: ${CONFIG[to_dir]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -match|-M|-m)
                CONFIG[match]="$2"
                echo "match: ${CONFIG[match]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -command|-c|-C)
                CONFIG[command]="$2"
                echo "command: ${CONFIG[command]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -number|-n|-N)
                CONFIG[start]="$2"
                CONFIG[end]="$3"
                echo "line_number: ${CONFIG[line_number]}" >> "${PATHS[log_dir]}/logs"
                shift 3
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
                echo "$1 is not an option"
                ;;
        esac
    done
}

# 函数：one to all
process_one_to_all() {
    local target_dir="$1"
    
    if [ -z "$(find "$target_dir" -mindepth 1 -type d)" ]; then
        if [[ "$target_dir" == *"${CONFIG[match]}"* ]]; then
            for element in "${elements[@]}"; do
                if [[ $target_dir == *"/$element/"* ]]; then
                    cp "${CONFIG[file]}" "$target_dir/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                    sed -i "s/Ag/$element/g" "$target_dir/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                fi
            done
        else
            echo "No matching directory found."
            exit 1
        fi
    fi
}

# 函数：M to M-2H
process_m_to_m2h() {
    local target_dir="$1"
    
    if [ -z "$(find "$target_dir" -mindepth 1 -type d)" ]; then
        if [[ "$target_dir" == *"${CONFIG[match]}"* ]]; then
            mkdir -p "$target_dir/../M-2H" 2>> "${PATHS[log_dir]}/errors"
            cp "${CONFIG[file]}" "$target_dir/../M-2H/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
            sed -i "s/Ag/$element/g" "$target_dir/../M-2H/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
        fi
    fi
}

# 函数：M-2H to 2H
process_m2h_to_2h() {
    local target_dir="$1"
    
    if [ -z "$(find "$target_dir" -mindepth 1 -type d)" ]; then
        
        if [[ "$target_dir" == *"${CONFIG[match]}"* ]]; then
            if [[ "$target_dir" == *"M-2H"* ]]; then
                if [ -f "$target_dir/CONTCAR" ]; then
                    mkdir -p "$target_dir/../2H" 2>> "${PATHS[log_dir]}/errors"
                    cp "$target_dir/CONTCAR" "$target_dir/../2H/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                    sed -i "6c\ H" "$target_dir/../2H/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                    sed -i "7c\ 2" "$target_dir/../2H/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                    sed -i "${CONFIG[start]},${CONFIG[end]}d" "$target_dir/../2H/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                else
                    echo "NO CONTCAR in $target_dir" >&2
                fi
            fi
        fi
    fi
}

# 函数：主程序
main() {
    local command="${CONFIG[command]}"
    
    # 检查目标目录是否存在
    if [[ ! -d "${CONFIG[to_dir]}" ]]; then
        error_exit "Target directory ${CONFIG[to_dir]} does not exist"
    fi
    
    case "$command" in
        0)  # one to all
            find "${CONFIG[to_dir]}" -mindepth 1 -type d | while read -r target_dir; do
                process_one_to_all "$target_dir"
            done
            ;;
        1)  # M to M-2H
            find "${CONFIG[to_dir]}" -mindepth 1 -type d | while read -r target_dir; do
                process_m_to_m2h "$target_dir"
            done
            ;;
        2)  # M-2H to 2H
            find "${CONFIG[to_dir]}" -mindepth 1 -type d | while read -r target_dir; do
                process_m2h_to_2h "$target_dir"
            done
            ;;
        help)
            show_help
            ;;
        *)
            error_exit "Invalid command: $command"
            ;;
    esac
}

# 初始化日志
logging 0 
logging 1 "pos-to-all"

# 解析命令行参数
parse_arguments "$@"

# 执行主程序
main

# 记录结果
result $? "pos-to-all"