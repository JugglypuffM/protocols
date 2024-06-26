import base64
import json
import mimetypes
import os
from client import base64string

mimetypes.init()


class Attachment:
    def __init__(self, filename):
        file_extension = os.path.splitext(filename)[1]
        content_type = mimetypes.types_map[file_extension]
        name = filename.split('/')[-1]
        base64_filename = f"=?UTF-8?B?{base64string(name)}?="
        base64_attachment = self.get_file_content(filename)
        self.content = f'Content-Type: {content_type}; name="{base64_filename}"\n' \
                       f'Content-Disposition: attachment; filename="{base64_filename}"\n' \
                       f'Content-Transfer-Encoding: base64\n' \
                       f'\n' \
                       f'{base64_attachment}'

    @staticmethod
    def get_file_content(filename):
        with open(filename, "rb") as f:
            return base64.b64encode(f.read()).decode()


class ConfigData:
    def __init__(self, path: str):
        self.port = 465
        with open(path, encoding="utf8") as file:
            config = json.load(file)
            self.host_address = config["host_address"]
            self.user_address = config["user_address"]
            self.user_name = self.user_address.split('@')[0]
            self.password = config["password"]
            self.recipients = config["recipients"]
            self.message_file = config["message_file"]
            self.subject = config["subject"]
            self.attachments = config["attachments"]


class Message:
    def __init__(self, config):
        targets_address = ','.join(f'"{x}" <{x}>' for x in config.recipients)
        self.boundary = f'BoUnD1234567890987654321BoUnD'
        self.header = f'From:{config.user_address}\n' \
                      f'To:{targets_address}\n' \
                      f'Subject: =?UTF-8?B?{base64string(config.subject or "No subject")}?=\n' \
                      f'Content-type: multipart/mixed; boundary={self.boundary}\n' \
                      f'\n'
        self.text = self.get_text(config.message_file).replace('\n.', '\n..')

    def append(self, message):
        self.text += f'{self.get_start_boundary()}\n{message}'

    def end(self):
        self.text += f'\n{self.get_end_boundary()}\n.\n'

    def get_start_boundary(self):
        return f'--{self.boundary}'

    def get_end_boundary(self):
        return f'--{self.boundary}--'

    def get_content(self):
        return f'{self.header}\n{self.text}'

    @staticmethod
    def get_text(filename):
        with open(filename, "r", encoding="utf8") as f:
            message = "".join(f.readlines())
        content = f'Content-Transfer-Encoding: 8bit\n' \
                  f"Content-Type: text/plain; charset=utf-8\n\n" \
                  f"{message}"
        return content