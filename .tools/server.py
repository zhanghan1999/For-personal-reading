# -*- coding: utf-8 -*-
"""server.py — 导师文集本地服务器。
- 静态托管整个站点（http://127.0.0.1:8790/）
- POST /anno 把批注内容写入 批注/annotations.js（网页自动保存批注用）
- 启动成功后自动打开首页
用法：双击「启动导师文集.bat」或运行 python server.py
"""
import os, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # C:\导师文集
PORT = 8790
ANNO_FILE = os.path.join(ROOT, '批注', 'annotations.js')


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_POST(self):
        if self.path.rstrip('/') == '/anno':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = self.rfile.read(length).decode('utf-8')
                os.makedirs(os.path.dirname(ANNO_FILE), exist_ok=True)
                with open(ANNO_FILE, 'w', encoding='utf-8') as f:
                    f.write(data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
                print('批注已自动保存 -> %s' % ANNO_FILE)
                sys.stdout.flush()
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        sys.stdout.write('[%s] %s\n' % (self.log_date_time_string(), fmt % args))
        sys.stdout.flush()


def main():
    os.makedirs(os.path.dirname(ANNO_FILE), exist_ok=True)
    try:
        server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    except OSError as e:
        print('端口 %d 被占用：%s' % (PORT, e))
        input('按回车键退出…')
        return
    url = 'http://127.0.0.1:%d/' % PORT
    print('=' * 52)
    print('  导师文集 · 本地服务器已启动')
    print('  首页地址：%s' % url)
    print('  批注自动保存：%s' % ANNO_FILE)
    print('  关闭本窗口即停止服务')
    print('=' * 52)
    # 启动成功后自动打开首页
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止。')
        sys.exit(0)


if __name__ == '__main__':
    main()
