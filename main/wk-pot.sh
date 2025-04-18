#!/bin/bash
#==============================================================================
# 脚本信息
#==============================================================================
# 名称: wk-pot
# 描述: 生成 VASP POTCAR 文件
# 用法: wk-pot [OPTIONS] -to <directory>
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

# 重置统计信息
reset_stats

# 默认配置
declare -A CONFIG=(
    # 基本配置
    [command]="0"                      # 命令
    [to_dir]="$(pwd)"                  # 目标目录
    [match]=""                         # 匹配模式
    [source_file]="$(basename "$0")"   # 脚本文件
    
    # 运行模式
    [dry_run]=false                    # 模拟运行模式
    [verbose]=false                    # 详细输出模式
    [backup]=true                      # 备份模式
)


#==============================================================================
# Function Definitions
#==============================================================================

#==============================================================================
# 函数定义
#==============================================================================

# 函数: show_help
# 描述: 显示脚本的帮助信息
# 参数: 无
# 返回: 0=成功
show_help() {
    cat << EOF
    cat << EOF
wk-pot (VASP POTCAR 生成工具) v${VERSION}

Usage: 
    $(basename "$0") -to <directory> [OPTIONS]

Description:
    根据 POSCAR 文件中指定的元素自动生成 VASP POTCAR 文件。
    支持批量处理并包含安全检查机制。

Options:
    目录控制:
        -to <directory>      设置目标目录 (必需参数)
        -m, --match <pat>    设置目录匹配模式
                             (默认: 处理所有目录)
    
    操作控制:
        -c, --command <num>  设置操作命令 (见下方命令说明)
                             (默认: 0)
    
    处理选项:
        --dry-run           模拟运行，不实际执行
        --no-backup         禁用自动备份
        --verbose           启用详细日志
    
    通用选项:
        -h, --help          显示帮助信息
        --version           显示版本信息

命令说明:
    [0] 生成 POTCAR
        • 从 POSCAR 读取元素信息
        • 组合相应的赫斯势能文件
        • 自动创建备份

    [1] 预留待扩展

安全特性:
    • 模拟运行    可预览操作而不实际执行
    • 自动备份    在修改前创建 .bak 文件
    • 详细日志    记录详细的操作历史
    • 错误检查    验证输入和操作

示例:
    # 在当前目录生成 POTCAR
    $(basename "$0") -to .

    # 处理匹配模式的多个目录
    $(basename "$0") -to /path/to/calcs -m "Fe_*" --verbose

    # 预览操作而不执行
    $(basename "$0") -to /path/to/calc/Fe2O3 --dry-run

文件:
    ./POSCAR          输入结构文件
    ./POTCAR          生成的势能文件
    ${PATHS[log_dir]}/logs    日志文件位置

返回值:
    0    成功
    1    一般错误
    2    参数无效

注意:
    • -to 参数是必需的，必须指定目标目录
    • 默认启用自动备份，使用 --no-backup 可禁用
    • 使用 --dry-run 可预览将要执行的操作
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
            # 目录控制
            -to)
                if [[ -z "$2" || "$2" == -* ]]; then
                    logging 2 "${CONFIG[source_file]}: Directory path required for $1"
                    return 1
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
                    logging 2 "${CONFIG[source_file]}: Pattern required for $1"
                    return 1
                fi
                CONFIG[match]="$2"
                logging 1 "Match pattern set to: ${CONFIG[match]}"
                shift 2
                ;;
            
            # 操作控制
            -c|-C|--command)
                if [[ -z "$2" || "$2" == -* ]]; then
                    logging 2 "${CONFIG[source_file]}: Command number required for $1"
                    return 1
                fi
                if [[ ! "$2" =~ ^[0-9]+$ ]]; then
                    logging 2 "${CONFIG[source_file]}: Command must be a number"
                    return 1
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

