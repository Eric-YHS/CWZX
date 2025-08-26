#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实股票数据服务
使用腾讯、新浪等API获取真实股票数据
"""

import requests
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional

class RealStockService:
    """真实股票数据服务"""
    
    def __init__(self):
        self.tencent_base = "http://qt.gtimg.cn"
        self.sina_base = "https://hq.sinajs.cn"
        self.eastmoney_base = "http://push2.eastmoney.com"
        
    def _format_market_code(self, code: str) -> str:
        """格式化股票代码，添加市场前缀"""
        if code.startswith('6'):
            return f"sh{code}"
        elif code.startswith('0') or code.startswith('3'):
            return f"sz{code}"
        elif code.startswith('900'):
            return f"sh{code}"  # B股
        else:
            return code
    
    def get_stock_data(self, code: str) -> Optional[Dict]:
        """获取股票实时数据"""
        # 如果是指数代码，使用东方财富API
        if code in ['000001', '399001', '399006', '000300', '000016']:
            return self._get_index_from_eastmoney(code)
        
        try:
            # 使用腾讯股票API
            formatted_code = self._format_market_code(code)
            url = f"{self.tencent_base}/q={formatted_code}"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.text
                # 解析腾讯数据格式：v_sh600519="1~贵州茅台~1680.00~20.00~1.20~..."
                pattern = rf'v_{formatted_code}="([^"]+)";'
                match = re.search(pattern, data)
                
                if match:
                    values = match.group(1).split('~')
                    if len(values) >= 10:
                        # 腾讯数据格式说明：
                        # 0: 未知, 1: 股票名称, 2: 当前价, 3: 昨收, 4: 开盘, 5: 最高, 6: 最低, 7: 买入价, 8: 卖出价, 9: 成交量
                        try:
                            current_price = float(values[3]) if values[3] else 0
                            yesterday_close = float(values[4]) if values[4] else current_price
                            change_amount = current_price - yesterday_close
                            change_percent = (change_amount / yesterday_close * 100) if yesterday_close > 0 else 0
                            
                            return {
                                "code": code,
                                "name": values[1],
                                "current_price": round(current_price, 2),
                                "change_amount": round(change_amount, 2),
                                "change_percent": round(change_percent, 2),
                                "open": float(values[5]) if values[5] else current_price,
                                "high": float(values[6]) if values[6] else current_price,
                                "low": float(values[7]) if values[7] else current_price,
                                "volume": int(values[9]) if values[9] else 0,
                                "timestamp": datetime.now().isoformat()
                            }
                        except (ValueError, IndexError):
                            pass
            
            # 如果腾讯API失败，尝试新浪API
            return self._get_from_sina(code)
            
        except Exception as e:
            print(f"获取股票数据失败 {code}: {e}")
            return None
    
    def _get_index_from_eastmoney(self, code: str) -> Optional[Dict]:
        """从东方财富获取指数数据"""
        try:
            # 东方财富API需要不同的secid格式
            # 1.000001 表示上证指数
            secid_map = {
                '000001': '1.000001',  # 上证指数
                '399001': '0.399001',  # 深证成指
                '399006': '0.399006',  # 创业板指
                '000300': '1.000300',  # 沪深300
                '000016': '1.000016'   # 上证50
            }
            
            secid = secid_map.get(code)
            if not secid:
                return None
                
            url = f"{self.eastmoney_base}/api/qt/stock/get"
            params = {
                'secid': secid,
                'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f169,f170,f171,f172,f168'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    d = data['data']
                    # f43: 当前价(需要除以100), f60: 昨收(需要除以100)
                    # f169: 涨跌额(需要除以100), f170: 涨跌幅(需要除以100)
                    current_price = float(d.get('f43', 0)) / 100
                    yesterday_close = float(d.get('f60', 0)) / 100
                    change_amount = float(d.get('f169', 0)) / 100
                    change_percent = float(d.get('f170', 0)) / 100
                    
                    return {
                        "code": code,
                        "name": d.get('f58', ''),
                        "current_price": round(current_price, 2),
                        "change_amount": round(change_amount, 2),
                        "change_percent": round(change_percent, 2),
                        "open": float(d.get('f46', 0)) / 100,
                        "high": float(d.get('f44', 0)) / 100,
                        "low": float(d.get('f45', 0)) / 100,
                        "volume": int(d.get('f47', 0)),
                        "timestamp": datetime.now().isoformat()
                    }
            
            return None
            
        except Exception as e:
            print(f"东方财富获取指数数据失败 {code}: {e}")
            return None
    
    def _get_from_sina(self, code: str) -> Optional[Dict]:
        """从新浪获取股票数据"""
        try:
            # 新浪API需要不同的格式
            if code.startswith('6'):
                market = 'sh'
            else:
                market = 'sz'
            
            url = f"{self.sina_base}/rn={int(time.time())}&list={market}{code}"
            headers = {
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.text
                pattern = rf'var hq_str_{market}{code}="([^"]+)";'
                match = re.search(pattern, data)
                
                if match:
                    values = match.group(1).split(',')
                    if len(values) >= 10:
                        # 新浪数据格式：
                        # 0: 股票名称, 1: 开盘, 2: 昨收, 3: 当前价, 4: 最高, 5: 最低, 6: 买入价, 7: 卖出价, 8: 成交量, 9: 成交额
                        try:
                            current_price = float(values[3]) if values[3] else 0
                            yesterday_close = float(values[2]) if values[2] else current_price
                            change_amount = current_price - yesterday_close
                            change_percent = (change_amount / yesterday_close * 100) if yesterday_close > 0 else 0
                            
                            return {
                                "code": code,
                                "name": values[0],
                                "current_price": round(current_price, 2),
                                "change_amount": round(change_amount, 2),
                                "change_percent": round(change_percent, 2),
                                "open": float(values[1]) if values[1] else current_price,
                                "high": float(values[4]) if values[4] else current_price,
                                "low": float(values[5]) if values[5] else current_price,
                                "volume": int(float(values[8])) if values[8] else 0,
                                "timestamp": datetime.now().isoformat()
                            }
                        except (ValueError, IndexError):
                            pass
        except Exception as e:
            print(f"新浪API获取失败 {code}: {e}")
        
        return None
    
    def search_stocks(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索股票"""
        try:
            # 使用东方财富API搜索股票
            url = f"{self.eastmoney_base}/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': str(limit * 2),  # 获取更多结果以便筛选
                'po': '0',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'fs': 'm:0+t:6,m:0+t:80,m:0+t:81,m:1+t:2,m:1+t:23',  # 沪深A股
                'fields': 'f12,f14,f3,f62',  # f12:代码, f14:名称, f3:涨跌幅, f62:市值
                'fid': 'f3',  # 按涨跌幅排序
                'keyword': keyword
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get('diff'):
                    stocks = data['data']['diff']
                    results = []
                    
                    for stock in stocks[:limit]:
                        # 获取更详细的信息
                        code = stock.get('f12', '')
                        name = stock.get('f14', '')
                        
                        results.append({
                            "code": code,
                            "name": name
                        })
                    
                    return results
            
            # 如果东方财富失败，返回一些常见股票
            common_stocks = [
                {"code": "600519", "name": "贵州茅台"},
                {"code": "000001", "name": "平安银行"},
                {"code": "000858", "name": "五粮液"},
                {"code": "601318", "name": "中国平安"},
                {"code": "600036", "name": "招商银行"},
                {"code": "000002", "name": "万科A"},
                {"code": "600276", "name": "恒瑞医药"},
                {"code": "300750", "name": "宁德时代"}
            ]
            
            # 过滤包含关键词的股票
            results = []
            for stock in common_stocks:
                if keyword in stock["name"] or keyword in stock["code"]:
                    results.append(stock)
            
            return results[:limit]
            
        except Exception as e:
            print(f"搜索股票失败: {e}")
            return []
    
    def get_market_indices(self) -> Dict:
        """获取市场指数"""
        indices = {}
        try:
            # 获取主要指数
            index_codes = {
                "000001": "上证指数",
                "399001": "深证成指", 
                "399006": "创业板指",
                "000300": "沪深300",
                "000016": "上证50"
            }
            
            for code, name in index_codes.items():
                data = self.get_stock_data(code)
                if data:
                    indices[code] = {
                        "name": name,
                        "current_price": data["current_price"],
                        "change_percent": data["change_percent"]
                    }
            
            return indices
            
        except Exception as e:
            print(f"获取指数失败: {e}")
            return {}

# 创建全局实例
real_stock_service = RealStockService()

# 测试函数
def test_service():
    """测试服务"""
    print("测试真实股票数据服务...")
    
    # 测试获取单只股票
    stock = real_stock_service.get_stock_data("600519")
    if stock:
        print(f"贵州茅台: {stock}")
    
    # 测试搜索
    results = real_stock_service.search_stocks("平安")
    print(f"搜索'平安'的结果: {results}")
    
    # 测试指数
    indices = real_stock_service.get_market_indices()
    print(f"市场指数: {indices}")

if __name__ == "__main__":
    test_service()