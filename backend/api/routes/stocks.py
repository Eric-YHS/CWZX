from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from models.schemas import StockInfo, MarketOverview
from services.stock_service import StockService

router = APIRouter()

@router.get("/search", response_model=List[StockInfo])
async def search_stocks(
    keyword: str = Query("", min_length=0),
    limit: int = Query(10, ge=1, le=50)
):
    """搜索股票"""
    try:
        stock_service = StockService()
        # 如果keyword为空，获取所有股票
        if keyword == "":
            stocks = await stock_service.get_all_stocks(limit)
        else:
            stocks = await stock_service.search_stocks(
                keyword=keyword,
                limit=limit
            )
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stock_code}", response_model=StockInfo)
async def get_stock_info(stock_code: str):
    """获取股票基本信息"""
    try:
        stock_service = StockService()
        stock = await stock_service.get_stock_info(stock_code)
        if not stock:
            raise HTTPException(status_code=404, detail="股票不存在")
        return stock
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{stock_code}/quote")
async def get_stock_quote(stock_code: str):
    """获取股票实时行情"""
    try:
        stock_service = StockService()
        quote = await stock_service.get_stock_quote(stock_code)
        if not quote:
            raise HTTPException(status_code=404, detail="无法获取股票行情")
        return quote
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/funds/list")
async def get_funds_list():
    """获取基金列表"""
    try:
        stock_service = StockService()
        funds = await stock_service.get_fund_data()
        return funds
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indices/list")
async def get_indices_list():
    """获取指数列表"""
    try:
        stock_service = StockService()
        indices = await stock_service.get_index_data()
        return indices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hot/list")
async def get_hot_stocks():
    """获取热门股票列表"""
    try:
        stock_service = StockService()
        hot_stocks = await stock_service.get_hot_stocks()
        return hot_stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/industry/distribution")
async def get_industry_distribution():
    """获取行业分布"""
    try:
        stock_service = StockService()
        industry_data = await stock_service.get_industry_distribution()
        return industry_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/overview", response_model=MarketOverview)
async def get_market_overview():
    """获取市场概览"""
    try:
        stock_service = StockService()
        market_overview = await stock_service.get_market_overview()
        return market_overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))