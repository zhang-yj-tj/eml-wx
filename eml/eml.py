from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64
import json
import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re

def generate_salt():
    """生成一个随机盐值"""
    return os.urandom(16)

def derive_key(password, salt):
    """使用PBKDF2HMAC生成一个密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password)

def decrypt_message(key, encrypted_message):
    """使用AES解密消息"""
    try:
        encrypted_message = base64.urlsafe_b64decode(encrypted_message)
        iv = encrypted_message[:16]
        ciphertext = encrypted_message[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_message.decode('utf-8')
    except Exception as e:
        print(f"解密失败: {e}")
        raise

def read_config(config_path):
    """读取配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("配置文件格式错误")
        return None

def load_auth_info():
    """从 auth.json 文件加载认证信息，并解密AES加密的密码"""
    try:
        # 修改路径到 eml 目录下
        with open(os.path.join('eml', 'auth.json'), 'r', encoding='utf-8') as f:
            auth_info = json.load(f)
        
        # 获取配置文件中的主密码
        config_path = os.path.join('eml', 'config.json')
        config = read_config(config_path)
        
        if not config or 'master_password' not in config:
            raise ValueError("配置文件中未找到主密码")
        
        master_encrypted_password = auth_info['master']['password']
        master_salt = base64.urlsafe_b64decode(auth_info['master']['salt'])
        master_password = base64.urlsafe_b64decode(config['master_password'])

        # 派生主密钥
        master_key = derive_key(master_password, master_salt)
        
        # 解密IMAP密码
        imap_salt = base64.urlsafe_b64decode(auth_info['imap']['salt'])
        imap_key = derive_key(master_password, imap_salt)
        auth_info['imap']['password'] = decrypt_message(imap_key, auth_info['imap']['password'])
        
        # 解密SMTP密码
        smtp_salt = base64.urlsafe_b64decode(auth_info['smtp']['salt'])
        smtp_key = derive_key(master_password, smtp_salt)
        auth_info['smtp']['password'] = decrypt_message(smtp_key, auth_info['smtp']['password'])
        
        # 解码Base64编码的邮箱地址
        auth_info['imap']['username'] = base64.urlsafe_b64decode(auth_info['imap']['username']).decode('utf-8')
        auth_info['smtp']['username'] = base64.urlsafe_b64decode(auth_info['smtp']['username']).decode('utf-8')
        
        return auth_info
    except FileNotFoundError:
        print("auth.json 文件未找到")
        raise
    except json.JSONDecodeError:
        print("auth.json 文件格式错误")
        raise
    except Exception as e:
        print(f"加载认证信息时发生错误: {e}")
        raise

def clean(subject):
    """清理邮件主题中的特殊字符"""
    return subject.replace('\r', '').replace('\n', '').replace(' ', '')

def get_file_extension(filename):
    """获取文件扩展名"""
    _, ext = os.path.splitext(filename)
    return ext

def save_attachment(payload, filename, folder_path, index):
    """保存附件到指定文件夹，并按索引重命名，保留扩展名"""
    # 解码附件文件名
    decoded_filename = ""
    for part in decode_header(filename):
        if isinstance(part[0], bytes):
            try:
                decoded_filename += part[0].decode(part[1] or "utf-8")
            except UnicodeDecodeError:
                decoded_filename += part[0].decode("latin-1")
        else:
            decoded_filename += part[0]

    # 清理文件名中的非法字符
    cleaned_filename = re.sub(r'[\\/*?:"<>|]', '', decoded_filename)

    # 获取文件扩展名
    file_ext = get_file_extension(cleaned_filename)

    # 生成新的文件名
    new_filename = f"file{index}{file_ext}"

    filepath = os.path.join(folder_path, new_filename)
    with open(filepath, 'wb') as f:
        f.write(payload)
    print(f"保存附件: {decoded_filename} -> {new_filename}")
    return new_filename

