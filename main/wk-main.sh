#!/bin/bash
#
# 脚本名称: wk-main
# 描述: VASP 计算批处理主控脚本
# 用法: wk-main [OPTIONS]
# 作者: wukai
# 创建日期: 2024-10-23
# 更新日期: 2025-02-24

set -e  # 遇到错误立即退出
set -u  # 使用未定义的变量时报错

# 版本信息
VERSION="1.0.0"

# 加载必要的配置文件和函数
. functions

# 重置统计信息
reset_stats

# 默认配置
declare -A CONFIG=(
    # 通用配置
    [command]="0"
    [to_dir]="$(pwd)"
    [match]=""
    [file]="POSCAR"
    [dry_run]=false
    [force]=false
    [verbose]=false
    
    # VASP 作业配置
    [screen]="OUTCAR"
    [job_id_1]=0
    [job_id_2]=1
)

# 函数：显示版本信息
show_version() {
    echo "wk-main version ${VERSION}"
}

# 函数：显示统计信息
show_stats() {
    local duration=$1
    
    logging 1 "Statistics:"
    logging 1 "  Total operations:          ${STATS[total]}"
    logging 1 "  Successfully processed:    ${STATS[processed]}"
    logging 1 "  Failed operations:         ${STATS[failed]}"
    if [[ ${STATS[skipped]} -gt 0 ]]; then
        logging 1 "  Skipped operations:        ${STATS[skipped]}"
    fi
    logging 1 "  Processing time:          ${duration}s"
    
    # 如果有失败，返回非零状态
    if [[ ${STATS[failed]} -gt 0 ]]; then
        return 1
    fi
    return 0
}

# 函数：显示帮助信息
show_help() {
    cat << EOF
wk-main - VASP Calculation Batch Processor v${VERSION}

Usage: $(basename "$0") [OPTIONS]

Description:
    Main script for managing VASP calculations workflow.
    Coordinates multiple sub-scripts for structure preparation,
    pseudopotential generation, and job submission.

Options:
    -to,                --to_dir    Set target directory (default: current directory)
    -m|-M|-match,       --match     Set match pattern for directories
    -c|-C|-command,     --command   Set operation command (default: 0)
    -f|-F|-file,        --file      Set input file (default: POSCAR)
    -screen,            --screen    Set screen file (default: OUTCAR)
    -job,               --job       Set job ID range (default: 0,1)
    -v|-verbose,        --verbose   Enable verbose output
    -d|-dry-run,        --dry-run   Show what would be done without making changes
    -f|-force,          --force     Force overwrite existing files
    -h|-help,           --help      Show this help message
    --version                       Show version information

Commands:
    0: Prepare and run VASP calculations
       - Generate POSCAR files
       - Create POTCAR files
       - Copy input files (KPOINTS, vasp.sbatch)
       - Submit jobs

    1: Process M to M-H conversion
       - Convert M structures to M-H
       - Generate POTCAR files
       - Copy input files
       - Submit jobs

    2: Process calculation results
       - Check calculation status
       - Collect and analyze results

Examples:
    # Prepare and run calculations with verbose output
    $(basename "$0") -to /path/to/dir -m "Fe_*" -c 0 -f POSCAR -v

    # Process M to M-H conversion (dry run)
    $(basename "$0") -to /path/to/calcs -m "M-H" -c 1 -d

    # Check calculation results
    $(basename "$0") -to /path/to/calcs -m "*" -c 2

    # Submit jobs with specific IDs
    $(basename "$0") -to /path/to/calcs -m "Fe_*" -c 0 -job 1 10

Note:
    - Use --dry-run to preview changes without modifying files
    - Use --force to overwrite existing files
    - Use --verbose for detailed progress information
    - All sub-commands inherit the common options
EOF
}

