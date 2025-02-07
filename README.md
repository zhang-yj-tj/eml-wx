# 微信邮件通知互传转发器 / WeChatMailBridge
基于wxauto的邮箱连通多微信通知系统 / Mail Connected Multi-WeChat Notification System Based on WXAuto
## 项目概述 / Project Overview
本项目用于微信消息的邮件聚合通知。 / This project is used for aggregating WeChat messages via email notifications.

### 基于开源项目 / Based on Open-Source Project
本项目基于开源项目wxauto：[GitHub - cluic/wxauto](https://github.com/cluic/wxauto)。 / This project is based on the open-source project wxauto: [GitHub - cluic/wxauto](https://github.com/cluic/wxauto).

### 运行环境 / Operating Environment
运行环境需要Windows 10+系统，安装Python 3.9及以上版本和微信3.9.x.x版本。 / The operating environment requires Windows 10+ system with Python 3.9 or above and WeChat version 3.9.x.x installed.

---

## 原理与优势 / Principles and Advantages
### 原理 / Principle
安全地获取微信消息并转发到邮箱，同时可以从邮箱读取消息并转发到微信。 / Safely retrieve WeChat messages and forward them to email, and also read messages from email and forward them to WeChat.

### 优势 / Advantages
- 采用延迟模拟输入，不易封号。 / Uses delayed simulated input, reducing the risk of account blocking.
- 采用ID区分，一个邮箱可控制多个微信。 / Uses ID differentiation, allowing one email to control multiple WeChat accounts.

---

## 使用方法 / Usage
### 首次使用 / First-Time Use
1. 配置此微信的自定义名称：ID文件。 / Configure a custom name for this WeChat account: ID file.
2. 运行debug文件，填写邮箱地址，同步联系人列表。 / Run the debug file, enter the email address, and synchronize the contact list.
3. 运行main文件。 / Run the main file.

### 常规使用 / Regular Use
- 运行main文件。 / Run the main file.

### 注意事项 / Notes
- 更改微信名或添加联系人后，均需要运行debug文件更新联系人列表。 / After changing WeChat names or adding contacts, you need to run the debug file to update the contact list.

---

## 邮件格式 / Email Format

### 发送微信邮件格式 / Sending WeChat Email Format
- **主题**：发送微信id{你填写的自定义id} / **Subject**: Send WeChat ID{Your custom ID}
- **正文**：要发送的微信对象名（同步联系人列表后可以不填写全名，但不可以有错误拼写），要发送的内容，若出现连续三个换行，则后文抛弃。 / **Body**: The name of the WeChat contact to send to (after synchronizing the contact list, you can omit the full name but must not have any spelling errors), the content to send. If three consecutive line breaks appear, the subsequent content will be discarded.
- **附件**：要发送的文件（所有文件发送时会被重命名！）。 / **Attachment**: Files to send (all files will be renamed upon sending!).

### 接受微信邮件格式 / Receiving WeChat Email Format
- **主题**：微信通知id{你填写的自定义id} / **Subject**: WeChat Notification ID{Your custom ID}
- **正文**：支持多条消息合并接受，具体格式自行测试。 / **Body**: Supports merging multiple messages, the specific format needs to be tested.
- **附件**：微信接收到的文件（保留原名称）。 / **Attachment**: Files received by WeChat (original names are retained).

---

## 联系作者 / Contact the Author
- **邮箱** / **Email**: zhang.ershi@qq.com
- **微信号** / **WeChat ID**: zhang_tjnk

---

## 免责声明 / Disclaimer
- 代码仅用于学习使用，禁止用于实际生产项目，请勿用于非法用途和商业用途！如因此产生任何法律纠纷，均与作者无关！
- The code is for learning purposes only and should not be used in production projects. It must not be used for illegal or commercial purposes! The author shall not be liable for any legal disputes arising from its use!
