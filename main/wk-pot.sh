#!/bin/bash
#
# 脚本名称: wk-pot
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

# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Description:
    Generate POTCAR files for VASP calculations based on POSCAR files.
    Creates POTCAR files by combining pseudopotentials for elements in POSCAR.

Options:
    -to,                --to_dir    Set target directory (required): directory containing POSCAR files
    -m|-M|-match,       --match     Set match pattern for directories: pattern to filter target directories
    -c|-C|-command,     --command   Set operation command (default: 0)
    -h|-help,           --help      Show this help message

Commands:
    0: Generate POTCAR files based on elements in POSCAR
    1: Reserved for future use

Examples:
    # Generate POTCAR for current directory
    $(basename "$0") -to .

    # Generate POTCAR for all matching directories
    $(basename "$0") -to /path/to/calcs -m "Fe_*"

    # Generate POTCAR for specific calculation
    $(basename "$0") -to /path/to/calc/Fe2O3
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

# 函数：验证POSCAR格式
validate_poscar() {
    local poscar_file="$1"
    
    # 检查文件是否存在
    if [[ ! -f "$poscar_file" ]]; then
        echo "Error: POSCAR file does not exist: $poscar_file" >&2
        return 1
    fi

    # 检查文件是否至少有8行
    if [[ $(wc -l < "$poscar_file") -lt 8 ]]; then
        echo "Error: POSCAR file is too short" >&2
        return 1
    fi

    # 检查第2行是否为数字（scaling factor）
    if ! awk 'NR==2 {exit !($1+0==$1)}' "$poscar_file"; then
        echo "Error: Line 2 (scaling factor) must be a number" >&2
        return 1
    fi

    # 检查第3-5行是否为3个数字（晶格向量）
    for i in {3..5}; do
        if ! awk -v line=$i 'NR==line {exit !(NF==3 && $1+0==$1 && $2+0==$2 && $3+0==$3)}' "$poscar_file"; then
            echo "Error: Line $i must contain 3 numbers (lattice vectors)" >&2
            return 1
        fi
    done

    # 检查第6行是否包含元素名称
    if ! awk 'NR==6 {exit (NF==0)}' "$poscar_file"; then
        echo "Error: Line 6 must contain element names" >&2
        return 1
    fi

    # 检查第7行是否包含对应数量的数字
    if ! awk 'NR==6{elements=NF} NR==7{exit !(NF==elements && $1+0==$1)}' "$poscar_file"; then
        echo "Error: Line 7 must contain the same number of integers as elements in line 6" >&2
        return 1
    fi

    # 检查第8/9行是否包含 "Direct" 或 "Cartesian"
    if ! awk 'NR==8{if($0~/^[Ss]elective[[:space:]]*[Dd]ynamics/){next} else{coord=$0}} NR==9{if(NR==9 && coord==""){coord=$0}} END{exit !(coord~/^[Dd]irect/ || coord~/^[Cc]artesian/)}' "$poscar_file"; then
        echo "Error: Coordinates must be specified as either Direct or Cartesian" >&2
        return 1
    fi

    return 0
}

# 函数：创建 POTCAR 文件
create_potcar() {
    local target_dir="$1"
    if [[ -f "$target_dir/POSCAR" ]]; then
        if ! validate_poscar "$target_dir/POSCAR"; then
            echo "Error: Invalid POSCAR format in $target_dir/POSCAR" >&2
            return
        fi
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

# 主程序
main() {
    local command="${CONFIG[command]}"
    local to_dir="${CONFIG[to_dir]}"
    local match="${CONFIG[match]}"
    
    case "$command" in
        0)  
        # 创建 POTCAR 文件
            find "$to_dir" -mindepth 1 -type d | while read -r target_dir; do
                [[ "$target_dir" == *"$match"* ]] && create_potcar "$target_dir"
                :
            done
            ;;
        1)  

                :
            ;;
        help)
            show_help
            ;;
        *)
            logging  "Invalid command: ${command}"
            show_help
            exit 1
            ;;
    esac
}

# 启动
logging 0
logging 1 "pot-to-all"

# 解析命令行参数
parse_arguments "$@"
# 执行主程序
main
# 记录结果
result $? "wk-pot"