import os
from friends.find_friends import rec_friend
from log.print_log import log_message
import psutil
import subprocess
from main import main

def stop_pro(main_program_name):
    # 查找所有正在运行的 Python 进程
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                print(f"Checking process: {proc.info['pid']} - CMDLINE: {proc.info['cmdline']}")
                if proc.info['cmdline'] and any(main_program_name in arg for arg in proc.info['cmdline']):
                    print(f"Terminating process: {proc.info['pid']} - {proc.info['cmdline']}")
                    proc.terminate()
                    proc.wait()  # 等待进程终止
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print(f"Exception occurred for PID: {proc.info.get('pid')}, Name: {proc.info.get('name')}")


def delete_log_files():
    log_folder = 'log'
    # 遍历log文件夹中的所有文件
    for filename in os.listdir(log_folder):
        if filename.endswith('.log'):
            file_path = os.path.join(log_folder, filename)
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

def delete_all_files():
    folder = 'wxauto文件'
    # 遍历folder文件夹中的所有文件
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

stop_pro('main.py')
log_message('debug:停止主程序')
while True:
    print("\n请输入选择:")
    print("1. 同步联系人列表")
    print("2. 更改邮箱")
    print("3. 删除所有保存的文件")
    print("4. 删除日志文件")
    print("5. 退出")
    print("6. 退出并启动主程序")


    choice = input("您的选择是: ")

    if choice == '1':
        log_message('debug:同步联系人列表')
        rec_friend()
    elif choice == '2':
        log_message('debug:更改邮箱')
        os.system('cd eml&ouput_auth.py')
    elif choice == '3':
        log_message('debug:删除所有保存的文件')
        delete_all_files()
    elif choice == '4':
        log_message('debug:删除日志文件')
        delete_log_files()
    elif choice == '5':
        log_message('debug:退出')
        print("退出程序")
        break
    elif choice == '6':
        log_message('debug:退出并启动主程序')
        print("主程序开始运行...")
        main()
        break
    else:
        print("无效的选择，请重新输入")

