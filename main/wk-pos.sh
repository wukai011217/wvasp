#!/bin/bash
#==============================================================================
# 脚本信息
#==============================================================================
# 名称: pos-to-all
# 描述: 生成和修改 POSCAR 文件
# 用法: pos-to-all [OPTIONS]
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
    [file]="POSCAR"                    # 输入文件
    [command]="0"                      # 命令
    [to_dir]="$(pwd)"                  # 目标目录
    [match]=""                         # 匹配字符
    [source_file]="$(basename "$0")"   # 脚本文件
    
    # 运行模式
    [dry_run]=false                    # 模拟运行模式
    [verbose]=false                    # 详细输出模式
    [backup]=true                      # 备份模式
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
===============================================================================
                           POSCAR Processing Tool
===============================================================================

Usage: 
    $(basename "$0") [OPTIONS]

Description:
    A versatile tool for processing VASP POSCAR structure files. Supports multiple
    operations including element substitution, structure transformations, and
    charge analysis. Features dry-run mode and automatic backups for safety.

Options:
    File Control:
        -f, --file FILE      Specify input file (default: POSCAR)
        -to DIR             Set target directory (default: current)
        -m, --match PAT     Match pattern for elements/structures
    
    Operation Control:
        -c, --command NUM   Set operation mode (see Commands below)
    
    Safety Options:
        --dry-run          Preview changes without modifying files
        --no-backup        Disable automatic backup creation
        --verbose          Enable detailed operation logging
    
    General:
        -h, --help         Show this help message
        --version          Display version information

Commands:
    [0] POSCAR 复制和替换
        • 复制 POSCAR 到指定目录
        • 替换元素符号
        • 自动创建备份
    
    [1] M 到 M-H 转换
        • 处理 M 结构中的氢原子
        • 生成 M-H 结构
        • 保持其他原子位置不变

    [2] Bader 电荷分析
        • 准备 Bader 分析目录
        • 复制必要的输入文件
        • 配置计算参数

    [3] M-H 到 2H 相变
        • 将 M-H 结构转换为 2H 相
        • 调整原子位置
        • 维持对称性
    
    [4] FFF 模式处理
        • 处理 POSCAR 中的 T/F 标记
        • 将 z < 0.2 的原子设为固定 (F)
        • 保持其他原子的约束不变

Safety Features:
    • Dry Run Mode     - Preview all operations before execution
    • Auto Backup     - Creates .bak files before modifications
    • Verbose Logging - Detailed operation tracking

Examples:
    0. Preview Element Substitution:
       $(basename "$0") -f POSCAR -to /path/to/M -c 0 -m "Fe_*" 

    1. Process M to M-H:
       $(basename "$0") -to /path/to/M -c 1 -m "M/ads"

    2. process ads to bader:
       $(basename "$0") -to /path/to/ads  -c 2 -m "M/ads" 

    3. Process M to M-2H:
       $(basename "$0") -to /path/to/M -c 3 -m "M/ads"

    4. Process FFF Format:
       $(basename "$0") -to /path/to/fff -c 4 -m "M/ads"

Best Practices:
    • Always use --dry-run first to preview changes
    • Keep backups enabled unless specifically not needed
    • Use verbose mode for detailed operation logs
    • Verify input files before processing
EOF
}

# 函数: parse_arguments
# 描述: 解析命令行参数并设置配置
# 参数:
#   $@ - 命令行参数
# 返回: 0=成功, 1=失败
parse_arguments() {
    # 处理特定参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -f|-F|--file)
                if [[ -z "$2" || "$2" == -* ]]; then
                    logging 2 "${CONFIG[source_file]}: File name required for $1"
                    return 1
                fi
                CONFIG[file]="$2"
                logging 1 "Input file set to: ${CONFIG[file]}"
                shift 2
                ;;
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
                    return 1 # wukai_test
                fi
                break
                ;;
        esac
    done
    
}

# 函数: process_one_to_all
# 描述: 复制POSCAR并替换其中的元素
# 参数:
#   $1 - 目标目录
# 返回: 0=成功, 1=失败

