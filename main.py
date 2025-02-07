from core import try_wxrec, try_mailrec, do_wxsend
from log.print_log import log_message
import random
import time
import multiprocessing
import os
import sys
import psutil

def check_and_terminate_same_program():
    # 获取当前脚本的文件名
    current_process_name = os.path.basename(sys.argv[0])
    # 获取当前进程的 PID
    current_pid = os.getpid()

    print(f"Current Process Name: {current_process_name}, Current PID: {current_pid}")

    # 遍历所有正在运行的进程，并获取每个进程的 pid 和 name 属性
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 检查进程名是否与当前脚本的文件名相同，并且进程 ID 不是当前进程的 ID
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                print(f"Checking process: {proc.info['pid']} - CMDLINE: {proc.info['cmdline']}")
                if any(current_process_name in arg for arg in proc.info['cmdline']) and proc.info['pid'] != current_pid:
                    # 打印要终止的进程信息
                    print(f"Terminating process {proc.info['pid']} - CMDLINE: {proc.info['cmdline']}")
                    # 终止该进程
                    proc.terminate()
                    proc.wait()  # 等待进程终止
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # 忽略如果在检查过程中某个进程已经不存在的情况
            # 忽略如果没有权限终止某个进程的情况
            print(f"Exception occurred for PID: {proc.info.get('pid')}, Name: {proc.info.get('name')}")


def wait(a, b):
    sleep_duration = random.uniform(a, b)
    print(f"Waiting for {sleep_duration:.2f} seconds...")
    time.sleep(sleep_duration)

def main():
    while True:
        log_message('main:读取wx消息')
        try:
            print('读取wx消息')
            if try_wxrec():
                log_message('main:成功读取，等待1')
                print('等待1')
                wait(15, 30)
            else:
                print('等待2')
                log_message('main:无消息，等待2')
                for i in range(1, random.randint(20,25)):
                    wait(10, 30)
                    log_message('main:读取mail消息')
                    a = try_mailrec()
                    print('读取mail消息')
                    if a:
                        print('等待执行')
                        text, name, n_f = a
                        while try_wxrec():
                            print('成功读取')
                            log_message('main:读取wx消息')
                            wait(15, 30)
                        print('执行')
                        log_message('main:发送wx消息')
                        do_wxsend(text, name, n_f)
                        wait(15, 30)
        except Exception as e:
            print(f"An error occurred: {e}")
            # 可以在这里添加更多的错误处理逻辑，比如记录日志等
            wait(60,120)  # 发生错误后等待一段时间再继续

if __name__ == "__main__":
    log_message('进入主程序段')
    # 调用之前定义的函数来检查并终止同名进程
    check_and_terminate_same_program()
    # 在这里放置你的主程序逻辑
    print("主程序开始运行...")
    main()
