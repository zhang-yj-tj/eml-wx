import os
import json
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets
import string

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

def encrypt_message(key, plaintext):
    """使用AES加密消息"""
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
    return base64.urlsafe_b64encode(iv + ciphertext).decode('utf-8')

def write_config(config_path, config_data):
    """写入配置文件"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

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

def generate_strong_password(length=32):
    """生成一个强密码"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def main():
    config_path = 'config.json'
    
    # 生成强密码
    master_password = generate_strong_password().encode('utf-8')
    
    # 将主密码存储在配置文件中
    config = {'master_password': base64.urlsafe_b64encode(master_password).decode('utf-8')}
    write_config(config_path, config)
    print("生成的主密码已存储在配置文件中")

    # 询问用户输入IMAP和SMTP地址及密码
    imap_username = input("请输入IMAP用户名 (明文): ")
    imap_password = input("请输入IMAP密码 (明文): ")
    smtp_username = input("请输入SMTP用户名 (明文): ")
    smtp_password = input("请输入SMTP密码 (明文): ")

    # 生成盐值
    master_salt = generate_salt()
    imap_salt = generate_salt()
    smtp_salt = generate_salt()

    # 派生密钥
    master_key = derive_key(master_password, master_salt)
    imap_key = derive_key(master_password, imap_salt)
    smtp_key = derive_key(master_password, smtp_salt)

    # 加密密码
    encrypted_imap_password = encrypt_message(imap_key, imap_password)
    encrypted_smtp_password = encrypt_message(smtp_key, smtp_password)

    # 创建 auth.json 数据
    auth_info = {
        "master": {
            "password": base64.urlsafe_b64encode(master_password).decode('utf-8'),
            "salt": base64.urlsafe_b64encode(master_salt).decode('utf-8')
        },
        "imap": {
            "username": base64.urlsafe_b64encode(imap_username.encode('utf-8')).decode('utf-8'),
            "password": encrypted_imap_password,
            "salt": base64.urlsafe_b64encode(imap_salt).decode('utf-8')
        },
        "smtp": {
            "username": base64.urlsafe_b64encode(smtp_username.encode('utf-8')).decode('utf-8'),
            "password": encrypted_smtp_password,
            "salt": base64.urlsafe_b64encode(smtp_salt).decode('utf-8')
        }
    }

    # 写入 auth.json 文件
    with open('auth.json', 'w', encoding='utf-8') as f:
        json.dump(auth_info, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
