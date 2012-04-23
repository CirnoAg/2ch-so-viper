#!/usr/bin/python
import urllib, urllib2, cookielib, re, random, time, sys
from poster.encode import multipart_encode

class SosachThread:
    def __init__(self, html):
        self._posts = SosachThread.parse_posts(html)
        
    def get_random_post(self):
        if not self._posts:
            return ('', '')
        return random.choice(self._posts)
        
    def get_posts(self):
        return list(self._posts)
          
    @staticmethod
    def parse_posts(html):
        result = list()
        
        posts = re.findall(r'<table id="post_(.*?)" class="post"><tbody>(.*?)</tbody></table>', html)
        for post in posts:
            id, body = post
            result.append((id, SosachThread.parse_comment(body)))
        
        return result
        
    @staticmethod
    def parse_comment(body):
        search_res = re.search(r'<blockquote><p>(.*?)</p></blockquote>', body)
        if not search_res:
            return ''
        
        comment = search_res.group(1)
        
        comment = re.sub(
            r'<a onmouseover="showPostPreview\(event\)" onmouseout="delPostPreview\(event\)" href=".*?" onclick="highlight\(.*?\)">(.*?)</a>',
            r'\1',
            comment
            )
        comment = re.sub(r'<span class="unkfunc">(.*?)</span>', r'\1', comment)
        comment = re.sub(r'<span class="spoiler">(.*?)</span>', r'%%\1%%', comment)
        comment = re.sub(r'<em>(.*?)</em>', r'*\1*', comment)
        comment = re.sub(r'<strong>(.*?)</strong>', r'**\1**', comment)
        comment = re.sub(r'<a href=".*?" rel="nofollow">(.*?)</a>', r'\1', comment)
        
        comment = comment.replace('&gt;', '>')
        comment = comment.replace('&quot;', '"')
        comment = comment.replace('&#39;', "'")
        comment = comment.replace('&#44;', ',')
        comment = comment.replace('<br />', '\n')
        
        return comment

class SosachHttpClient:
    def __init__(self, proxy = None):      
        
        self.cookie_handler   = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.redirect_handler = urllib2.HTTPRedirectHandler()
        self.http_handler     = urllib2.HTTPHandler()
        self.https_handler    = urllib2.HTTPSHandler()
   
        self.opener = urllib2.build_opener(
            self.http_handler,
            self.https_handler,
            self.cookie_handler,
            self.redirect_handler
            )
        
        if proxy:
            self.proxy_handler = urllib2.ProxyHandler(proxy)
            self.opener.add_handler(self.proxy_handler)
        
        self.opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3')
            ]
   
    def request(self, url, params = {}, timeout = 10):
        """
        Sends http-request to server, and returns response. 
        If params is null, it uses GET method, else, uses POST.
        
        >>> print client.request(
            'https://auth.mail.ru/cgi-bin/auth',
            {'Domain': 'mail.ru', 'Login': 'login', 'Password': 'password'}
            )
        """
        
        if params:
            params = urllib.urlencode(params)
            html = self.opener.open(url, params, timeout)
        else:
            html = self.opener.open(url)
        
        return html.read()
        
    def post_request(self, url, data, headers = {}, timeout = 10):
        request = urllib2.Request(url, data, headers)
        return self.opener.open(request).read()
        
    def get_thread(self, board, id):
        html = self.request('http://2ch.so/%s/res/%s.html' % (board, str(id)))
        return SosachThread(html)
        
    def post_in_thread(
        self, 
        board,
        id,
        link = '',
        name = '',
        email = '',
        title = '',
        comment = '',
        file = '',
        makewatermark = '',
        video = '',
        recaptcha_response_field = ''
        ):
        
        datagen, headers = multipart_encode({
            'task':	                    '\xd1\x80\xd0\xbe\x73\x74',
            'parent':                   str(id),
            'link':                     link,
            'akane':                    name,
            'nabiki':                   email,
            'kasumi':                   title,
            'shampoo':                  comment + ' ' * random.randint(1, 100),
            'file':                     '',
            'makewatermark':            makewatermark,
            'video':                    video,
            'recaptcha_response_field':	recaptcha_response_field,
            })
            
        headers['User-agent'] = 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3'
        
        data = b''.join([x for x in datagen])
        
        response = self.post_request('http://2ch.so/%s/wakaba.pl' % board, data, headers)
        if not response or response.find('<font size="5">Ошибка:') != -1:
            return False
        return True
        
def autobump(board, thread, timeout = 15):
    client = SosachHttpClient()
    while True:
        res = client.post_in_thread(board, thread, comment = 'bump')
        if not res:
            print 'bump faild!' 
            continue
        print 'thread /%s/%s bumped' % (board, str(thread))
        time.sleep(timeout)
        
def get_thread(board, thread):
    client = SosachHttpClient()
    for post in client.get_thread(board, thread).get_posts():
        id, comment = post
        print 'ID: %s\n%s\n-----' % (id, comment.decode('utf-8'))
        
def main(args):
    if len(args) != 3:
        print '''Usage: viper.py <board> <thread> <task>\nAvalible tasks:\nbump\nget_thread'''
        exit()

    board = args[0]
    thread = args[1]
    task = args[2]
    
    if task == 'bump':
        autobump(board, thread)
    elif task == 'get_thread':
        get_thread(board, thread)
    else:
        print 'unknown task ' + task
        
if __name__ == "__main__":
    main(sys.argv[1:])