#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财闻智析 - 完整功能启动脚本
包含所有API和真实数据支持
"""

import os
import sys
import subprocess
import time
import requests
import json
import asyncio
from datetime import datetime
from pathlib import Path

# 加载环境变量
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"已加载环境变量配置")
except ImportError:
    print("警告: python-dotenv 未安装，请运行: pip install python-dotenv")

# 设置编码
if sys.platform == "win32":
    os.system("chcp 65001")

print("财闻智析 - 智能金融决策平台")
print("=" * 60)

# 获取项目根目录
project_dir = Path(__file__).parent
os.chdir(project_dir)

print(f"项目目录: {project_dir}")

# 添加backend目录到路径
sys.path.insert(0, str(project_dir / "backend"))

# 导入Flask
try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    print("✓ Flask已安装")
except ImportError:
    print("\n正在安装Flask...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"], check=True)
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    print("✓ Flask安装完成")

# 检查RAG服务
RAG_AVAILABLE = False
try:
    from services.rag_service import get_rag_service
    RAG_AVAILABLE = True
    print("✓ RAG服务已导入")
except ImportError as e:
    print(f"⚠ RAG服务导入失败: {e}")

# 检查真实股票服务
STOCK_SERVICE_AVAILABLE = False
try:
    from real_stock_service import real_stock_service
    STOCK_SERVICE_AVAILABLE = True
    print("✓ 真实股票服务已导入")
except ImportError as e:
    print(f"⚠ 真实股票服务导入失败: {e}")

# 检查AI服务
AI_SERVICE_AVAILABLE = False
try:
    from ai_service import ai_service
    AI_SERVICE_AVAILABLE = True
    print("✓ AI服务已导入")
except ImportError as e:
    print(f"⚠ AI服务导入失败: {e}")

# 检查新闻服务
NEWS_SERVICE_AVAILABLE = False
news_service = None
try:
    from services.news_service import NewsService
    news_service = NewsService()
    NEWS_SERVICE_AVAILABLE = True
    print("✓ 新闻服务已导入")
except ImportError as e:
    print(f"⚠ 新闻服务导入失败: {e}")

def get_stock_distribution():
    """获取A股涨跌分布数据 - 使用真实数据和智能估算"""
    # 获取当前时间，判断是否为交易时间
    current_time = datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    # 交易时间：9:30-11:30, 13:00-15:00
    is_trading_time = ((hour == 9 and minute >= 30) or (hour == 10 and minute < 60) or 
                      (hour == 11 and minute < 30) or 
                      (hour == 13 and minute >= 0) or (hour == 14 and minute < 60) or
                      (hour == 15 and minute == 0))
    
    # 如果是非交易时间，返回估算数据
    if not is_trading_time:
        print(f"当前为非交易时间({hour:02d}:{minute:02d})，使用估算数据")
        # 基于主要指数涨跌幅估算市场情绪
        try:
            # 获取上证指数数据
            sh_index_data = None
            if STOCK_SERVICE_AVAILABLE:
                sh_index_data = real_stock_service.get_stock_data("000001")
            
            if sh_index_data and sh_index_data.get("change_percent") is not None:
                sh_change = sh_index_data["change_percent"]
                # 根据指数涨跌幅估算市场涨跌分布
                if sh_change > 1.0:  # 大涨
                    up_ratio = 0.7
                    down_ratio = 0.1
                    flat_ratio = 0.2
                elif sh_change > 0.5:  # 小涨
                    up_ratio = 0.5
                    down_ratio = 0.2
                    flat_ratio = 0.3
                elif sh_change > -0.5:  # 震荡
                    up_ratio = 0.3
                    down_ratio = 0.3
                    flat_ratio = 0.4
                elif sh_change > -1.0:  # 小跌
                    up_ratio = 0.2
                    down_ratio = 0.5
                    flat_ratio = 0.3
                else:  # 大跌
                    up_ratio = 0.1
                    down_ratio = 0.7
                    flat_ratio = 0.2
                
                # 尝试获取真实的股票总数
                total_stocks = 5330  # 默认值
                try:
                    # 使用东方财富API获取真实总数
                    url = "http://push2.eastmoney.com/api/qt/clist/get"
                    params = {
                        'pn': '1', 
                        'pz': '1',  # 只需要获取总数
                        'po': '0', 
                        'np': '1',
                        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                        'fltt': '2', 
                        'invt': '2', 
                        'fid': 'f3',
                        'fs': 'm:0+t:6,m:0+t:80,m:0+t:81,m:1+t:2,m:1+t:23,m:0+t:7,m:1+t:3',  # 沪深A股+北交所
                        'fields': 'f3'
                    }
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('data'):
                            total_stocks = data['data'].get('total', 5330)
                            print(f"获取到真实股票总数: {total_stocks}只")
                except Exception as e:
                    print(f"获取股票总数失败，使用默认值: {e}")
                up_stocks = int(total_stocks * up_ratio)
                down_stocks = int(total_stocks * down_ratio)
                flat_stocks = total_stocks - up_stocks - down_stocks
                trading_stocks = int(total_stocks * 0.8)  # 假设80%的股票有交易
                
                return {
                    "up_stocks": up_stocks,
                    "down_stocks": down_stocks,
                    "flat_stocks": flat_stocks,
                    "trading_stocks": trading_stocks,
                    "total_stocks": total_stocks,
                    "is_trading_time": False,
                    "method": "index_estimation",
                    "message": f"基于上证指数({sh_change:+.2f}%)估算"
                }
            else:
                # 如果获取不到指数数据，使用中性分布
                # 尝试获取真实股票总数
                default_total = 5330
                try:
                    url = "http://push2.eastmoney.com/api/qt/clist/get"
                    params = {
                        'pn': '1', 'pz': '1', 'po': '0', 'np': '1',
                        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                        'fltt': '2', 'invt': '2', 'fid': 'f3',
                        'fs': 'm:0+t:6,m:0+t:80,m:0+t:81,m:1+t:2,m:1+t:23,m:0+t:7,m:1+t:3',
                        'fields': 'f3'
                    }
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('data'):
                            default_total = data['data'].get('total', 5330)
                except:
                    pass
                
                return {
                    "up_stocks": int(default_total * 0.3),
                    "down_stocks": int(default_total * 0.3),
                    "flat_stocks": default_total - int(default_total * 0.3) - int(default_total * 0.3),
                    "trading_stocks": int(default_total * 0.8),
                    "total_stocks": default_total,
                    "is_trading_time": False,
                    "method": "default_fallback",
                    "message": "使用默认分布估算"
                }
        except Exception as e:
            print(f"估算涨跌分布失败: {e}")
            # 返回默认分布，尝试获取真实总数
            default_total = 5330
            try:
                url = "http://push2.eastmoney.com/api/qt/clist/get"
                params = {
                    'pn': '1', 'pz': '1', 'po': '0', 'np': '1',
                    'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                    'fltt': '2', 'invt': '2', 'fid': 'f3',
                    'fs': 'm:0+t:6,m:0+t:80,m:0+t:81,m:1+t:2,m:1+t:23,m:0+t:7,m:1+t:3',
                    'fields': 'f3'
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data'):
                        default_total = data['data'].get('total', 5330)
            except:
                pass
            
            return {
                "up_stocks": int(default_total * 0.3),
                "down_stocks": int(default_total * 0.3),
                "flat_stocks": default_total - int(default_total * 0.3) - int(default_total * 0.3),
                "trading_stocks": int(default_total * 0.8),
                "total_stocks": default_total,
                "is_trading_time": False,
                "method": "default_fallback",
                "message": "使用默认分布估算"
            }
    
    try:
        # 使用东方财富API获取真实的涨跌分布
        # 扩展数据源以包含更多市场
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': '1', 
            'pz': '10000',  # 增加到10000条
            'po': '0', 
            'np': '1',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': '2', 
            'invt': '2', 
            'fid': 'f3',  # 按涨跌幅排序
            # 扩展市场范围：沪深A股 + 北交所
            'fs': 'm:0+t:6,m:0+t:80,m:0+t:81,m:1+t:2,m:1+t:23,m:0+t:7,m:1+t:3',  
            'fields': 'f3,f12,f14,f47,f62'  # f3=涨跌幅, f12=代码, f14=名称, f47=成交量, f62=最新价
        }
        
        print("正在获取真实涨跌分布数据...")
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and data['data'].get('diff'):
                stocks = data['data']['diff']
                total_stocks = data['data'].get('total', len(stocks))
                
                # 统计涨跌分布和交易状态
                up_count = 0
                down_count = 0
                flat_count = 0
                trading_count = 0
                valid_count = 0
                
                for stock in stocks:
                    try:
                        # f3是涨跌幅字段
                        change_percent = float(stock.get('f3', 0))
                        volume = int(stock.get('f47', 0))  # f47是成交量字段
                        
                        valid_count += 1
                        
                        # 统计涨跌
                        if change_percent > 0:
                            up_count += 1
                        elif change_percent < 0:
                            down_count += 1
                        else:
                            flat_count += 1
                        
                        # 统计有交易的股票（成交量大于0）
                        if volume > 0:
                            trading_count += 1
                    except (ValueError, TypeError):
                        flat_count += 1
                
                print(f"获取到真实涨跌数据: 总计{total_stocks}只, 上涨{up_count}只, 下跌{down_count}只, 平盘{flat_count}只, 有交易{trading_count}只")
                
                return {
                    "up_stocks": up_count,
                    "down_stocks": down_count,
                    "flat_stocks": flat_count,
                    "trading_stocks": trading_count,
                    "total_stocks": total_stocks,  # 使用API返回的真实总数
                    "is_trading_time": is_trading_time,
                    "method": "eastmoney_real_data_expanded"
                }
    except Exception as e:
        print(f"获取真实涨跌数据失败: {e}")
    
    # 如果获取失败，返回空数据，尝试获取真实总数
    default_total = 5330
    try:
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': '1', 'pz': '1', 'po': '0', 'np': '1',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': '2', 'invt': '2', 'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:0+t:81,m:1+t:2,m:1+t:23,m:0+t:7,m:1+t:3',
            'fields': 'f3'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                default_total = data['data'].get('total', 5330)
                print(f"获取到真实股票总数: {default_total}只")
    except Exception as e:
        print(f"获取股票总数失败: {e}")
    
    print("无法获取涨跌数据")
    return {
        "up_stocks": 0,
        "down_stocks": 0,
        "flat_stocks": 0,
        "trading_stocks": 0,
        "total_stocks": default_total,  # 使用真实总数
        "is_trading_time": False,
        "method": "data_unavailable"
    }

# 创建Flask应用
app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 获取前端目录
frontend_dir = project_dir / "前端-main" / "UI"
print(f"前端目录: {frontend_dir}")
print(f"前端目录存在: {frontend_dir.exists()}")

# API路由
@app.route('/api')
def api_info():
    return jsonify({"message": "财闻智析 API", "status": "running"})

@app.route('/api/v1/stocks/market/overview')
def get_market_overview():
    """获取市场概览"""
    try:
        # 获取真实指数数据
        indices = []
        if STOCK_SERVICE_AVAILABLE:
            market_indices = real_stock_service.get_market_indices()
            for code, data in market_indices.items():
                indices.append({
                    "code": code,
                    "name": data["name"],
                    "current_price": data["current_price"],
                    "change_percent": data["change_percent"]
                })
        
        # 如果真实服务不可用，使用模拟数据
        if not indices:
            indices = [
                {
                    "code": "000001",
                    "name": "上证指数",
                    "current_price": 3883.56,
                    "change_percent": 1.51
                },
                {
                    "code": "399001", 
                    "name": "深证成指",
                    "current_price": 12441.07,
                    "change_percent": 2.26
                },
                {
                    "code": "399006",
                    "name": "创业板指", 
                    "current_price": 2762.99,
                    "change_percent": 3.0
                },
                {
                    "code": "000300",
                    "name": "沪深300",
                    "current_price": 4469.22,
                    "change_percent": 2.08
                },
                {
                    "code": "000016",
                    "name": "上证50",
                    "current_price": 2989.85,
                    "change_percent": 2.09
                }
            ]
        
        distribution_data = get_stock_distribution()
        
        return jsonify({
            "major_indices": indices,
            "up_stocks": distribution_data.get("up_stocks", 0),
            "down_stocks": distribution_data.get("down_stocks", 0),
            "flat_stocks": distribution_data.get("flat_stocks", 0),
            "trading_stocks": distribution_data.get("trading_stocks", 0),
            "total_stocks": distribution_data.get("total_stocks", 5330),
            "is_trading_time": distribution_data.get("is_trading_time", False),
            "distribution_method": distribution_data.get("method", "unknown"),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        print(f"Error in market overview: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/stocks/sh-index')
def get_sh_index():
    """获取上证指数数据"""
    try:
        # 使用真实股票服务获取数据
        if STOCK_SERVICE_AVAILABLE:
            index_data = real_stock_service.get_stock_data("000001")
            if index_data:
                return jsonify({
                    "code": index_data.get("code"),
                    "name": index_data.get("name"),
                    "current_price": index_data.get("current_price"),
                    "change_percent": index_data.get("change_percent")
                })
        
        # 如果真实服务不可用，使用模拟数据
        return jsonify({
            "code": "000001",
            "name": "上证指数",
            "current_price": 3883.56,
            "change_percent": 1.51
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/stocks/sh-index/volume')
def get_sh_index_volume():
    """获取上证指数成交量"""
    try:
        # 使用腾讯API获取真实成交量数据
        import re
        url = "http://qt.gtimg.cn/q=sh000001"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.text
            pattern = r'v_sh000001=\"([^\"]+)\";'
            match = re.search(pattern, data)
            
            if match:
                values = match.group(1).split('~')
                if len(values) > 6 and values[6]:
                    volume = int(values[6]) / 10000  # 转换为万手
                    print(f"成功获取真实成交量: {volume}万手")
                    return jsonify({
                        "volume": round(volume, 2),
                        "source": "tencent_api"
                    })
        
        # 如果腾讯API失败，尝试东方财富API
        eastmoney_url = "http://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'secid': '1.000001',
            'fields': 'f47'  # f47是成交量字段
        }
        response = requests.get(eastmoney_url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and data['data'].get('f47'):
                volume = int(data['data']['f47']) / 10000  # 转换为万手
                return jsonify({
                    "volume": round(volume, 2),
                    "source": "eastmoney_api"
                })
        
        # 如果都失败，返回空
        return jsonify({"error": "无法获取成交量数据"}), 500
        
    except Exception as e:
        print(f"获取成交量失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/stocks/stats')
def get_stock_stats():
    """获取股票统计数据"""
    try:
        distribution_data = get_stock_distribution()
        trading_count = distribution_data.get("trading_stocks", 0)
        total_count = distribution_data.get("total_stocks", 5330)
        is_trading_time = distribution_data.get("is_trading_time", False)
        
        # 添加说明信息
        note = ""
        if not is_trading_time:
            note = "（非交易时间）"
        
        return jsonify({
            "trading_count": trading_count,
            "total_count": total_count,
            "is_trading_time": is_trading_time,
            "note": note,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/stocks/distribution')
def get_stock_distribution_api():
    distribution_data = get_stock_distribution()
    
    return jsonify({
        "up_stocks": distribution_data.get("up_stocks", 0),
        "down_stocks": distribution_data.get("down_stocks", 0),
        "flat_stocks": distribution_data.get("flat_stocks", 0),
        "total_stocks": distribution_data.get("total_stocks", 5330),
        "up_ratio": distribution_data.get("up_stocks", 0) / max(distribution_data.get("total_stocks", 1), 1) * 100,
        "down_ratio": distribution_data.get("down_stocks", 0) / max(distribution_data.get("total_stocks", 1), 1) * 100,
        "flat_ratio": distribution_data.get("flat_stocks", 0) / max(distribution_data.get("total_stocks", 1), 1) * 100,
        "method": distribution_data.get("method", "unknown"),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/v1/funds')
def get_funds():
    """获取基金列表 - 标准API"""
    # 模拟基金数据，确保change字段是字符串格式
    funds = [
        {"code": "000001", "name": "华夏成长混合", "type": "混合型", "nav": 2.456, "change": "+1.20%"},
        {"code": "000002", "name": "易方达蓝筹精选", "type": "股票型", "nav": 3.128, "change": "-0.50%"},
        {"code": "000003", "name": "南方稳健成长", "type": "混合型", "nav": 1.876, "change": "+0.80%"},
        {"code": "000004", "name": "嘉实沪深300", "type": "指数型", "nav": 4.321, "change": "+2.10%"},
        {"code": "000005", "name": "广发稳健增长", "type": "混合型", "nav": 1.654, "change": "+0.30%"}
    ]
    return jsonify(funds)

@app.route('/api/v1/stocks/search')
def search_stocks():
    """搜索股票"""
    try:
        keyword = request.args.get('keyword', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not keyword:
            return jsonify([])
        
        # 使用真实股票服务搜索
        if STOCK_SERVICE_AVAILABLE:
            results = real_stock_service.search_stocks(keyword, limit)
            
            # 为每个结果添加实时价格信息
            for result in results:
                stock_data = real_stock_service.get_stock_data(result['code'])
                if stock_data:
                    result.update(stock_data)
            
            return jsonify(results)
        else:
            # 模拟股票数据库
            stock_db = [
                {"code": "600519", "name": "贵州茅台", "market": "上海", "current_price": 1850.00, "change_percent": 2.5},
                {"code": "000001", "name": "平安银行", "market": "深圳", "current_price": 15.30, "change_percent": -1.2},
                {"code": "000858", "name": "五粮液", "market": "深圳", "current_price": 128.50, "change_percent": 1.8},
                {"code": "600036", "name": "招商银行", "market": "上海", "current_price": 35.60, "change_percent": 0.5},
                {"code": "600276", "name": "恒瑞医药", "market": "上海", "current_price": 45.20, "change_percent": -0.8},
                {"code": "300750", "name": "宁德时代", "market": "深圳", "current_price": 210.50, "change_percent": 3.2},
                {"code": "000895", "name": "双汇发展", "market": "深圳", "current_price": 25.60, "change_percent": 0.3},
                {"code": "601318", "name": "中国平安", "market": "上海", "current_price": 52.30, "change_percent": -1.5},
                {"code": "600887", "name": "伊利股份", "market": "上海", "current_price": 32.80, "change_percent": 0.8},
                {"code": "000002", "name": "万科A", "market": "深圳", "current_price": 18.90, "change_percent": -0.6}
            ]
            
            # 搜索匹配的股票
            results = []
            for stock in stock_db:
                if (keyword in stock['code'] or 
                    keyword in stock['name'] or 
                    keyword.lower() in stock['name'].lower()):
                    results.append(stock)
                    if len(results) >= limit:
                        break
            
            return jsonify(results)
        
    except Exception as e:
        print(f"搜索股票失败: {e}")
        return jsonify([])

@app.route('/api/v1/stocks/<stock_code>')
def get_stock_info(stock_code):
    """获取股票基本信息"""
    try:
        # 使用真实股票服务获取数据
        if STOCK_SERVICE_AVAILABLE:
            stock_data = real_stock_service.get_stock_data(stock_code)
            if stock_data:
                return jsonify(stock_data)
        
        # 如果真实服务不可用或获取失败，使用模拟数据
        mock_data = {
            "600519": {
                "code": "600519",
                "name": "贵州茅台",
                "current_price": 1850.00,
                "change_percent": 2.5,
                "market": "上海",
                "industry": "白酒"
            },
            "000001": {
                "code": "000001",
                "name": "平安银行",
                "current_price": 15.30,
                "change_percent": -1.2,
                "market": "深圳",
                "industry": "银行"
            }
        }
        
        if stock_code in mock_data:
            return jsonify(mock_data[stock_code])
        else:
            return jsonify({"error": "股票代码不存在"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/stocks/<stock_code>/quote')
def get_stock_quote(stock_code):
    """获取股票实时行情"""
    try:
        # 使用真实股票服务获取数据
        if STOCK_SERVICE_AVAILABLE:
            stock_data = real_stock_service.get_stock_data(stock_code)
            if stock_data:
                # 格式化返回数据
                quote_data = {
                    "code": stock_data.get("code"),
                    "name": stock_data.get("name"),
                    "current_price": stock_data.get("current_price"),
                    "change_percent": stock_data.get("change_percent"),
                    "open": stock_data.get("open"),
                    "high": stock_data.get("high"),
                    "low": stock_data.get("low"),
                    "volume": stock_data.get("volume")
                }
                return jsonify(quote_data)
        
        # 如果真实服务不可用或获取失败，使用模拟数据
        mock_data = {
            "600519": {
                "code": "600519",
                "name": "贵州茅台",
                "current_price": 1850.00,
                "change_percent": 2.5,
                "open": 1820.00,
                "high": 1860.00,
                "low": 1815.00,
                "volume": 12500
            },
            "000001": {
                "code": "000001",
                "name": "平安银行",
                "current_price": 15.30,
                "change_percent": -1.2,
                "open": 15.50,
                "high": 15.60,
                "low": 15.20,
                "volume": 25000
            }
        }
        
        if stock_code in mock_data:
            return jsonify(mock_data[stock_code])
        else:
            return jsonify({"error": "股票代码不存在"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/stocks/funds/list')
def get_funds_list():
    """获取基金列表"""
    try:
        funds = [
            {"code": "000001", "name": "华夏成长混合", "type": "混合型", "nav": 2.456, "change": "+1.20%"},
            {"code": "000002", "name": "易方达蓝筹精选", "type": "股票型", "nav": 3.128, "change": "-0.50%"},
            {"code": "000003", "name": "南方稳健成长", "type": "混合型", "nav": 1.876, "change": "+0.80%"}
        ]
        return jsonify(funds)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/stocks/indices/list')
def get_indices_list():
    """获取指数列表"""
    try:
        indices = [
            {"code": "000001", "name": "上证指数", "price": 3883.56, "change": "+1.51%"},
            {"code": "399001", "name": "深证成指", "price": 12441.07, "change": "+2.26%"},
            {"code": "399006", "name": "创业板指", "price": 2762.99, "change": "+3.00%"}
        ]
        return jsonify(indices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/news/latest')
def get_latest_news():
    """获取最新新闻"""
    try:
        # 模拟新闻数据
        news = [
            {
                "title": "央行降准释放流动性，A股市场迎来利好",
                "source": "新华社",
                "content": "中国人民银行宣布降准0.5个百分点，释放长期资金约1万亿元。",
                "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": "贵州茅台一季度净利润超预期，股价创历史新高",
                "source": "上海证券报",
                "content": "贵州茅台发布一季度财报，净利润同比增长20%。",
                "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RAG相关API
@app.route('/api/v1/rag/search')
def rag_search():
    """RAG知识检索"""
    try:
        query = request.args.get('q', '')
        top_k = int(request.args.get('top_k', 5))
        threshold = float(request.args.get('threshold', 0.1))
        
        if RAG_AVAILABLE:
            rag_service = get_rag_service()
            results = rag_service.search(query, top_k=top_k, threshold=threshold)
            return jsonify(results)
        else:
            # 返回空结果
            return jsonify([])
    except Exception as e:
        print(f"RAG搜索失败: {e}")
        return jsonify([])

@app.route('/api/v1/rag/analyze')
def rag_analyze():
    """RAG可信度分析"""
    try:
        content = request.args.get('content', '')
        
        if RAG_AVAILABLE:
            rag_service = get_rag_service()
            result = rag_service.analyze_content_credibility(content)
            return jsonify(result)
        else:
            # 返回默认分析结果
            return jsonify({
                "credibility_score": 0.5,
                "confidence": 0.0,
                "factors": [],
                "warning": "RAG服务未启用"
            })
    except Exception as e:
        print(f"RAG分析失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/rag/stats')
def rag_stats():
    """获取RAG知识库统计信息"""
    try:
        if RAG_AVAILABLE:
            rag_service = get_rag_service()
            stats = rag_service.get_stats()
            return jsonify({
                "status": "enabled",
                "total_documents": stats.get('total', 0),
                "total": stats.get('total', 0),  # 添加 total 字段兼容前端
                "by_type": stats.get('by_type', {}),
                "by_source": stats.get('by_source', {}),
                "vector_dimensions": stats.get('vector_dimensions', 0)
            })
        else:
            # 返回默认统计信息
            return jsonify({
                "total_documents": 0,
                "total": 0,  # 添加 total 字段兼容前端
                "by_type": {},
                "by_source": {},
                "vector_dimensions": 0,
                "error": "RAG服务未启用"
            })
    except Exception as e:
        print(f"获取RAG统计失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/chat/status')
def chat_status():
    """获取AI服务状态"""
    try:
        if AI_SERVICE_AVAILABLE:
            status = ai_service.get_service_status()
            return jsonify({
                "available": any(s['available'] for s in status.values()),
                "services": status
            })
        else:
            return jsonify({
                "available": False,
                "error": "AI服务未启用"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/chat/message', methods=['POST'])
def chat_message():
    """AI聊天功能"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({"success": False, "response": "消息不能为空"}), 400
        
        # 使用真实的AI服务
        if AI_SERVICE_AVAILABLE:
            result = ai_service.chat(message, session_id)
            return jsonify(result)
        else:
            # 如果AI服务不可用，返回模拟回复
            response = f"这是对'{message}'的模拟回复。AI服务未配置，请设置API密钥以启用真实AI服务。"
            
            return jsonify({
                "success": True,
                "response": response,
                "session_id": session_id,
                "service_used": "simulation"
            })
        
    except Exception as e:
        print(f"聊天失败: {e}")
        return jsonify({"success": False, "response": f"处理消息时出错: {str(e)}"}), 500