process_one_to_all() {
    local target_dir="$1"
    
    # 检查目标目录（检查目录是否存在、是否为空、是否匹配模式）
    check_path "$target_dir" "directory" true "${CONFIG[match]}" || return 0
    
    # 记录总文件数
    update_stats "total"
    
    # 处理元素替换
    local element_found=false
    for element in "${ELEMENTS[@]}"; do
        if [[ $target_dir == *"/$element/"* ]]; then
            element_found=true
            local target_file="$target_dir/POSCAR"
            
            # 检查目标文件
            if [[ -f "$target_file" ]]; then
                    logging 1 "Warning: POSCAR already exists in $target_dir"
                    if [[ "${CONFIG[backup]}" == true ]]; then
                        if ! create_backup "$target_file"; then
                            update_stats "failed"
                            return 0
                        fi
                    else
                        logging 1 "Skipping existing file: $target_file"
                        update_stats "skipped"
                        return 0
                    fi
            fi
            
            # 模拟运行模式
            if [[ "${CONFIG[dry_run]}" == true ]]; then
                logging 1 "[DRY RUN] Would copy ${CONFIG[file]} to $target_file"
                logging 1 "[DRY RUN] Would replace 'Ag' with '$element'"
                return 0
            fi
            
            # 复制和替换
            if cp "${CONFIG[file]}" "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
                if sed -i "s/Ag/$element/g" "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
                    update_stats "processed"
                    logging 1 "Successfully processed: $target_file"
                else
                    logging 2 "${CONFIG[source_file]}: Failed to replace element in $target_file"
                    update_stats "failed"
                fi
            else
                logging 2 "${CONFIG[source_file]}: Failed to copy file to $target_file"
                update_stats "failed"
            fi
        fi
    done
    
    # 检查是否找到元素
    if [[ "$element_found" != true ]]; then
        logging 1 "No matching element found in directory: $target_dir"
        update_stats "skipped"
    fi
    
    return 0
}

# 函数: process_m_to_mh
# 描述: 处理 M 到 M-H 结构的转换
# 参数:
#   $1 - 目标目录
# 返回: 0=成功, 1=失败
process_m_to_mh() {
    local target_dir="$1"
    
    # 检查目标目录（检查目录是否存在、是否为空、是否匹配模式）
    check_path "$target_dir" "directory" true "${CONFIG[match]}" || return 0
    
    # 检查是否为 M 目录
    if [[ ! "$target_dir" == *"/M/ads" ]]; then
        logging 1 "Not a M directory: $target_dir"
        update_stats "skipped"
        return 0
    fi

    # 记录总文件数
    update_stats "total"


    
    # 检查和验证 CONTCAR 文件
    local contcar_file="$target_dir/CONTCAR"
    if ! check_path "$contcar_file" "file"; then
        logging 2 "${CONFIG[source_file]}: CONTCAR not found in $target_dir"
        update_stats "failed"
        return 0
    fi
    
    if ! validate_poscar "$contcar_file"; then
        logging 2 "${CONFIG[source_file]}: Invalid CONTCAR format in $target_dir"
        update_stats "failed"
        return 0
    fi
    
    # 模拟运行模式
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would process M to M-H conversion in $target_dir"
        logging 1 "[DRY RUN] Would create M-H directory and copy modified CONTCAR"
        return 0
    fi

    # 创建 M-H 目录
    local mh_dir="$target_dir/../../M-H/ads" #wukai
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would create directory: $mh_dir"
        return 0
    fi
    
    if ! mkdir -p "$mh_dir" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "${CONFIG[source_file]}: Failed to create directory: $mh_dir"
        update_stats "failed"
        return 1
    fi
    
    # 检查目标文件
    local target_file="$mh_dir/POSCAR"
    if [[ -f "$target_file" ]]; then
            logging 1 "Warning: POSCAR already exists in $mh_dir"
            if [[ "${CONFIG[backup]}" == true ]]; then
                if ! create_backup "$target_file"; then
                    update_stats "failed"
                    return 1
                fi
            else
                logging 1 "Skipping existing file: $target_file"
                update_stats "skipped"
                return 0
            fi
    fi
    
    # 复制文件
    if ! cp "$contcar_file" "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "${CONFIG[source_file]}: Failed to copy CONTCAR to $target_file"
        update_stats "failed"
        return 0
    fi
    
    # 计算原子总数
    local num=$(awk 'NR==7 {sum=0; for(i=1; i<=NF; i++) sum+=$i; print sum}' "$target_file")
    if [[ -z "$num" ]]; then
        logging 2 "${CONFIG[source_file]}: Failed to calculate atom count in $target_file"
        update_stats "failed"
        return 0
    fi
    num=$(($num + 9))
    
    # 修改文件
    if ! sed -i '6s/$/ H/' "$target_file" 2>> "${PATHS[log_dir]}/logs" || \
       ! sed -i "${num}a\0.446598 0.216020 0.433410 T T T " "$target_file" 2>> "${PATHS[log_dir]}/logs" || \
       ! sed -i '7s/$/ 1/' "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "${CONFIG[source_file]}: Failed to modify POSCAR in $mh_dir"
        update_stats "failed"
        return 0
    fi
    
    # 更新统计信息
    update_stats "processed"
    logging 1 "Successfully processed: $target_file"
    
    return 0
}

