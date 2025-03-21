#!/bin/bash
#==============================================================================
# 脚本信息
#==============================================================================
# 名称: wk-dda
# 描述: 处理和分析 Bader 数据，输出结果到文件
# 用法: wk-dda [OPTIONS]
# 作者: wukai
# 版本: 1.0.0
# 日期: 2024-10-23

#==============================================================================
# 初始化
#==============================================================================

# 错误处理
set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 加载外部依赖
. functions

# 版本信息
VERSION="1.0.0"

# 默认配置
declare -A CONFIG=(
    # 基本配置
    [root_dir]="$(pwd)"                  # 源目录
    [file]="ACF.dat"                     # 要分析的文件
    [command]="0"                        # 命令
    [number]="1"                         # 原子编号
    [output_dir]=""                      # 输出目录
    [source_file]="$(basename "$0")"     # 脚本文件
    
    # 运行模式
    [dry_run]=false                      # 模拟运行模式
    [verbose]=false                      # 详细输出模式

)

# 重置统计信息
reset_stats



#==============================================================================
# 函数定义
#==============================================================================

# 函数: show_help
# 描述: 显示脚本的帮助信息
# 参数: 无
# 返回: 0=成功
show_help() {
    cat << EOF
wk-dda (VASP Bader Data Analysis) v${VERSION}

Usage: 
    $(basename "$0") [OPTIONS]

Description:
    Process and analyze Bader charge analysis data from VASP calculations.
    Extracts specific data from files and outputs results to summary files.
    Supports dry-run mode and detailed output options.

Options:
    -d, -D, --dir DIR       Set source directory
                            (default: current directory)
    -f, -F, --file NAME     Set target file to analyze
                            (default: ACF.dat)
    -n, -N, --number NUM    Set atomic number to process
                            (default: 1)
    -o, -O, --output DIR    Set output directory
                            (default: work directory)
    -c, -C, --command NUM   Set operation command
                            (default: 0)
    --dry-run              Show what would be done
    -v, --verbose          Enable detailed output
    -h, --help             Show this help message
    --version              Show version information

Commands:
    0    Process Bader data
         - Extracts charge data for specified atom
         - Creates summary files:
           * good_datas: successful extractions
           * bad_datas: failed extractions
           * datas: complete status log
    1    Reserved for future use

Output Files:
    good_datas  Contains successfully processed data
    bad_datas   Lists directories with missing or invalid files
    datas       Complete processing log with status codes

Examples:
    # Process default atom from ACF.dat files
    $(basename "$0")

    # Process specific atom with custom output
    $(basename "$0") -d /path/to/calcs -n 5 -o /path/to/output

    # Show what would be processed without making changes
    $(basename "$0") -d /path/to/calcs --dry-run

    # Enable verbose output for debugging
    $(basename "$0") -d /path/to/calcs -v

Note:
    The script processes Bader charge analysis data from VASP calculations.
    Use --dry-run to preview operations without making changes.
    Use --verbose for detailed processing information.
EOF
}

# 函数: check_path
# 描述: 检查路径是否存在，如果不存在则创建
# 参数:
#   $1 - 路径
#   $2 - 路径类型 (source/output)
# 返回: 0=成功, 1=失败
check_path() {
    local path="$1"
    local path_type="$2"
    
    if [[ ! -d "$path" ]]; then
        if [[ "$path_type" == "source" ]]; then
            echo "Error: Source directory does not exist: $path" >&2
            exit 1
        elif [[ "${CONFIG[dry_run]}" != true ]]; then
            if ! mkdir -p "$path"; then
                echo "Error: Failed to create directory: $path" >&2
                exit 1
            fi
            logging 1 "Created directory: $path"
        fi
    fi
}

# 函数: init_output_files
# 描述: 初始化输出文件，写入头部信息
# 参数: 无
# 返回: 0=成功
init_output_files() {
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        return 0
    fi
    
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local header="=%.0s"
    
    # 初始化每个输出文件
    for file in "datas" "good_datas" "bad_datas"; do
        {
            printf "$header" {1..100}
            echo -e "\nScript: wk-dda v${VERSION}"
            echo "Time: $timestamp"
            echo -e "\nProcessing results:\n"
        } > "${CONFIG[output_dir]}/$file"
    done
}

