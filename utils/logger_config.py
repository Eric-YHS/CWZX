#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
为整个项目提供统一的日志配置
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(
    level=logging.INFO,
    log_dir=None,
    max_file_size=10*1024*1024,  # 10MB
    backup_count=5
):
    """
    设置日志配置
    
    Args:
        level: 日志级别
        log_dir: 日志文件目录
        max_file_size: 单个日志文件最大大小
        backup_count: 保留的日志文件数量
    """
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除已有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 如果指定了日志目录，添加文件处理器
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成日志文件名
        log_file = log_dir / f"cwzx_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name):
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        Logger: 日志器实例
    """
    return logging.getLogger(name)


# 默认日志配置
def setup_default_logging():
    """设置默认日志配置"""
    # 获取项目根目录
    project_dir = Path(__file__).parent
    log_dir = project_dir / "logs"
    
    return setup_logging(
        level=logging.INFO,
        log_dir=log_dir
    )


# 错误日志装饰器
def log_errors(logger=None):
    """
    错误日志装饰器
    
    Usage:
        @log_errors()
        def risky_function():
            # 可能出错的代码
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = logger or logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                func_logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


# 性能监控装饰器
def log_performance(logger=None, threshold=1.0):
    """
    性能监控装饰器
    
    Args:
        logger: 日志器
        threshold: 性能阈值（秒），超过此值会记录警告
        
    Usage:
        @log_performance(threshold=0.5)
        def slow_function():
            # 耗时的操作
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = logger or logging.getLogger(func.__module__)
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold:
                    func_logger.warning(
                        f"Performance: {func.__name__} took {execution_time:.2f}s "
                        f"(threshold: {threshold}s)"
                    )
                else:
                    func_logger.debug(
                        f"Performance: {func.__name__} took {execution_time:.2f}s"
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                func_logger.error(
                    f"Error in {func.__name__} after {execution_time:.2f}s: {str(e)}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


# 初始化默认日志
if __name__ != "__main__":
    setup_default_logging()