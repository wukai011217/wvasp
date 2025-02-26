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

# 版本信息
VERSION="1.0.0"

# 默认配置
declare -A CONFIG=(
    [to_dir]=""
    [file]="print_out"
    [command]="0"
    [match]=""
    [max_tail_lines]=10     # 错误日志显示的最大行数
    [source_file]="$(basename "$0")"     # 脚本文件

    # 运行模式
    [dry_run]=false                      # 模拟运行模式
    [verbose]=false                      # 详细输出模式
    [backup]=true                        # 备份模式
)

# 重置统计信息
reset_stats




# 帮助信息
show_help() {
    cat << EOF
wk-che (VASP Calculation Checker) v${VERSION}

Usage: 
    $(basename "$0") [OPTIONS]

Description:
    Check VASP calculation results, validate output files, and collect data.
    Lists successful calculations and records error information for failed ones.
    Analyzes convergence and energy information from output files.

Required Files:
    - OUTCAR:    VASP output file containing calculation details
    - print_out: Additional output file with energy information

Options:
    -d, -D, --dir DIR     Set root directory for analysis
                          (default: current directory)
    -m, -M, --match PAT   Set match pattern for directories
                          (default: process all directories)
    -f, -F, --file NAME   Set output file to analyze
                          (default: print_out)
    -c, -C, --command NUM Set operation command (default: 0)
    -h, --help           Show this help message and exit
    -v, --version        Show version information

Commands:
    0    Check calculation status and collect data
         - Validates OUTCAR convergence
         - Analyzes energy information
         - Records success/failure status
    1    Reserved for future use

Output Files:
    - datas:      Status summary of all calculations
    - good_datas: Details of successful calculations
    - bad_datas:  Error logs and details of failed calculations

Examples:
    # Check calculations in current directory
    $(basename "$0")

    # Check calculations in specific directory with pattern matching
    $(basename "$0") -d /path/to/calcs -m "Fe_*"

    # Show version information
    $(basename "$0") -v

Note:
    Exit codes in datas file:
     1: Successful calculation
    -1: Unexpected termination
    -2: Convergence not reached
EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -to)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Directory path required for $1" >&2
                    exit 1
                fi
                CONFIG[to_dir]="$2"
                logging 1 "TO_DIR set to: ${CONFIG[to_dir]}"
                shift 2
                ;;
            -file|-F|-f|--file)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: File name required for $1" >&2
                    exit 1
                fi
                CONFIG[file]="$2"
                logging 1 "File to analyze: ${CONFIG[file]}"
                shift 2
                ;;
            -command|-c|-C|--command)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Command number required for $1" >&2
                    exit 1
                fi
                if [[ ! "$2" =~ ^[0-9]+$ ]]; then
                    echo "Error: Command must be a number" >&2
                    exit 1
                fi
                CONFIG[command]="$2"
                logging 1 "Command set to: ${CONFIG[command]}"
                shift 2
                ;;
            -match|-M|-m|--match)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Match pattern required for $1" >&2
                    exit 1
                fi
                CONFIG[match]="$2"
                logging 1 "Pattern for matching directories: ${CONFIG[match]}"
                shift 2
                ;;
            # 运行模式
            --dry-run)
                CONFIG[dry_run]=true
                logging 1 "Dry run mode enabled"
                shift 1
                ;;
            --verbose)
                CONFIG[verbose]=true
                logging 1 "Verbose output enabled"
                shift 1
                ;;
            --no-backup)
                CONFIG[backup]=false
                logging 1 "Backup mode disabled"
                shift 1
                ;;
            
            # 常规选项
            -h|--help)
                show_help
                shift 1
                return 0
                ;;
            --version)
                echo "${CONFIG[source_file]} : version $VERSION"
                shift 1
                return 0
                ;;
            --)
                shift
                break
                ;;
            *)
                if [[ "$1" == -* ]]; then
                    logging 2 "${CONFIG[source_file]}: Invalid option: $1"
                    show_help
                    return 1
                fi
                break
                ;;
        esac
    done
}

# 检查计算是否收敛
check_convergence() {
    local outcar="$1"
    local output_file="$2"
    
    # 检查OUTCAR文件
    if [[ ! -f "${outcar}" ]]; then
        return 1
    fi
    
    # 检查是否包含收敛信息
    if ! grep -q "reached" "${outcar}"; then
        return 2
    fi
    
    # 检查输出文件
    if [[ -f "${output_file}" ]] && ! grep -q "reached" "${output_file}"; then
        return 3
    fi
    
    return 0
}

