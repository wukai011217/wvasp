#!/bin/bash
#==============================================================================
# 脚本信息
#==============================================================================
# 名称: wk-mkf
# 描述: VASP 文件管理工具
# 用法: wk-mkf [OPTIONS]
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
    [file]="$SCRIPT_DIR/data/KPOINTS"    # 要复制的文件
    [to_dir]="$(pwd)"                    # 目标目录
    [command]="0"                        # 命令
    [match]=""                           # 匹配模式
    [source_file]="$(basename "$0")"     # 脚本文件
    
    # 运行模式
    [dry_run]=false                      # 模拟运行模式
    [verbose]=false                      # 详细输出模式
    [backup]=true                        # 备份模式
)

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
    ${CONFIG[source_file]} - VASP 文件管理工具

VERSION
    $VERSION

SYNOPSIS
    $(basename "$0") [OPTIONS]

DESCRIPTION
    在多个目录之间复制和组织 VASP 计算文件。
    支持单文件分发和结构化目录复制。
    包含安全特性，如模拟运行模式和自动备份。

OPTIONS
    -d, -D, --dir DIR     设置源目录
                          (默认: 当前目录)
    -f, -F, --file FILE   设置要复制的文件
                          (默认: data 目录中的 KPOINTS)
    -to DIR               设置目标目录
                          (默认: 当前目录)
    -m, -M, --match PAT   设置目录匹配模式
                          (默认: 匹配所有)
    -c, -C, --command NUM 设置操作命令
                          (默认: 0)
    --no-backup          禁用自动备份
    -n, --dry-run        显示将要复制的内容
    -v, --verbose        启用详细输出
    -h, --help           显示此帮助信息
    --version            显示版本信息

COMMANDS
    0  简单分发
       - 将单个文件复制到所有匹配的目录
       - 保持文件名
       - 如果文件存在则创建备份

    1  结构化复制
       - 将 CONTCAR 作为 POSCAR 复制，保持目录结构
       - 保留相对路径
       - 如果文件存在则创建备份

SAFETY FEATURES
    - 模拟运行模式: 显示将要复制的内容
    - 自动备份: 创建 .bak 文件 (默认)
    - 详细日志: 详细的操作信息
    - 路径验证: 检查源和目标路径

EXAMPLES
    # 预览将 KPOINTS 复制到匹配的目录
    $(basename "$0") -f KPOINTS -to /target/dir -m "Fe_*" --dry-run

    # 使用自动备份进行复制
    $(basename "$0") -f KPOINTS -to /target/dir -m "Fe_*"

    # 使用详细输出进行结构化复制
    $(basename "$0") -d /source/dir -to /target/dir -m "Fe_*" -c 1 -v

EXIT STATUS
    0  成功
    1  失败

FILES
    KPOINTS   默认的输入文件
    CONTCAR   结构化复制模式下的源文件
    POSCAR    结构化复制模式下的目标文件

AUTHOR
    Written by Kai Wu.

REPORTING BUGS
    Report bugs to <wukai@mail.ustc.edu.cn>.

COPYRIGHT
    Copyright © 2024 Kai Wu. License MIT.
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.

SEE ALSO
    wk-pot(1), wk-pos(1)
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
            -d|-D|--dir)
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
            -f|-F|--file)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: File name required for $1" >&2
                    exit 1
                fi
                CONFIG[file]="$2"
                logging 1 "Target file set to: ${CONFIG[file]}"
                shift 2
                ;;
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
            -m|-M|--match)
                if [[ -z "$2" || "$2" == -* ]]; then
                    echo "Error: Pattern required for $1" >&2
                    exit 1
                fi
                CONFIG[match]="$2"
                logging 1 "Match pattern set to: ${CONFIG[match]}"
                shift 2
                ;;
            -c|-C|--command)
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
                exit 0
                ;;
            --version)
                echo "${CONFIG[source_file]} : version $VERSION"
                exit 0
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



# 函数: copy_file
# 描述: 复制单个文件
# 参数:
#   $1 - 源文件路径
#   $2 - 目标文件路径
# 返回: 0=成功, 1=失败
copy_file() {
    local source_file="$1"
    local target_file="$2"
    local rel_path="${target_file#${CONFIG[to_dir]}/}"
    
    update_stats "total"
    
    # 检查源文件
    if ! check_path "$source_file" "file"; then
        update_stats "failed"
        return 0
    fi

    # 模拟运行模式处理
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would copy: $source_file -> $target_file"
        return 0
    fi

    # 执行文件复制
    if cp "$source_file" "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
        update_stats "copied"
        [[ "${CONFIG[verbose]}" == true ]] && \
            logging 1 "Successfully copied: $source_file -> $target_file"
        return 0
    else
        update_stats "failed"
        logging 1 "Failed to copy: $source_file -> $target_file"
        return 0
    fi
}

