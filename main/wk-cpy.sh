#!/bin/bash
#
# 脚本名称: wk-cpy
# 描述: 复制指定文件到目标目录，保持目录结构
# 用法: ./wk-cpy [OPTIONS]
# 作者: wukai
# 日期: 2024-01-18

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 加载配置和函数
. functions

# 函数：显示版本信息
show_version() {
    logging 1 "wk-cpy v${VERSION}"
}

# 版本信息
VERSION="1.0.0"

# 默认配置
declare -A CONFIG=(
    [root_dir]="$(pwd)"     # 源目录
    [file]="CONTCAR"        # 要复制的文件
    [to_dir]="$(pwd)"       # 目标目录
    [match]=""              # 目录匹配模式
    [command]="0"           # 命令
    [source_file]="$(basename "$0")"     # 脚本文件

    # 运行模式
    [dry_run]=false                      # 模拟运行模式
    [verbose]=false                      # 详细输出模式
    [backup]=true                        # 备份模式
    [preserve]=true         # 是否保持目录结构
    # [overwrite]=false       # 是否覆盖现有文件
    # [dry_run]=false         # 模拟运行模式
)



# 帮助信息
show_help() {
    cat << EOF
wk-cpy (VASP File Copy Utility) v${VERSION}

Usage: 
    $(basename "$0") [OPTIONS]

Description:
    Copy specified files between directories while maintaining directory structure.
    Useful for organizing VASP calculation files across different setups.
    Supports pattern matching and dry-run mode.

Options:
    -d, -D, --dir DIR      Set source directory
                           (default: current directory)
    -f, -F, --file NAME    Set file to copy
                           (default: CONTCAR)
    -t, --to DIR           Set destination directory
                           (default: current directory)
    -m, -M, --match PAT    Set directory match pattern
                           (default: process all directories)
    -c, -C, --command NUM  Set operation command
                           (default: 0)
    --no-preserve          Don't preserve directory structure
    --overwrite           Overwrite existing files
    -n, --dry-run         Show what would be done without copying
    -h, --help            Show this help message and exit
    -v, --version         Show version information

Commands:
    0    Copy files while maintaining structure
         - Creates target directories as needed
         - Preserves relative paths by default
         - Skips existing files unless --overwrite
    1    Reserved for future use

Examples:
    # Copy CONTCAR files from current directory
    $(basename "$0") --to /target/dir

    # Copy specific files with pattern matching
    $(basename "$0") -d /source/dir -f POSCAR -t /target/dir -m "Fe_*"

    # Show what would be copied without actually copying
    $(basename "$0") -d /source/dir -t /target/dir --dry-run

    # Copy files without preserving directory structure
    $(basename "$0") -d /source/dir -t /target/dir --no-preserve

Note:
    The script will maintain the relative directory structure by default.
    Use --no-preserve to copy files directly to the target directory.
    Use --overwrite to replace existing files in the target directory.
EOF
}

# 解析命令行参数
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
                logging 1 "File to copy set to: ${CONFIG[file]}"
                shift 2
                ;;
            -to|-t|--to)
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
                logging 1 "Destination directory set to: ${CONFIG[to_dir]}"
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

# # 检查源文件
# check_source_file() {
#     local source_dir="$1"
#     local file="${CONFIG[file]}"
#     local source_file="$source_dir/$file"
    
#     if [[ ! -f "$source_file" ]]; then
#         logging 1 "Source file not found: $source_file"
#         return 1
#     fi
    
#     return 0
# }

# # 检查目标文件
# check_target_file() {
#     local target_file="$1"
    
#     if [[ -f "$target_file" ]] && [[ "${CONFIG[overwrite]}" != true ]]; then
#         logging 1 "Target file exists (use --overwrite to replace): $target_file"
#         return 1
#     fi
    
#     return 0
# }

# 复制文件
copy_file() {
    local source_dir="$1"
    local rel_path="$2"
    local source_file="$source_dir/${CONFIG[file]}"
    local dest_dir
    local dest_file
    
    # 根据是否保持目录结构决定目标路径
    if [[ "${CONFIG[preserve]}" == true ]]; then
        dest_dir="${CONFIG[to_dir]}/$rel_path"
        dest_file="$dest_dir/${CONFIG[file]}"
    else
        dest_dir="${CONFIG[to_dir]}"
        dest_file="$dest_dir/${rel_path}_${CONFIG[file]}"
    fi
    
    # 检查源文件
    if ! check_path  "$source_dir" "directory"; then
        return 1
    fi
    
    # 检查目标文件
    if ! check_path  "$dest_file" "file"; then
        return 0  # 跳过已存在的文件
    fi
    
    # 如果是模拟运行模式
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would copy $source_file to $dest_file"
        return 0
    fi
    
    # 创建目标目录
    if ! mkdir -p "$dest_dir"; then
        logging 1 "Failed to create directory: $dest_dir"
        return 1
    fi
    
    # 复制文件
    if cp -a "$source_file" "$dest_file" 2>> "${PATHS[log_dir]}/errors"; then
        logging 1 "Successfully copied ${CONFIG[file]} to $dest_file"
        return 0
    else
        logging 1 "Failed to copy ${CONFIG[file]} to $dest_file"
        return 1
    fi
}

# 获取相对路径
get_relative_path() {
    local full_path="$1"
    echo "$(awk -F/ '{print $(NF-2)"/"$(NF-1)"/"$NF}' <<< "$full_path")"
}


# 处理单个目录
process_directory() {
    local target_dir="$1"
    local rel_path
    
    # 检查目录名是否匹配模式
    if [[ -z "${CONFIG[match]}" || "$target_dir" == *"${CONFIG[match]}"* ]]; then
        # 获取相对路径
        rel_path="$(get_relative_path "$target_dir")"
        logging 1 "Processing directory: $rel_path"
        
        # 复制文件
        if copy_file "$target_dir" "$rel_path"; then
            update_stats "copied"
        else
            local status=$?
            if [[ $status -eq 2 ]]; then
                update_stats "skipped"
            else
                update_stats "failed"
            fi
        fi
    fi
}

# 主程序
main() {
    local start_time=$(date +%s)
    
    # 检查配置并显示
    check_config_and_display || {
        logging 2 "${CONFIG[source_file]} : Failed to check configuration"
        return 1
    }

    # 定义命令映射
    declare -A COMMAND_MAP=(
        [0]="Copy files to matching directories:process_all_directories"
        [1]="Copy with structure preservation:process_with_structure"
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

            # 初始化处理
            case "${CONFIG[command]}" in
                0)
                    # 处理所有叶子目录
                    find "${CONFIG[root_dir]}" -type d | while read -r target_dir; do
                        # 检查是否是叶子目录
                        if [[ -z "$(find "$target_dir" -mindepth 1 -type d)" ]]; then
                            process_directory "$target_dir" || return 1
                        fi
                    done
                    ;;
                1)
                    # 保持目录结构的复制
                    logging 1 "Command 1 is reserved for future use"
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