@app.route('/api/v1/analysis/analyze', methods=['POST'])
def analyze_stock():
    """股票分析API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据为空"}), 400
        
        stock_code = data.get('stock_code', '')
        query = data.get('query', '')
        
        if not stock_code:
            return jsonify({"error": "股票代码不能为空"}), 400
        
        print(f"收到股票分析请求: 股票代码={stock_code}, 查询={query}")
        
        # 获取股票基本信息
        stock_info = None
        if STOCK_SERVICE_AVAILABLE:
            try:
                stock_data = real_stock_service.get_stock_data(stock_code)
                if stock_data:
                    stock_info = {
                        "code": stock_data.get("code", stock_code),
                        "name": stock_data.get("name", "未知"),
                        "current_price": stock_data.get("current_price", 0),
                        "change_percent": stock_data.get("change_percent", 0),
                        "volume": stock_data.get("volume", 0)
                    }
            except Exception as e:
                print(f"获取股票信息失败: {e}")
        
        # 如果没有真实数据，使用模拟数据
        if not stock_info:
            stock_info = {
                "code": stock_code,
                "name": get_stock_name_by_code(stock_code),
                "current_price": 0,
                "change_percent": 0,
                "volume": 0
            }
        
        # 获取相关新闻
        news_list = []
        if NEWS_SERVICE_AVAILABLE:
            try:
                # 搜索相关新闻 - 使用asyncio.run运行异步方法
                news = asyncio.run(news_service.search_news(f"{stock_info['name']} {stock_code}", limit=5))
                news_list = [
                    {
                        "title": item.title if hasattr(item, 'title') else item.get("title", ""),
                        "content": item.content if hasattr(item, 'content') else item.get("content", ""),
                        "publish_time": item.publish_time if hasattr(item, 'publish_time') else item.get("publish_time", ""),
                        "source": item.source if hasattr(item, 'source') else item.get("source", ""),
                        "sentiment": item.sentiment if hasattr(item, 'sentiment') else item.get("sentiment", 0)
                    }
                    for item in news
                ]
            except Exception as e:
                print(f"获取新闻失败: {e}")
        
        # 生成分析报告
        analysis_report = generate_stock_analysis(stock_info, news_list, query)
        
        return jsonify({
            "stock_info": stock_info,
            "news": news_list,
            "analysis": analysis_report,
            "query": query,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        print(f"股票分析失败: {e}")
        return jsonify({"error": str(e)}), 500

def get_stock_name_by_code(code):
    """根据股票代码获取股票名称"""
    # 常见股票代码映射
    stock_map = {
        "600519": "贵州茅台",
        "000001": "平安银行",
        "000002": "万科A",
        "600036": "招商银行",
        "600000": "浦发银行",
        "600519": "贵州茅台",
        "000858": "五粮液"
    }
    return stock_map.get(code, f"股票{code}")

def generate_stock_analysis(stock_info, news_list, query):
    """生成股票分析报告"""
    analysis = {
        "summary": "",
        "technical_analysis": "",
        "news_analysis": "",
        "risk_analysis": "",
        "recommendation": ""
    }
    
    try:
        # 基本面摘要
        price = stock_info.get("current_price", 0)
        change = stock_info.get("change_percent", 0)
        stock_name = stock_info.get("name", "未知股票")
        
        analysis["summary"] = f"{stock_name}({stock_info['code']})当前股价为{price}元，今日涨跌幅{change:+.2f}%。"
        
        # 技术分析
        if change > 5:
            analysis["technical_analysis"] = "股价今日大幅上涨，表现强劲。"
        elif change > 2:
            analysis["technical_analysis"] = "股价今日稳步上涨，趋势向好。"
        elif change < -5:
            analysis["technical_analysis"] = "股价今日大幅下跌，需谨慎关注。"
        elif change < -2:
            analysis["technical_analysis"] = "股价今日有所回落，建议观望。"
        else:
            analysis["technical_analysis"] = "股价今日窄幅震荡，趋势不明。"
        
        # 新闻分析
        if news_list:
            positive_news = sum(1 for n in news_list if n.get("sentiment", 0) > 0.5)
            negative_news = sum(1 for n in news_list if n.get("sentiment", 0) < 0.3)
            
            if positive_news > negative_news:
                analysis["news_analysis"] = f"近期市场情绪偏积极，有{positive_news}条正面新闻。"
            elif negative_news > positive_news:
                analysis["news_analysis"] = f"近期市场情绪偏谨慎，有{negative_news}条负面新闻。"
            else:
                analysis["news_analysis"] = "近期市场情绪相对中性。"
        else:
            analysis["news_analysis"] = "暂无相关新闻信息。"
        
        # 风险分析
        if abs(change) > 10:
            analysis["risk_analysis"] = "股价波动较大，投资风险较高，请谨慎决策。"
        elif abs(change) > 5:
            analysis["risk_analysis"] = "股价波动适中，需注意风险控制。"
        else:
            analysis["risk_analysis"] = "股价相对稳定，风险相对较低。"
        
        # 建议
        if change > 3:
            analysis["recommendation"] = "短期表现强势，但需注意回调风险，建议分批建仓。"
        elif change < -3:
            analysis["recommendation"] = "短期有所调整，可关注企稳信号，逢低布局。"
        else:
            analysis["recommendation"] = "股价相对平稳，建议结合大盘走势综合判断。"
        
        # 如果有特定查询，定制分析
        if query and "买入" in query:
            analysis["recommendation"] += " 建议关注公司基本面变化，控制仓位。"
        elif query and "卖出" in query:
            analysis["recommendation"] += " 请根据个人投资策略和风险承受能力决策。"
        
    except Exception as e:
        print(f"生成分析报告失败: {e}")
        analysis["summary"] = "分析生成失败，请稍后再试。"
    
    return analysis

# 静态文件路由 - 必须放在所有API路由之后
@app.route('/')
def serve_index():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # 如果是API路径，返回404
    if path.startswith('api/'):
        return jsonify({"detail": "Not Found"}), 404
    
    try:
        return send_from_directory(frontend_dir, path)
    except:
        # 如果文件不存在，返回index.html（SPA支持）
        return send_from_directory(frontend_dir, 'index.html')

# 启动服务器
print("\n启动Flask服务器...")
print("访问地址: http://localhost:8000")
print("API文档: http://localhost:8000/api")
print("\n" + "=" * 60)
print("服务器正在运行，请在浏览器中访问：")
print("  http://localhost:8000")
print("\n按 Ctrl+C 停止服务")
print("=" * 60)

app.run(host='0.0.0.0', port=8000, debug=False)