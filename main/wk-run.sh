#!/bin/bash
#==============================================================================
# 脚本信息
#==============================================================================
# 名称: wk-run
# 描述: 运行 VASP 计算任务，检查必要文件并提交作业
# 用法: wk-run [OPTIONS]
# 作者: wukai
# 版本: 1.0.0
# 日期: 2024-01-18

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
    [run_dir]="$(pwd)"                   # 运行目录
    [to_dir]="$(pwd)"                    # 目标目录
    [match]=""                           # 匹配模式
    [screen]="OUTCAR"                    # 输出文件
    [command]="0"                        # 命令
    [max_jobs]=100                       # 最大作业数
    [source_file]="$(basename "$0")"     # 脚本文件
    
    # 运行模式
    [dry_run]=false                      # 模拟运行模式
    [verbose]=false                      # 详细输出模式
)

# 作业计数器
declare -i job_count=0

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
wk-run (VASP 作业提交工具) v${VERSION}

Usage: 
    $(basename "$0") [OPTIONS]

Description:
    在集群上提交和管理 VASP 计算作业。检查必要的输入文件，并在队列限制下
    处理作业提交。支持作业模板和不同的计算队列。

必需文件:
    • POSCAR:  结构文件
    • INCAR:   输入参数
    • KPOINTS: 能带采样点
    • POTCAR:  赫斯势能

Options:
    目录控制:
        -d, -D, --dir DIR     设置提交作业的根目录
                              (默认: 当前目录)
        -m, -M, --match PAT   设置目录匹配模式
                              (默认: 处理所有目录)
    
    作业控制:
        -s, -S, --screen FILE 设置作业状态检查文件
                              (默认: OUTCAR)
    
    操作控制:
        -c, -C, --command NUM 设置操作命令 (见下方命令说明)
                              (默认: 0)
    
    安全选项:
        -n, --dry-run        模拟运行，不实际提交作业
    
    通用选项:
        -h, --help           显示帮助信息
        --version            显示版本信息

命令说明:
    [0] 提交新的 VASP 作业
        • 检查必要的文件
        • 遵循作业限制 (最多 ${CONFIG[max_jobs]} 个)
        • 跳过已有输出的目录

    [1] 重新提交失败的作业
        • 基于 check-res 的结果
        • 仅处理失败的作业

示例:
    # 在当前目录提交作业
    $(basename "$0")

    # 在指定目录下使用模式匹配提交作业
    $(basename "$0") -d /path/to/calcs -m "Fe_*"

    # 模拟运行，不实际提交作业
    $(basename "$0") --dry-run

注意:
    • 脚本会自动跳过已有输出文件的目录，以避免重复提交
    • 使用 --screen 参数可指定检查的输出文件
    • 最多同时运行 ${CONFIG[max_jobs]} 个作业
EOF
}

# 函数: parse_arguments
# 描述: 解析命令行参数并设置配置
# 参数:
#   $@ - 命令行参数
# 返回: 0=成功, 1=失败
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

# 函数: check_vasp_files
# 描述: 检查必要的 VASP 输入文件
# 参数:
#   $1 - 目标目录路径
# 返回: 0=成功, 1=失败
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

# 函数: submit_vasp_job
# 描述: 提交 VASP 作业
# 参数:
#   $1 - 目标目录路径
# 返回: 0=成功, 1=失败
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

# 函数: check_work_directory
# 描述: 检查并创建工作目录
# 参数: 无
# 返回: 0=成功, 1=失败
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

# 函数: submit_new_jobs
# 描述: 提交新作业
# 参数: 无
# 返回: 0=成功, 1=失败
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

# 函数: resubmit_failed_jobs
# 描述: 重新提交失败的作业
# 参数: 无
# 返回: 0=成功, 1=失败
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

#==============================================================================
# 程序入口
#==============================================================================

# 函数: main
# 描述: 主程序入口
# 参数: 无
# 返回: 0=成功
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