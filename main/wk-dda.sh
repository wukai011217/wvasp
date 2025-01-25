#!/bin/bash
#
# 脚本名称: filename
# 描述: 处理和分析 Bader 数据，输出结果到文件
# 用法: ./filename [OPTIONS]
# 作者: wukai
# 日期: 2024-10-23

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 加载配置和函数
. functions

# 默认变量
declare -A CONFIG=(
    [root_dir]="$(pwd)"
    [file]="ACF.dat"
    [command]="0"
    [number]="1"
)



# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Description:
    Process and analyze Bader charge analysis data from VASP calculations.
    Extracts specific data from files and outputs results to a summary file.

Options:
    -d|-D|-dir,         --dir       Set root directory (default: current directory): directory containing Bader output files
    -f|-F|-file,        --file      Set target file (default: ACF.dat): file to extract data from
    -n|-N|-number,      --number    Set line number to extract (default: 1): specific atomic number to process
    -c|-C|-command,     --command   Set operation command (default: 0)
    -h|-help,           --help      Show this help message

Commands:
    0: Extract and process data from specified line number in Bader output files
    1: Reserved for future use

Examples:
    # Process default line from ACF.dat files
    $(basename "$0")

    # Process specific line from Bader analysis files in target directory
    $(basename "$0") -d /path/to/calcs -f ACF.dat -n 5
EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -dir|-D|-d)
                CONFIG[root_dir]="$2"
                logging 1 "ROOT_DIR set to: ${CONFIG[root_dir]}"
                shift 2
                ;;
            -file|-F|-f)
                CONFIG[file]="$2"
                logging 1 "File set to: ${CONFIG[file]}"
                shift 2
                ;;
            -command|-c|-C)
                CONFIG[command]="$2"
                logging 1 "Command set to: ${CONFIG[command]}"
                shift 2
                ;;
            -number|-n|-N)
                CONFIG[number]=$(($2 + 2))  # 内部处理逻辑，增加偏移量
                logging 1 "Number set to: ${CONFIG[number]}"
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

# 函数：处理 Bader 数据
process_bader() {
    local root_dir="${CONFIG[root_dir]}"
    local file="${CONFIG[file]}"
    local number="${CONFIG[number]}"
    local good_datas_file="${PATHS[work_dir]}/good_datas"



    # 遍历目录
    find "$root_dir" -mindepth 1 -type d | while read -r target_dir; do
        if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
            if [[ -f "$target_dir/${CONFIG[file]}" ]]; then
                # 使用 awk 提取指定行的指定列
                echo " 1 $target_dir" >> "${PATHS[work_dir]}/datas"
                echo " $target_dir" >> "$good_datas_file"
                awk "NR==$number {print \$5}" "$target_dir/${CONFIG[file]}" >> "$good_datas_file"
            else
                echo "Missing ${CONFIG[file]} file in: $target_dir" >> "${PATHS[work_dir]}/bad_datas"
                echo " -1 $target_dir" >> "${PATHS[work_dir]}/datas"
            fi
        fi
    done

    logging 1 "Bader processing completed"
}

# 主程序
main() {
    local command="${CONFIG[command]}"

    case "$command" in
        0)  # 处理 Bader 数据
            logging 1 "Processing Bader data"
            process_bader
            ;;
        1)
            logging 1 "No operation defined for command 1"
            ;;
        help)
            show_help
            ;;
        *)
            error_exit "Invalid command: ${command}"
            ;;
    esac
}

# 日志记录
logging 0
logging 1 "filename started"

{
    printf '=%.0s' {1..100}
    echo
    echo time: $(date "+%Y-%m-%d %H:%M:%S")
    ech
} | tee -a "${PATHS[work_dir]}/datas" "${PATHS[work_dir]}/good_datas" "${PATHS[work_dir]}/bad_datas" > /dev/null

# 启动脚本
parse_arguments "$@"

# 执行主程序
main

# 记录结果
result $? "filename"
logging 1 "filename completed"