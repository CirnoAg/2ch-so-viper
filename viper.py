import socket

HOST = '2ch.so'
PORT = 80
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

request = "GET http://2ch.so/b/ HTTP/1.1\r\n"
headers = {
    'Host': '2ch.so',
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'utf-8',
    'Connection': 'close'
    }

request += '\r\n'.join(['%s:%s' % (k, v) for k, v in headers.items()]) + '\r\n\r\n'
print 'Request:'
print repr(request)

s.sendall(request)
data = s.recv(1024)

print 'Received:'
print repr(data)

s.close()