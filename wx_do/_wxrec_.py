#微信接受消息，不支持合并的聊天记录！！

from wxauto import WeChat
import re

def re_name(text):
    # 使用正则表达式匹配第一个“提到：”之后的内容
    match = re.search(r'提到：(.*)', text)
    if match:
        return match.group(1).strip()
    else:
        return None
    
def is_path_format(text):
    # 正则表达式模式
    windows_path_pattern = r'^[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$'
    unix_path_pattern = r'^/(?:[^/\0]*)*$'
    
    # 检查 Windows 路径
    if re.match(windows_path_pattern, text):
        return True
    
    # 检查 Unix/Linux/Mac 路径
    if re.match(unix_path_pattern, text):
        return True
    
    return False


def new_msg(msgs):
    # 提取name和con
    name = list(msgs.keys())[0]
    con = [f"{item[0]}提到：{item[1]}" for item in msgs[name]]
    
    return name, con

def read_msg(le):
    result = []
    wx = WeChat()
    # 获取当前聊天窗口消息
    msgs = wx.GetAllMessage(
        savepic   = True,   # 保存图片
        savefile  = True,   # 保存文件
        savevoice = True    # 保存语音转文字内容
    )
    k=0
    i=len(msgs)-1
    while k<le:
        msg=msgs[i]
        if msg.type == 'friend':
            sender = msg.sender_remark # 这里可以将msg.sender改为msg.sender_remark，获取备注名
            result.append(f'{sender}提到：{msg.content}')
            k=k+1
        i=i-1
    result.reverse()  # 反向排列结果数组
    return result

def wxrec():
    result = []
    wx = WeChat()
    # 获取下一条新消息
    msgs = wx.GetNextNewMessage()
    print(msgs)
    if msgs != {}:
        name, rawcon = new_msg(msgs)
        print(rawcon)
        a = [item[0] for item in msgs[name]]
        if a[-1] == 'Self':
            return 0
        try:
            con = read_msg(len(rawcon))
            # 遍历rawcon和con两个数组
            print(con)
            wx.SwitchToContact()
            for i in range(len(rawcon)):
                if rawcon[i] != con[i] and is_path_format(re_name(con[i])):
                    result.append('<文件>：' + con[i])
                elif con[i] not in rawcon:
                    result.append('语音或特殊消息：' + con[i])
                else:
                    result.append(con[i])
            return name, result
        except Exception as e:
            print(f"An error occurred: {e}")
            return name, rawcon
    else:
        return 0
    

#name, text =wxrec()
#print(name,text)
