from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from models.schemas import ChatRequest, ChatResponse, ChatMessage
from services.chat_service import ChatService

router = APIRouter()

class GeneralChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@router.post("/message")
async def general_chat_message(request: GeneralChatRequest):
    """通用聊天消息"""
    try:
        chat_service = ChatService()
        response = await chat_service.general_chat(
            message=request.message,
            session_id=request.session_id
        )
        # 确保返回格式一致
        if response.get("success"):
            return {
                "response": response["content"],
                "session_id": response.get("session_id"),
                "success": True
            }
        else:
            return {
                "response": response.get("error", "未知错误"),
                "success": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/financial-message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """发送财经聊天消息"""
    try:
        chat_service = ChatService()
        response = await chat_service.process_message(
            message=request.message,
            context=request.context,
            stock_code=request.stock_code
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis")
async def financial_analysis_chat(
    stock_code: str,
    question: str,
    context: List[ChatMessage] = []
):
    """财经分析专用聊天"""
    try:
        chat_service = ChatService()
        response = await chat_service.financial_analysis(
            stock_code=stock_code,
            question=question,
            context=context
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))