# 函数：执行批量 VASP 流程
run_batch_vasp() {
    local file="$1"
    local to_dir="$2"
    local match="$3"
    
    # 更新统计信息
    ((STATS[total]++))
    
    # 执行 pos-to-all
    logging 1 "Step 1/3: Generating POSCAR files"
    if ! wk-pos.sh -f "${file}" -to "${to_dir}" -m "${match}" \
        ${CONFIG[verbose]} && -v \
        ${CONFIG[dry_run]} && -d \
        ${CONFIG[force]} && -f; then
        logging 1 "Error: Failed to generate POSCAR files"
        ((STATS[failed]++))
        return 1
    fi
    
    # 执行 pot-to-all
    logging 1 "Step 2/3: Creating POTCAR files"
    if ! wk-pot.sh -to "${to_dir}" -m "${match}" \
        ${CONFIG[verbose]} && -v \
        ${CONFIG[dry_run]} && -d \
        ${CONFIG[force]} && -f; then
        logging 1 "Error: Failed to create POTCAR files"
        ((STATS[failed]++))
        return 1
    fi
    
    # 执行 mkf-in-loop
    logging 1 "Step 3/3: Copying input files"
    local success=true
    for input_file in KPOINTS vasp.sbatch; do
        if [[ "${CONFIG[verbose]}" == true ]]; then
            logging 1 "  Processing ${input_file}"
        fi
        
        if ! wk-mkf.sh -f "$SCRIPT_DIR/data/${input_file}" -c 0 \
            -to "${to_dir}" -m "${match}" \
            ${CONFIG[verbose]} && -v \
            ${CONFIG[dry_run]} && -d \
            ${CONFIG[force]} && -f; then
            logging 1 "Error: Failed to copy ${input_file}"
            success=false
            break
        fi
    done
    
    # 检查结果
    if [[ "$success" == true ]]; then
        ((STATS[processed]++))
        return 0
    else
        ((STATS[failed]++))
        return 1
    fi
}

# 函数：执行 M to M-H 流程
run_m_to_m-h() {
    local to_dir="$1"
    local match="$2"
    
    # 更新统计信息
    ((STATS[total]++))
    
    # 执行 pos-to-all
    logging 1 "Step 1/3: Converting M to M-H structures"
    if ! wk-pos.sh -to "${to_dir}" -c 1 \
        ${CONFIG[verbose]} && -v \
        ${CONFIG[dry_run]} && -d \
        ${CONFIG[force]} && -f; then
        logging 1 "Error: Failed to convert M to M-H structures"
        ((STATS[failed]++))
        return 1
    fi
    
    # 执行 pot-to-all
    logging 1 "Step 2/3: Creating POTCAR files"
    if ! wk-pot.sh -to "${to_dir}" -m "${match}" \
        ${CONFIG[verbose]} && -v \
        ${CONFIG[dry_run]} && -d \
        ${CONFIG[force]} && -f; then
        logging 1 "Error: Failed to create POTCAR files"
        ((STATS[failed]++))
        return 1
    fi
    
    # 执行 mkf-in-loop
    logging 1 "Step 3/3: Copying input files"
    local success=true
    for input_file in KPOINTS vasp.sbatch; do
        if [[ "${CONFIG[verbose]}" == true ]]; then
            logging 1 "  Processing ${input_file}"
        fi
        
        if ! wk-mkf.sh -f "$SCRIPT_DIR/data/${input_file}" -c 0 \
            -to "${to_dir}" -m "${match}" \
            ${CONFIG[verbose]} && -v \
            ${CONFIG[dry_run]} && -d \
            ${CONFIG[force]} && -f; then
            logging 1 "Error: Failed to copy ${input_file}"
            success=false
            break
        fi
    done
    
    # 检查结果
    if [[ "$success" == true ]]; then
        ((STATS[processed]++))
        return 0
    else
        ((STATS[failed]++))
        return 1
    fi
}

# 函数：结果处理
result_processing() {
    local file="$1"
    local to_dir="$2"
    local match="$3"
    
    # 更新统计信息
    ((STATS[total]++))
    
    # 执行结果检查
    logging 1 "Processing: Checking calculation results"
    if ! wk-che.sh -to "${to_dir}" -m "${match}" \
        ${CONFIG[verbose]} && -v \
        ${CONFIG[dry_run]} && -d; then
        logging 1 "Error: Failed to check calculation results"
        ((STATS[failed]++))
        return 1
    fi
    
    ((STATS[processed]++))
    return 0
}

# 函数：验证参数
validate_args() {
    # 检查目标目录
    if [[ ! -d "${CONFIG[to_dir]}" ]]; then
        error_exit "Target directory ${CONFIG[to_dir]} does not exist"
    fi
    
    # 检查目标目录权限
    if [[ ! -w "${CONFIG[to_dir]}" ]]; then
        error_exit "Target directory ${CONFIG[to_dir]} is not writable"
    fi
    
    # 检查命令
    case "${CONFIG[command]}" in
        0|1|2)
            :;;
        *)
            error_exit "Invalid command: ${CONFIG[command]}"
            ;;
    esac
    
    # 检查作业 ID 范围
    if [[ ${CONFIG[job_id_1]} -gt ${CONFIG[job_id_2]} ]]; then
        error_exit "Invalid job ID range: ${CONFIG[job_id_1]} > ${CONFIG[job_id_2]}"
    fi
}

