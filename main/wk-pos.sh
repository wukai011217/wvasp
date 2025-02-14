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
    Process and manipulate POSCAR structure files for VASP calculations.
    Supports copying structures, generating M-2H structures, and converting between different phases.

Options:
    -f|-F|-file,        --file      Set input file (default: POSCAR): source structure file
    -to,                --to_dir    Set target directory (required): destination for processed structures
    -m|-M|-match,       --match     Set match pattern for elements: filter for target elements/structures
    -n|-N|-number,      --number    Set atomic number (default: 0): specific atom to process
    -c|-C|-command,     --command   Set operation command (default: 0)
    -h|-help,           --help      Show this help message

Commands:
    0: Copy POSCAR to specified elements directories
    1: Generate M-2H structure from M structure (removes H atoms)
    2: Convert M-2H to 2H structure (structural phase transformation)

Examples:
    # Copy POSCAR to directories matching element pattern
    $(basename "$0") -f POSCAR -to /path/to/calcs -m "Fe_*"

    # Generate M-2H structure from M structure
    $(basename "$0") -f POSCAR -to /path/to/M2H -c 1

    # Convert M-2H structure to 2H phase
    $(basename "$0") -f POSCAR -to /path/to/2H -c 2
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
        echo $target_dir
        if [[ "$target_dir" == *"${CONFIG[match]}"* ]]; then
            for element in "${elements[@]}"; do
                if [[ $target_dir == *"/$element/"* ]]; then
                    cp "${CONFIG[file]}" "$target_dir/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                    sed -i "s/Ag/$element/g" "$target_dir/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                fi
            done
        else
            echo "$target_dir not match ${CONFIG[match]} found."
        fi
    fi
}

# 函数：M to M-H
process_m_to_mh() {
    local target_dir="$1"
    
    if [ -z "$(find "$target_dir" -mindepth 1 -type d)" ]; then
        
        if [[ "$target_dir" == *"${CONFIG[match]}"* ]]; then
            if [[ "$target_dir" == *"M" ]]; then
                if [ -f "$target_dir/CONTCAR" ]; then
                    mkdir -p "$target_dir/../M-H" 2>> "${PATHS[log_dir]}/errors"
                    cp "$target_dir/CONTCAR" "$target_dir/../M-H/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                    num=$(awk 'NR==7 {print}' "$target_dir/../M-H/POSCAR" | awk '{sum=0; for(i=1; i<=NF; i++) sum+=$i; print sum}')
                    num=$(($num + 9))
                    if ! check_file "$target_dir/../M-H/POSCAR"; then
                        error_exit "POSCAR is not a linux format in $target_dir/../M-H/POSCAR"
                        dos2unix "$target_dir/../M-H/POSCAR"
                    fi
                    sed -i '6s/$/ H/' "$target_dir/../M-H/POSCAR" 
                    sed -i "${num}a\0.446598 0.216020 0.433410 T T T " "$target_dir/../M-H/POSCAR" 
                    sed -i '7s/$/ 1/' "$target_dir/../M-H/POSCAR" 
                else
                    echo "NO CONTCAR in $target_dir" >&2
                fi
            fi
        fi
    fi
}

