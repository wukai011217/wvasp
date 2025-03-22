#!/bin/bash
#==============================================================================
# 脚本信息
#==============================================================================
# 名称: wk-bdr
# 描述: 执行Bader电荷分析，处理VASP的AECCAR文件并生成分析结果
# 用法: wk-bdr [OPTIONS]
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
    [root_dir]="$(pwd)"     # 根目录
    [command]="0"           # 命令
    [source_file]="$(basename "$0")"   # 脚本文件
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
wk-bdr (Bader 电荷分析工具) v${VERSION}

Usage: 
    $(basename "$0") [OPTIONS]

Description:
    执行 Bader 电荷分析的工具脚本。处理 VASP 输出的 AECCAR0、AECCAR2
    和 CHGCAR 文件，使用 Bader 方法计算电荷密度分布。

所需文件:
    - AECCAR0: 核心电荷密度
    - AECCAR2: 价电子电荷密度
    - CHGCAR:  总电荷密度

Options:
    目录控制:
        -d, -D, --dir DIR     设置分析根目录
                              (默认: 当前目录)
    
    操作控制:
        -c, -C, --command NUM 设置操作命令 (见下方命令说明)
    
    通用选项:
        -h, --help           显示帮助信息
        --version            显示版本信息

命令说明:
    [0] 执行 Bader 电荷分析
        • 检查所需文件是否存在
        • 跳过已有 ACF.dat 的目录
        • 仅处理叶子目录

    [1] 预留待扩展

示例:
    # 在当前目录执行分析
    $(basename "$0")

    # 在指定目录执行分析
    $(basename "$0") -d /path/to/vasp/output -m "Fe_*"

    # 显示版本信息
    $(basename "$0") --version

注意:
    脚本会自动处理指定根目录下的所有叶子目录。为避免重复计算，
    已包含 ACF.dat 文件的目录将被跳过。
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
            -dir|-D|-d|--dir)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Directory path required for $1" >&2
                    exit 1
                fi
                CONFIG[root_dir]="$2"
                logging 1 "Root directory set to: ${CONFIG[root_dir]}"
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
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                echo "wk-bdr version ${VERSION}"
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

# 函数: run_bader_analysis
# 描述: 在指定目录执行Bader电荷分析
# 参数:
#   $1 - 目标目录
# 返回: 0=成功
run_bader_analysis() {
    local target_dir="$1"
    local current_dir="$(pwd)"
    
    cd "$target_dir"
    logging 1 "Running Bader analysis in: $target_dir"
    
    # 更新统计信息
    update_stats "total"
    
    # 执行Bader分析
    if chgsum.pl AECCAR0 AECCAR2; then
        if bader CHGCAR -ref CHGCAR_sum; then
            logging 1 "Bader analysis completed successfully in: $target_dir"
            update_stats "processed"
        else
            logging 1 "Bader analysis failed in: $target_dir"
            update_stats "failed"
        fi
    else
        logging 1 "chgsum.pl failed in: $target_dir"
        update_stats "failed"
    fi
    
    cd "$current_dir"
}

# 函数: check_files
# 描述: 检查目录中是否存在所需的文件
# 参数:
#   $1 - 目标目录
# 返回: 0=成功
check_files() {
    local dir="$1"
    local missing_files=()
    local required_files=("AECCAR0" "AECCAR2" "CHGCAR")
    
    update_stats "total"
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$dir/$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        logging 1 "Missing required files in $dir: ${missing_files[*]}"
        update_stats "skipped"
        return 0
    fi
    
    # 检查是否已经存在 ACF.dat
    if [[ -f "$dir/ACF.dat" ]]; then
        logging 1 "ACF.dat already exists in $dir"
        update_stats "skipped"
        return 0
    fi
    
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
    case "${CONFIG[command]}" in
        0)
            find "${CONFIG[root_dir]}" -type d | while read -r target_dir; do
                # 检查是否是叶子目录
                if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
                    if [[ -f "$target_dir/ACF.dat" ]]; then
                        logging 1 "ACF.dat already exists in: $target_dir"
                        update_stats "skipped"
                    else
                        if check_files "$target_dir" "AECCAR0" "AECCAR2"; then
                            run_bader_analysis "$target_dir"
                        else
                            logging 1 "Missing AECCAR files in: $target_dir"
                            update_stats "failed"
                        fi
                    fi
                fi
            done
            ;;
        1)
            logging 1 "Command 1 is reserved for future use"
            ;;
        help)
            show_help
            ;;
        *)
            echo "Error: ${CONFIG[command]} is not a valid command" >&2
            show_help
            exit 1
            ;;
    esac
}

# 初始化脚本
initialize || { logging 2 "${CONFIG[source_file]} : Failed to initialize script"; exit 1; }

# 解析命令行参数
parse_arguments "$@" || { logging 2 "${CONFIG[source_file]} : Failed to parse arguments"; exit 1; }

# 记录运行环境
log_environment

# 执行主程序
main || { logging 2 "${CONFIG[source_file]} : Failed to execute main function"; exit 1; }