# 函数: parse_arguments
# 描述: 解析命令行参数并设置配置
# 参数:
#   $@ - 命令行参数
# 返回: 0=成功, 1=失败
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -dir|-D|-d|--dir)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Directory path required for $1" >&2
                    exit 1
                fi
                # 确保获得绝对路径
                if [[ "$2" = /* ]]; then
                    CONFIG[root_dir]="$2"
                else
                    CONFIG[root_dir]="$(pwd)/$2"
                fi
                logging 1 "Source directory set to: ${CONFIG[root_dir]}"
                shift 2
                ;;
            -file|-F|-f|--file)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: File name required for $1" >&2
                    exit 1
                fi
                CONFIG[file]="$2"
                logging 1 "Target file set to: ${CONFIG[file]}"
                shift 2
                ;;
            -number|-n|-N|--number)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Number required for $1" >&2
                    exit 1
                fi
                if [[ ! "$2" =~ ^[0-9]+$ ]]; then
                    echo "Error: Invalid number: $2" >&2
                    exit 1
                fi
                CONFIG[number]=$(($2 + 2))  # 内部处理逻辑，增加偏移量
                logging 1 "Atomic number set to: $2 (internal: ${CONFIG[number]})"
                shift 2
                ;;
            -output|-o|-O|--output)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Directory path required for $1" >&2
                    exit 1
                fi
                # 确保获得绝对路径
                if [[ "$2" = /* ]]; then
                    CONFIG[output_dir]="$2"
                else
                    CONFIG[output_dir]="$(pwd)/$2"
                fi
                logging 1 "Output directory set to: ${CONFIG[output_dir]}"
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
            --dry-run|--verbose|-h|--help|--version)
                if parse_common_args "wk-dda" "$1"; then
                    shift
                    continue
                fi
                ;;
            --)
                shift
                break
                ;;
            *)
                echo "Error: Invalid option: $1" >&2
                show_help
                exit 1
                ;;
        esac
    done
    
    # 设置默认输出目录
    if [[ -z "${CONFIG[output_dir]}" ]]; then
        CONFIG[output_dir]="${PATHS[work_dir]}"
    fi
    
    # 检查路径
    check_path "${CONFIG[root_dir]}" "source"
    check_path "${CONFIG[output_dir]}" "output"
}

# 函数: process_directory
# 描述: 处理单个目录中的 Bader 数据
# 参数:
#   $1 - 目录路径
# 返回: 0=成功
process_directory() {
    local target_dir="$1"
    local file="${CONFIG[file]}"
    local number="${CONFIG[number]}"
    local target_file="$target_dir/$file"
    local rel_path="${target_dir#${CONFIG[root_dir]}/}"
    
    update_stats "total"
    
    if [[ "${CONFIG[verbose]}" == true ]]; then
        logging 1 "Processing directory: $rel_path"
    fi
    
    # 检查文件是否存在
    if [[ ! -f "$target_file" ]]; then
        if [[ "${CONFIG[dry_run]}" == true ]]; then
            logging 1 "[DRY RUN] Would skip missing file: $target_file"
            return 1
        fi
        echo "Missing $file in: $rel_path" >> "${CONFIG[output_dir]}/bad_datas"
        echo " -1 $rel_path" >> "${CONFIG[output_dir]}/datas"
        update_stats "failed"
        return 1
    fi
    
    # 检查文件是否可读
    if [[ ! -r "$target_file" ]]; then
        if [[ "${CONFIG[dry_run]}" == true ]]; then
            logging 1 "[DRY RUN] Would skip unreadable file: $target_file"
            return 1
        fi
        echo "Cannot read $file in: $rel_path" >> "${CONFIG[output_dir]}/bad_datas"
        echo " -1 $rel_path" >> "${CONFIG[output_dir]}/datas"
        update_stats "failed"
        return 1
    fi
    
    # 如果是模拟运行模式
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would process file: $target_file"
        return 0
    fi
    
    # 提取数据
    local data
    data=$(awk -v num="$number" 'NR==num {print $5}' "$target_file" 2>/dev/null)
    
    if [[ -n "$data" ]]; then
        echo " 1 $rel_path" >> "${CONFIG[output_dir]}/datas"
        echo " $rel_path" >> "${CONFIG[output_dir]}/good_datas"
        echo " $data" >> "${CONFIG[output_dir]}/good_datas"
        update_stats "success"
        
        if [[ "${CONFIG[verbose]}" == true ]]; then
            logging 1 "Successfully processed: $rel_path (value: $data)"
        fi
    else
        echo "Failed to extract data from $file in: $rel_path" >> "${CONFIG[output_dir]}/bad_datas"
        echo " -1 $rel_path" >> "${CONFIG[output_dir]}/datas"
        update_stats "failed"
        
        if [[ "${CONFIG[verbose]}" == true ]]; then
            logging 1 "Failed to process: $rel_path"
        fi
    fi
}

# 函数: process_bader
# 描述: 处理 Bader 电荷分析数据
# 参数:
#   $1 - 数据文件路径
#   $2 - 原子编号
# 返回: 0=成功, 1=失败
process_bader() {
    local start_time=$(date +%s)
    
    # 初始化输出文件
    init_output_files
    
    # 显示配置信息
    if [[ "${CONFIG[verbose]}" == true ]]; then
        logging 1 "Configuration:"
        logging 1 "  Source directory: ${CONFIG[root_dir]}"
        logging 1 "  Target file: ${CONFIG[file]}"
        logging 1 "  Atomic number: $((${CONFIG[number]} - 2))"
        logging 1 "  Output directory: ${CONFIG[output_dir]}"
        logging 1 "  Dry run mode: ${CONFIG[dry_run]}"
        logging 1 "  Verbose mode: ${CONFIG[verbose]}"
    fi
    
    # 遍历目录
    find "${CONFIG[root_dir]}" -mindepth 1 -type d | while read -r target_dir; do
        # 检查是否是叶子目录
        if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
            process_directory "$target_dir"
        fi
    done
    
    # 显示统计信息
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    logging 1 "\nProcessing Summary:"
    logging 1 "  Total directories: ${STATS[total]}"
    logging 1 "  Successful: ${STATS[success]}"
    logging 1 "  Failed: ${STATS[failed]}"
    logging 1 "  Duration: ${duration} seconds"
    
    # 如果有失败的情况，返回非零状态
    [[ ${STATS[failed]} -eq 0 ]]
}

#==============================================================================
# 程序入口
#==============================================================================

# 函数: main
# 描述: 主程序入口
# 参数: 无
# 返回: 0=成功
main() {
    case "${CONFIG[command]}" in
        0)
            if [[ "${CONFIG[dry_run]}" == true ]]; then
                logging 1 "Running in dry-run mode - no files will be modified"
            fi
            
            if ! process_bader; then
                if [[ "${CONFIG[dry_run]}" != true ]]; then
                    logging 1 "Some files failed to process. Check ${CONFIG[output_dir]}/bad_datas for details."
                fi
                return 1
            fi
            ;;
            
        1)
            logging 1 "Command 1 is reserved for future use"
            ;;
            
        help)
            show_help
            ;;
            
        *)
            echo "Error: Invalid command: ${CONFIG[command]}" >&2
            show_help
            exit 1
            ;;
    esac
}

#==============================================================================
# 脚本执行入口
#==============================================================================

# 初始化脚本
initialize || { logging 2 "${CONFIG[source_file]} : Failed to initialize script"; exit 1; }

# 解析命令行参数
parse_arguments "$@" || { logging 2 "${CONFIG[source_file]} : Failed to parse arguments"; exit 1; }

# 记录运行环境
log_environment

# 执行主程序
main || { logging 2 "${CONFIG[source_file]} : Failed to execute main function"; exit 1; }