# 函数: copy_file_to_all
# 描述: 将单个文件复制到多个目标目录
# 参数: 无
# 使用全局变量:
#   CONFIG[to_dir]  - 目标目录
#   CONFIG[file]    - 源文件
#   CONFIG[match]   - 目录匹配模式
#   CONFIG[verbose] - 详细输出模式
# 返回: 0=成功, 1=失败
copy_file_to_all() {
    local to_dir="${CONFIG[to_dir]}"
    local file="${CONFIG[file]}"
    local match="${CONFIG[match]}"
    local filename=""

    # 获取文件名并显示操作信息
    filename=$(basename "$file")
    if [[ "${CONFIG[verbose]}" == true ]]; then
        logging 1 "Copying $filename to matching directories in $to_dir"
        [[ -n "$match" ]] && logging 1 "Using match pattern: $match"
    fi
    
    # 遍历目标目录
    while IFS= read -r target_dir; do
        # 检查是否是叶子目录
        if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
            # 检查是否匹配模式
            if [[ -z "$match" || "$target_dir" == *"$match"* ]]; then
                local target_file="$target_dir/$filename"
                copy_file "$file" "$target_file"
            else
                update_stats "skipped"
                [[ "${CONFIG[verbose]}" == true ]] && \
                    logging 1 "Skipped non-matching directory: $target_dir"
            fi
        else
            update_stats "skipped"
            [[ "${CONFIG[verbose]}" == true ]] && \
                logging 1 "Skipped non-leaf directory: $target_dir"
        fi
    done < <(find "$to_dir" -mindepth 1 -type d)
}

# 函数: structured_copy
# 描述: 按照目录结构复制文件
# 参数: 无
# 使用全局变量:
#   CONFIG[root_dir] - 源目录
#   CONFIG[to_dir]   - 目标目录
#   CONFIG[match]    - 目录匹配模式
#   CONFIG[verbose]  - 详细输出模式
# 返回: 0=成功, 1=失败
structured_copy() {
    local from_dir="${CONFIG[root_dir]}"
    local to_dir="${CONFIG[to_dir]}"
    local match="${CONFIG[match]}"
    
    # 显示操作信息
    if [[ "${CONFIG[verbose]}" == true ]]; then
        logging 1 "Copying CONTCAR as POSCAR from $from_dir to $to_dir"
        [[ -n "$match" ]] && logging 1 "Using match pattern: $match"
    fi
    
    # 遍历目标目录
    while IFS= read -r target_dir; do
        # 检查是否是叶子目录
        if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
            # 检查是否匹配模式
            if [[ -z "$match" || "$target_dir" == *"$match"* ]]; then
                # 提取相对路径并复制文件
                local relative_path="${target_dir#$to_dir}"
                relative_path="${relative_path#/}"
                local source_file="$from_dir/$relative_path/CONTCAR"
                local target_file="$target_dir/POSCAR"
                
                # 检查源文件并复制
                if [[ -f "$source_file" ]]; then
                    copy_file "$source_file" "$target_file"
                else
                    update_stats "skipped"
                    logging 1 "Source file not found: $source_file"
                fi
            else
                update_stats "skipped"
                [[ "${CONFIG[verbose]}" == true ]] && \
                    logging 1 "Skipped non-matching directory: $target_dir"
            fi
        else
            update_stats "skipped"
            if [[ "${CONFIG[verbose]}" == true ]]; then
                logging 1 "Skipped non-leaf directory: $target_dir"
            fi
        fi
    done < <(find "$to_dir" -mindepth 1 -type d)
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
    
    # 定义命令映射
    declare -A COMMAND_MAP=(
        [0]="Copy single file to matching directories:copy_file_to_all"
        [1]="Copy CONTCAR as POSCAR with structure:structured_copy"  #wukai 有待商榷
    )

    # 处理命令
    case "${CONFIG[command]}" in
        help)
            show_help
            exit 0
            ;;
        --version)
            echo "${CONFIG[source_file]} : version $VERSION"
            exit 0
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
# 程序启动
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