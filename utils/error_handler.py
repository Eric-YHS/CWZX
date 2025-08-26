#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一错误处理模块
提供统一的异常处理和错误响应
"""

import traceback
import json
from typing import Dict, Any, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ErrorCode:
    """错误代码定义"""
    # 通用错误
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    INVALID_PARAMETER = 1001
    MISSING_PARAMETER = 1002
    
    # API相关错误
    API_ERROR = 2000
    API_TIMEOUT = 2001
    API_RATE_LIMIT = 2002
    API_NOT_AVAILABLE = 2003
    
    # 数据相关错误
    DATA_NOT_FOUND = 3000
    DATA_INVALID = 3001
    DATA_PARSE_ERROR = 3002
    
    # 服务相关错误
    SERVICE_UNAVAILABLE = 4000
    SERVICE_TIMEOUT = 4001
    SERVICE_INTERNAL_ERROR = 4002
    
    # 认证相关错误
    AUTH_REQUIRED = 5000
    AUTH_FAILED = 5001
    AUTH_EXPIRED = 5002
    
    # 权限相关错误
    PERMISSION_DENIED = 6000
    
    # 资源相关错误
    RESOURCE_NOT_FOUND = 7000
    RESOURCE_CONFLICT = 7001


class ErrorMessages:
    """错误消息定义"""
    MESSAGES = {
        ErrorCode.SUCCESS: "成功",
        ErrorCode.UNKNOWN_ERROR: "未知错误",
        ErrorCode.INVALID_PARAMETER: "无效参数",
        ErrorCode.MISSING_PARAMETER: "缺少必要参数",
        ErrorCode.API_ERROR: "API调用错误",
        ErrorCode.API_TIMEOUT: "API调用超时",
        ErrorCode.API_RATE_LIMIT: "API调用频率限制",
        ErrorCode.API_NOT_AVAILABLE: "API服务不可用",
        ErrorCode.DATA_NOT_FOUND: "数据未找到",
        ErrorCode.DATA_INVALID: "数据无效",
        ErrorCode.DATA_PARSE_ERROR: "数据解析错误",
        ErrorCode.SERVICE_UNAVAILABLE: "服务不可用",
        ErrorCode.SERVICE_TIMEOUT: "服务超时",
        ErrorCode.SERVICE_INTERNAL_ERROR: "服务内部错误",
        ErrorCode.AUTH_REQUIRED: "需要认证",
        ErrorCode.AUTH_FAILED: "认证失败",
        ErrorCode.AUTH_EXPIRED: "认证已过期",
        ErrorCode.PERMISSION_DENIED: "权限不足",
        ErrorCode.RESOURCE_NOT_FOUND: "资源未找到",
        ErrorCode.RESOURCE_CONFLICT: "资源冲突"
    }


class CWZXException(Exception):
    """自定义异常基类"""
    
    def __init__(
        self,
        code: int = ErrorCode.UNKNOWN_ERROR,
        message: str = None,
        details: Dict[str, Any] = None,
        original_error: Exception = None
    ):
        self.code = code
        self.message = message or ErrorMessages.MESSAGES.get(code, "未知错误")
        self.details = details or {}
        self.original_error = original_error
        self.timestamp = datetime.now()
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "code": self.code,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }
        
        if self.details:
            result["details"] = self.details
        
        if self.original_error:
            result["original_error"] = str(self.original_error)
        
        return result


class APIError(CWZXException):
    """API相关错误"""
    pass


class DataError(CWZXException):
    """数据相关错误"""
    pass


class ServiceError(CWZXException):
    """服务相关错误"""
    pass


class AuthError(CWZXException):
    """认证相关错误"""
    pass


def handle_api_error(func):
    """
    API错误处理装饰器
    
    Usage:
        @handle_api_error
        def api_function():
            # API调用代码
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CWZXException as e:
            logger.error(f"API error in {func.__name__}: {e.message}", exc_info=True)
            return error_response(e.code, e.message, e.details)
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            return error_response(ErrorCode.UNKNOWN_ERROR, "服务器内部错误")
    
    return wrapper


def error_response(
    code: int,
    message: str = None,
    details: Dict[str, Any] = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """
    生成错误响应
    
    Args:
        code: 错误代码
        message: 错误消息
        details: 详细信息
        status_code: HTTP状态码
        
    Returns:
        Dict: 错误响应字典
    """
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message or ErrorMessages.MESSAGES.get(code, "未知错误"),
            "timestamp": datetime.now().isoformat()
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def success_response(
    data: Any = None,
    message: str = "成功",
    meta: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    生成成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        meta: 元数据
        
    Returns:
        Dict: 成功响应字典
    """
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if meta:
        response["meta"] = meta
    
    return response


def log_and_raise(
    error_class: type[CWZXException],
    code: int,
    message: str = None,
    details: Dict[str, Any] = None,
    original_error: Exception = None,
    logger_instance: logging.Logger = None
):
    """
    记录日志并抛出异常
    
    Args:
        error_class: 异常类
        code: 错误代码
        message: 错误消息
        details: 详细信息
        original_error: 原始异常
        logger_instance: 日志器实例
    """
    log_instance = logger_instance or logger
    
    # 记录错误日志
    log_message = message or ErrorMessages.MESSAGES.get(code, "未知错误")
    log_instance.error(
        f"{error_class.__name__}: {log_message}",
        extra={"code": code, "details": details},
        exc_info=original_error is not None
    )
    
    # 抛出异常
    raise error_class(code, message, details, original_error)


def safe_execute(
    func,
    default_value=None,
    error_class=ServiceError,
    code=ErrorCode.SERVICE_INTERNAL_ERROR,
    logger_instance: logging.Logger = None
):
    """
    安全执行函数，捕获所有异常
    
    Args:
        func: 要执行的函数
        default_value: 出错时的默认返回值
        error_class: 错误类
        code: 错误代码
        logger_instance: 日志器实例
        
    Returns:
        函数执行结果或默认值
    """
    log_instance = logger_instance or logger
    
    try:
        return func()
    except CWZXException:
        # 已经是自定义异常，直接抛出
        raise
    except Exception as e:
        log_instance.error(f"Error executing {func.__name__}: {str(e)}", exc_info=True)
        if default_value is not None:
            return default_value
        raise error_class(code, f"执行失败: {str(e)}", original_error=e)


def retry_on_error(
    max_retries=3,
    delay=1,
    backoff=2,
    exceptions=(Exception,)
):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 延迟倍数
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after {wait_time}s: {str(e)}"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"Failed after {max_retries} retries for {func.__name__}: {str(e)}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator