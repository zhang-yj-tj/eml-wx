# friends/unlock.py
import sqlite3
import json
import os
import urllib.parse

def get_friend(database_name):
    # 自动添加 .db 后缀
    database_name_with_extension = f"{database_name}.db"
    
    # 获取 friends 文件夹的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构造 auth.json 和数据库文件的路径
    auth_json_path = os.path.join(script_dir, 'auth.json')
    db_path = os.path.join(script_dir, database_name_with_extension)

    # 加载auth.json文件以获取数据库密码
    try:
        with open(auth_json_path, 'r') as f:
            auth_data = json.load(f)
    except FileNotFoundError:
        print("auth.json 文件未找到，请确保已正确生成并存储密码。")
        return None

    # 获取数据库密码
    if db_path in auth_data:
        password = auth_data[db_path]
    else:
        print(f"数据库 '{db_path}' 的密码未在 auth.json 文件中找到。")
        return None

    # 连接到SQLCipher数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 解密数据库
    encoded_password = urllib.parse.quote(password)
    cursor.execute(f'PRAGMA key = "{encoded_password}"')

    # 查询联系人表中的所有数据
    cursor.execute('SELECT * FROM contacts')
    rows = cursor.fetchall()

    # 关闭连接
    conn.close()

    return rows

if __name__ == "__main__":
    name = input('请输入要解锁的用户名:')
    # 示例调用
    contacts = get_friend(name)
    for i in contacts:
        print(i)
    input()
