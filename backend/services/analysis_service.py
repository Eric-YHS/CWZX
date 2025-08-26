from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio

from models.schemas import AnalysisRequest, AnalysisResponse, NewsArticle, SentimentType
from services.news_service import NewsService
from services.llm_service import ZhipuAIService
from services.database import get_db
from sqlalchemy.orm import Session

class AnalysisService:
    """分析服务"""
    
    def __init__(self):
        self.news_service = NewsService()
        self.llm_service = ZhipuAIService()
    
    async def analyze_news_impact(
        self,
        stock_code: str,
        query: str,
        analysis_type: str = "news_impact"
    ) -> AnalysisResponse:
        """分析新闻对股票的影响"""
        # 获取相关新闻
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        related_news = await self.news_service.get_stock_news(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            limit=10
        )
        
        if not related_news:
            return AnalysisResponse(
                stock_code=stock_code,
                analysis_type=analysis_type,
                result={
                    "message": f"未找到与股票 {stock_code} 相关的最新新闻",
                    "sentiment": "neutral",
                    "impact_level": "无"
                },
                related_news=[],
                timestamp=datetime.now()
            )
        
        # 合并新闻内容进行分析
        news_content = "\n\n".join([f"{news.title}\n{news.content}" for news in related_news[:3]])
        
        # 调用LLM分析
        analysis_result = await self.llm_service.analyze_news_impact(
            news_content=news_content,
            stock_code=stock_code
        )
        
        if analysis_result["success"]:
            try:
                # 处理可能的Markdown代码块包装
                content = analysis_result["content"].strip()
                if content.startswith("```json"):
                    content = content[7:]  # 移除开头的```json
                if content.endswith("```"):
                    content = content[:-3]  # 移除结尾的```
                content = content.strip()
                
                result_data = json.loads(content)
                
                # 更新新闻的情感分析结果
                await self._update_news_sentiment(related_news, result_data["sentiment"])
                
                return AnalysisResponse(
                    stock_code=stock_code,
                    analysis_type=analysis_type,
                    result=result_data,
                    related_news=related_news,
                    timestamp=datetime.now()
                )
            except json.JSONDecodeError as e:
                return AnalysisResponse(
                    stock_code=stock_code,
                    analysis_type=analysis_type,
                    result={
                        "message": "分析结果解析失败",
                        "raw_response": analysis_result["content"],
                        "error": str(e)
                    },
                    related_news=related_news,
                    timestamp=datetime.now()
                )
        else:
            return AnalysisResponse(
                stock_code=stock_code,
                analysis_type=analysis_type,
                result={
                    "error": analysis_result["error"]
                },
                related_news=related_news,
                timestamp=datetime.now()
            )
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析文本情感倾向"""
        system_prompt = """请分析以下文本的情感倾向。

要求：
1. 判断是积极、消极还是中性
2. 给出置信度（0-1）
3. 简要说明原因

请以JSON格式返回：
{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.8,
    "reason": "原因说明"
}"""

        response = await self.llm_service.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"文本内容：\n{text}"}
            ],
            thinking=False
        )
        
        if response["success"]:
            try:
                return json.loads(response["content"])
            except json.JSONDecodeError:
                return {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "reason": "无法解析分析结果"
                }
        else:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "reason": f"分析失败：{response['error']}"
            }
    
    async def predict_trend(self, stock_code: str, days: int = 7) -> Dict[str, Any]:
        """预测股票趋势"""
        # 获取历史新闻数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        historical_news = await self.news_service.get_stock_news(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            limit=50
        )
        
        if not historical_news:
            return {
                "stock_code": stock_code,
                "trend": "neutral",
                "confidence": 0.5,
                "message": "数据不足，无法进行趋势预测"
            }
        
        # 分析历史情绪
        news_content = "\n\n".join([f"{news.title}\n{news.content}" for news in historical_news])
        
        system_prompt = f"""基于以下历史新闻，预测股票 {stock_code} 未来 {days} 天的趋势。

请考虑：
1. 历史情绪变化
2. 重大事件影响
3. 市场环境
4. 行业趋势

请以JSON格式返回：
{{
    "trend": "上涨/下跌/震荡",
    "confidence": 0.8,
    "key_factors": ["因素1", "因素2"],
    "time_frame": "{days}天",
    "risk_level": "低/中/高",
    "suggestion": "建议"
}}"""

        response = await self.llm_service.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"历史新闻：\n{news_content}"}
            ],
            thinking=False
        )
        
        if response["success"]:
            try:
                result = json.loads(response["content"])
                result["stock_code"] = stock_code
                return result
            except json.JSONDecodeError:
                return {
                    "stock_code": stock_code,
                    "trend": "neutral",
                    "confidence": 0.5,
                    "message": "趋势预测解析失败"
                }
        else:
            return {
                "stock_code": stock_code,
                "trend": "neutral",
                "confidence": 0.5,
                "message": f"预测失败：{response['error']}"
            }
    
    async def _update_news_sentiment(self, news_list: List[NewsArticle], sentiment: str):
        """更新新闻的情感分析结果"""
        db = next(get_db())
        try:
            for news in news_list:
                db_news = db.query(NewsDB).filter(NewsDB.id == news.id).first()
                if db_news:
                    db_news.sentiment = sentiment
                    db_news.updated_at = datetime.now()
            
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"更新新闻情感时出错: {e}")
        finally:
            db.close()