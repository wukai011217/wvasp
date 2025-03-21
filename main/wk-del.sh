#!/bin/bash
#==============================================================================
# 脚本信息
#==============================================================================
# 名称: wk-del
# 描述: 删除指定目录下的特定文件
# 用法: wk-del [OPTIONS] -to <directory>
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
    [source_file]="$(basename "$0")"     # 脚本文件
    [to_dir]="$(pwd)"                   # 目标目录
    [file]="CHG"                        # 要删除的文件
    [command]="0"                       # 命令
    [match]=""                          # 目录匹配模式
    
    # 运行模式
    [dry_run]=false                      # 模拟运行模式
    [verbose]=false                      # 详细输出模式
    [regex]=false                        # 是否使用正则模式
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
NAME
    ${CONFIG[source_file]} - VASP 文件删除工具 v${VERSION}

SYNOPSIS
    $(basename "$0") [OPTIONS] -to <directory>

DESCRIPTION
    从 VASP 计算目录中删除指定文件。
    支持选择性删除指定文件或清理目标目录中的所有文件。
    提供模拟运行模式和详细输出功能。

OPTIONS
    -to <directory>       设置目标目录
                         (默认: 当前目录)

    -f, --file <name>     设置要删除的文件
                         (默认: CHG)

    -m, --match <pat>     设置目录匹配模式
                         (默认: 处理所有目录)

    -c, --command <num>   设置操作命令
                         (默认: 0)

    --regex              启用正则表达式模式
    --dry-run        显示将要删除的文件
    --verbose        启用详细输出
    -h, --help           显示此帮助信息
    --version            显示版本信息

COMMANDS
    0    删除指定文件
         - 仅删除指定的文件
         - 保持目录结构
         - 跳过不存在的文件

    1    删除所有文件 (危险)
         - 删除叶子目录中的所有文件
         - 保持目录结构
         - 请谨慎使用

SAFETY FEATURES
    --dry-run        显示将要删除的文件

EXAMPLES

    # 预览将要删除的文件
    $(basename "$0") -to /path/to/calcs -f WAVECAR --dry-run

    # 删除所有文件
    $(basename "$0") -to /path/to/calcs -c 1 

NOTE
    命令 1 很危险，因为它会删除目标目录中的所有文件。
    总是先使用 --dry-run 预览将要删除的文件。
    谨慎使用 --force 选项。
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
            -file|-F|-f|--file)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: File name required for $1" >&2
                    exit 1
                fi
                CONFIG[file]="$2"
                logging 1 "Target file set to: ${CONFIG[file]}"
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
            -match|-m|-M|--match)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Match pattern required for $1" >&2
                    exit 1
                fi
                CONFIG[match]="$2"
                logging 1 "Match pattern set to: ${CONFIG[match]}"
                shift 2
                ;;
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
            
            # 常规选项
            -h|--help)
                show_help
                exit 0
                ;;
            --version)
                echo "${CONFIG[source_file]} : version $VERSION"
                exit 0
                ;;
            --regex)
                CONFIG[regex]=true
                logging 1 "Regex mode enabled"
                shift 1
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
    
}