# 函数: process_m_to_m2h
# 描述: 处理 M 到 M-2H 结构的转换
# 参数:
#   $1 - 目标目录
# 返回: 0=成功, 1=失败

process_m_to_m2h() {
    local target_dir="$1"
    
    # 检查目标目录（检查目录是否存在、是否为空、是否匹配模式）
    check_path "$target_dir" "directory" true "${CONFIG[match]}" || return 0
    
    # 检查是否为 M/ads 目录
    if [[ ! "$target_dir" == *"M/ads" ]]; then
        logging 1 "Not a M/ads directory: $target_dir"
        update_stats "skipped"
        return 0
    fi


    
    # 记录总文件数
    update_stats "total"
    
    # 检查和验证 CONTCAR 文件
    local contcar_file="$target_dir/CONTCAR"
    if ! check_path "$contcar_file" "file"; then
        logging 2 "${CONFIG[source_file]}: CONTCAR not found in $target_dir"
        update_stats "failed"
        return 0
    fi
    
    if ! validate_poscar "$contcar_file"; then
        logging 2 "${CONFIG[source_file]}: Invalid CONTCAR format in $target_dir"
        update_stats "failed"
        return 0
    fi
    
    # 模拟运行模式
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would process M to M-2H conversion in $target_dir"
        logging 1 "[DRY RUN] Would create M-2H directory and copy modified CONTCAR"
        return 0
    fi

    # 创建 M-2H/ads 目录
    local m2h_dir="$target_dir/../../M-2H/ads"
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would create directory: $m2h_dir"
        return 0
    fi
    
    if ! mkdir -p "$m2h_dir" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "${CONFIG[source_file]}: Failed to create directory: $m2h_dir"
        update_stats "failed"
        return 1
    fi
    
    # 检查目标文件
    local target_file="$m2h_dir/POSCAR"
    if [[ -f "$target_file" ]]; then
            logging 1 "Warning: POSCAR already exists in $m2h_dir"
            if [[ "${CONFIG[backup]}" == true ]]; then
                if ! create_backup "$target_file"; then
                    update_stats "failed"
                    return 1
                fi
            else
                logging 1 "Skipping existing file: $target_file"
                update_stats "skipped"
                return 0
            fi
    fi
    
    # 复制文件
    if ! cp "$contcar_file" "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "Failed to copy CONTCAR to $target_file"
        update_stats "failed"
        return 0
    fi
    
    # 计算原子总数
    local num=$(awk 'NR==7 {sum=0; for(i=1; i<=NF; i++) sum+=$i; print sum}' "$target_file")
    if [[ -z "$num" ]]; then
        logging 2 "Failed to calculate atom count in $target_file"
        update_stats "failed"
        return 0
    fi
    num=$(($num + 9))
    
    # 计算目标原子位置
    local tar=$(awk 'NR==7 {sum=0; for(i=1; i<=2; i++) sum+=$i; print sum}' "$target_file")
    if [[ -z "$tar" ]]; then
        logging 2 "Failed to calculate target atom position in $target_file"
        update_stats "failed"
        return 0
    fi
    tar=$(($tar + 9))
    
    # 修改文件
    if ! sed -i '6s/$/ H/' "$target_file" 2>> "${PATHS[log_dir]}/logs" || \
       ! sed -i "${num}a\0.446598 0.216020 0.433410 T T T " "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "Failed to add H atom in $target_file"
        update_stats "failed"
        return 0
    fi
    
    # 调整原子位置
    if ! awk -v tar=$tar -v num=$num 'NR==tar {line=$0} NR==num+1 {print line} {print}' "$target_file" > "$target_file.temp" && \
       mv "$target_file.temp" "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "Failed to adjust atom positions in $target_file"
        update_stats "failed"
        return 0
    fi
    
    # 调整 Z 坐标
    if ! awk -v num=$num 'NR == num+1 { $3 = $3 + 0.1 } { print }' "$target_file" > "$target_file.temp" && \
       mv "$target_file.temp" "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "Failed to adjust Z coordinate in $target_file"
        update_stats "failed"
        return 0
    fi
    
    # 更新原子数
    if ! sed -i '7s/$/ 2/' "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "Failed to update atom count in $target_file"
        update_stats "failed"
        return 0
    fi

    rm "$target_file.temp"

    # 更新统计信息
    update_stats "processed"
    logging 1 "Successfully processed: $target_file"
    
    return 0
}
    

