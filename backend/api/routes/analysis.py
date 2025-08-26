from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List

from models.schemas import AnalysisRequest, AnalysisResponse
from services.analysis_service import AnalysisService

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_news_impact(request: AnalysisRequest):
    """分析新闻对股票的影响"""
    try:
        analysis_service = AnalysisService()
        result = await analysis_service.analyze_news_impact(
            stock_code=request.stock_code,
            query=request.query,
            analysis_type=request.analysis_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment")
async def analyze_sentiment(text: str):
    """分析文本情感倾向"""
    try:
        analysis_service = AnalysisService()
        sentiment = await analysis_service.analyze_sentiment(text)
        return {"sentiment": sentiment, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trend")
async def predict_trend(stock_code: str, days: int = 7):
    """预测股票趋势"""
    try:
        analysis_service = AnalysisService()
        prediction = await analysis_service.predict_trend(
            stock_code=stock_code,
            days=days
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))