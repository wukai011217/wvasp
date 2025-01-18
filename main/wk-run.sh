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

# 默认配置
declare -A CONFIG=(
    [to_dir]="$(pwd)"
    [match]=""
    [screen]="OUTCAR"
    [command]="0"
)

# 作业计数器
declare -i job_count=0
declare -i MAX_JOBS=100



# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Description:
    Submit VASP jobs to the cluster in leaf directories.

Options:
    -d, -dir      Set root directory (default: current directory)
    -m, -match    Set match pattern for directories
    -c, -command  Set operation command (default: 0)
    -h, --help    Show this help message

Commands:
    0: Submit jobs in matching leaf directories
    1: Reserved for future use

Example:
    $(basename "$0") -d /path/to/dir -m "pattern"
EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -dir|-D|-d)
                if [[ "$2" == *"$WORK_DIR"* ]]; then
                    CONFIG[to_dir]="$2"
                else 
                    CONFIG[to_dir]="$(pwd)/$2"
                fi
                logging 1 "Target directory set to: ${CONFIG[to_dir]}"
                shift 2
                ;;
            -match|-M|-m)
                CONFIG[match]="$2"
                logging 1 "Match pattern set to: ${CONFIG[match]}"
                shift 2
                ;;
            -screen|-S|-s)
                CONFIG[screen]="$2"
                logging 1 "Screen file set to: ${CONFIG[screen]}"
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

# 检查必要的VASP输入文件
check_vasp_files() {
    local dir="$1"
    local required_files=("POSCAR" "INCAR" "KPOINTS" "POTCAR")
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$dir/$file" ]]; then
            return 1
        fi
    done
    return 0
}

# 提交VASP作业
submit_vasp_job() {
    local target_dir="$1"
    
    cd "$target_dir"
    echo "$target_dir" 2>> "$WORK_DIR/errors" 1>> "$WORK_DIR/logs"
    
    # 记录作业信息
    ((job_count++))
    echo "$job_count $target_dir" >> "$WORK_DIR/job"
    
    # 实际的作业提交命令（取消注释以启用）
    # sbatch vasp.sbatch >> "$WORK_DIR/job"
}

# 主程序
main() {
    case "${CONFIG[command]}" in
        0)
            find "${CONFIG[to_dir]}" -mindepth 1 -type d | while read -r target_dir; do
                # 检查是否是叶子目录
                if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
                    # 检查目录名是否匹配模式
                    if [[ -z "${CONFIG[match]}" || "$target_dir" == *"${CONFIG[match]}"* ]]; then
                        # 检查必要的VASP文件
                        if check_vasp_files "$target_dir"; then
                            # 检查是否已经有输出文件
                            if ! compgen -G "$target_dir/*${CONFIG[screen]}*" > /dev/null; then
                                submit_vasp_job "$target_dir"
                                
                                # 检查是否达到最大作业数
                                if ((job_count >= MAX_JOBS)); then
                                    logging 1 "Reached maximum job count ($MAX_JOBS)"
                                    break
                                fi
                            fi
                        fi
                    fi
                fi
            done
            ;;
        *)
            echo "Error: ${CONFIG[command]} is not a valid command" >&2
            show_help
            exit 1
            ;;
    esac
}

# 日志记录
logging 0
logging 1 "wk-run started"

# 启动脚本
parse_arguments "$@"

# 执行主程序
main

# 结果检查
result $? "wk-run"