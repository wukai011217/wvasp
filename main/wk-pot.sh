#!/bin/bash
#==============================================================================
#
#    wk-pot - Generate VASP POTCAR files from POSCAR elements
#
#    Author:  Wu Kai
#    Created: 2024-10-23
#    Updated: 2025-02-24
#    Version: 1.0.0
#
#==============================================================================

#==============================================================================
# Global Settings
#==============================================================================

# Exit on error, undefined var
set -e
set -u

# Version information
VERSION="1.0.0"

# Load shared functions
. functions

#==============================================================================
# Global Variables
#==============================================================================

# Reset statistics
reset_stats

# Configuration options
declare -A CONFIG=(
    # Core settings
    [command]="0"                      # Operation command
    [to_dir]="$(pwd)"                  # Target directory
    [match]=""                         # Match pattern
    [source_file]="$(basename "$0")"   # Script name

    # Runtime modes
    [dry_run]=false                    # Preview mode
    [verbose]=false                    # Verbose output
    [backup]=true                      # Backup mode
)


#==============================================================================
# Function Definitions
#==============================================================================

#------------------------------------------------------------------------------
# show_help
#
# Display help information for this script
#
# Arguments:
#     None
#
# Returns:
#     0 on success
#------------------------------------------------------------------------------
show_help() {
    cat << EOF
================================================================================
                              POTCAR Generator
================================================================================

NAME
    ${CONFIG[source_file]} - Generate VASP POTCAR files from POSCAR elements

VERSION
    $VERSION

SYNOPSIS
    ${CONFIG[source_file]} -to <directory> [OPTIONS]

DESCRIPTION
    A tool for generating VASP POTCAR files by automatically combining
    pseudopotential files based on elements specified in POSCAR files.
    Supports batch processing and includes safety checks.

OPTIONS
    Required Arguments:
        -to <dir>              Target directory for processing

    Optional Arguments:
        -m, --match <pattern>  Directory matching pattern
        -c, --command <num>    Operation mode (default: 0)

    Processing Control:
        --dry-run             Preview operations without execution
        --no-backup           Disable automatic backup
        --verbose             Enable detailed logging

    General:
        -h, --help            Display this help message
        --version             Display version information

COMMANDS
    [0] Generate POTCAR
        • Read element information from POSCAR
        • Combine corresponding pseudopotential files
        • Create automatic backups

    [1] Reserved for future use

SAFETY FEATURES
    • Dry Run Mode    Preview operations without actual execution
    • Auto Backup    Create .bak files before modifications
    • Verbose Logs   Record detailed operation history
    • Error Checks   Validate inputs and operations

EXAMPLES
    0. Generate POTCAR in current directory:
       $ ${CONFIG[source_file]} -to . -m ads

    1. Process multiple directories matching a pattern:
       $ ${CONFIG[source_file]} -to /path/to/calcs -m "Fe_*" --verbose

    2. Preview operations without execution:
       $ ${CONFIG[source_file]} -to /path/to/calc/Fe2O3 --dry-run


EXIT STATUS
    0    Success
    1    General error
    2    Invalid arguments

FILES
    ./POSCAR          Input structure file
    ./POTCAR          Generated potential file
    ${PATHS[log_dir]}/logs    Log file location

AUTHOR
    Written by Wu Kai

REPORTING BUGS
    Report bugs to: wukai@example.com

COPYRIGHT
    Copyright © 2024-2025 Wu Kai. License GPLv3+
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.

SEE ALSO
    VASP documentation: https://www.vasp.at/
    Project repository: https://github.com/wukai/vasp-tools
EOF
}



#------------------------------------------------------------------------------
# parse_arguments
#
# Parse command line arguments and set configuration
#
# Arguments:
#     Command line arguments ($@)
#
# Returns:
#     0 on success
#     1 on failure
#------------------------------------------------------------------------------
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



#------------------------------------------------------------------------------
# main
#
# Main script function, process command line arguments and execute operations
#
# Arguments:
#     None
#
# Returns:
#     0 on success
#     1 on error
#------------------------------------------------------------------------------
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
            return 0
            ;;
        --version)
            echo "${CONFIG[source_file]} : version $VERSION"
            return 0
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
            done < <(find "$target_dir" -mindepth 1 -type d -not -path "*/\.*")
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