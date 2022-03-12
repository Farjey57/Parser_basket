#import requests

#res = requests.get('https://stepic.org/favicon.ico').headers
#print(res)

import socket
import os
import sys

#создаем сокет TCP/IP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('0.0.0.0', 2222) # ip и порт сервера
print('Старт сервера на {} порт {}'.format(*server_address))
s.bind(server_address)
s.listen(10)

while True:
    conn, adr = s.accept()
    child_pid = os.fork()
    if child_pid == 0:
        while True:
            data = conn.recv(1024)
            if not data or data == b'close':
                break
            conn.send(data)
        conn.close()
        sys.exit()
    else:
        conn.close()