#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财闻智析 - 启动器程序
自动启动完整服务
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """检查并安装依赖"""
    print("检查依赖...")
    try:
        import flask
        import flask_cors
        print("✓ Flask已安装")
    except ImportError:
        print("正在安装Flask...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"], check=True)
        print("✓ Flask安装完成")

def start_server():
    """启动服务器"""
    # 获取项目目录
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("\n财闻智析 - 智能金融决策平台")
    print("=" * 50)
    print(f"项目目录: {project_dir}")
    
    # 检查依赖
    check_dependencies()
    
    # 添加backend目录到路径
    sys.path.insert(0, str(project_dir / "backend"))
    
    # 导入并启动完整服务
    try:
        import complete_start
        print("\n服务启动完成！")
        print("访问地址: http://localhost:8000")
        print("=" * 50)
    except ImportError as e:
        print(f"错误: 无法导入complete_start模块: {e}")
        return
    
    # 保持程序运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")

if __name__ == "__main__":
    start_server()