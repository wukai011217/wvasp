#!/bin/bash
# 定义起始和结束的作业ID

#default
start=616242
end=616327

#help
if [ $# -eq 2 ]; then
    start=$1
    end=$2
fi

# 打印起始和结束的作业ID
echo "起始作业ID: $start"
echo "结束作业ID: $end"

# 使用Bash循环遍历范围
for (( i=$start; i<=$end; i++ )); do
  scancel $i
done