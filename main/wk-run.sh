#!/bin/bash
#
# 脚本名称: wk-run
# 描述: 运行VASP计算任务，检查必要文件并提交作业
# 用法: ./wk-run [OPTIONS]
# 作者: wukai
# 日期: 2024-01-18

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 加载配置和函数
. functions

# 版本信息
VERSION="1.0.0"

# 默认配置
declare -A CONFIG=(
    [run_dir]="$(pwd)"
    [to_dir]="$(pwd)"
    [match]=""
    [screen]="OUTCAR"
    [command]="0"
    [max_jobs]=100        # 最大作业数
    [source_file]="$(basename "$0")"     # 脚本文件

    [dry_run]=false       # 模拟运行模式
    [verbose]=false       # 详细输出模式
    [backup]=true         # 备份模式
)

# 作业计数器
declare -i job_count=0



# 帮助信息
show_help() {
    cat << EOF
wk-run (VASP Job Submission) v${VERSION}

Usage: 
    $(basename "$0") [OPTIONS]

Description:
    Submit and manage VASP calculation jobs on the cluster.
    Checks for required input files and handles job submission with queue limits.
    Supports job templates and different queues.
11
Required Files:
    - POSCAR:  Structure file
    - INCAR:   Input parameters
    - KPOINTS: k-points settings
    - POTCAR:  Pseudopotentials

Options:
    -d, -D, --dir DIR      Set root directory for submissions
                           (default: current directory)
    -m, -M, --match PAT    Set match pattern for directories
                           (default: process all directories)
    -s, -S, --screen FILE  Set screen file for job status check
                           (default: OUTCAR)
    -t, -T, --template FILE Set job script template
                           (default: use system template)
    -q, -Q, --queue NAME   Set queue for job submission
                           (default: normal)
    -n, --dry-run         Show what would be done without submitting
    -c, -C, --command NUM Set operation command (default: 0)
    -h, --help            Show this help message and exit
    -v, --version         Show version information

Commands:
    0    Submit new VASP jobs
         - Checks required files
         - Respects job limit (${CONFIG[max_jobs]} max)
         - Skips directories with existing output
    1    Resubmit failed jobs from check-res results

Examples:
    # Submit jobs in current directory
    $(basename "$0")

    # Submit jobs with custom template and queue
    $(basename "$0") -t custom.sbatch -q gpu

    # Submit jobs in specific directory with pattern matching
    $(basename "$0") -d /path/to/calcs -m "Fe_*"

    # Show what would be done without submitting
    $(basename "$0") --dry-run

Note:
    The script will automatically skip directories that already
    have output files (specified by --screen) to avoid duplicate
    submissions.
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
                # 确保获得绝对路径
                if [[ "$2" = /* ]]; then
                    CONFIG[to_dir]="$2"
                else
                    CONFIG[to_dir]="$(pwd)/$2"
                fi
                logging 1 "Target directory set to: ${CONFIG[to_dir]}"
                shift 2
                ;;
            -match|-M|-m|--match)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Match pattern required for $1" >&2
                    exit 1
                fi
                CONFIG[match]="$2"
                logging 1 "Match pattern set to: ${CONFIG[match]}"
                shift 2
                ;;
            -screen|-S|-s|--screen)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Screen file required for $1" >&2
                    exit 1
                fi
                CONFIG[screen]="$2"
                logging 1 "Screen file set to: ${CONFIG[screen]}"
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
            --dry-run)
                CONFIG[dry_run]=true
                logging 1 "Dry run mode enabled"
                shift
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
            -h|--help)
                show_help
                exit 0
                ;;
            --version)
                echo "wk-run version ${VERSION}"
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

# 检查必要的VASP输入文件
check_vasp_files() {
    local dir="$1"
    local missing_files=()
    local required_files=("POSCAR" "INCAR" "KPOINTS" "POTCAR")
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$dir/$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        logging 1 "Missing required files in $dir: ${missing_files[*]}"
        return 1
    fi
    return 0
}

# 提交VASP作业
submit_vasp_job() {
    local target_dir="$1"
    local dry_run="${CONFIG[dry_run]}"
    local max_jobs="${CONFIG[max_jobs]}"
    
    # 检查作业数量限制
    if ((job_count >= max_jobs)); then
        logging 1 "Reached maximum job count ($max_jobs)"
        return 1
    fi
    
    cd "$target_dir" || {
        logging 1 "Error: Failed to change to directory $target_dir"
        return 1
    }
    
    
    # 记录作业信息
    ((job_count+=1))
    echo "$job_count $target_dir" >> "${PATHS[work_dir]}/job"
    
    # 提交作业
    if [[ "$dry_run" == true ]]; then
        logging 1 "[DRY RUN] Would submit job in: $target_dir"
    else
        if sbatch vasp.sbatch >> "${PATHS[work_dir]}/job" 2>/dev/null; then
            logging 1 "Successfully submitted job in: $target_dir"
        else
            logging 1 "Failed to submit job in: $target_dir"
            return 1
        fi
    fi
    
    return 0
}

# 检查并创建工作目录
check_work_directory() {
    local work_dir="${PATHS[work_dir]}"
    
    # 检查并创建工作目录
    if [[ ! -d "$work_dir" ]]; then
        mkdir -p "$work_dir" || {
            logging 1 "Error: Failed to create work directory: $work_dir"
            return 1
        }
    fi
    
    # 初始化作业日志文件
    echo "# Job submission log - $(date '+%Y-%m-%d %H:%M:%S')" > "$work_dir/job"
    echo "# Directory: ${CONFIG[to_dir]}" >> "$work_dir/job"
    echo "# Pattern: ${CONFIG[match]:-'all'}" >> "$work_dir/job"
    echo "---" >> "$work_dir/job"
    
    return 0
}

# 提交新作业
submit_new_jobs() {
    local to_dir="${CONFIG[to_dir]}"
    local match="${CONFIG[match]}"
    local screen="${CONFIG[screen]}"
    local processed_count=0
    local submitted_count=0
    local error_count=0
    
    
    # 遍历目录
    while IFS= read -r target_dir; do
        # 检查是否为叶目录
        if [[ -z "$(find "$target_dir" -mindepth 1 -type d 2>/dev/null)" ]]; then
            # 检查目录名是否匹配模式
            if [[ -z "$match" || "$target_dir" == *"${match}"* ]]; then
                ((processed_count++))
                
                # 检查是否已经有输出文件
                if compgen -G "$target_dir/*${screen}*" > /dev/null; then
                    logging 1 "Skipping $target_dir: Output file exists"
                    continue
                fi
                
                # 检查必要的VASP文件
                if check_vasp_files "$target_dir"; then
                    if submit_vasp_job "$target_dir"; then
                        ((submitted_count++))
                    else
                        ((error_count++))
                    fi
                else
                    ((error_count++))
                fi
                
                # 检查是否达到最大作业数
                if ((job_count >= CONFIG[max_jobs])); then
                    logging 1 "Reached maximum job count (${CONFIG[max_jobs]})"
                    break
                fi
            fi
        fi
    done < <(find "$to_dir" -mindepth 1 -type d)
    
    # 输出统计信息
    logging 1 "Summary:"
    logging 1 "- Processed directories: $processed_count"
    logging 1 "- Submitted jobs: $submitted_count"
    logging 1 "- Errors: $error_count"
    
    return 0
}

# 重新提交失败的作业
resubmit_failed_jobs() {
    local datas_file="${PATHS[work_dir]}/datas"
    local resubmitted_count=0
    local error_count=0
    
    if [[ ! -f "$datas_file" ]]; then
        logging 1 "Error: Data file not found: $datas_file"
        return 1
    fi
    
    logging 1 "Resubmitting failed jobs..."
    
    # 遍历失败的作业
    while IFS= read -r target_dir; do
        if [[ -d "$target_dir" ]]; then
            if submit_vasp_job "$target_dir"; then
                ((resubmitted_count++))
            else
                ((error_count++))
            fi
        else
            logging 1 "Directory not found: $target_dir"
            ((error_count++))
        fi
        cd "${CONFIG[run_dir]}" || {
            logging 1 "Error: Failed to change to directory $target_dir"
        }
        # 检查是否达到最大作业数
        if ((job_count >= CONFIG[max_jobs])); then
            logging 1 "Reached maximum job count (${CONFIG[max_jobs]})"
            break
        fi
    done < <(grep " -[12] " "$datas_file" | awk '{print $2}' | tr -d ' ')
    
    # 输出统计信息
    logging 1 "Resubmission summary:"
    logging 1 "- Resubmitted jobs: $resubmitted_count"
    logging 1 "- Errors: $error_count"
    
    return 0
}

# 主程序
main() {
    local start_time=$(date +%s)
    
    # 检查配置并显示
    check_config_and_display || {
        logging 2 "${CONFIG[source_file]} : Failed to check configuration"
        return 1
    }
    
    # 初始化工作目录
    check_work_directory || {
        logging 2 "${CONFIG[source_file]} : Failed to initialize work directory"
        return 1
    }

    # 定义命令映射
    declare -A COMMAND_MAP=(
        [0]="Submit new VASP jobs:submit_new_jobs"
        [1]="Resubmit failed jobs:resubmit_failed_jobs"
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
        [0-1])
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

            # 初始化作业日志文件
            {
                echo "# Job submission log - $(date '+%Y-%m-%d %H:%M:%S')"
                echo "# Directory: ${CONFIG[to_dir]}"
                echo "# Pattern: ${CONFIG[match]:-'all'}"
                echo "---"
            } > "${PATHS[work_dir]}/job"

            # 执行命令处理函数
            $processor || {
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