# 函数：解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -c|-C|-command|--command)
                CONFIG[command]="$2"
                shift 2
                ;;
            -m|-M|-match|--match)
                CONFIG[match]="$2"
                shift 2
                ;;
            -f|-F|-file|--file)
                CONFIG[file]="$2"
                shift 2
                ;;
            -to|--to_dir)
                CONFIG[to_dir]="$2"
                shift 2
                ;;
            -screen|--screen)
                CONFIG[screen]="$2"
                shift 2
                ;;
            -job|--job)
                if [[ $# -lt 3 ]]; then
                    error_exit "Error: -job requires two values"
                fi
                CONFIG[job_id_1]="$2"
                CONFIG[job_id_2]="$3"
                shift 3
                ;;
            -v|--verbose|-verbose)
                CONFIG[verbose]=true
                shift
                ;;
            -d|--dry-run|-dry-run)
                CONFIG[dry_run]=true
                shift
                ;;
            -f|--force|-force)
                CONFIG[force]=true
                shift
                ;;
            -h|--help|-help)
                show_help
                exit 0
                ;;
            --version)
                show_version
                exit 0
                ;;
            --)
                shift
                break
                ;;
            *)
                error_exit "Error: Unknown option $1"
                ;;
        esac
    done
    
    # 验证参数
    validate_args
    
    # 记录配置
    if [[ "${CONFIG[verbose]}" == true ]]; then
        logging 1 "Configuration:"
        logging 1 "  Command: ${CONFIG[command]}"
        logging 1 "  Target Directory: ${CONFIG[to_dir]}"
        logging 1 "  Match Pattern: ${CONFIG[match]}"
        logging 1 "  Input File: ${CONFIG[file]}"
        logging 1 "  Screen File: ${CONFIG[screen]}"
        logging 1 "  Job ID Range: ${CONFIG[job_id_1]}-${CONFIG[job_id_2]}"
        logging 1 "  Dry Run: ${CONFIG[dry_run]}"
        logging 1 "  Force: ${CONFIG[force]}"
        logging 1 "  Verbose: ${CONFIG[verbose]}"
    fi
}

# 函数：清理临时文件
cleanup() {
    local exit_code=$?
    
    # 删除临时文件
    find "${CONFIG[to_dir]}" -name "*.tmp" -type f -delete 2>/dev/null
    
    # 记录结果
    result $exit_code "wk-main"
    
    exit $exit_code
}

# 函数：信号处理
signal_handler() {
    logging 1 "\nOperation interrupted by user"
    cleanup
    exit 1
}

# 函数：主程序
main() {
    local command="${CONFIG[command]}"
    local start_time=$(date +%s)
    
    # 设置退出和信号处理
    trap cleanup EXIT
    trap signal_handler INT TERM
    
    # 检查必要的命令
    for cmd in awk sed find mv cp mkdir dos2unix; do
        if ! command -v $cmd &>/dev/null; then
            error_exit "Required command not found: $cmd"
        fi
    done
    
    # 处理命令
    case "${command}" in
        0)  # 执行批量 VASP 流程
            logging 1 "Processing: VASP Calculation Preparation"
            if [[ "${CONFIG[dry_run]}" == true ]]; then
                logging 1 "[DRY RUN] Would prepare VASP calculations"
            else
                run_batch_vasp "${CONFIG[file]}" "${CONFIG[to_dir]}" "${CONFIG[match]}"
            fi
            ;;
        1)  # 执行批量 M to M-H 流程
            logging 1 "Processing: M to M-H Conversion"
            if [[ "${CONFIG[dry_run]}" == true ]]; then
                logging 1 "[DRY RUN] Would process M to M-H conversion"
            else
                run_m_to_m-h "${CONFIG[to_dir]}" "${CONFIG[match]}"
            fi
            ;;
        2)  # 结果处理
            logging 1 "Processing: Calculation Results"
            if [[ "${CONFIG[dry_run]}" == true ]]; then
                logging 1 "[DRY RUN] Would process calculation results"
            else
                result_processing "${CONFIG[file]}" "${CONFIG[to_dir]}" "${CONFIG[match]}"
            fi
            ;;
        *)
            error_exit "Invalid command: ${command}"
            ;;
    esac
    
    # 计算运行时间
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # 显示统计信息
    show_stats "$duration"
    return $?
}

# 初始化日志
logging 0
logging 1 "wk-main v${VERSION}"

# 解析命令行参数
parse_arguments "$@"

# 执行主程序
main