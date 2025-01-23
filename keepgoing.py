import time
import sys
import select

exit_symbol = 'q'  # 设置退出符号为 'q'

print(f"程序运行中...输入 '{exit_symbol}' 可以退出程序")

while True:
    time.sleep(100)
    print("Keep going")
    
    # 检查是否有输入
    if sys.stdin.isatty() and sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        user_input = sys.stdin.readline().strip()
        if user_input == exit_symbol:
            print("程序退出...")
            break