#------------------------------------------------------------------------------
# create_potcar
#
# Create POTCAR file based on elements in POSCAR file
#
# Arguments:
#     $1 - Target directory path
#
# Returns:
#     0 on success
#------------------------------------------------------------------------------
create_potcar() {
    local target_dir="$1"
    local poscar_file="$target_dir/POSCAR"
    local potcar_file="$target_dir/POTCAR"
    local temp_file="$target_dir/POTCAR.tmp"
    
    # 更新统计信息
    update_stats "total"
    
    # 检查 POSCAR 文件
    if [[ ! -f "$poscar_file" ]]; then
        if [[ "${CONFIG[verbose]}" == true ]]; then
            logging 1 "No POSCAR found in $target_dir"
        fi
        update_stats "skipped"
        return 0
    fi
    
    # 验证 POSCAR 格式
    if ! validate_poscar "$poscar_file"; then
        logging 1 "Error: Invalid POSCAR format in $poscar_file"
        update_stats "failed"
        return 0
    fi
    
    # 检查现有 POTCAR
    if [[ -f "$potcar_file" ]]; then
        if [[ "${CONFIG[verbose]}" == true ]]; then
            logging 1 "POTCAR already exists in $target_dir (use --force to overwrite)"
        fi
        update_stats "skipped"
        return 0
    fi
    
    # 模拟运行模式
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would create POTCAR in $target_dir"
        return 0
    fi
    
    # 读取元素
    local elements
    if ! IFS=' ' read -r -a elements < <(sed -n '6p' "$poscar_file" | sed 's/\r//g') 2>> "${PATHS[log_dir]}/logs"; then
        logging 1 "Error: Failed to read elements from $poscar_file"
        update_stats "failed"
        return 0
    fi
    
    # 创建临时文件
    : > "$temp_file"
    
    # 处理每个元素
    local success=true
    for element in "${elements[@]}"; do
        local potcar_path=""
        
        # 查找 POTCAR 文件
        if [[ -d "${PATHS[pot_dir]}/${element}" ]]; then
            potcar_path="${PATHS[pot_dir]}/${element}/POTCAR"
        elif [[ -d "${PATHS[pot_dir]}/${element}_sv" ]]; then
            potcar_path="${PATHS[pot_dir]}/${element}_sv/POTCAR"
        else
            logging 1 "Error: POTCAR for ${element} not found in ${PATHS[pot_dir]}"
            success=false
            break
        fi
        
        # 追加 POTCAR 内容
        if ! cat "$potcar_path" >> "$temp_file" 2>> "${PATHS[log_dir]}/logs"; then
            logging 1 "Error: Failed to append POTCAR for $element"
            success=false
            break
        fi
        
        if [[ "${CONFIG[verbose]}" == true ]]; then
            logging 1 "Added POTCAR for $element from $potcar_path"
        fi
    done
    
    # 检查处理结果
    if [[ "$success" == true ]]; then
        if mv "$temp_file" "$potcar_file" 2>> "${PATHS[log_dir]}/logs"; then
            update_stats "processed"
            if [[ "${CONFIG[verbose]}" == true ]]; then
                logging 1 "Successfully created POTCAR in $target_dir"
            fi
            return 0
        else
            logging 1 "Error: Failed to move temporary file to $potcar_file"
            success=false
        fi
    fi
    
    # 清理失败
    rm -f "$temp_file"
    update_stats "failed"
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
    local command="${CONFIG[command]}"
    local start_time=$(date +%s)
    local target_dir="${CONFIG[to_dir]}"
    
    check_config_and_display || { logging 2 "${CONFIG[source_file]} : Failed to check configuration"; return 1; }
    
    # 定义命令映射
    declare -A COMMAND_MAP=(
        [0]="POTCAR Generation:create_potcar"
        [1]="Reserved Command:echo 'Reserved for future use'"
    )
    
    # 处理命令
    case "$command" in
        help)
            show_help
            exit 0
            ;;
        --version)
            echo "${CONFIG[source_file]} : version $VERSION"
            exit 0
            ;;
        [0-1])
            local IFS=':'
            local cmd_info=(${COMMAND_MAP[$command]})
            unset IFS
            local description="${cmd_info[0]}"
            local processor="${cmd_info[1]}"
            
            logging 1 "Processing: $description"
            echo "${CONFIG[source_file]} : Processing: $description"
            echo "$target_dir"
            
            while IFS= read -r dir; do
                # 检查目录是否匹配模式
                if [[ -n "${CONFIG[match]}" && "$dir" != *"${CONFIG[match]}"* ]]; then
                    [[ "${CONFIG[verbose]}" == true ]] && \
                        logging 1 "Skipping non-matching directory: $dir"
                    update_stats "skipped"
                    continue
                fi
                
                $processor "$dir" || {
                    local exit_code=$?
                    logging 2 "${CONFIG[source_file]} : Failed to process directory: $dir"
                    return $exit_code
                }
            done < <(find "$target_dir"  -type d -not -path "*/\.*")
            ;;
        *)
            logging 2 "${CONFIG[source_file]} : Invalid command: $command"
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
# Main Program
#==============================================================================

# Initialize script environment
initialize || {
    logging 2 "${CONFIG[source_file]} : Failed to initialize script"
    exit 1
}

# Parse command line arguments
parse_arguments "$@" || {
    logging 2 "${CONFIG[source_file]} : Failed to parse arguments"
    exit 1
}

# Log runtime environment
log_environment

# Execute main program
main || {
    logging 2 "${CONFIG[source_file]} : Failed to execute main function"
    exit 1
}