# 函数: delete_file
# 描述: 删除指定目录下的单个文件
# 参数:
#   $1 - 目标目录路径
# 返回: 0=成功, 1=失败
#   0 - 成功(包括跳过和模拟运行)
#   1 - 失败
delete_file() {
    local target_dir="$1"
    local target_file="$target_dir/${CONFIG[file]}"
    local rel_path="${target_dir#${CONFIG[to_dir]}/}"
    
    update_stats "total"

    # 模拟运行模式检查
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would delete: $target_file"
        return 0
    fi

    # 正则模式处理
    if [[ "${CONFIG[regex]}" == true ]]; then
        # 检查匹配文件
        if ! ls "$target_dir"/*"${CONFIG[file]}"* >/dev/null 2>&1; then
            [[ "${CONFIG[verbose]}" == true ]] && \
                logging 1 "No matching files found in: $target_dir"
            update_stats "skipped"
            return 0
        fi

        # 删除匹配文件
        if rm "$target_dir"/*"${CONFIG[file]}"* 2>>"${PATHS[log_dir]}/logs"; then
            update_stats "deleted"
            [[ "${CONFIG[verbose]}" == true ]] && \
                logging 1 "Successfully deleted matching files in: $target_dir"
            return 0
        else
            update_stats "failed"
            logging 2 "Failed to delete files in: $target_dir"
            return 1
        fi
    fi

    # 普通模式处理
    if ! check_path "$target_file" "file"; then
        [[ "${CONFIG[verbose]}" == true ]] && \
            logging 1 "Skipping non-existent file: $target_file"
        update_stats "skipped"
        return 0
    fi

    # 检查文件权限
    if [[ ! -w "$target_file" ]]; then
        logging 2 "File not writable: $target_file"
        update_stats "failed"
        return 1
    fi

    # 删除文件
    if rm "$target_file" 2>>"${PATHS[log_dir]}/logs"; then
        update_stats "deleted"
        [[ "${CONFIG[verbose]}" == true ]] && \
            logging 1 "Successfully deleted: $target_file"
        return 0
    else
        update_stats "failed"
        logging 2 "Failed to delete: $target_file"
        return 1
    fi
}

# 函数: delete_all_files
# 描述: 删除目录中的所有文件
# 参数:
#   $1 - 目标目录路径
# 返回: 0=成功, 1=失败
#   0 - 成功(包括跳过和模拟运行)
#   1 - 失败
delete_all_files() {
    local target_dir="$1"
    local rel_path="${target_dir#${CONFIG[to_dir]}/}"
    local file_count
    
    # 检查是否是叶子目录
    if [[ -n "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
        [[ "${CONFIG[verbose]}" == true ]] && \
            logging 1 "Skipping non-leaf directory: $target_dir"
        return 0
    fi
    
    # 统计文件数量
    file_count=$(find "$target_dir" -maxdepth 1 -type f | wc -l)
    update_stats "total" "$file_count"
    
    # 检查是否有文件需要删除
    if [[ $file_count -eq 0 ]]; then
        [[ "${CONFIG[verbose]}" == true ]] && \
            logging 1 "No files to delete in: $target_dir"
        update_stats "skipped"
        return 0
    fi
    
    # 模拟运行模式
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would delete $file_count files from: $target_dir"
        return 0
    fi
    
    # 删除所有文件
    if rm -f "$target_dir"/* 2>>"${PATHS[log_dir]}/logs"; then
        update_stats "deleted" "$file_count"
        [[ "${CONFIG[verbose]}" == true ]] && \
            logging 1 "Successfully deleted $file_count files from: $target_dir"
        return 0
    else
        update_stats "failed" "$file_count"
        logging 2 "Failed to delete files from: $target_dir"
        return 1
    fi
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
    
    # 如果是命令 1，显示警告
    if [[ "${CONFIG[command]}" == "1" ]]; then
        echo "WARNING: Command 1 will delete ALL files in target directories!"
        if [[ "${CONFIG[dry_run]}" != true ]]; then
            echo "Use --dry-run to preview what will be deleted."
            sleep 5  # 给用户时间阅读警告
        fi
    fi
    
    # 定义命令映射
    declare -A COMMAND_MAP=(
        [0]="Delete specific files:delete_specific_files"
        [1]="Delete all files (DANGEROUS):delete_all_directories"  #wukai 与其他文件风格不统一
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
            
            # 处理目录
            local find_args=("${CONFIG[to_dir]}" -mindepth 1 -type d)
            [[ -n "${CONFIG[match]}" ]] && find_args+=(-path "*${CONFIG[match]}*")
            
            # 执行命令处理函数
            case "$processor" in
                delete_specific_files)
                    find "${find_args[@]}" | while read -r target_dir; do
                        delete_file "$target_dir" || return 1
                    done
                    ;;
                delete_all_directories)
                    find "${find_args[@]}" | while read -r target_dir; do
                        delete_all_files "$target_dir" || return 1
                    done
                    ;;
            esac
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
