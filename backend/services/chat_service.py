from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from models.schemas import ChatRequest, ChatResponse, ChatMessage
from services.llm_service import ZhipuAIService
from services.news_service import NewsService
from services.rag_service import get_rag_service, search_knowledge, analyze_credibility
from models.schemas import NewsType

class ChatService:
    """聊天服务"""
    
    def __init__(self):
        self.llm_service = ZhipuAIService()
        self.news_service = NewsService()
        self.rag_service = get_rag_service()
        self.sessions = {}  # 简单的会话存储，生产环境应使用数据库或Redis
    
    async def general_chat(
        self,
        message: str,
        session_id: str = None
    ) -> Dict[str, Any]:
        """通用聊天功能"""
        # 获取会话历史
        history = []
        if session_id and session_id in self.sessions:
            history = self.sessions[session_id]
        
        # RAG检索相关知识
        rag_context = ""
        credibility_info = None
        
        try:
            # 检索相关知识
            knowledge_results = self.rag_service.search(message, top_k=3, threshold=0.3)
            if knowledge_results:
                rag_context = "\n\n基于知识库的相关信息：\n"
                for i, result in enumerate(knowledge_results[:2], 1):
                    rag_context += f"{i}. {result.get('title', '未知标题')}\n"
                    rag_context += f"   内容摘要: {result.get('content', '')[:200]}...\n"
                    rag_context += f"   来源: {result.get('source', '未知来源')}\n"
                    rag_context += f"   相似度: {result.get('similarity', 0):.2f}\n\n"
            
            # 对用户消息进行可信度分析
            credibility_result = self.rag_service.analyze_content_credibility(message)
            if credibility_result.get('credibility_score', 0.5) < 0.6:
                credibility_info = {
                    "score": credibility_result.get('credibility_score', 0.5),
                    "assessment": credibility_result.get('assessment', ''),
                    "risk_level": credibility_result.get('risk_level', ''),
                    "evidence_count": len(credibility_result.get('evidence', []))
                }
        
        except Exception as e:
            print(f"RAG检索失败: {e}")
        
        # 构建增强的提示词
        enhanced_message = message
        if rag_context:
            enhanced_message = f"{message}{rag_context}\n\n请基于以上知识库信息，结合你的专业知识来回答用户的问题。如果知识库信息与问题相关，请优先参考知识库内容。"
        
        # 调用LLM服务
        response = await self.llm_service.general_chat(
            message=enhanced_message,
            context=history
        )
        
        if response["success"]:
            # 更新会话历史
            if session_id:
                if session_id not in self.sessions:
                    self.sessions[session_id] = []
                
                # 添加对话记录
                self.sessions[session_id].append({
                    "role": "user",
                    "content": message
                })
                self.sessions[session_id].append({
                    "role": "assistant",
                    "content": response["content"]
                })
                
                # 限制历史长度
                if len(self.sessions[session_id]) > 20:  # 保留最近10轮对话
                    self.sessions[session_id] = self.sessions[session_id][-20:]
            
            result = {
                "success": True,
                "content": response["content"],
                "session_id": session_id
            }
            
            # 添加RAG相关信息到响应中
            if knowledge_results:
                result["knowledge_used"] = len(knowledge_results)
                result["knowledge_sources"] = list(set([r.get('source', '') for r in knowledge_results]))
            
            if credibility_info:
                result["credibility_warning"] = credibility_info
            
            return result
        else:
            return {
                "success": False,
                "error": response.get("error", "未知错误")
            }
    
    async def process_message(
        self,
        message: str,
        context: List[ChatMessage] = None,
        stock_code: Optional[str] = None
    ) -> ChatResponse:
        """处理聊天消息"""
        # 转换上下文格式
        history = []
        if context:
            for msg in context:
                history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # RAG检索增强
        knowledge_context = ""
        credibility_warning = None
        
        try:
            # 检索相关知识
            knowledge_results = self.rag_service.search(message, top_k=3, threshold=0.2)
            if knowledge_results:
                knowledge_context = "\n\n相关知识参考：\n"
                for result in knowledge_results:
                    knowledge_context += f"- {result.get('title', '')}: {result.get('content', '')[:150]}...\n"
                    knowledge_context += f"  (来源: {result.get('source', '')}, 相似度: {result.get('similarity', 0):.2f})\n"
            
            # 可信度分析
            if any(keyword in message for keyword in ['谣言', '假消息', '传闻', '听说', '网传']):
                credibility_result = self.rag_service.analyze_content_credibility(message)
                if credibility_result.get('credibility_score', 0.5) < 0.5:
                    credibility_warning = {
                        "message": "注意：检测到可能存在不实信息，请谨慎对待",
                        "score": credibility_result.get('credibility_score', 0.5),
                        "risk_level": credibility_result.get('risk_level', '')
                    }
        
        except Exception as e:
            print(f"RAG增强失败: {e}")
        
        # 构建增强消息
        enhanced_message = message
        if knowledge_context:
            enhanced_message = f"{message}{knowledge_context}\n\n请结合以上知识库信息，提供准确、全面的回答。"
        
        # 调用LLM服务
        response = await self.llm_service.investment_advisor_chat(
            user_message=enhanced_message,
            context=history,
            stock_code=stock_code
        )
        
        if response["success"]:
            # 构建回复
            response_content = response["content"]
            
            # 如果有可信度警告，添加到回复中
            if credibility_warning:
                response_content = f"[WARN] {credibility_warning['message']}\n\n{response_content}"
            
            assistant_message = ChatMessage(
                role="assistant",
                content=response_content,
                timestamp=datetime.now()
            )
            
            # 更新上下文
            new_context = (context or []) + [
                ChatMessage(role="user", content=message, timestamp=datetime.now()),
                assistant_message
            ]
            
            # 生成建议
            suggestions = await self._generate_suggestions(message, stock_code)
            
            # 获取相关数据
            related_data = None
            if stock_code:
                related_data = await self._get_related_data(stock_code)
            
            # 添加RAG相关信息
            if related_data is None:
                related_data = {}
            
            if knowledge_results:
                related_data["rag_knowledge_count"] = len(knowledge_results)
                related_data["rag_sources"] = list(set([r.get('source', '') for r in knowledge_results]))
            
            return ChatResponse(
                response=response_content,
                context=new_context,
                suggestions=suggestions,
                related_data=related_data
            )
        else:
            return ChatResponse(
                response=f"抱歉，处理您的请求时出现错误：{response['error']}",
                context=context or [],
                suggestions=[]
            )
    
    async def financial_analysis(
        self,
        stock_code: str,
        question: str,
        context: List[ChatMessage] = None
    ) -> ChatResponse:
        """财经分析专用聊天"""
        # 获取相关新闻
        related_news = await self.news_service.get_stock_news(
            stock_code=stock_code,
            limit=5
        )
        
        # 构建系统提示
        system_prompt = f"""你是一个专业的金融分析师，正在分析股票 {stock_code}。

以下是相关的最新新闻：
{self._format_news_for_llm(related_news)}

请基于以上信息，专业地回答用户的问题。"""
        
        # 转换上下文格式
        history = [{"role": "system", "content": system_prompt}]
        if context:
            for msg in context:
                history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 调用LLM
        response = await self.llm_service.chat_completion(
            messages=history + [{"role": "user", "content": question}],
            thinking=True
        )
        
        if response["success"]:
            assistant_message = ChatMessage(
                role="assistant",
                content=response["content"],
                timestamp=datetime.now()
            )
            
            new_context = (context or []) + [
                ChatMessage(role="user", content=question, timestamp=datetime.now()),
                assistant_message
            ]
            
            return ChatResponse(
                response=response["content"],
                context=new_context,
                suggestions=[
                    f"查看{stock_code}最新财务报告",
                    f"分析{stock_code}技术指标",
                    f"了解{stock_code}行业动态"
                ],
                related_data={"related_news_count": len(related_news)}
            )
        else:
            return ChatResponse(
                response=f"分析失败：{response['error']}",
                context=context or [],
                suggestions=[]
            )
    
    async def _generate_suggestions(self, message: str, stock_code: Optional[str] = None) -> List[str]:
        """生成建议问题"""
        suggestions = []
        
        if stock_code:
            suggestions.extend([
                f"分析{stock_code}的最新走势",
                f"{stock_code}值得长期持有吗？",
                f"{stock_code}有哪些风险因素？"
            ])
        else:
            # 根据消息内容生成建议
            if "推荐" in message or "哪个" in message:
                suggestions.extend([
                    "请分析当前市场热点板块",
                    "有哪些低估值股票值得关注？",
                    "如何构建投资组合？"
                ])
            elif "风险" in message or "跌" in message:
                suggestions.extend([
                    "如何控制投资风险？",
                    "止损策略有哪些？",
                    "熊市该如何投资？"
                ])
            else:
                suggestions.extend([
                    "当前市场整体趋势如何？",
                    "如何进行基本面分析？",
                    "技术分析常用指标有哪些？"
                ])
        
        return suggestions[:3]  # 最多返回3个建议
    
    async def _get_related_data(self, stock_code: str) -> Dict[str, Any]:
        """获取相关数据"""
        try:
            # 获取最新新闻
            latest_news = await self.news_service.get_stock_news(
                stock_code=stock_code,
                limit=3
            )
            
            return {
                "stock_code": stock_code,
                "latest_news_count": len(latest_news),
                "news_sentiment": self._analyze_news_sentiment(latest_news)
            }
        except Exception as e:
            print(f"获取相关数据时出错: {e}")
            return {}
    
    def _format_news_for_llm(self, news_list: List) -> str:
        """格式化新闻内容给LLM"""
        if not news_list:
            return "暂无相关新闻"
        
        formatted = []
        for news in news_list[:3]:  # 只取前3条
            formatted.append(f"- {news.title}（{news.source}，{news.publish_time.strftime('%Y-%m-%d')}）")
        
        return "\n".join(formatted)
    
    def _analyze_news_sentiment(self, news_list: List) -> Dict[str, Any]:
        """简单分析新闻情感"""
        if not news_list:
            return {"sentiment": "neutral", "count": 0}
        
        positive = sum(1 for news in news_list if news.sentiment == "positive")
        negative = sum(1 for news in news_list if news.sentiment == "negative")
        neutral = sum(1 for news in news_list if news.sentiment == "neutral")
        
        if positive > negative:
            sentiment = "positive"
        elif negative > positive:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "count": len(news_list),
            "positive": positive,
            "negative": negative,
            "neutral": neutral
        }
    
    async def rag_enhanced_chat(
        self,
        message: str,
        context: List[ChatMessage] = None,
        use_credibility_check: bool = True
    ) -> ChatResponse:
        """
        RAG增强的聊天功能
        
        使用知识库检索相关信息，提供更准确的回答
        """
        try:
            # 检索相关知识
            knowledge_results = self.rag_service.search(message, top_k=5, threshold=0.2)
            
            # 可信度分析
            credibility_result = None
            if use_credibility_check:
                credibility_result = self.rag_service.analyze_content_credibility(message)
            
            # 构建知识上下文
            knowledge_context = ""
            if knowledge_results:
                knowledge_context = "\n\n=== 知识库相关信息 ===\n"
                for i, result in enumerate(knowledge_results, 1):
                    knowledge_context += f"{i}. 标题: {result.get('title', '无标题')}\n"
                    knowledge_context += f"   类型: {result.get('type', '未知')}\n"
                    knowledge_context += f"   内容: {result.get('content', '')[:200]}...\n"
                    knowledge_context += f"   来源: {result.get('source', '未知来源')}\n"
                    knowledge_context += f"   相似度: {result.get('similarity', 0):.3f}\n\n"
                
                knowledge_context += "=== 请基于以上信息回答问题 ===\n"
            
            # 构建增强的提示
            enhanced_message = f"{message}{knowledge_context}"
            
            # 转换上下文格式
            history = []
            if context:
                for msg in context:
                    history.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # 调用LLM
            response = await self.llm_service.general_chat(
                message=enhanced_message,
                context=history
            )
            
            if response["success"]:
                response_content = response["content"]
                
                # 添加可信度警告
                if credibility_result and credibility_result.get('credibility_score', 0.5) < 0.5:
                    warning = f"\n\n[WARN] 可信度警告: {credibility_result.get('assessment', '')}"
                    warning += f" (风险等级: {credibility_result.get('risk_level', '')}, 评分: {credibility_result.get('credibility_score', 0):.2f})"
                    response_content += warning
                
                # 构建回复消息
                assistant_message = ChatMessage(
                    role="assistant",
                    content=response_content,
                    timestamp=datetime.now()
                )
                
                # 更新上下文
                new_context = (context or []) + [
                    ChatMessage(role="user", content=message, timestamp=datetime.now()),
                    assistant_message
                ]
                
                # 生成建议
                suggestions = [
                    "详细解释这个问题",
                    "查看相关证据和来源",
                    "分析信息的可信度"
                ]
                
                # 构建相关数据
                related_data = {
                    "knowledge_count": len(knowledge_results),
                    "knowledge_sources": list(set([r.get('source', '') for r in knowledge_results])) if knowledge_results else [],
                    "knowledge_types": list(set([r.get('type', '') for r in knowledge_results])) if knowledge_results else []
                }
                
                if credibility_result:
                    related_data["credibility"] = {
                        "score": credibility_result.get('credibility_score', 0.5),
                        "assessment": credibility_result.get('assessment', ''),
                        "risk_level": credibility_result.get('risk_level', ''),
                        "evidence_count": len(credibility_result.get('evidence', []))
                    }
                
                return ChatResponse(
                    response=response_content,
                    context=new_context,
                    suggestions=suggestions,
                    related_data=related_data
                )
            else:
                return ChatResponse(
                    response=f"RAG增强聊天失败: {response.get('error', '未知错误')}",
                    context=context or [],
                    suggestions=[]
                )
        
        except Exception as e:
            return ChatResponse(
                response=f"抱歉，处理您的请求时出现错误: {str(e)}",
                context=context or [],
                suggestions=[]
            )
    
    async def search_knowledge_base(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        直接搜索知识库
        """
        try:
            results = self.rag_service.search(query, top_k=top_k, threshold=0.1)
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "count": 0
            }
    
    async def analyze_content_credibility(self, content: str) -> Dict[str, Any]:
        """
        分析内容可信度
        """
        try:
            result = self.rag_service.analyze_content_credibility(content)
            return {
                "success": True,
                "analysis": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """
        获取RAG知识库统计信息
        """
        try:
            return self.rag_service.get_stats()
        except Exception as e:
            return {
                "error": str(e),
                "total": 0
            }