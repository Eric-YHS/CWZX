"""
RAG相关的API接口
提供知识检索、可信度分析等功能
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from services.rag_service import get_rag_service, search_knowledge, analyze_credibility

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG知识检索"])


class SearchRequest(BaseModel):
    """检索请求模型"""
    query: str = Field(..., description="检索查询文本", min_length=1)
    top_k: int = Field(default=5, description="返回结果数量", ge=1, le=20)
    threshold: float = Field(default=0.1, description="相似度阈值", ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """检索结果模型"""
    id: str
    type: str
    title: str
    content: str
    similarity: float
    source: str
    additional_info: Dict[str, Any] = Field(default_factory=dict)


class CredibilityRequest(BaseModel):
    """可信度分析请求模型"""
    content: str = Field(..., description="待分析内容", min_length=1)


class Evidence(BaseModel):
    """证据模型"""
    type: str
    similarity: float
    title: str
    source: str
    result: Optional[str] = None


class CredibilityResult(BaseModel):
    """可信度分析结果模型"""
    credibility_score: float = Field(..., description="可信度评分 0-1")
    assessment: str = Field(..., description="评估结果")
    risk_level: str = Field(..., description="风险等级")
    evidence_summary: Dict[str, int] = Field(..., description="证据统计")
    evidence: List[Evidence] = Field(..., description="支撑证据")
    analysis_time: str = Field(..., description="分析时间")


class StatsResult(BaseModel):
    """统计信息结果模型"""
    total: int
    by_type: Dict[str, int]
    by_source: Dict[str, int]
    vector_dimensions: int


@router.post("/search", response_model=List[SearchResult])
async def search_knowledge_api(request: SearchRequest):
    """
    知识检索API
    
    根据查询文本检索相关知识
    """
    try:
        logger.info(f"收到知识检索请求: query={request.query}, top_k={request.top_k}")
        
        rag_service = get_rag_service()
        results = rag_service.search(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        # 转换结果格式
        search_results = []
        for result in results:
            additional_info = {}
            for key, value in result.items():
                if key not in ['id', 'type', 'title', 'content', 'similarity', 'source']:
                    additional_info[key] = value
            
            search_results.append(SearchResult(
                id=result.get('id', ''),
                type=result.get('type', ''),
                title=result.get('title', ''),
                content=result.get('content', '')[:500] + '...' if len(result.get('content', '')) > 500 else result.get('content', ''),
                similarity=result.get('similarity', 0.0),
                source=result.get('source', ''),
                additional_info=additional_info
            ))
        
        return search_results
        
    except Exception as e:
        logger.error(f"知识检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"知识检索失败: {str(e)}")


@router.get("/search", response_model=List[SearchResult])
async def search_knowledge_get(
    q: str = Query(..., description="检索查询文本", min_length=1),
    top_k: int = Query(default=5, description="返回结果数量", ge=1, le=20),
    threshold: float = Query(default=0.1, description="相似度阈值", ge=0.0, le=1.0)
):
    """
    知识检索API (GET方式)
    
    根据查询文本检索相关知识
    """
    request = SearchRequest(query=q, top_k=top_k, threshold=threshold)
    return await search_knowledge_api(request)


@router.post("/analyze", response_model=CredibilityResult)
async def analyze_credibility_api(request: CredibilityRequest):
    """
    内容可信度分析API
    
    分析给定内容的可信度，基于知识库中的谣言和新闻数据
    """
    try:
        logger.info(f"收到可信度分析请求: content length={len(request.content)}")
        
        rag_service = get_rag_service()
        result = rag_service.analyze_content_credibility(request.content)
        
        # 转换证据格式
        evidence_list = []
        for evidence in result.get('evidence', []):
            evidence_list.append(Evidence(
                type=evidence.get('type', ''),
                similarity=evidence.get('similarity', 0.0),
                title=evidence.get('title', ''),
                source=evidence.get('source', ''),
                result=evidence.get('result')
            ))
        
        return CredibilityResult(
            credibility_score=result.get('credibility_score', 0.5),
            assessment=result.get('assessment', ''),
            risk_level=result.get('risk_level', ''),
            evidence_summary=result.get('evidence_summary', {}),
            evidence=evidence_list,
            analysis_time=result.get('analysis_time', '')
        )
        
    except Exception as e:
        logger.error(f"可信度分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"可信度分析失败: {str(e)}")


@router.get("/analyze", response_model=CredibilityResult)
async def analyze_credibility_get(
    content: str = Query(..., description="待分析内容", min_length=1)
):
    """
    内容可信度分析API (GET方式)
    
    分析给定内容的可信度
    """
    request = CredibilityRequest(content=content)
    return await analyze_credibility_api(request)


@router.get("/knowledge/{knowledge_type}")
async def get_knowledge_by_type(
    knowledge_type: str,
    limit: int = Query(default=10, description="返回数量限制", ge=1, le=100)
):
    """
    根据类型获取知识
    
    支持的类型：
    - rumor_detection: 谣言检测
    - news_classification: 新闻分类
    """
    try:
        logger.info(f"获取知识类型: {knowledge_type}, limit={limit}")
        
        rag_service = get_rag_service()
        results = rag_service.get_knowledge_by_type(knowledge_type, limit)
        
        return {
            "knowledge_type": knowledge_type,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"获取知识失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取知识失败: {str(e)}")


@router.get("/stats", response_model=StatsResult)
async def get_knowledge_stats():
    """
    获取知识库统计信息
    
    返回知识库的统计数据，包括总数量、类型分布、来源分布等
    """
    try:
        logger.info("获取知识库统计信息")
        
        rag_service = get_rag_service()
        stats = rag_service.get_stats()
        
        return StatsResult(
            total=stats.get('total', 0),
            by_type=stats.get('by_type', {}),
            by_source=stats.get('by_source', {}),
            vector_dimensions=stats.get('vector_dimensions', 0)
        )
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    RAG服务健康检查
    
    检查RAG服务是否正常运行
    """
    try:
        rag_service = get_rag_service()
        stats = rag_service.get_stats()
        
        return {
            "status": "healthy",
            "knowledge_base_loaded": stats.get('total', 0) > 0,
            "total_knowledge": stats.get('total', 0),
            "vector_ready": stats.get('vector_dimensions', 0) > 0
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }