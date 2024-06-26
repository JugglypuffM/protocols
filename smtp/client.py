import time
import socket
import ssl
from base64 import b64encode
from domain import *


def base64string(msg):
    return b64encode(msg.encode()).decode()


def request(socket, request):
    socket.send((request + '\n').encode())
    recv_data = socket.recv(65535).decode()
    return recv_data


def create_send_message(config):
    subject = config.subject
    message = Message(config)
    if not config.attachments:
        return f'Subject: =?UTF-8?B?{base64string(subject)}?=\n{message.text}\n.\n'
    message.append(message.text)
    attachments = [Attachment(filename).content for filename in config.attachments]
    [message.append(a) for a in attachments]
    message.end()
    return message.get_content()


def main():
    config = ConfigData("./contents/config.json")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((config.host_address, config.port))
        client = ssl.wrap_socket(client)
        client.recv(1024)
        request(client, f'EHLO {config.user_name}')
        print(f'USERNAME: {config.user_name}\nPASSWORD: {config.password}\n')
        base64login = base64string(config.user_address)
        base64password = base64string(config.password)
        request(client, 'AUTH LOGIN')
        request(client, base64login)
        print('Authentication successful\n' if '2.7.0' in request(client, base64password)
              else 'Wrong login or password\n')
        print('FROM:', request(client, f'MAIL FROM:{config.user_address}')[10::])
        for recipients in config.recipients:
            time.sleep(1)
            print('TO:', request(client, f'RCPT TO:{recipients}')[10::])
        request(client, 'DATA')
        print(request(client, create_send_message(config))[10::])


if __name__ == "__main__":
    main()