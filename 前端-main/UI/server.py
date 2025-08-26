
import os
import sys
import http.server
import socketserver
from pathlib import Path

# 设置工作目录
os.chdir(Path(__file__).parent)

print(f"前端服务目录: {os.getcwd()}")

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默日志
    
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

# 启动服务器
print("前端服务器启动在端口 8081")
with socketserver.TCPServer(("", 8081), MyHTTPRequestHandler) as httpd:
    httpd.serve_forever()
