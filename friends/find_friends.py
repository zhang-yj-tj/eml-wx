# friends/find_friends.py
from wxauto import WeChat
import sqlite3
import secrets
import string
import json
from io import StringIO
from contextlib import redirect_stdout
import re
import os
import urllib.parse

def generate_strong_password(length=32):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def rec_friend():
    try:
        # 创建一个StringIO对象用于保存输出
        output = StringIO()

        # 使用redirect_stdout上下文管理器重定向标准输出
        with redirect_stdout(output):
            # 初始化WxAuto对象，任何print语句或标准输出都会被重定向到output
            wx = WeChat()

        # 获取输出内容，并关闭StringIO对象
        output_content = output.getvalue()
        output.close()

        # 打印捕获的输出内容以验证是否成功
        print(f"捕获的输出内容是:\n{output_content}")

        # 构建正则表达式模式，其中'：'之后的内容会被捕获
        pattern = r'^初始化成功，获取到已登录窗口：(.+)$'

        # 使用re.match尝试从字符串的开始位置匹配模式
        match = re.match(pattern, output_content)

        if not match:
            print("未找到匹配的用户名")
            return

        # 如果匹配成功，提取第一个捕获组，即用户名
        username = match.group(1)
        print(f"提取的用户名是: {username}")

        # 获取所有好友信息
        friend_infos = wx.GetAllFriends()
        
        # 切换到通讯录页面
        wx.SwitchToContact()

        # 确保 friend_infos 是一个列表
        if not isinstance(friend_infos, list):
            print("获取的好友信息格式不正确。")
            return

        contacts = friend_infos

        # 数据库名称
        database_name = f"{username}.db"
        print(f"生成的数据库名称是: {database_name}")

        # 获取 friends 文件夹的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 构造 auth.json 和数据库文件的路径
        auth_json_path = os.path.join(script_dir, 'auth.json')
        db_path = os.path.join(script_dir, database_name)

        # 加载现有的auth.json文件或创建一个新的
        try:
            with open(auth_json_path, 'r') as f:
                auth_data = json.load(f)
        except FileNotFoundError:
            auth_data = {}

        password = generate_strong_password()
        auth_data[db_path] = password
        print(f"生成的新密码是: {password}")

        # 将更新后的auth_data写回auth.json文件
        with open(auth_json_path, 'w') as f:
            json.dump(auth_data, f, indent=4)

        # 连接到SQLCipher数据库（如果数据库不存在，则会自动创建）
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 加密数据库
        encoded_password = urllib.parse.quote(password)
        cursor.execute(f'PRAGMA key = "{encoded_password}"')

        # 创建联系人表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            remark TEXT,
            tags TEXT
        )
        ''')

        # 清空 contacts 表以覆盖原有数据
        cursor.execute('DELETE FROM contacts')
        
        # 插入联系人数据
        for contact in contacts:
            # 确保tags是一个可迭代对象
            if isinstance(contact['tags'], list):
                tags_str = ', '.join(contact['tags'])
            else:
                tags_str = ''
            cursor.execute('INSERT INTO contacts (nickname, remark, tags) VALUES (?, ?, ?)', 
                           (contact['nickname'], contact['remark'], tags_str))

        # 提交事务并关闭连接
        conn.commit()
        conn.close()

        print(f"联系人已成功存储到加密的数据库 '{db_path}' 中。")

    except Exception as e:
        print(f"发生错误: {e}")

# 示例调用
#rec_friend()
