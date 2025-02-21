#!/bin/bash
#
# 脚本名称: vasp_batch_processor.sh
# 描述: 给出一个 xsd 结构，生成多种元素的 VASP 输入文件并运行 VASP
# 用法: ./vasp_batch_processor.sh [OPTIONS]
# 作者: wukai
# 创建日期: 2024-10-23

set -e  # 遇到错误立即退出
set -u  # 使用未定义的变量时报错

# 加载必要的配置文件和函数
. functions


# 默认配置
declare -A CONFIG=(
    [command]="0"
    [root_dir]="$(pwd)"
    [match]=""
    [file]="POSCAR"
    [to_dir]="$(pwd)"
    [screen]="OUTCAR"
    [job_id_1]=0
    [job_id_2]=1
)

# 帮助信息
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Description:
    Main script for managing VASP calculations workflow.

Options:
    -d|-D|-dir,         --dir       Set root directory (default: current directory): directory for existing files to be operated
    -m|-M|-match,       --match     Set match pattern for directories
    -c|-C|-command,     --command   Set operation command (default: 0)
    -f|-F|-file,        --file      Set input file (default: POSCAR): file for operation
    -to,                --to_dir    Set target directory: directory for generated files
    -screen,            --screen    Set screen file (default: OUTCAR): file for checking calculation status
    -job,               --job       Set job ID for calculation (default: 0): VASP calculation ID in the form of (start,end)
    -h|-help,           --help      Show this help message

Commands:
    0: Prepare and run VASP calculations

Examples:
    # Prepare and run calculations
    $(basename "$0") -to /path/to/dir -m "pattern" -c 0 -f POSCAR
    $(basename "$0") -help
EOF
}

# 函数：执行批量 VASP 流程
run_batch_vasp() {
    local file="$1"
    local to_dir="$2"
    local match="$3"
    
    # 执行 pos-to-all
    echo "pos-to-all" 
    wk-pos.sh -f "${file}" -to "${to_dir}" -match "${match}" || \
        error_exit "pos-to-all failed"

    # 执行 pot-to-all
    echo "pot-to-all"
    wk-pot.sh -to "${to_dir}" -match "${match}" || \
        error_exit "pot-to-all failed"

    # 执行 mkf-in-loop
    echo "mkf-in-loop"
    for input_file in KPOINTS vasp.sbatch; do
        wk-mkf.sh -f "$SCRIPT_DIR/data/${input_file}" -c 0 -to "${to_dir}" -match "${match}" || \
            error_exit "mkf-in-loop failed for ${input_file}"
    done
}

# 函数：执行 M to M-H 流程
run_m_to_m-h() {
    local to_dir="$1"
    local match="$2"

    # 执行 pos-to-all（命令 1）
    wk-pos.sh -to "${to_dir}"  -command 1 || \
        error_exit "pos-to-all failed"

    # 执行 pot-to-all（命令 0）
    wk-pot.sh -to "${to_dir}" -match "${match}" -command 0 || \
        error_exit "pot-to-all failed"

    # 执行 mkf-in-loop
    for input_file in KPOINTS vasp.sbatch; do
        wk-mkf.sh -f "$SCRIPT_DIR/data/${input_file}" -c 0 -to "${to_dir}" -match "${match}" || \
            error_exit "mkf-in-loop failed for ${input_file}"
    done
}

result_processing() {
    local file="$1"
    local to_dir="$2"
    local match="$3"
    
    # 执行 pos-to-all
    echo "pos-to-all"
    wk-che.sh  -to "${to_dir}" -match "${match}" || \
        error_exit "pos-to-all failed"
}

# 函数：解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -c|-command|-C)
                CONFIG[command]="$2"
                echo "command: ${CONFIG[command]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -d|-dir|-D)
                CONFIG[root_dir]="$2"
                echo "ROOT_DIR: ${CONFIG[root_dir]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -m|-match|-M)
                CONFIG[match]="$2"
                echo "match: ${CONFIG[match]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -f|-file|-F)
                CONFIG[file]="$2"
                echo "file: ${CONFIG[file]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -to)
                CONFIG[to_dir]="$2"
                echo "TO_DIR: ${CONFIG[to_dir]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -screen)
                CONFIG[screen]="$2"
                echo "screen: ${CONFIG[screen]}" >> "${PATHS[log_dir]}/logs"
                shift 2
                ;;
            -job)
                if [[ $# -lt 3 ]]; then
                    echo "Error: -job requires two values" >&2
                    exit 1
                fi
                CONFIG[job_id_1]="$2"
                CONFIG[job_id_2]="$3"
                echo "job_ID_1: ${CONFIG[job_id_1]}" >> "${PATHS[log_dir]}/logs"
                echo "job_ID_2: ${CONFIG[job_id_2]}" >> "${PATHS[log_dir]}/logs"
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
                echo "Error: Unknown option $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 函数：主程序
main() {
    local command="${CONFIG[command]}"
    local file="${CONFIG[file]}"
    local to_dir="${CONFIG[to_dir]}"
    local match="${CONFIG[match]}"

    case "${command}" in
        0)  # 执行批量 VASP 流程
            echo "command: 执行批量vasp的流程" >> "${PATHS[log_dir]}/logs"
            run_batch_vasp "${file}" "${to_dir}" "${match}"
            ;;
        1)  # 执行批量 M to M-H 流程
            echo "command: 执行批量vaspM to M-H的流程" >> "${PATHS[log_dir]}/logs"
            run_m_to_m-h  "${to_dir}" "${match}"
            ;;
        2) #结果处理
            echo "command: 结果处理" >> "${PATHS[log_dir]}/logs"
            result_processing "${file}" "${to_dir}" "${match}"  
            ;;
        *)
            echo "command: ${command} is not defined"
            ;;
    esac
}

# 初始化日志
{
    printf '*%.0s' {1..100}
    echo
} | tee -a "${PATHS[result_dir]}/results" "${PATHS[log_dir]}/logs" "${PATHS[log_dir]}/errors" > /dev/null

# 解析命令行参数
parse_arguments "$@"

# 执行主程序
main

# 记录结果
{
    printf '=%.0s' {1..50}
    echo
    result $? "main"
} >> "${PATHS[result_dir]}/results"

# 结束
{
    printf '*%.0s' {1..100}
    echo
    result $? "main"
} | tee -a "${PATHS[result_dir]}/results" "${PATHS[log_dir]}/logs" "${PATHS[log_dir]}/errors" > /dev/null