def read_id_file():
    """读取名为 id 的文件并返回其内容"""
    try:
        with open('id', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("id 文件未找到")
        return None
    except Exception as e:
        print(f"读取 id 文件时发生错误: {e}")
        return None

def read_eml():
    id_content = read_id_file()
    if id_content is None:
        print("无法读取 id 文件，退出程序")
        return "", 0

    auth_info = load_auth_info()

    # QQ邮箱的IMAP服务器地址
    imap_server = 'imap.qq.com'

    # 邮箱用户名和密码
    username = auth_info['imap']['username']
    password = auth_info['imap']['password']

    attachment_folder_send = 'attachments_send'
    attachment_folder_recv = 'wxauto文件'
    
    # 创建或清空附件文件夹
    if os.path.exists(attachment_folder_send):
        for file in os.listdir(attachment_folder_send):
            file_path = os.path.join(attachment_folder_send, file)
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(attachment_folder_send)

    if not os.path.exists(attachment_folder_recv):
        os.makedirs(attachment_folder_recv)

    mail_content = ""
    attachment_count = 0

    try:
        # 连接到IMAP服务器
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        mail.select('INBOX')

        # 搜索未读邮件
        search_criteria = f'(UNSEEN SUBJECT "发送微信id{id_content}")'
        status, messages = mail.search(None, search_criteria.encode('utf-8'))
        if status != 'OK':
            print('未找到邮件')
            return mail_content, attachment_count

        messages = messages[0].split()

        if not messages:
            print('没有未读邮件')
            return mail_content, attachment_count

        found_email = False
        for emailid in messages:
            # 获取邮件信息
            status, email_data = mail.fetch(emailid, '(RFC822)')
            if status != 'OK':
                print(f'未能获取ID为{emailid}的邮件')
                continue
            
            # 解析邮件信息
            raw_email = email_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # 解码邮件主题
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                try:
                    subject = subject.decode(encoding or "utf-8")
                except UnicodeDecodeError:
                    subject = subject.decode("latin-1")

            # 清理邮件主题
            cleaned_subject = clean(subject)

            # 解析发件人地址
            from_ = parseaddr(msg.get('From'))[1]

            # 检查发件人和主题是否匹配
            if from_ == username and cleaned_subject.startswith(f'发送微信id{id_content}'):
                # 标记邮件为已读
                mail.store(emailid, '+FLAGS', '\\Seen')

                # 提取邮件内容
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            payload = part.get_payload(decode=True)
                            charset = part.get_content_charset() or 'utf-8'
                            mail_content += payload.decode(charset)

                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                payload = part.get_payload(decode=True)
                                attachment_count += 1
                                save_attachment(payload, filename, attachment_folder_send, attachment_count)

                else:
                    payload = msg.get_payload(decode=True)
                    charset = msg.get_content_charset() or 'utf-8'
                    mail_content += payload.decode(charset)

                found_email = True
                break

        if not found_email:
            print("没有找到符合条件的邮件")

    except Exception as e:
        print(f"发生错误: {e}")

    finally:
        try:
            # 关闭连接
            mail.close()
            mail.logout()
        except:
            pass

    return mail_content, attachment_count

def send_eml(content, attachment_names=None):
    id_content = read_id_file()
    if id_content is None:
        print("无法读取 id 文件，退出程序")
        return

    auth_info = load_auth_info()

    # SMTP服务器地址
    smtp_server = 'smtp.qq.com'
    port = 587

    # 发件人和收件人
    sender_email = auth_info['smtp']['username']
    receiver_email = auth_info['imap']['username']  # 假设接收邮件的邮箱也是发送邮件的邮箱
    password = auth_info['smtp']['password']

    # 创建MIME多部分消息
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = f'微信通知id{id_content}'

    # 添加邮件正文
    message.attach(MIMEText(content, 'plain'))

    # 添加附件（如果有的话）
    if attachment_names:
        for attachment_name in attachment_names:
            attachment_path = os.path.join('wxauto文件', attachment_name)
            
            # 调试信息：打印附件路径
            print(f"附件路径: {attachment_path}")
            
            if os.path.isfile(attachment_path):
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    
                    # 使用正确的文件名编码方式
                    filename = os.path.basename(attachment_name)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )
                    message.attach(part)
                    print(f"成功附加附件: {attachment_name}")
            else:
                print(f"附件 {attachment_name} 不存在")

    # 连接到SMTP服务器并发送邮件
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print("邮件发送成功")
    except Exception as e:
        print(f"发送邮件时出错: {e}")
    finally:
        server.quit()


