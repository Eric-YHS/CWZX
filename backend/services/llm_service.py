from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()

class ZhipuAIService:
    """智谱AI服务"""
    
    def __init__(self):
        self.api_key = os.getenv("ZHIPUAI_API_KEY")
        self.model = os.getenv("ZHIPUAI_MODEL", "glm-4")
        
        # 如果没有API密钥，使用模拟模式
        if not self.api_key or self.api_key == "your_zhipuai_api_key_here":
            print("[WARN] 警告: 未配置智谱AI密钥，将使用模拟模式")
            print("   请在 .env 文件中设置 ZHIPUAI_API_KEY")
            print("   获取地址: https://open.bigmodel.cn/")
            self.client = None
            self.mock_mode = True
        else:
            try:
                self.client = ZhipuAI(api_key=self.api_key)
                self.mock_mode = False
                print("[OK] 智谱AI服务初始化成功")
            except Exception as e:
                print(f"[ERROR] 智谱AI初始化失败: {e}")
                self.client = None
                self.mock_mode = True
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.6,
        thinking: bool = True
    ) -> Dict[str, Any]:
        """调用智谱AI聊天完成接口"""
        # 模拟模式
        if self.mock_mode or not self.client:
            return await self._mock_chat_completion(messages)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "reasoning_content": getattr(response.choices[0].message, 'reasoning_content', ''),
                "usage": getattr(response, 'usage', None)
            }
        except Exception as e:
            print(f"智谱AI调用失败: {e}")
            # 降级到模拟模式
            return await self._mock_chat_completion(messages)
    
    async def _mock_chat_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """模拟聊天回复"""
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # 根据用户消息类型返回不同的模拟回复
        if "你好" in user_message or "hello" in user_message.lower():
            mock_reply = "你好！我是财闻智析的AI助手，很高兴为您服务。请问有什么可以帮助您的吗？"
        elif "股票" in user_message or "投资" in user_message:
            mock_reply = "关于股票投资，我建议您：\n1. 关注公司基本面\n2. 分散投资风险\n3. 做好长期规划\n\n请记住，投资有风险，决策需谨慎。建议咨询专业的投资顾问。"
        elif "市场" in user_message:
            mock_reply = "当前市场情况复杂，建议您：\n1. 关注经济数据\n2. 注意政策变化\n3. 保持理性投资\n\n请问您具体想了解哪个方面的信息？"
        elif "RAG" in user_message or "检索" in user_message:
            mock_reply = "RAG检索增强生成功能已经集成，可以帮助您：\n1. 检索相关知识\n2. 验证信息可信度\n3. 提供更准确的回答\n\n请问您想检索什么信息？"
        else:
            mock_reply = f"您好！关于“{user_message[:20]}...”的问题，我很乐意帮助您。\n\n由于当前处于演示模式（未配置智谱AI密钥），我无法提供实时的智能分析。\n\n请在 .env 文件中配置 ZHIPUAI_API_KEY 来启用完整功能。"
        
        return {
            "success": True,
            "content": mock_reply,
            "reasoning_content": "",
            "usage": {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150}
        }
    
    async def analyze_news_impact(
        self,
        news_content: str,
        stock_code: str,
        stock_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """分析新闻对股票的影响"""
        system_prompt = f"""你是一个专业的金融分析师，请分析以下新闻对股票 {stock_code} 的影响。

要求：
1. 判断新闻是利好、利空还是中性
2. 详细分析原因
3. 预测短期影响（1-3天）
4. 给出投资建议
5. 分析影响程度（轻微/中等/重大）

请严格按照JSON格式返回，不要添加任何markdown代码块标记：
{{
    "sentiment": "positive/negative/neutral",
    "analysis": "详细分析内容",
    "short_term_impact": "短期影响预测",
    "suggestion": "投资建议",
    "impact_level": "轻微/中等/重大"
}}"""

        user_prompt = f"新闻内容：\n{news_content}"

        response = await self.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            thinking=False
        )
        
        return response
    
    async def general_chat(
        self,
        message: str,
        context: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """通用聊天功能，偏向金融主题"""
        system_prompt = """你是一个专业的金融AI助手，擅长解答各种问题，但尤其擅长金融、投资、经济相关的话题。

无论用户问什么问题，你都应该：
1. 如果问题与金融、投资、经济相关，请提供专业、准确的回答
2. 如果问题与其他领域相关，也可以回答，但可以适当引导到金融角度
3. 保持友好、专业的语气
4. 在涉及投资建议时，请提醒"投资有风险，决策需谨慎"
5. 如果涉及具体股票，请建议用户查看专业分析报告

请用中文回答。"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加上下文
        if context:
            messages.extend(context[-10:])  # 保留最近10轮对话
        
        # 添加用户消息
        messages.append({"role": "user", "content": message})
        
        response = await self.chat_completion(
            messages=messages,
            max_tokens=2048,
            temperature=0.7
        )
        
        return response
    
    async def analyze_financial_report(
        self,
        report_content: str,
        stock_code: str,
        stock_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """分析财务报告"""
        system_prompt = f"""你是一个专业的财务分析师，请分析以下财务报告。

股票代码：{stock_code}
股票名称：{stock_name or '未知'}

请从以下角度分析：
1. 营收表现
2. 盈利能力
3. 现金流状况
4. 偿债能力
5. 同比变化
6. 未来展望

请以JSON格式返回：
{{
    "revenue_analysis": "营收分析",
    "profitability_analysis": "盈利能力分析",
    "cash_flow_analysis": "现金流分析",
    "debt_analysis": "偿债能力分析",
    "year_over_year": "同比变化分析",
    "outlook": "未来展望",
    "overall_rating": "买入/持有/卖出",
    "key_highlights": ["关键亮点1", "关键亮点2"]
}}"""

        user_prompt = f"财务报告内容：\n{report_content}"

        response = await self.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            thinking=False
        )
        
        return response
    
    async def investment_advisor_chat(
        self,
        user_message: str,
        context: List[Dict[str, str]] = None,
        stock_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """投资顾问聊天"""
        system_prompt = """你是一个专业的投资顾问，请根据用户的问题提供投资建议。

注意事项：
1. 提供客观、理性的分析
2. 不做具体的买卖推荐
3. 提醒投资风险
4. 建议用户进行独立研究
5. 不要提供保证收益的承诺

请用专业但易懂的语言回答用户问题。"""

        # 构建消息历史
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.extend(context)
        
        # 添加股票上下文
        if stock_code:
            user_message = f"关于股票 {stock_code}：{user_message}"
        
        messages.append({"role": "user", "content": user_message})

        response = await self.chat_completion(
            messages=messages,
            thinking=True
        )
        
        return response
    
    async def market_sentiment_analysis(
        self,
        news_list: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """市场情绪分析"""
        # 合并新闻内容
        combined_content = "\n\n".join([f"{news['title']}\n{news['content']}" for news in news_list])
        
        system_prompt = """请分析以下财经新闻反映的市场情绪。

请从以下维度分析：
1. 整体市场情绪（乐观/悲观/中性）
2. 主要影响因素
3. 热点板块
4. 风险提示
5. 投资者情绪指标

请以JSON格式返回：
{{
    "overall_sentiment": "乐观/悲观/中性",
    "key_factors": ["因素1", "因素2"],
    "hot_sectors": ["板块1", "板块2"],
    "risk_alerts": ["风险1", "风险2"],
    "investor_sentiment": "贪婪/恐惧/理性",
    "summary": "总结分析"
}}"""

        user_prompt = f"新闻内容：\n{combined_content}"

        response = await self.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            thinking=False
        )
        
        return response