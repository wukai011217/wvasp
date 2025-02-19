#!/bin/bash
#
# 脚本名称: check-res
# 描述: 检查计算结果是否正确，对正确的结果列出文件夹，对错误的结果记录错误信息
# 用法: ./check-res [OPTIONS]
# 作者: wukai
# 日期: 2024-10-23

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 加载配置和函数
. functions

# 默认配置
declare -A CONFIG=(
    [root_dir]="$(pwd)"
    [file]="print_out"
    [command]="0"
    [match]=""
)



# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Description:
    Check VASP calculation results, validate output files, and collect data.
    Lists successful calculations and records error information for failed ones.

Options:
    -d|-D|-dir,         --dir       Set root directory (default: current directory): directory containing VASP calculations
    -m|-M|-match,       --match     Set match pattern for directories: pattern to filter target directories
    -c|-C|-command,     --command   Set operation command (default: 0)
    -h|-help,           --help      Show this help message

Commands:
    0: Check calculation status and collect data from matching directories
    1: Reserved for future use

Examples:
    # Check calculations in current directory
    $(basename "$0")

    # Check calculations in specific directory with pattern matching
    $(basename "$0") -d /path/to/calcs -m "Fe_*"
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
                logging 1 "File to analyze: ${CONFIG[file]}"
                shift 2
                ;;
            -command|-c|-C)
                CONFIG[command]="$2"
                logging 1 "Command set to: ${CONFIG[command]}"
                shift 2
                ;;
            -match|-M|-m)
                CONFIG[match]="$2"
                logging 1 "Pattern for matching directories: ${CONFIG[match]}"
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
                echo "Error: $1 is not a valid option." >&2
                show_help
                exit 1
                ;;
        esac
    done
}

# 函数：检查单个目录
check_directory() {
    local root_dir="$1"             # 从 CONFIG 中获取根目录
    local match="${CONFIG[match]}"   # 从 CONFIG 中获取匹配模式
    local file="${CONFIG[file]}"     # 从 CONFIG 中获取要分析的文件
    local work_dir="${PATHS[work_dir]}"


    # 找到 root_dir 下的所有目录，并逐一处理
    find "$root_dir" -mindepth 1 -type d | while read -r target_dir; do
        # 检查是否为叶目录（无子目录）
        if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
            # 文件夹名称需匹配指定模式
            if [[ "$target_dir" == *"${match}"* ]]; then

                local outcar="${target_dir}/OUTCAR"
                local output_file="${target_dir}/${file}"

                # 检查是否存在 OUTCAR 且包含 "reached" 字符
                if [[ ! -f "${outcar}" ]] || ! grep -q "reached" "${outcar}"; then
                    echo " -1 $target_dir" >> "${work_dir}/datas"
                    echo "=====================================================" >> "${work_dir}/bad_datas"
                    echo "unexpected end of calculation | $target_dir" >> "${work_dir}/bad_datas"
                    echo "" >> "${work_dir}/bad_datas"
                    tail -n 10 "${target_dir}/print_out" >> "${work_dir}/bad_datas" 2>> "${work_dir}/bad_datas" || echo "Missing print_out file in: $target_dir"
                else
                    # 计算结果正确
                    echo " 1 $target_dir" >> "${work_dir}/datas"
                    echo "$target_dir" >> "${work_dir}/good_datas"
       
                    # 提取 print_out 中的 "E0"，记录最后一行
                    if [[ -f "${output_file}" ]]; then
                        grep "E0" "${output_file}" | tail -n 1 >> "${work_dir}/good_datas"
                        grep  "reached" "${output_file}" >> "${work_dir}/good_datas"|| echo "unreached" >> "${work_dir}/good_datas"
                    fi
                fi
            fi
        fi
    done
}

# 主程序
main() {
    local root_dir="${CONFIG[root_dir]}"
    local command="${CONFIG[command]}"

    # 检查目标目录是否存在
    if [[ ! -d "${root_dir}" ]]; then
        error_exit "Root directory ${root_dir} does not exist."
    fi

    case "${command}" in
        0)
            check_directory ${CONFIG[root_dir]}
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
logging 1 "check-res started"

{
    printf '=%.0s' {1..100}
    echo
    echo time: $(date "+%Y-%m-%d %H:%M:%S")
    echo
} | tee -a "${PATHS[work_dir]}/datas" "${PATHS[work_dir]}/good_datas" "${PATHS[work_dir]}/bad_datas" > /dev/null

# 启动脚本
parse_arguments "$@"

# 执行主程序
main

# 记录结果
result $? "check-res"
logging 1 "check-res completed"