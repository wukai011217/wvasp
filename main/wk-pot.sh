#!/bin/bash
#
# 脚本名称: xsd-to-input
# 描述: 根据 POSCAR 创建 INCAR 和 POTCAR，复制 KPOINTS 和 vasp.sbatch
# 用法: ./xsd-to-input.sh [OPTIONS]
# 作者: wukai
# 创建日期: 2024-10-23

set -e  # 遇到错误立即退出
set -u  # 使用未定义的变量时报错

# 加载配置和函数
. functions

# 默认配置
declare -A CONFIG=(
    [command]="0"
    [to_dir]="$(pwd)"
    [match]=""
)

# 函数：显示帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]
Options:
    -to           Set target directory
    -m, -match    Set match pattern
    -c, -command  Set command (0: create POTCAR, 1: H addition for 2H)
Example:
    $(basename "$0") -to /path/to/dir -m "pattern" -c 0
EOF
}

# 函数：解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -to)
                CONFIG[to_dir]="$2"
                logging 1 "TO_DIR: ${CONFIG[to_dir]}"
                shift 2
                ;;
            -match|-M|-m)
                CONFIG[match]="$2"
                logging 1 "match: ${CONFIG[match]}"
                shift 2
                ;;
            -command|-c|-C)
                CONFIG[command]="$2"
                logging 1 "command: ${CONFIG[command]}"
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

# 函数：创建 POTCAR 文件
create_potcar() {
    local target_dir="$1"
    if [[ -f "$target_dir/POSCAR" ]]; then
        logging 1 "Found POSCAR in $target_dir"
        
        # 读取元素
        IFS=' ' read -r -a eles < <(sed -n '6p' "$target_dir/POSCAR" | sed 's/\r//g') 2>> "${PATHS[log_dir]}/errors"
        
        # 删除旧的 POTCAR
        rm -f "$target_dir/POTCAR" 2>> "${PATHS[log_dir]}/errors"
        
        # 为每个元素追加对应的 POTCAR
        for element in "${eles[@]}"; do
            if [[ -d "${PATHS[pot_dir]}/${element}" ]]; then
                cat "${PATHS[pot_dir]}/${element}/POTCAR" >> "$target_dir/POTCAR" 2>> "${PATHS[log_dir]}/errors"
            elif [[ -d "${PATHS[pot_dir]}/${element}_sv" ]]; then
                cat "${PATHS[pot_dir]}/${element}_sv/POTCAR" >> "$target_dir/POTCAR" 2>> "${PATHS[log_dir]}/errors"
            else
                logging 1 "Warning: POTCAR for ${element} not found in ${PATHS[pot_dir]}"
            fi
        done
    else
        logging 1 "NO POSCAR in $target_dir"
    fi
}

# 函数：处理2H的H添加
process_2h() {
    local target_dir="$1"
    if [[ -f "$target_dir/POSCAR" ]]; then
        cat "${PATHS[pot_dir]}/H/POTCAR" >> "$target_dir/POTCAR" 2>> "${PATHS[log_dir]}/errors"
    else
        logging 1 "NO POSCAR in $target_dir"
    fi
}

# 主程序
main() {
    local command="${CONFIG[command]}"
    local to_dir="${CONFIG[to_dir]}"
    local match="${CONFIG[match]}"
    
    case "$command" in
        0)  
        # 创建 POTCAR 文件
            find "$to_dir" -type d | while read -r target_dir; do
                if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
                    [[ "$target_dir" == *"$match"* ]] && create_potcar "$target_dir"
                    :
                fi
            done
            ;;
        1)  
        # 针对 2H 添加 POTCAR的处理
            find "$to_dir" -type d | while read -r target_dir; do
                if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
                    [[ "$target_dir" == *"2H"* ]] && process_2h "$target_dir"
                    :
                fi
            done
            ;;
        help)
            show_help
            ;;
        *)
            logging 1 "Invalid command: ${command}"
            show_help
            exit 1
            ;;
    esac
}

# 启动
logging 1 "Starting mk-pot"

# 解析命令行参数
parse_arguments "$@"
# 执行主程序
main
# 记录结果
result $? "xsd-to-input"