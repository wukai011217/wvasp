#!/bin/bash

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

# 设置输出颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -ne 1 ]; then
    echo "Usage: $0 <functions_file>"
    exit 1
fi

functions_file="$1"

# 检查文件是否存在
if [ ! -f "$functions_file" ]; then
    echo "Error: File '$functions_file' not found"
    exit 1
fi

echo -e "\n${GREEN}=== 全局变量 ===${NC}"
# 提取declare语句定义的全局变量
grep -A 1 "^declare" "$functions_file" | while read -r line; do
    if [[ $line == declare* ]]; then
        echo -e "${BLUE}$line${NC}"
    elif [[ $line == \#* ]]; then
        echo "$line"
    fi
done

echo -e "\n${GREEN}=== 函数定义 ===${NC}"
# 提取函数名和注释
awk '
    /^# 函数:/ {
        # 保存函数名注释
        comment = $0
        # 继续读取描述和参数
        while (getline && $0 ~ /^#/) {
            comment = comment "\n" $0
        }
        # 读取函数定义行
        if ($0 ~ /^[a-zA-Z0-9_-]+\(\)/) {
            # 提取函数名
            split($0, a, "()")
            funcname = a[1]
            print "\n" comment
            print "函数定义: " funcname
        }
    }
' "$functions_file"
