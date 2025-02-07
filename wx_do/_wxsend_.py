from wxauto import WeChat
import os

def wxsend(msg, who, n):
    wx = WeChat()
    try:
        
        # 发送消息
        if msg:
            wx.SendMsg(msg=msg, who=who)
        
        # 准备文件路径列表
        files = []
        folder_path = r'D:\Desktop\pywx\attachments_send'
        
        # 确保文件夹存在
        if not os.path.exists(folder_path):
            return "错误: 指定的文件夹不存在且无法创建。"
        
        for i in range(1, n + 1):
            file_name = f'file{i}'
            file_path = None
            
            # 查找文件夹中匹配的文件
            for filename in os.listdir(folder_path):
                if filename.startswith(file_name):
                    file_path = os.path.join(folder_path, filename)
                    break
            
            if not file_path:
                return f"错误: 文件 {file_name} 在指定文件夹中未找到。"
            
            files.append(file_path)
        
        # 发送文件
        if files:
            wx.SendFiles(filepath=files, who=who)
        wx.SwitchToContact()
        
        return False
    
    except Exception as e:
        wx.SwitchToContact()
        return f"发生错误: {e}"



