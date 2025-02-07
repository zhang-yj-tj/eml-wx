import logging
import os
from datetime import datetime
import inspect

logger = None

def setup_logger():
    global logger
    if logger:
        return logger
    
    # 确保log文件夹存在
    log_folder = 'log'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # 生成日志文件名，包含当前时间
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = f'{timestamp}.log'
    log_filepath = os.path.join(log_folder, log_filename)

    # 创建一个logger对象
    logger = logging.getLogger('example_logger')
    logger.setLevel(logging.DEBUG)  # 设置日志级别为DEBUG

    # 创建一个file handler，将日志写入到文件中，并指定编码为utf-8
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 创建一个formatter，并将其添加到handler中
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(variables)s')
    file_handler.setFormatter(formatter)

    # 将handler添加到logger中
    logger.addHandler(file_handler)
    
    return logger

def log_message(message):
    logger = setup_logger()
    
    # 获取调用者帧
    frame = inspect.currentframe().f_back
    # 获取局部变量字典
    local_vars = frame.f_locals
    
    # 使用logger记录消息
    extra = {'variables': str(local_vars)}
    logger.debug(message, extra=extra)



