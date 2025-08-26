from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from models.schemas import NewsArticle, NewsType
from services.database import NewsDB, get_db

class NewsService:
    def __init__(self):
        pass
    
    async def get_latest_news(
        self,
        limit: int = 20,
        offset: int = 0,
        news_type: Optional[NewsType] = None,
        stock_code: Optional[str] = None
    ) -> List[NewsArticle]:
        """获取最新新闻"""
        db = next(get_db())
        try:
            query = db.query(NewsDB)
            
            if news_type:
                query = query.filter(NewsDB.news_type == news_type.value)
            
            if stock_code:
                query = query.filter(
                    or_(
                        NewsDB.stock_codes.contains([stock_code]),
                        NewsDB.title.contains(stock_code),
                        NewsDB.content.contains(stock_code)
                    )
                )
            
            news_list = query.order_by(desc(NewsDB.publish_time)).offset(offset).limit(limit).all()
            
            return [
                NewsArticle(
                    id=news.id,
                    title=news.title,
                    content=news.content,
                    source=news.source,
                    publish_time=news.publish_time,
                    news_type=news.news_type,
                    stock_codes=news.stock_codes or [],
                    tags=news.tags or [],
                    url=news.url,
                    sentiment=news.sentiment,
                    impact_analysis=news.impact_analysis,
                    created_at=news.created_at
                )
                for news in news_list
            ]
        finally:
            db.close()
    
    async def search_news(
        self,
        keyword: str,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[NewsArticle]:
        """搜索新闻"""
        db = next(get_db())
        try:
            query = db.query(NewsDB).filter(
                or_(
                    NewsDB.title.contains(keyword),
                    NewsDB.content.contains(keyword)
                )
            )
            
            if start_date:
                query = query.filter(NewsDB.publish_time >= start_date)
            
            if end_date:
                query = query.filter(NewsDB.publish_time <= end_date)
            
            news_list = query.order_by(desc(NewsDB.publish_time)).limit(limit).all()
            
            return [
                NewsArticle(
                    id=news.id,
                    title=news.title,
                    content=news.content,
                    source=news.source,
                    publish_time=news.publish_time,
                    news_type=news.news_type,
                    stock_codes=news.stock_codes or [],
                    tags=news.tags or [],
                    url=news.url,
                    sentiment=news.sentiment,
                    impact_analysis=news.impact_analysis,
                    created_at=news.created_at
                )
                for news in news_list
            ]
        finally:
            db.close()
    
    async def get_news_by_id(self, news_id: str) -> Optional[NewsArticle]:
        """根据ID获取新闻详情"""
        db = next(get_db())
        try:
            news = db.query(NewsDB).filter(NewsDB.id == news_id).first()
            
            if news:
                return NewsArticle(
                    id=news.id,
                    title=news.title,
                    content=news.content,
                    source=news.source,
                    publish_time=news.publish_time,
                    news_type=news.news_type,
                    stock_codes=news.stock_codes or [],
                    tags=news.tags or [],
                    url=news.url,
                    sentiment=news.sentiment,
                    impact_analysis=news.impact_analysis,
                    created_at=news.created_at
                )
            return None
        finally:
            db.close()
    
    async def get_stock_news(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 20
    ) -> List[NewsArticle]:
        """获取特定股票的新闻"""
        db = next(get_db())
        try:
            news_list = db.query(NewsDB).filter(
                and_(
                    or_(
                        NewsDB.stock_codes.contains([stock_code]),
                        NewsDB.title.contains(stock_code),
                        NewsDB.content.contains(stock_code)
                    ),
                    NewsDB.publish_time >= start_date,
                    NewsDB.publish_time <= end_date
                )
            ).order_by(desc(NewsDB.publish_time)).limit(limit).all()
            
            return [
                NewsArticle(
                    id=news.id,
                    title=news.title,
                    content=news.content,
                    source=news.source,
                    publish_time=news.publish_time,
                    news_type=news.news_type,
                    stock_codes=news.stock_codes or [],
                    tags=news.tags or [],
                    url=news.url,
                    sentiment=news.sentiment,
                    impact_analysis=news.impact_analysis,
                    created_at=news.created_at
                )
                for news in news_list
            ]
        finally:
            db.close()