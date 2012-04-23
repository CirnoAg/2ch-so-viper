#!/usr/bin/python
import socket

HOST = '2ch.so'
PORT = 80
LINK = '/b/'

def get_request():
    request = "GET %s HTTP/1.0\r\n" % LINK
    headers = {
        'Host': HOST,
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'utf-8',
        'Accept-Language':	'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
        'Connection': 'close'
        }
    request += '\r\n'.join(['%s:%s' % (k, v) for k, v in headers.items()]) + '\r\n\r\n'
    
    return request
    
def read_data(s):
    data = b''
    while True:
        part = s.recv(1024)
        if not part:
            break
        data += part
        
    return data 
    
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    s.sendall(get_request())

    data = read_data(s)
    data = data[data.find(b'\r\n\r\n') + 4:]

    with open('index.html', 'wb') as f:
        f.write(data)

    s.close()

if __name__ == "__main__":
    main()