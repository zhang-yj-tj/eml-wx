from eml.eml import read_eml, send_eml
from wx_do._wxrec_ import wxrec
from friends.find_friends import rec_friend
from friends.unlock import get_friend
from wx_do._wxsend_ import wxsend
from log.print_log import log_message

import time
import os
from wxauto import WeChat
import random
import re
from io import StringIO
from contextlib import redirect_stdout

def find_user():
    log_message('core:匹配user')
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
    return username

def is_file(s):
    pattern = r'^<文件>：'
    match = re.match(pattern, s)
    return match is not None
def remove_file(s):
    pattern = r'^<文件>：'
    cleaned_name = re.sub(pattern, '', s)
    return os.path.basename(cleaned_name)

def eml_text(text):
    log_message('core:匹配eml')
    # 统一换行符为 \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 匹配第一个换行符的位置
    match = re.search(r'\n', text)
    if match:
        index = match.start()
        before_newline = text[:index]
        after_newline = text[index+1:]
    else:
        before_newline = text
        after_newline = ''
    
    # 匹配第一次连续三个换行，并保留换行前的部分
    match = re.search(r'^(.*?)(?=\n{3,})', after_newline, re.DOTALL)
    if match:
        result = match.group(1)
    else:
        result = after_newline
    
    # 将所有的两次换行替换为一次换行
    result = re.sub(r'\n{2,}', '\n', result)
    
    return before_newline, result

def match_friend(data, target):
    log_message('core:匹配fri')
    if target == '':
        return ('-', '-', '文件传输助手', '-')
    for item in data:
        if item[2] == target:
            return item
    for item in data:
        if item[2] and target in item[2]:  # 检查 item[2] 是否为空
            return item
    for item in data:
        if item[1] == target:
            return item
    return ('-', '-', target, '-')

def try_wxrec():
    log_message('core:读取wx消息')
    a = wxrec()
    #这里加入自动回复（如需要）
    if a!=0:
        log_message('core:读取成功，转发eml')
        name,con=a
        f = []
        t = name+'中：\n\n'
        for i in con:
            if is_file(i):
                f.append(remove_file(i))
                t = t + '发出了文件' + remove_file(i) + '\n\n'
            else:
                t = t + i + '\n\n'
        send_eml(t,f)
        return True
    else:
        return False

def try_mailrec():
    log_message('core:读取mail消息')
    raw,n_f = read_eml()
    if raw!='':
        name ,text = eml_text(raw)
        name = match_friend(get_friend(find_user()),name)
        return text ,name , n_f
    else:
        return False

def do_wxsend(text,name,n_f):
    log_message('core:发送wx消息')
    z = wxsend(text , name[2] , n_f)
    if z:
        send_eml('发送失败！\n\n发给'+str(name)+'时产生错误信息：\n'+z)
        return True
    else:
        send_eml('发送成功！\n\n'+str(name)+'：\n'+text+'；\n'+str(n_f)+'个附件')
        return False
