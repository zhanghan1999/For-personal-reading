# -*- coding: utf-8 -*-
"""server.py — 导师文集本地服务器。
- 静态托管整个站点（http://127.0.0.1:8790/）
- POST /anno 把批注内容写入 批注/annotations.js（网页自动保存批注用）
- POST /page-write 把某阅读页的 <main> 内容写回文章 HTML（补充注释公共入库用）
- 启动成功后自动打开首页
用法：双击「启动导师文集.bat」或运行 python server.py
"""
import os, sys, re, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # C:\导师文集
PORT = 8790
ANNO_FILE = os.path.join(ROOT, '批注', 'annotations.js')

MAIN_RE = re.compile(r'<main\b[^>]*>.*?</main>', re.S)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_POST(self):
        p = self.path.rstrip('/')
        if p == '/anno':
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
        elif p == '/page-write':
            self.handle_page_write()
        else:
            self.send_error(404)

    def handle_page_write(self):
        """把阅读页 <main> 内容写回文章 HTML（补充注释公共写入）。"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            rel = (data.get('path') or '').replace('\\', '/')
            main_html = data.get('mainHtml', '')
            # 路径校验：必须是站点内 .html 文件，禁止穿越
            if (not rel.endswith('.html') or rel.startswith('/')
                    or '..' in rel.split('/')):
                self.send_error(400, 'bad path')
                return
            fp = os.path.normpath(os.path.join(ROOT, rel))
            if not (fp.startswith(ROOT + os.sep) and os.path.isfile(fp)):
                self.send_error(403, 'forbidden')
                return
            html = open(fp, encoding='utf-8').read()
            new_html, n = MAIN_RE.subn(
                '<main id="main">' + main_html + '</main>', html, count=1)
            if n == 0:
                self.send_error(500, 'main not found')
                return
            tmp = fp + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(new_html)
            os.replace(tmp, fp)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            print('文章已写回 -> %s' % fp)
            sys.stdout.flush()
        except Exception as e:
            self.send_error(500, str(e))

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