process_m_to_m2h() {
    local target_dir="$1"
    
    if [ -z "$(find "$target_dir" -mindepth 1 -type d)" ]; then

        if [[ "$target_dir" == *"${CONFIG[match]}"* ]]; then
            if [[ "$target_dir" == *"M/ads" ]]; then
            
                if [ -f "$target_dir/CONTCAR" ]; then
                    mkdir -p "$target_dir/../../M-2H/ads" 2>> "${PATHS[log_dir]}/errors"
                    cp "$target_dir/CONTCAR" "$target_dir/../../M-2H/ads/POSCAR" 2>> "${PATHS[log_dir]}/errors" 
                    num=$(awk 'NR==7 {print}' "$target_dir/../../M-2H/ads/POSCAR" | awk '{sum=0; for(i=1; i<=NF; i++) sum+=$i; print sum}')
                    num=$(($num + 9))
                    if ! check_file "$target_dir/../../M-2H/ads/POSCAR"; then
       
                        echo "POSCAR is not a linux format in $target_dir/../../M-2H/ads/POSCAR"

                        dos2unix "$target_dir/../../M-2H/ads/POSCAR"
                    fi
                    echo "$target_dir"
                    sed -i '6s/$/ H/' "$target_dir/../../M-2H/ads/POSCAR" 
                    sed -i "${num}a\0.446598 0.216020 0.433410 T T T " "$target_dir/../../M-2H/ads/POSCAR" 
                    tar=$(awk 'NR==7 {print}' "$target_dir/../../M-2H/ads/POSCAR" | awk '{sum=0; for(i=1; i<=2; i++) sum+=$i; print sum}')
                    
                    tar=$(($tar + 9))
                    echo "$tar"
                    awk -v tar=$tar -v num=$num 'NR==tar {line=$0} NR==num+1 {print line } {print}' "$target_dir/../../M-2H/ads/POSCAR" > "$target_dir/../../M-2H/ads/temp" && mv "$target_dir/../../M-2H/ads/temp" "$target_dir/../../M-2H/ads/POSCAR"
                    awk  -v num=$num 'NR == num+1 { $3 = $3 + 0.1 } { print }' "$target_dir/../../M-2H/ads/POSCAR" > "$target_dir/../../M-2H/ads/temp" && mv "$target_dir/../../M-2H/ads/temp" "$target_dir/../../M-2H/ads/POSCAR"
                    sed -i '7s/$/ 2/' "$target_dir/../../M-2H/ads/POSCAR" 
                else
                    echo "NO CONTCAR in $target_dir" >&2
                fi
            fi
        fi
    fi
}

process_ads_to_bader() {
    local target_dir="$1"
    if [ -z "$(find "$target_dir" -mindepth 1 -type d)" ]; then
        if [[ "$target_dir" == *"${CONFIG[match]}"* ]]; then
            if [[ "$target_dir" == *"/ads" ]]; then
                if validate_poscar "$target_dir/CONTCAR"; then
                    mkdir -p "$target_dir/../bader" 2>> "${PATHS[log_dir]}/errors"
                    cp "$target_dir/CONTCAR" "$target_dir/../bader/POSCAR" 
                    cp "$target_dir/POTCAR" "$target_dir/../bader/POTCAR"
                    cp "$target_dir/KPOINTS" "$target_dir/../bader/KPOINTS"
                    cp "$target_dir/vasp.sbatch" "$target_dir/../bader/vasp.sbatch"
                else
                    echo "NO CONTCAR in $target_dir" >&2
                fi
            fi
        fi
    fi
}

process_FFF() {
    local target_dir="$1"
    if [ -z "$(find "$target_dir" -mindepth 1 -type d)" ]; then
        if [[ "$target_dir" == *"${CONFIG[match]}"* ]]; then
            if  validate_poscar "$target_dir/POSCAR"; then
                awk 'NR>=10 {if ($3 < 0.2) gsub("T", "F")}1' "$target_dir/POSCAR" > "$target_dir/POSCAR.tmp" && mv "$target_dir/POSCAR.tmp" "$target_dir/POSCAR"
            else
                echo "NO POSCAR in $target_dir" >&2
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
                process_m_to_mh "$target_dir"
            done
            ;;
        2)  # ads to bader
            find "${CONFIG[to_dir]}" -mindepth 1 -type d | while read -r target_dir; do
                process_ads_to_bader "$target_dir"
            done
            ;;
        3)  # M to M-2H
            find "${CONFIG[to_dir]}" -mindepth 1 -type d | while read -r target_dir; do
                process_m_to_m2h "$target_dir"
            done
            ;;
        4)  # TTT -> FFF
            find "${CONFIG[to_dir]}" -mindepth 1 -type d | while read -r target_dir; do
                process_FFF "$target_dir"
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