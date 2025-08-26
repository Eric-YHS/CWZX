from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from models.schemas import NewsArticle, NewsType, SentimentType
from services.news_service import NewsService

router = APIRouter()

@router.get("/latest", response_model=List[NewsArticle])
async def get_latest_news(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    news_type: Optional[NewsType] = None,
    stock_code: Optional[str] = None
):
    """获取最新新闻"""
    try:
        news_service = NewsService()
        news_list = await news_service.get_latest_news(
            limit=limit,
            offset=offset,
            news_type=news_type,
            stock_code=stock_code
        )
        return news_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[NewsArticle])
async def search_news(
    keyword: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """搜索新闻"""
    try:
        news_service = NewsService()
        news_list = await news_service.search_news(
            keyword=keyword,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        return news_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{news_id}", response_model=NewsArticle)
async def get_news_detail(news_id: str):
    """获取新闻详情"""
    try:
        news_service = NewsService()
        news = await news_service.get_news_by_id(news_id)
        if not news:
            raise HTTPException(status_code=404, detail="新闻不存在")
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{stock_code}", response_model=List[NewsArticle])
async def get_stock_news(
    stock_code: str,
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100)
):
    """获取特定股票的新闻"""
    try:
        news_service = NewsService()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        news_list = await news_service.get_stock_news(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return news_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))