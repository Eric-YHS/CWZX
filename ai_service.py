#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI聊天服务
支持多种AI服务的接入
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# 尝试导入智谱AI SDK
try:
    from zai import ZhipuAiClient
    ZHIPUAI_AVAILABLE = True
except ImportError:
    ZHIPUAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIService:
    """AI聊天服务类"""
    
    def __init__(self):
        # 支持的AI服务配置
        self.services = {
            'zhipu': {
                'api_key': os.getenv('ZHIPUAI_API_KEY'),
                'model': 'glm-4.5',
                'enabled': ZHIPUAI_AVAILABLE
            },
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-3.5-turbo'
            },
            'azure': {
                'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
                'base_url': os.getenv('AZURE_OPENAI_ENDPOINT'),
                'model': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                'api_version': '2024-02-01'
            },
            'qwen': {
                'api_key': os.getenv('DASHSCOPE_API_KEY'),
                'base_url': 'https://dashscope.aliyuncs.com/api/v1',
                'model': 'qwen-turbo'
            },
            'wenxin': {
                'api_key': os.getenv('BAIDU_API_KEY'),
                'secret_key': os.getenv('BAIDU_SECRET_KEY'),
                'base_url': 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat',
                'model': 'ernie-turbo-8k'
            },
            'xunfei': {
                'app_id': os.getenv('XUNFEI_APP_ID'),
                'api_key': os.getenv('XUNFEI_API_KEY'),
                'api_secret': os.getenv('XUNFEI_API_SECRET'),
                'base_url': 'wss://spark-api.xf-yun.com/v3.1/chat',
                'model': 'spark-lite'
            }
        }
        
        # 默认服务优先级
        self.service_priority = ['zhipu', 'openai', 'qwen', 'wenxin', 'azure', 'xunfei']
        
        # 会话历史记录
        self.sessions = {}
        
    def _get_available_service(self) -> Optional[str]:
        """获取可用的AI服务"""
        for service_name in self.service_priority:
            service = self.services[service_name]
            if service_name == 'zhipu' and service.get('api_key') and service.get('enabled'):
                return service_name
            elif service_name == 'openai' and service.get('api_key'):
                return service_name
            elif service_name == 'azure' and all([service.get('api_key'), service.get('base_url'), service.get('model')]):
                return service_name
            elif service_name == 'qwen' and service.get('api_key'):
                return service_name
            elif service_name == 'wenxin' and all([service.get('api_key'), service.get('secret_key')]):
                return service_name
            elif service_name == 'xunfei' and all([service.get('app_id'), service.get('api_key'), service.get('api_secret')]):
                return service_name
        return None
    
    def _get_session_history(self, session_id: str, max_length: int = 10) -> List[Dict]:
        """获取会话历史"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        history = self.sessions[session_id]
        # 只保留最近的max_length条对话
        if len(history) > max_length * 2:  # 乘以2因为每轮对话包含用户和AI的消息
            history = history[-max_length * 2:]
            self.sessions[session_id] = history
        
        return history
    
    def _add_to_history(self, session_id: str, role: str, content: str):
        """添加消息到历史记录"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def _call_openai(self, messages: List[Dict], service_config: Dict) -> Optional[str]:
        """调用OpenAI服务"""
        try:
            headers = {
                'Authorization': f"Bearer {service_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': service_config['model'],
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 2000
            }
            
            response = requests.post(
                f"{service_config['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"OpenAI API调用失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"调用OpenAI服务失败: {e}")
            return None
    
    def _call_qwen(self, messages: List[Dict], service_config: Dict) -> Optional[str]:
        """调用通义千问服务"""
        try:
            headers = {
                'Authorization': f"Bearer {service_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            # 转换消息格式
            input_messages = []
            for msg in messages:
                input_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            
            data = {
                'model': service_config['model'],
                'input': {
                    'messages': input_messages
                },
                'parameters': {
                    'temperature': 0.7,
                    'max_tokens': 2000
                }
            }
            
            response = requests.post(
                f"{service_config['base_url']}/services/aigc/text-generation/generation",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'output' in result and 'text' in result['output']:
                    return result['output']['text']
                elif 'output' in result and 'choices' in result['output']:
                    return result['output']['choices'][0]['message']['content']
            else:
                logger.error(f"通义千问API调用失败: {response.status_code} - {response.text}")
            
            return None
                
        except Exception as e:
            logger.error(f"调用通义千问服务失败: {e}")
            return None
    
    def _call_zhipu(self, messages: List[Dict], service_config: Dict) -> Optional[str]:
        """调用智谱AI服务"""
        try:
            if not ZHIPUAI_AVAILABLE:
                logger.error("智谱AI SDK未安装")
                return None
            
            # 创建客户端
            client = ZhipuAiClient(api_key=service_config['api_key'])
            
            # 转换消息格式，排除system消息（因为glm-4.5可能不支持）
            chat_messages = []
            for msg in messages:
                if msg['role'] != 'system':  # 跳过system消息
                    chat_messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            # 调用API
            response = client.chat.completions.create(
                model=service_config['model'],
                messages=chat_messages,
                thinking={
                    "type": "enabled",    # 启用深度思考模式
                },
                max_tokens=4096,
                temperature=0.6
            )
            
            # 获取回复
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            
            return None
            
        except Exception as e:
            logger.error(f"调用智谱AI服务失败: {e}")
            return None
    
    def _call_wenxin(self, messages: List[Dict], service_config: Dict) -> Optional[str]:
        """调用文心一言服务"""
        try:
            # 获取access token
            token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={service_config['api_key']}&client_secret={service_config['secret_key']}"
            token_response = requests.get(token_url, timeout=10)
            if token_response.status_code != 200:
                logger.error("获取文心一言access token失败")
                return None
            
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            
            # 构建请求
            headers = {
                'Content-Type': 'application/json'
            }
            
            # 转换消息格式
            if len(messages) > 0:
                # 文心一言只支持单轮对话或简单的上下文
                last_user_msg = messages[-1] if messages[-1]['role'] == 'user' else messages[-2] if len(messages) >= 2 else messages[0]
                content = last_user_msg['content']
            else:
                content = ""
            
            data = {
                'messages': [
                    {
                        'role': 'user',
                        'content': content
                    }
                ]
            }
            
            response = requests.post(
                f"{service_config['base_url']}/completions?access_token={access_token}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    return result['result']
            else:
                logger.error(f"文心一言API调用失败: {response.status_code} - {response.text}")
            
            return None
                
        except Exception as e:
            logger.error(f"调用文心一言服务失败: {e}")
            return None
    
    def chat(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """AI聊天接口"""
        if not message.strip():
            return {
                'success': False,
                'response': '消息不能为空',
                'session_id': session_id
            }
        
        # 获取可用的AI服务
        service_name = self._get_available_service()
        
        if not service_name:
            return {
                'success': False,
                'response': '抱歉，目前没有可用的AI服务。请配置AI服务的API密钥。',
                'session_id': session_id,
                'error': 'no_available_service'
            }
        
        # 获取历史对话
        history = self._get_session_history(session_id or 'default')
        
        # 构建消息列表
        messages = []
        
        # 添加系统提示
        messages.append({
            'role': 'system',
            'content': '你是一个专业的金融投资顾问，擅长回答关于股票、基金、投资理财等方面的问题。请提供专业、准确、客观的建议。'
        })
        
        # 添加历史对话
        for msg in history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # 添加当前消息
        messages.append({
            'role': 'user',
            'content': message
        })
        
        # 调用AI服务
        response = None
        service_config = self.services[service_name]
        
        if service_name == 'zhipu':
            response = self._call_zhipu(messages, service_config)
        elif service_name == 'openai':
            response = self._call_openai(messages, service_config)
        elif service_name == 'qwen':
            response = self._call_qwen(messages, service_config)
        elif service_name == 'wenxin':
            response = self._call_wenxin(messages, service_config)
        # 可以继续添加其他服务的调用
        
        if response:
            # 添加到历史记录
            if session_id:
                self._add_to_history(session_id, 'user', message)
                self._add_to_history(session_id, 'assistant', response)
            
            return {
                'success': True,
                'response': response,
                'session_id': session_id,
                'service_used': service_name
            }
        else:
            return {
                'success': False,
                'response': f'抱歉，AI服务暂时无法响应。请稍后再试。',
                'session_id': session_id,
                'error': 'service_error'
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取各AI服务的状态"""
        status = {}
        for name, config in self.services.items():
            if name == 'zhipu':
                status[name] = {
                    'available': bool(config.get('api_key')) and config.get('enabled'),
                    'model': config.get('model'),
                    'sdk_available': ZHIPUAI_AVAILABLE
                }
            elif name == 'openai':
                status[name] = {
                    'available': bool(config.get('api_key')),
                    'model': config.get('model')
                }
            elif name == 'azure':
                status[name] = {
                    'available': all([config.get('api_key'), config.get('base_url'), config.get('model')]),
                    'model': config.get('model')
                }
            elif name == 'qwen':
                status[name] = {
                    'available': bool(config.get('api_key')),
                    'model': config.get('model')
                }
            elif name == 'wenxin':
                status[name] = {
                    'available': all([config.get('api_key'), config.get('secret_key')]),
                    'model': config.get('model')
                }
            elif name == 'xunfei':
                status[name] = {
                    'available': all([config.get('app_id'), config.get('api_key'), config.get('api_secret')]),
                    'model': config.get('model')
                }
        
        return status

# 创建全局实例
ai_service = AIService()

# 测试函数
def test_ai_service():
    """测试AI服务"""
    print("测试AI聊天服务...")
    
    # 测试聊天功能
    result = ai_service.chat("你好，请介绍一下你自己")
    print(f"AI回复: {result}")
    
    # 查看服务状态
    status = ai_service.get_service_status()
    print(f"AI服务状态: {status}")

if __name__ == "__main__":
    test_ai_service()