# 记录错误信息
log_error() {
    local target_dir="$1"
    local error_type="$2"
    local work_dir="$3"
    local output_file="$4"
    local max_lines="${CONFIG[max_tail_lines]}"
    
    # 写入错误分隔符
    echo "====================================================="  >> "${work_dir}/bad_datas"
    
    # 根据错误类型记录信息
    case "$error_type" in
        1)
            echo " -1 $target_dir" >> "${work_dir}/datas"
            echo "OUTCAR file missing | $target_dir" >> "${work_dir}/bad_datas"
            ;;
        2)
            echo " -1 $target_dir" >> "${work_dir}/datas"
            echo "Unexpected end of calculation | $target_dir" >> "${work_dir}/bad_datas"
            ;;
        3)
            echo " -2 $target_dir" >> "${work_dir}/datas"
            echo "Convergence not reached | $target_dir" >> "${work_dir}/bad_datas"
            ;;
    esac
    
    echo "" >> "${work_dir}/bad_datas"
    
    # 记录输出文件的最后几行
    if [[ -f "${output_file}" ]]; then
        tail -n "${max_lines}" "${output_file}" >> "${work_dir}/bad_datas" 2>/dev/null
    else
        echo "Missing output file: ${output_file}" >> "${work_dir}/bad_datas"
    fi
}

# 记录成功信息
log_success() {
    local target_dir="$1"
    local work_dir="$2"
    local output_file="$3"
    
    echo " 1 $target_dir" >> "${work_dir}/datas"
    echo "$target_dir" >> "${work_dir}/good_datas"
    
    # 提取能量信息
    if [[ -f "${output_file}" ]]; then
        grep "E0" "${output_file}" | tail -n 1 >> "${work_dir}/good_datas"
    fi
}

# 函数：检查单个目录
check_directory() {
    local to_dir="$1"              # 从 CONFIG 中获取根目录
    local match="${CONFIG[match]}"   # 从 CONFIG 中获取匹配模式
    local file="${CONFIG[file]}"     # 从 CONFIG 中获取要分析的文件
    local work_dir="${PATHS[work_dir]}"
    # 找到 to_dir 下的所有目录，并逐一处理
    while IFS= read -r target_dir; do
        # 检查是否为叶目录（无子目录）
        if [[ -z "$(find "$target_dir" -mindepth 1 -type d 2>/dev/null)" ]]; then
            # 文件夹名称需匹配指定模式
            if [[ -z "$match" || "$target_dir" == *"${match}"* ]]; then
                update_stats "total"
                
                local outcar="${target_dir}/OUTCAR"
                local output_file="${target_dir}/${file}"
                
                # 检查收敛状态
                check_convergence "$outcar" "$output_file"
                local conv_status=$?
                
                case $conv_status in
                    0)  # 成功
                        log_success "$target_dir" "$work_dir" "$output_file"
                        update_stats "success"
                        ;;
                    *)  # 失败
                        log_error "$target_dir" "$conv_status" "$work_dir" "$output_file"
                        update_stats "failed"
                        ;;
                esac
            fi
        fi
    done < <(find "$to_dir" -mindepth 1 -type d)
    
    return 0
}


# 主程序
main() {
    local to_dir="${CONFIG[to_dir]}"
    local command="${CONFIG[command]}"
    local start_time=$(date +%s)

    # 检查配置并显示
    check_config_and_display || {
        logging 2 "${CONFIG[source_file]} : Failed to check configuration"
        return 1
    }

    # 定义命令映射
    declare -A COMMAND_MAP=(
        [0]="Check calculation status:check_directory"
    )

    # 处理命令
    case "${CONFIG[command]}" in
        help)
            show_help
            return 0
            ;;
        --version)
            echo "${CONFIG[source_file]} : version $VERSION"
            return 0
            ;;
        [0])
            # 解析命令信息
            local IFS=':'
            local cmd_info=(${COMMAND_MAP[${CONFIG[command]}]})
            unset IFS
            local description="${cmd_info[0]}"
            local processor="${cmd_info[1]}"
            
            # 显示命令信息
            [[ "${CONFIG[dry_run]}" == true ]] && \
                logging 1 "[DRY RUN] Command ${CONFIG[command]}: $description"
            logging 1 "Processing: $description"
            echo "${CONFIG[source_file]} : Processing: $description"
            echo "${CONFIG[to_dir]}"

            # 初始化数据文件
            {
                printf '=%.0s' {1..100}
                echo
                echo "Time: $(date "+%Y-%m-%d %H:%M:%S")"
                echo
            } | tee -a "${PATHS[work_dir]}/datas" "${PATHS[work_dir]}/good_datas" "${PATHS[work_dir]}/bad_datas" > /dev/null

            # 执行命令处理函数
            $processor "${CONFIG[to_dir]}" || {
                local exit_code=$?
                logging 2 "${CONFIG[source_file]} : Failed to execute command: $description"
                return $exit_code
            }
            ;;
        *)
            logging 2 "${CONFIG[source_file]} : Invalid command: ${CONFIG[command]}"
            return 1
            ;;
    esac

    # 计算和显示统计信息
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    show_stats "$duration"

    return 0
}

#==============================================================================
# 脚本执行入口
#==============================================================================

# 初始化脚本环境
initialize || {
    logging 2 "${CONFIG[source_file]} : Failed to initialize script"
    exit 1
}

# 解析命令行参数
parse_arguments "$@" || {
    logging 2 "${CONFIG[source_file]} : Failed to parse arguments"
    exit 1
}

# 记录运行环境信息
log_environment

# 执行主程序
main || {
    logging 2 "${CONFIG[source_file]} : Failed to execute main function"
    exit 1
}