# 函数: process_ads_to_bader
# 描述: 准备 Bader 电荷分析所需的文件和目录
# 参数:
#   $1 - 目标目录
# 返回: 0=成功, 1=失败

process_ads_to_bader() {
    local target_dir="$1"
    
    # 检查目标目录（检查目录是否存在、是否为空、是否匹配模式）
    check_path "$target_dir" "directory" true "${CONFIG[match]}" || return 0


    
    # 检查是否为 ads 目录
    if [[ ! "$target_dir" == *"/ads" ]]; then
        logging 1 "Not an ads directory: $target_dir"
        update_stats "skipped"
        return 0
    fi
    
    # 记录总文件数
    update_stats "total"
    
    # 检查必要文件
    local required_files=("CONTCAR" "POTCAR" "KPOINTS" "vasp.sbatch")
    local missing_files=()
    for file in "${required_files[@]}"; do
        if ! check_path "$target_dir/$file" "file"; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        logging 2 "Missing required files in $target_dir: ${missing_files[*]}"
        update_stats "failed"
        return 0
    fi
    
    # 验证 CONTCAR 文件
    if ! validate_poscar "$target_dir/CONTCAR"; then
        logging 2 "Invalid CONTCAR format in $target_dir"
        update_stats "failed"
        return 0
    fi
    
        # 模拟运行模式
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would process Bader charge analysis in $target_dir"
        logging 1 "[DRY RUN] Would create CHGCAR and AECCAR files"
        return 0
    fi

    # 创建 bader 目录
    local bader_dir="$target_dir/../bader"
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would create directory: $bader_dir"
        logging 1 "[DRY RUN] Would copy VASP files to: $bader_dir"
        return 0
    fi
    
    if ! mkdir -p "$bader_dir" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "Failed to create directory: $bader_dir"
        update_stats "failed"
        return 1
    fi
    
    # 检查目标文件
    local files_exist=false
    for file in "${required_files[@]}"; do
        local target_file="$bader_dir/${file/CONTCAR/POSCAR}"
        if [[ -f "$target_file" ]]; then
            files_exist=true
            break
        fi
    done
    
    if [[ "$files_exist" == true ]]; then
            logging 1 "Warning: Files already exist in $bader_dir"
            if [[ "${CONFIG[backup]}" == true ]]; then
                for file in "${required_files[@]}"; do
                    local target_file="$bader_dir/${file/CONTCAR/POSCAR}"
                    if [[ -f "$target_file" ]]; then
                        if ! create_backup "$target_file"; then
                            update_stats "failed"
                            return 1
                        fi
                    fi
                done
            else
                logging 1 "Skipping existing files in: $bader_dir"
                update_stats "skipped"
                return 0
            fi
    fi
    
    # 复制文件
    local success=true
    for file in "${required_files[@]}"; do
        local source_file="$target_dir/$file"
        local target_file="$bader_dir/${file/CONTCAR/POSCAR}"
        if ! cp "$source_file" "$target_file" 2>> "${PATHS[log_dir]}/logs"; then
            logging 2 "Failed to copy $file to $target_file"
            success=false
            break
        fi
    done
    
    if [[ "$success" != true ]]; then
        update_stats "failed"
        return 0
    fi
    
    # 更新统计信息
    update_stats "processed"
    logging 1 "Successfully prepared Bader analysis in $bader_dir"
    
    return 0
}

# 函数: process_FFF
# 描述: 处理 POSCAR 文件的 FFF 模式，设置原子的固定状态
# 参数:
#   $1 - 目标目录
# 返回: 0=成功, 1=失败

