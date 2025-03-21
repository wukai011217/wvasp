#!/bin/bash
#==============================================================================
# 脚本信息
#==============================================================================
# 名称: wk-sca
# 描述: 批量取消 SLURM 作业
# 用法: wk-sca [START_ID] [END_ID]
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
start=616242
end=616327

#==============================================================================
# 函数定义
#==============================================================================

# 函数: show_help
# 描述: 显示脚本的帮助信息
# 参数: 无
# 返回: 0=成功
show_help() {
    cat << EOF
wk-sca (SLURM Job Cancellation) v${VERSION}

Usage: 
    $(basename "$0") [START_ID] [END_ID]

Description:
    Cancel a range of SLURM jobs by their IDs.
    If no IDs are provided, uses default range.

Arguments:
    START_ID    Starting job ID (default: $start)
    END_ID      Ending job ID (default: $end)

Example:
    $(basename "$0") 100000 100010    # Cancel jobs from 100000 to 100010
    $(basename "$0")                  # Use default range
EOF
}

# 函数: parse_arguments
# 描述: 解析命令行参数
# 参数:
#   $@ - 命令行参数
# 返回: 0=成功
parse_arguments() {
    # 检查参数个数
    if [ $# -eq 2 ]; then
        start=$1
        end=$2
    elif [ $# -eq 1 ] && [ "$1" = "--help" -o "$1" = "-h" ]; then
        show_help
        exit 0
    elif [ $# -ne 0 ]; then
        echo "Error: Invalid number of arguments" >&2
        show_help
        exit 1
    fi
}

# 函数: cancel_jobs
# 描述: 取消指定范围的作业
# 参数: 无
# 返回: 0=成功
cancel_jobs() {
    # 打印起始和结束的作业 ID
    echo "起始作业 ID: $start"
    echo "结束作业 ID: $end"

    # 使用 Bash 循环遍历范围
    for (( i=$start; i<=$end; i++ )); do
        scancel $i
    done
}

#==============================================================================
# 程序启动
#==============================================================================

# 解析命令行参数
parse_arguments "$@"

# 取消作业
cancel_jobs