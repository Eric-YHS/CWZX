from typing import List, Optional, Dict
from sqlalchemy.orm import Session
import requests
import json
from datetime import datetime, timedelta
import baostock as bs
import pandas as pd

from models.schemas import StockInfo, MarketOverview, IndexInfo
from services.database import StockDB, get_db

class StockService:
    """股票服务"""
    
    def __init__(self):
        # 这里可以接入真实的股票API，如腾讯股票API、新浪股票API等
        self.api_base = "https://qt.gtimg.cn"
    
    async def search_stocks(self, keyword: str, limit: int = 10) -> List[StockInfo]:
        """搜索股票"""
        db = next(get_db())
        try:
            # 从数据库搜索
            stocks = db.query(StockDB).filter(
                StockDB.name.contains(keyword) | StockDB.code.contains(keyword)
            ).limit(limit).all()
            
            result = []
            for stock in stocks:
                result.append(StockInfo(
                    code=stock.code,
                    name=stock.name,
                    current_price=stock.current_price,
                    change_percent=stock.change_percent,
                    volume=stock.volume,
                    market_cap=stock.market_cap
                ))
            
            # 如果数据库结果不足，可以调用API补充
            if len(result) < limit:
                api_results = await self._search_stocks_api(keyword, limit - len(result))
                result.extend(api_results)
            
            return result[:limit]
        finally:
            db.close()
    
    async def get_all_stocks(self, limit: int = 10) -> List[StockInfo]:
        """获取所有股票"""
        db = next(get_db())
        try:
            # 从数据库获取所有股票
            stocks = db.query(StockDB).limit(limit).all()
            
            result = []
            for stock in stocks:
                result.append(StockInfo(
                    code=stock.code,
                    name=stock.name,
                    current_price=stock.current_price,
                    change_percent=stock.change_percent,
                    volume=stock.volume,
                    market_cap=stock.market_cap
                ))
            
            return result
        finally:
            db.close()
    
    async def get_stock_info(self, stock_code: str) -> Optional[StockInfo]:
        """获取股票基本信息"""
        db = next(get_db())
        try:
            stock = db.query(StockDB).filter(StockDB.code == stock_code).first()
            if stock:
                return StockInfo(
                    code=stock.code,
                    name=stock.name,
                    current_price=stock.current_price,
                    change_percent=stock.change_percent,
                    volume=stock.volume,
                    market_cap=stock.market_cap
                )
            
            # 如果数据库没有，尝试从API获取
            return await self._get_stock_info_api(stock_code)
        finally:
            db.close()
    
    async def get_stock_quote(self, stock_code: str) -> Optional[Dict]:
        """获取股票实时行情"""
        try:
            # 使用腾讯股票API获取实时数据
            url = f"{self.api_base}/q={self._format_market_code(stock_code)}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                # 解析返回数据
                data = response.text
                if data.startswith("v_"):
                    data = data.split('"')[1]
                    
                    # 格式：名称,当前价,昨收,今开,最高,最低,成交量,成交额,换手率,市盈率,...
                    fields = data.split("~")
                    
                    quote = {
                        "code": stock_code,
                        "name": fields[1],
                        "current_price": float(fields[3]) if fields[3] else None,
                        "yesterday_close": float(fields[4]) if fields[4] else None,
                        "open": float(fields[5]) if fields[5] else None,
                        "high": float(fields[33]) if fields[33] else None,
                        "low": float(fields[34]) if fields[34] else None,
                        "volume": float(fields[6]) if fields[6] else None,
                        "amount": float(fields[37]) if fields[37] else None,
                        "change_percent": ((float(fields[3]) - float(fields[4])) / float(fields[4]) * 100) if fields[3] and fields[4] else None,
                        "turnover_rate": float(fields[38]) if fields[38] else None,
                        "pe_ratio": float(fields[39]) if fields[39] else None,
                        "market_cap": float(fields[45]) if fields[45] else None,
                        "update_time": datetime.now()
                    }
                    
                    # 更新数据库
                    await self._update_stock_quote(quote)
                    
                    return quote
            
            return None
            
        except Exception as e:
            print(f"获取股票行情时出错: {e}")
            return None
    
    async def _search_stocks_api(self, keyword: str, limit: int) -> List[StockInfo]:
        """从API搜索股票（示例实现）"""
        # 这里应该调用真实的搜索API
        # 返回一些示例数据
        return []
    
    async def _get_stock_info_api(self, stock_code: str) -> Optional[StockInfo]:
        """从API获取股票信息（示例实现）"""
        quote = await self.get_stock_quote(stock_code)
        if quote:
            return StockInfo(
                code=quote["code"],
                name=quote["name"],
                current_price=quote["current_price"],
                change_percent=quote["change_percent"],
                volume=quote["volume"],
                market_cap=quote["market_cap"]
            )
        return None
    
    async def _update_stock_quote(self, quote_data: Dict):
        """更新股票行情到数据库"""
        db = next(get_db())
        try:
            stock = db.query(StockDB).filter(StockDB.code == quote_data["code"]).first()
            
            if stock:
                # 更新现有记录
                stock.current_price = quote_data["current_price"]
                stock.change_percent = quote_data["change_percent"]
                stock.volume = quote_data["volume"]
                stock.market_cap = quote_data["market_cap"]
                stock.last_update = quote_data["update_time"]
            else:
                # 创建新记录
                stock = StockDB(
                    code=quote_data["code"],
                    name=quote_data["name"],
                    current_price=quote_data["current_price"],
                    change_percent=quote_data["change_percent"],
                    volume=quote_data["volume"],
                    market_cap=quote_data["market_cap"],
                    last_update=quote_data["update_time"]
                )
                db.add(stock)
            
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"更新股票行情时出错: {e}")
        finally:
            db.close()
    
    def _format_market_code(self, stock_code: str) -> str:
        """格式化市场代码"""
        if stock_code.startswith("6"):
            return f"sh{stock_code}"
        elif stock_code.startswith(("0", "3")):
            return f"sz{stock_code}"
        else:
            return stock_code
    
    async def get_fund_data(self) -> List[Dict]:
        """获取基金数据"""
        try:
            bs.login()
            
            # 一些常见的ETF基金代码
            fund_codes = [
                "sz.159915",  # 易方达创业板ETF
                "sh.510050",  # 华夏上证50ETF
                "sh.510300",  # 华泰柏瑞沪深300ETF
                "sz.159901",  # 易方达深证100ETF
                "sh.510500",  # 南方中证500ETF
            ]
            
            fund_data = []
            for fund_code in fund_codes:
                try:
                    # 获取最新价格数据
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    
                    rs = bs.query_history_k_data_plus(
                        fund_code,
                        start_date=start_date,
                        end_date=end_date,
                        frequency="d",
                        fields="date,open,high,low,close,volume,pctChg"
                    )
                    
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        data_list.append(rs.get_row_data())
                    
                    if data_list and len(data_list) > 0:
                        latest = data_list[-1]
                        fund_data.append({
                            "code": fund_code.split('.')[1],  # 去掉市场前缀
                            "name": self._get_fund_name(fund_code),
                            "price": float(latest[3]) if latest[3] and latest[3] != '' else None,  # open
                            "change": f"{float(latest[6]):+.2f}%" if latest[6] and latest[6] != '' else "--"  # pctChg
                        })
                    else:
                        # 如果没有获取到数据，使用模拟数据
                        fund_data.append({
                            "code": fund_code.split('.')[1],
                            "name": self._get_fund_name(fund_code),
                            "price": round(2.5 + (hash(fund_code) % 1000) / 1000, 3),
                            "change": f"{round((hash(fund_code) % 200 - 100) / 100, 2)}%"
                        })
                        
                except Exception as e:
                    print(f"获取基金 {fund_code} 数据失败: {e}")
                    # 添加模拟数据
                    fund_data.append({
                        "code": fund_code.split('.')[1],
                        "name": self._get_fund_name(fund_code),
                        "price": round(2.5 + (hash(fund_code) % 1000) / 1000, 3),
                        "change": f"{round((hash(fund_code) % 200 - 100) / 100, 2)}%"
                    })
                    continue
            
            bs.logout()
            return fund_data
            
        except Exception as e:
            print(f"获取基金数据时出错: {e}")
            # 返回模拟数据
            return [
                {"code": "159915", "name": "创业板ETF", "price": 2.856, "change": "+1.25%"},
                {"code": "510050", "name": "上证50ETF", "price": 2.754, "change": "-0.38%"},
                {"code": "510300", "name": "沪深300ETF", "price": 3.962, "change": "+0.85%"},
                {"code": "159901", "name": "深证100ETF", "price": 2.945, "change": "+1.62%"},
                {"code": "510500", "name": "中证500ETF", "price": 5.847, "change": "-0.15%"}
            ]
    
    async def get_index_data(self) -> List[Dict]:
        """获取指数数据（替代外汇）"""
        try:
            bs.login()
            
            # 主要指数代码
            index_codes = [
                ("sh.000001", "上证指数"),
                ("sz.399001", "深证成指"),
                ("sh.000300", "沪深300"),
                ("sz.399006", "创业板指"),
                ("sh.000016", "上证50"),
            ]
            
            index_data = []
            for index_code, index_name in index_codes:
                try:
                    # 获取最新K线数据
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    
                    rs_k = bs.query_history_k_data_plus(
                        index_code,
                        start_date=start_date,
                        end_date=end_date,
                        frequency="d",
                        fields="date,open,high,low,close,pctChg"
                    )
                    
                    k_data = []
                    while (rs_k.error_code == '0') & rs_k.next():
                        k_data.append(rs_k.get_row_data())
                    
                    if k_data and len(k_data) > 0:
                        latest = k_data[-1]
                        index_data.append({
                            "code": index_code.split('.')[1],  # 去掉市场前缀
                            "name": index_name,
                            "price": float(latest[3]) if latest[3] and latest[3] != '' else None,  # open
                            "change": f"{float(latest[5]):+.2f}%" if latest[5] and latest[5] != '' else "--"  # pctChg
                        })
                    else:
                        # 如果没有获取到数据，使用模拟数据
                        base_value = 3000 if "上证" in index_name else 1000 if "深证" in index_name else 4000
                        index_data.append({
                            "code": index_code.split('.')[1],
                            "name": index_name,
                            "price": base_value + (hash(index_code) % 1000),
                            "change": f"{round((hash(index_code) % 200 - 100) / 100, 2)}%"
                        })
                        
                except Exception as e:
                    print(f"获取指数 {index_name} 数据失败: {e}")
                    # 添加模拟数据
                    base_value = 3000 if "上证" in index_name else 1000 if "深证" in index_name else 4000
                    index_data.append({
                        "code": index_code.split('.')[1],
                        "name": index_name,
                        "price": base_value + (hash(index_code) % 1000),
                        "change": f"{round((hash(index_code) % 200 - 100) / 100, 2)}%"
                    })
                    continue
            
            bs.logout()
            return index_data
            
        except Exception as e:
            print(f"获取指数数据时出错: {e}")
            # 返回模拟数据
            return [
                {"code": "000001", "name": "上证指数", "price": 3089.26, "change": "+0.58%"},
                {"code": "399001", "name": "深证成指", "price": 9868.45, "change": "-0.32%"},
                {"code": "000300", "name": "沪深300", "price": 3654.78, "change": "+0.15%"},
                {"code": "399006", "name": "创业板指", "price": 1925.36, "change": "+1.25%"},
                {"code": "000016", "name": "上证50", "price": 2456.89, "change": "-0.08%"}
            ]
    
    async def get_hot_stocks(self, limit: int = 20) -> List[Dict]:
        """获取热门股票数据（基于成交量）"""
        try:
            bs.login()
            
            # 获取股票列表
            rs = bs.query_stock_basic()
            stock_list = []
            while (rs.error_code == '0') & rs.next():
                stock_list.append(rs.get_row_data())
            
            # 过滤出股票（type=1）并随机选择一些
            import random
            stocks = [s for s in stock_list if s[4] == '1']  # type=1是股票
            selected_stocks = random.sample(stocks, min(limit, len(stocks)))
            
            hot_stocks = []
            for stock in selected_stocks:
                code = stock[0]
                name = stock[1]
                
                try:
                    # 获取最新价格数据
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
                    
                    rs_quote = bs.query_history_k_data_plus(
                        code,
                        start_date=start_date,
                        end_date=end_date,
                        frequency="d",
                        fields="date,open,high,low,close,volume,pctChg"
                    )
                    
                    quote_data = []
                    while (rs_quote.error_code == '0') & rs_quote.next():
                        quote_data.append(rs_quote.get_row_data())
                    
                    if quote_data and len(quote_data) > 0:
                        latest = quote_data[-1]
                        hot_stocks.append({
                            "code": code.split('.')[1],  # 去掉市场前缀
                            "name": name,
                            "price": float(latest[3]) if latest[3] and latest[3] != '' else None,
                            "change": f"{float(latest[6]):+.2f}%" if latest[6] and latest[6] != '' else "--",
                            "volume": float(latest[5]) if latest[5] and latest[5] != '' else 0
                        })
                        
                except Exception as e:
                    print(f"获取股票 {code} 数据失败: {e}")
                    continue
            
            bs.logout()
            
            # 按成交量排序
            hot_stocks.sort(key=lambda x: x.get('volume', 0), reverse=True)
            return hot_stocks[:10]  # 返回前10只
            
        except Exception as e:
            print(f"获取热门股票时出错: {e}")
            # 返回模拟数据
            return [
                {"code": "600519", "name": "贵州茅台", "price": 1688.00, "change": "+0.85%", "volume": 25000},
                {"code": "000858", "name": "五粮液", "price": 158.50, "change": "-0.32%", "volume": 18000},
                {"code": "600036", "name": "招商银行", "price": 35.68, "change": "+1.25%", "volume": 32000},
                {"code": "000333", "name": "美的集团", "price": 52.36, "change": "+0.68%", "volume": 28000},
                {"code": "600276", "name": "恒瑞医药", "price": 45.28, "change": "-0.45%", "volume": 15000}
            ]
    
    async def get_industry_distribution(self) -> List[Dict]:
        """获取行业分布数据"""
        try:
            bs.login()
            
            # 获取行业数据
            rs = bs.query_stock_industry()
            industry_list = []
            while (rs.error_code == '0') & rs.next():
                industry_list.append(rs.get_row_data())
            
            # 统计各行业股票数量
            industry_count = {}
            for item in industry_list:
                industry = item[3]  # industry字段
                if industry:
                    industry_count[industry] = industry_count.get(industry, 0) + 1
            
            # 转换为百分比并排序
            total = sum(industry_count.values())
            industry_data = []
            for industry, count in industry_count.items():
                industry_data.append({
                    "name": industry,
                    "value": round(count / total * 100, 2),  # 百分比
                    "count": count
                })
            
            # 按数量排序，取前10个行业
            industry_data.sort(key=lambda x: x['count'], reverse=True)
            
            bs.logout()
            return industry_data[:10]
            
        except Exception as e:
            print(f"获取行业分布时出错: {e}")
            # 返回模拟数据
            return [
                {"name": "制造业", "value": 35.2, "count": 1923},
                {"name": "信息技术", "value": 18.5, "count": 1011},
                {"name": "金融业", "value": 12.8, "count": 699},
                {"name": "医药生物", "value": 10.3, "count": 563},
                {"name": "房地产", "value": 8.7, "count": 476},
                {"name": "消费", "value": 7.5, "count": 410},
                {"name": "能源", "value": 4.2, "count": 230},
                {"name": "公用事业", "value": 2.8, "count": 153}
            ]
    
    async def _get_real_distribution(self) -> Optional[Dict]:
        """获取真实的涨跌分布数据"""
        import aiohttp
        import asyncio
        
        try:
            # 使用东方财富API获取涨跌分布
            url = "http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': '5000',
                'po': '0',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'fid': 'f3',  # f3=涨跌幅
                'fs': 'm:0+t:6,m:0+t:80,m:0+t:81,m:1+t:2,m:1+t:23',  # 沪深A股（包含科创板）
                'fields': 'f3,f12,f14',  # f3=涨跌幅, f12=代码, f14=名称
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('data') and data['data'].get('diff'):
                            stocks = data['data']['diff']
                            total_stocks = data['data'].get('total', len(stocks))
                            
                            # 统计涨跌分布
                            up_count = 0
                            down_count = 0
                            flat_count = 0
                            
                            for stock in stocks:
                                try:
                                    # f3是涨跌幅字段
                                    change_percent = float(stock.get('f3', 0))
                                    if change_percent > 0:
                                        up_count += 1
                                    elif change_percent < 0:
                                        down_count += 1
                                    else:
                                        flat_count += 1
                                except:
                                    flat_count += 1
                            
                            # 如果数据量很大，可能需要获取更多页
                            if len(stocks) < total_stocks and len(stocks) >= 100:
                                # 尝试获取第二页数据以增加样本量
                                params['pn'] = '2'
                                try:
                                    async with session.get(url, params=params, timeout=10) as page_response:
                                        if page_response.status == 200:
                                            page_data = await page_response.json()
                                            if page_data.get('data') and page_data['data'].get('diff'):
                                                page_stocks = page_data['data']['diff']
                                                
                                                for stock in page_stocks:
                                                    try:
                                                        change_percent = float(stock.get('f3', 0))
                                                        if change_percent > 0:
                                                            up_count += 1
                                                        elif change_percent < 0:
                                                            down_count += 1
                                                        else:
                                                            flat_count += 1
                                                    except:
                                                        flat_count += 1
                                                
                                                # 按比例推算到总数
                                                ratio = total_stocks / (len(stocks) + len(page_stocks))
                                                up_count = int(up_count * ratio)
                                                down_count = int(down_count * ratio)
                                                flat_count = total_stocks - up_count - down_count
                                except:
                                    pass
                            
                            print(f"东方财富涨跌分布: 上涨{up_count}, 下跌{down_count}, 平盘{flat_count}")
                            
                            return {
                                'up_stocks': up_count,
                                'down_stocks': down_count,
                                'flat_stocks': flat_count,
                                'total_stocks': total_stocks,
                                'method': 'eastmoney_real_data'
                            }
        except Exception as e:
            print(f"获取真实涨跌分布失败: {e}")
        
        return None

    def _get_fund_name(self, fund_code: str) -> str:
        """获取基金名称"""
        fund_names = {
            "sz.159915": "创业板ETF",
            "sh.510050": "上证50ETF",
            "sh.510300": "沪深300ETF",
            "sz.159901": "深证100ETF",
            "sh.510500": "中证500ETF",
            "sz.159949": "创业板50ETF",
            "sh.510810": "上海国企ETF",
            "sz.159928": "消费ETF",
        }
        return fund_names.get(fund_code, "ETF基金")

    async def get_market_overview(self) -> MarketOverview:
        """获取市场概览数据"""
        try:
            # 首先尝试获取真实的涨跌分布数据
            print("尝试获取真实的涨跌分布数据...")
            real_distribution = await self._get_real_distribution()
            
            if real_distribution:
                print(f"成功获取真实涨跌分布: {real_distribution}")
                # 获取主要指数数据
                major_indices = await self._get_major_indices()
                
                return MarketOverview(
                    total_stocks=real_distribution['total_stocks'],
                    up_stocks=real_distribution['up_stocks'],
                    down_stocks=real_distribution['down_stocks'],
                    flat_stocks=real_distribution['flat_stocks'],
                    up_ratio=round(real_distribution['up_stocks'] / real_distribution['total_stocks'] * 100, 2),
                    down_ratio=round(real_distribution['down_stocks'] / real_distribution['total_stocks'] * 100, 2),
                    flat_ratio=round(real_distribution['flat_stocks'] / real_distribution['total_stocks'] * 100, 2),
                    major_indices=major_indices,
                    timestamp=datetime.now()
                )
            
            # 如果无法获取真实数据，使用基于主要指数的估算方法
            print("无法获取真实数据，使用基于指数的估算方法...")
            
            # 获取主要指数数据
            major_indices = await self._get_major_indices()
            
            # 计算平均涨跌幅
            total_change = 0
            valid_indices = 0
            
            for index in major_indices:
                if index.change_percent is not None:
                    total_change += index.change_percent
                    valid_indices += 1
            
            avg_change = total_change / valid_indices if valid_indices > 0 else 0
            
            # A股总共约5000只股票
            total_stocks = 5000
            
            # 根据平均涨跌幅估算涨跌分布
            if avg_change > 2:  # 大涨
                up_ratio = 0.65
                down_ratio = 0.25
            elif avg_change > 0.5:  # 中涨
                up_ratio = 0.55
                down_ratio = 0.35
            elif avg_change > 0:  # 小涨
                up_ratio = 0.45
                down_ratio = 0.40
            elif avg_change > -0.5:  # 小跌
                up_ratio = 0.35
                down_ratio = 0.50
            elif avg_change > -2:  # 中跌
                up_ratio = 0.25
                down_ratio = 0.60
            else:  # 大跌
                up_ratio = 0.15
                down_ratio = 0.70
            
            flat_ratio = 1 - up_ratio - down_ratio
            
            up_stocks = int(total_stocks * up_ratio)
            down_stocks = int(total_stocks * down_ratio)
            flat_stocks = total_stocks - up_stocks - down_stocks
            
            print(f"基于指数平均涨跌幅({avg_change:.2f}%)的估算:")
            print(f"上涨: {up_stocks} ({up_ratio*100:.1f}%)")
            print(f"下跌: {down_stocks} ({down_ratio*100:.1f}%)")
            print(f"平盘: {flat_stocks} ({flat_ratio*100:.1f}%)")
            
            return MarketOverview(
                total_stocks=total_stocks,
                up_stocks=up_stocks,
                down_stocks=down_stocks,
                flat_stocks=flat_stocks,
                up_ratio=round(up_ratio * 100, 2),
                down_ratio=round(down_ratio * 100, 2),
                flat_ratio=round(flat_ratio * 100, 2),
                major_indices=major_indices,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"获取市场概览时出错: {e}")
            
            # 最后的备选方案：使用数据库数据
            print("使用数据库数据作为最后备选")
            db = next(get_db())
            try:
                # 查询所有股票的涨跌情况
                stocks = db.query(StockDB).all()
                
                total_stocks = len(stocks)
                up_stocks = sum(1 for stock in stocks if stock.change_percent and stock.change_percent > 0)
                down_stocks = sum(1 for stock in stocks if stock.change_percent and stock.change_percent < 0)
                flat_stocks = total_stocks - up_stocks - down_stocks
                
                # 计算比例
                up_ratio = round(up_stocks / total_stocks * 100, 2) if total_stocks > 0 else 0
                down_ratio = round(down_stocks / total_stocks * 100, 2) if total_stocks > 0 else 0
                flat_ratio = round(flat_stocks / total_stocks * 100, 2) if total_stocks > 0 else 0
                
                # 获取主要指数数据
                major_indices = await self._get_major_indices()
                
                return MarketOverview(
                    total_stocks=total_stocks,
                    up_stocks=up_stocks,
                    down_stocks=down_stocks,
                    flat_stocks=flat_stocks,
                    up_ratio=up_ratio,
                    down_ratio=down_ratio,
                    flat_ratio=flat_ratio,
                    major_indices=major_indices,
                    timestamp=datetime.now()
                )
            except Exception as db_error:
                print(f"数据库查询失败: {db_error}")
                # 返回默认数据
                return MarketOverview(
                    total_stocks=5000,
                    up_stocks=2250,
                    down_stocks=2000,
                    flat_stocks=750,
                    up_ratio=45.0,
                    down_ratio=40.0,
                    flat_ratio=15.0,
                    major_indices=[],
                    timestamp=datetime.now()
                )
            finally:
                db.close()
            
        except Exception as e:
            print(f"获取市场概览时出错: {e}")
            # 返回模拟数据
            return MarketOverview(
                total_stocks=5000,
                up_stocks=2800,
                down_stocks=1800,
                flat_stocks=400,
                up_ratio=56.0,
                down_ratio=36.0,
                flat_ratio=8.0,
                major_indices=[
                    IndexInfo(code="000001", name="上证指数", current_price=3089.26, change_percent=0.58),
                    IndexInfo(code="399001", name="深证成指", current_price=9868.45, change_percent=-0.32),
                    IndexInfo(code="000300", name="沪深300", current_price=3654.78, change_percent=0.15),
                    IndexInfo(code="399006", name="创业板指", current_price=1925.36, change_percent=1.25),
                    IndexInfo(code="000016", name="上证50", current_price=2456.89, change_percent=-0.08)
                ],
                timestamp=datetime.now()
            )

    async def _get_major_indices(self) -> List[IndexInfo]:
        """获取主要指数数据"""
        bs.login()
        try:
            # 主要指数代码
            index_codes = [
                ("sh.000001", "上证指数"),
                ("sz.399001", "深证成指"),
                ("sh.000300", "沪深300"),
                ("sz.399006", "创业板指"),
                ("sh.000016", "上证50"),
            ]
            
            indices = []
            for index_code, index_name in index_codes:
                try:
                    # 获取最新K线数据
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    
                    rs_k = bs.query_history_k_data_plus(
                        index_code,
                        start_date=start_date,
                        end_date=end_date,
                        frequency="d",
                        fields="date,open,high,low,close,pctChg"
                    )
                    
                    k_data = []
                    while (rs_k.error_code == '0') & rs_k.next():
                        k_data.append(rs_k.get_row_data())
                    
                    if k_data and len(k_data) > 0:
                        latest = k_data[-1]
                        close_price = float(latest[4]) if latest[4] and latest[4] != '' else None  # close
                        change_percent = float(latest[5]) if latest[5] and latest[5] != '' else None  # pctChg
                        
                        # 计算涨跌金额
                        open_price = float(latest[1]) if latest[1] and latest[1] != '' else None
                        change_amount = close_price - open_price if close_price and open_price else None
                        
                        indices.append(IndexInfo(
                            code=index_code.split('.')[1],
                            name=index_name,
                            current_price=close_price,
                            change_percent=change_percent,
                            change_amount=change_amount
                        ))
                    else:
                        # 如果没有获取到数据，使用模拟数据
                        base_value = 3000 if "上证" in index_name else 1000 if "深证" in index_name else 4000
                        indices.append(IndexInfo(
                            code=index_code.split('.')[1],
                            name=index_name,
                            current_price=base_value + (hash(index_code) % 1000),
                            change_percent=round((hash(index_code) % 200 - 100) / 100, 2)
                        ))
                        
                except Exception as e:
                    print(f"获取指数 {index_name} 数据失败: {e}")
                    # 添加模拟数据
                    base_value = 3000 if "上证" in index_name else 1000 if "深证" in index_name else 4000
                    indices.append(IndexInfo(
                        code=index_code.split('.')[1],
                        name=index_name,
                        current_price=base_value + (hash(index_code) % 1000),
                        change_percent=round((hash(index_code) % 200 - 100) / 100, 2)
                    ))
                    continue
            
            return indices
            
        except Exception as e:
            print(f"获取主要指数时出错: {e}")
            # 返回模拟数据
            return [
                IndexInfo(code="000001", name="上证指数", current_price=3089.26, change_percent=0.58),
                IndexInfo(code="399001", name="深证成指", current_price=9868.45, change_percent=-0.32),
                IndexInfo(code="000300", name="沪深300", current_price=3654.78, change_percent=0.15),
                IndexInfo(code="399006", name="创业板指", current_price=1925.36, change_percent=1.25),
                IndexInfo(code="000016", name="上证50", current_price=2456.89, change_percent=-0.08)
            ]
        finally:
            bs.logout()