process_FFF() {
    local target_dir="$1"
    
    # 检查目标目录（检查目录是否存在、是否为空、是否匹配模式）
    check_path "$target_dir" "directory" true "${CONFIG[match]}" || return 0
    
    # 记录总文件数
    update_stats "total"
    
    # 检查并验证 POSCAR 文件
    local poscar_file="$target_dir/POSCAR"
    if ! check_path "$poscar_file" "file"; then
        logging 2 "POSCAR not found in $target_dir"
        update_stats "failed"
        return 0
    fi
    
    if ! validate_poscar "$poscar_file"; then
        logging 2 "Invalid POSCAR format in $target_dir"
        update_stats "failed"
        return 0
    fi
    
    # 检查是否需要备份
    if [[ "${CONFIG[backup]}" == true ]]; then
        if ! create_backup "$poscar_file"; then
            logging 2 "Failed to create backup for POSCAR"
            update_stats "failed"
            return 1
        fi
    fi
    
    # 模拟运行模式
    if [[ "${CONFIG[dry_run]}" == true ]]; then
        logging 1 "[DRY RUN] Would convert T/F flags in: $poscar_file"
        return 0
    fi
    
    # 转换 T/F 标志
    local temp_file="$target_dir/POSCAR.tmp"
    if ! awk 'NR>=10 {if ($3 < 0.2) gsub("T", "F")}1' "$poscar_file" > "$temp_file" 2>> "${PATHS[log_dir]}/logs"; then #wukai 使用变量替换z轴
        logging 2 "Failed to process POSCAR in $target_dir"
        update_stats "failed"
        rm -f "$temp_file"
        return 0
    fi
    
    # 检查处理后的文件
    if ! validate_poscar "$temp_file"; then
        logging 2 "Invalid POSCAR format after processing in $target_dir"
        update_stats "failed"
        rm -f "$temp_file"
        return 0
    fi
    
    # 移动临时文件
    if ! mv "$temp_file" "$poscar_file" 2>> "${PATHS[log_dir]}/logs"; then
        logging 2 "Failed to update POSCAR in $target_dir"
        update_stats "failed"
        rm -f "$temp_file"
        return 0
    fi
    
    # 更新统计信息
    update_stats "processed"
    logging 1 "Successfully processed FFF mode in $target_dir"
    
    return 0
}

#==============================================================================
# 程序入口
#==============================================================================

# 函数: main
# 描述: 脚本的主函数，处理命令行参数并调用相应的处理函数
# 参数: 无
# 返回: 0=成功, 1=失败
#   0 - 成功
#   1 - 失败
main() {
    local command="${CONFIG[command]}"
    local start_time=$(date +%s)
    local target_dir="${CONFIG[to_dir]}"
    
    check_config_and_display || { logging 2 "${CONFIG[source_file]} : Failed to check configuration"; return 1; }

    # 定义命令映射
    declare -A COMMAND_MAP=(
        [0]="Element Substitution:process_one_to_all"
        [1]="M to M-H Conversion:process_m_to_mh"
        [2]="Bader Analysis Preparation:process_ads_to_bader"
        [3]="M to M-2H Conversion:process_m_to_m2h"
        [4]="FFF Mode Conversion:process_FFF"
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
        [0-4])
            local IFS=':'
            local cmd_info=(${COMMAND_MAP[$command]})
            unset IFS
            local description="${cmd_info[0]}"
            local processor="${cmd_info[1]}"
            logging 1 "Processing: $description"
            echo "${CONFIG[source_file]} Processing: $description"
            echo "$target_dir"
            while IFS= read -r dir; do
                # 检查目录是否有子目录
                if [ ! -z "$(find "$dir" -mindepth 1 -maxdepth 1 -type d 2>/dev/null)" ]; then
                    continue
                fi #wukai
                
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


# 初始化脚本
initialize || { logging 2 "${CONFIG[source_file]} : Failed to initialize script"; exit 1; }

# 解析命令行参数
parse_arguments "$@" || { logging 2 "${CONFIG[source_file]} : Failed to parse arguments"; exit 1; }

# 记录运行环境
log_environment

# 执行主程序
main || { logging 2 "${CONFIG[source_file]} : Failed to execute main function"; exit 1; }