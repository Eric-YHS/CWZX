// // 获取新闻数据并更新滚动新闻
// async function fetchNews() {
//     try {
//         const response = await fetch('http://localhost:8000/api/news', {
//             method: 'GET',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//         });

//         if (!response.ok) {
//             throw new Error('获取新闻失败，请稍后重试！');
//         }

//         const data = await response.json();
//         const newsList = document.getElementById('news-list');
//         newsList.innerHTML = '';
//         data.news.forEach((newsItem) => {
//             const li = document.createElement('li');
//             li.textContent = newsItem;
//             newsList.appendChild(li);
//         });
//     } catch (error) {
//         console.error('Error:', error);
//         alert('无法加载新闻，请检查网络或联系技术支持！');
//     }
// }

// // 页面加载完成后获取新闻
// document.addEventListener('DOMContentLoaded', fetchNews);

// 创建分析结果模态框
function createAnalysisModal() {
    const modal = document.createElement('div');
    modal.id = 'analysis-modal';
    modal.innerHTML = `
        <div class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>分析结果</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div id="analysis-result"></div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // 关闭按钮事件
    const closeBtn = modal.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });

    // 点击遮罩层关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal.querySelector('.modal-overlay')) {
            modal.remove();
        }
    });

    return modal;
}

// 添加模态框样式
const modalStyles = document.createElement('style');
modalStyles.textContent = `
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .modal-content {
        background: white;
        border-radius: 12px;
        width: 80%;
        max-width: 600px;
        max-height: 80vh;
        overflow: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #eee;
    }
    
    .modal-header h3 {
        margin: 0;
        color: #333;
    }
    
    .modal-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: #666;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background-color 0.2s;
    }
    
    .modal-close:hover {
        background-color: #f0f0f0;
    }
    
    .modal-body {
        padding: 1.5rem;
    }
    
    #analysis-result {
        white-space: pre-wrap;
        line-height: 1.6;
    }
    
    /* 分析结果样式 */
    .stock-info, .analysis-result, .related-news {
        margin-bottom: 20px;
        padding: 15px;
        border: 1px solid #eee;
        border-radius: 8px;
    }
    
    .stock-info h3, .analysis-result h3, .related-news h3 {
        margin-top: 0;
        color: #333;
        border-bottom: 2px solid #007bff;
        padding-bottom: 8px;
    }
    
    .analysis-content {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 4px;
        white-space: pre-wrap;
    }
    
    .analysis-sections {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    
    .analysis-section {
        background: #fff;
        padding: 12px;
        border-radius: 6px;
        border-left: 4px solid #007bff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .analysis-section h4 {
        margin: 0 0 8px 0;
        color: #333;
        font-size: 16px;
        font-weight: 600;
    }
    
    .analysis-section p {
        margin: 0;
        color: #555;
        line-height: 1.5;
    }
    
    .json-result {
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 15px;
        margin: 0;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
        line-height: 1.4;
        overflow-x: auto;
        white-space: pre;
    }
    
    .news-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .news-item {
        padding: 10px 0;
        border-bottom: 1px solid #eee;
    }
    
    .news-item:last-child {
        border-bottom: none;
    }
    
    .news-title {
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .news-meta {
        font-size: 0.9em;
        color: #666;
    }
    
    .news-meta span {
        margin-right: 15px;
    }
    
    .news-sentiment {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .news-sentiment.positive {
        background: #d4edda;
        color: #155724;
    }
    
    .news-sentiment.negative {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* AI思考状态样式 */
    .message.thinking {
        opacity: 0.7;
        font-style: italic;
        animation: thinking 1.5s ease-in-out infinite;
    }
    
    @keyframes thinking {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 1; }
    }
    
    .news-sentiment.neutral {
        background: #e2e3e5;
        color: #383d41;
    }
    
    .loading {
        text-align: center;
        padding: 20px;
        color: #666;
    }
    
    .loading::before {
        content: '';
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid #007bff;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
        margin-right: 10px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .error-message {
        color: #721c24;
        background: #f8d7da;
        padding: 15px;
        border-radius: 4px;
        border: 1px solid #f5c6cb;
    }
    
    .error-message h3 {
        margin-top: 0;
        color: #721c24;
    }
    
    .error-message ul {
        margin: 10px 0;
        padding-left: 20px;
    }
    
    .error-message li {
        margin: 5px 0;
    }
    
    .chart-loading {
        text-align: center;
        padding: 40px 20px;
        color: #666;
        font-size: 16px;
    }
    
    .chart-loading::before {
        content: '';
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid #007bff;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    /* 行情表格样式 */
    .market-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    
    .market-table th,
    .market-table td {
        padding: 10px;
        border: 1px solid #ddd;
        text-align: left;
    }
    
    .market-table th {
        background-color: #f1f1f1;
        font-weight: bold;
    }
    
    .market-table .positive {
        color: #28a745;
        font-weight: bold;
    }
    
    .market-table .negative {
        color: #dc3545;
        font-weight: bold;
    }
`;
document.head.appendChild(modalStyles);

// 获取情感文本
function getSentimentText(sentiment) {
    switch (sentiment) {
        case 'positive': return '利好';
        case 'negative': return '利空';
        case 'neutral': return '中性';
        default: return '未知';
    }
}



// 行情数据模拟
const marketData = {
    stocks: [
        { name: "贵州茅台", code: "600519", price: "1850.00", change: "+2.5%" },
        { name: "中国平安", code: "601318", price: "55.30", change: "-1.2%" },
    ],
    funds: [
        { name: "易方达蓝筹精选", code: "110011", price: "3.25", change: "+1.8%" },
        { name: "广发科技先锋", code: "005911", price: "2.98", change: "+0.5%" },
    ],
    forex: [
        { name: "美元/人民币", code: "USD/CNY", price: "6.89", change: "-0.1%" },
        { name: "欧元/美元", code: "EUR/USD", price: "1.12", change: "+0.3%" },
    ],
};

// 切换行情类型
document.querySelectorAll(".market-button").forEach((button) => {
    button.addEventListener("click", () => {
        // 移除所有按钮的 active 类
        document.querySelectorAll(".market-button").forEach((btn) => btn.classList.remove("active"));
        // 为当前按钮添加 active 类
        button.classList.add("active");

        // 获取按钮对应的行情类型
        const type = button.getAttribute("data-type");
        updateMarketContent(type);
    });
});

// 更新行情内容
async function updateMarketContent(type) {
    const marketContent = document.getElementById("market-content");

    // 显示加载中
    marketContent.innerHTML = "<p class='text-center'>正在加载数据...</p>";

    try {
        console.log('开始更新行情数据, 类型:', type);
        // 获取真实数据
        const realData = await updateMarketData();
        console.log('获取到的市场数据:', realData);
        
        const data = realData[type];

        if (!data || data.length === 0) {
            console.log(`${type} 数据为空，使用默认数据`);
            console.log('realData:', realData);
            console.log('type:', type);
            // 使用默认数据
            const defaultData = {
                stocks: [
                    { name: "贵州茅台", code: "600519", price: "1850.00", change: "+2.5%" },
                    { name: "中国平安", code: "601318", price: "55.30", change: "-1.2%" },
                    { name: "招商银行", code: "600036", price: "35.60", change: "+0.5%" }
                ],
                funds: [
                    { name: "易方达蓝筹精选", code: "110011", price: "3.25", change: "+1.8%" },
                    { name: "广发科技先锋", code: "005911", price: "2.98", change: "+0.5%" }
                ],
                forex: [
                    { name: "上证指数", code: "000001", price: "3100.50", change: "-0.1%" },
                    { name: "深证成指", code: "399001", price: "11200.30", change: "+0.3%" }
                ]
            };
            
            marketContent.innerHTML = generateMarketTable(defaultData[type]);
            return;
        }

        // 动态生成行情表格
        marketContent.innerHTML = generateMarketTable(data);
        console.log(`成功加载 ${data.length} 条 ${type} 数据`);
        
    } catch (error) {
        console.error('更新行情数据失败:', error);
        marketContent.innerHTML = `
            <div class="error-message">
                <h3>数据加载失败</h3>
                <p>无法获取 ${type} 数据: ${error.message}</p>
                <p>可能的原因：</p>
                <ul>
                    <li>后端服务未启动</li>
                    <li>网络连接异常</li>
                    <li>API接口问题</li>
                </ul>
                <button onclick="updateMarketContent('${type}')" style="margin-top: 10px; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">重试</button>
            </div>
        `;
    }
}

// 生成市场表格
function generateMarketTable(data) {
    if (!data || data.length === 0) {
        return "<p class='text-center'>暂无数据</p>";
    }
    
    let content = `
        <table class="market-table">
            <thead>
                <tr>
                    <th>名称</th>
                    <th>代码</th>
                    <th>价格</th>
                    <th>涨跌幅</th>
                </tr>
            </thead>
            <tbody>
    `;

    data.forEach((item) => {
        const changeClass = item.change && item.change.includes('+') ? 'positive' :
            item.change && item.change.includes('-') ? 'negative' : '';
        content += `
            <tr>
                <td>${item.name}</td>
                <td>${item.code}</td>
                <td>${item.price}</td>
                <td class="${changeClass}">${item.change}</td>
            </tr>
        `;
    });

    content += `
            </tbody>
        </table>
    `;
    
    return content;
}

// 默认加载股票行情 - 已移到底部的统一初始化函数中

// 获取相关元素
const floatingButton = document.getElementById("floating-button");
const aiWindow = document.getElementById("ai-window");
const closeButton = document.getElementById("close-button");
const chatLog = document.getElementById("chat-log");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");

// 显示 AI 窗口
floatingButton.addEventListener("click", () => {
    aiWindow.style.display = "flex";
});

// 关闭 AI 窗口
closeButton.addEventListener("click", () => {
    aiWindow.style.display = "none";
});

// 添加消息到聊天记录
function addMessageToChatLog(sender, message) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender); // 根据 sender 添加不同的样式
    
    // 如果是AI消息，使用marked.js渲染Markdown
    if (sender === "ai") {
        // 使用marked.js解析Markdown
        messageElement.innerHTML = marked.parse(message);
        
        // 为代码块添加样式
        const codeBlocks = messageElement.querySelectorAll('pre code');
        codeBlocks.forEach(block => {
            block.style.backgroundColor = '#f5f5f5';
            block.style.padding = '1em';
            block.style.borderRadius = '4px';
            block.style.display = 'block';
            block.style.overflow = 'auto';
        });
        
        // 为内联代码添加样式
        const inlineCodes = messageElement.querySelectorAll('code:not(pre code)');
        inlineCodes.forEach(code => {
            code.style.backgroundColor = '#f5f5f5';
            code.style.padding = '0.2em 0.4em';
            code.style.borderRadius = '3px';
            code.style.fontSize = '0.9em';
        });
    } else {
        // 用户消息保持原样，使用textContent避免XSS
        messageElement.textContent = message;
    }

    // 将消息添加到聊天记录
    const chatLog = document.getElementById("chat-log");
    chatLog.appendChild(messageElement);

    // 滚动到底部
    chatLog.scrollTop = chatLog.scrollHeight;
}

// 发送消息
sendButton.addEventListener("click", async () => {
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    // 显示用户消息
    addMessageToChatLog("user", userMessage);

    // 清空输入框
    chatInput.value = "";

    // 显示正在思考的提示
    const thinkingElement = document.createElement("div");
    thinkingElement.classList.add("message", "ai", "thinking");
    thinkingElement.textContent = "AI正在思考中（包含RAG知识检索）...";
    thinkingElement.id = "thinking-message"; // 添加ID方便查找
    chatLog.appendChild(thinkingElement);
    chatLog.scrollTop = chatLog.scrollHeight;

    try {
        console.log('发送消息到API:', userMessage);
        console.log('API地址:', DataService.baseURL + '/chat/message');

        // 先进行RAG知识检索
        let ragContext = "";
        try {
            const knowledgeResults = await DataService.searchKnowledge(userMessage, 3, 0.2);
            if (knowledgeResults && knowledgeResults.length > 0) {
                ragContext = "\n\n【相关知识检索结果】\n";
                knowledgeResults.forEach((result, index) => {
                    ragContext += `${index + 1}. ${result.title} (相似度: ${(result.similarity * 100).toFixed(1)}%)\n`;
                    ragContext += `   来源: ${result.source}\n`;
                    ragContext += `   内容: ${result.content}\n\n`;
                });
            }
        } catch (ragError) {
            console.warn('RAG检索失败:', ragError);
        }

        // 调用真实的API
        const response = await DataService.sendChatMessage(userMessage + ragContext);

        console.log('API响应:', response);

        // 移除思考提示
        const thinkingMsg = document.getElementById('thinking-message');
        if (thinkingMsg) {
            thinkingMsg.remove();
        }

        // 显示AI回复
        if (response && response.success && response.response) {
            addMessageToChatLog("ai", response.response);
        } else if (response && response.response) {
            // 即使success为false，也显示response内容
            addMessageToChatLog("ai", response.response);
        } else {
            console.error('API响应格式异常:', response);
            addMessageToChatLog("ai", "抱歉，我现在无法回答您的问题。可能的原因：\n1. 后端服务未启动\n2. API密钥配置问题\n3. 网络连接异常\n\n请检查控制台错误信息。");
        }
    } catch (error) {
        console.error('发送消息失败:', error);

        // 确保移除思考提示
        const thinkingMsg = document.getElementById('thinking-message');
        if (thinkingMsg) {
            thinkingMsg.remove();
        }

        // 显示更详细的错误信息
        let errorMessage = "抱歉，发送消息时出现错误：\n";
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorMessage += "网络连接失败，请检查：\n1. 后端服务是否启动 (http://localhost:8000)\n2. 网络连接是否正常";
        } else {
            errorMessage += error.message;
        }
        errorMessage += "\n\n请查看浏览器控制台获取更多详细信息。";

        addMessageToChatLog("ai", errorMessage);
    }
});

// 获取清除按钮
const clearButton = document.getElementById("clear-button");

// 清除聊天记录
clearButton.addEventListener("click", () => {
    const chatLog = document.getElementById("chat-log");
    chatLog.innerHTML = ""; // 清空聊天记录
});


// 窗口拖动和调整大小功能
const aiHeader = document.querySelector(".ai-header");
const resizeHandle = document.getElementById("resize-handle");

// 初始化变量
let isDragging = false;
let isResizing = false;
let originalWidth, originalHeight, originalX, originalY;
let startX, startY;
let originalLeft, originalTop;

// 添加窗口拖动功能
aiHeader.addEventListener("mousedown", (e) => {
    // 如果点击的是按钮，不触发拖动
    if (e.target.tagName === "BUTTON") return;

    isDragging = true;

    // 获取窗口当前位置
    const rect = aiWindow.getBoundingClientRect();
    originalLeft = rect.left;
    originalTop = rect.top;

    // 记录鼠标起始位置
    startX = e.clientX;
    startY = e.clientY;

    // 如果窗口是以 right 和 bottom 定位的，转换为 left 和 top
    if (!aiWindow.style.left) {
        aiWindow.style.left = originalLeft + "px";
        aiWindow.style.top = originalTop + "px";
        aiWindow.style.right = "auto";
        aiWindow.style.bottom = "auto";
    }

    // 设置样式以提高用户体验
    aiHeader.style.cursor = "grabbing";
    document.body.style.userSelect = "none";
});

// 监听鼠标按下事件，准备调整大小
resizeHandle.addEventListener("mousedown", (e) => {
    isResizing = true;

    // 记录初始窗口大小和位置
    const rect = aiWindow.getBoundingClientRect();
    originalWidth = rect.width;
    originalHeight = rect.height;
    originalLeft = rect.left;
    originalTop = rect.top;
    originalX = e.clientX;
    originalY = e.clientY;

    // 如果窗口是以 right 和 bottom 定位的，转换为 left 和 top
    if (!aiWindow.style.left) {
        aiWindow.style.left = originalLeft + "px";
        aiWindow.style.top = originalTop + "px";
        aiWindow.style.right = "auto";
        aiWindow.style.bottom = "auto";
    }

    document.body.style.userSelect = "none"; // 防止拖动时选中文本
    e.preventDefault();
});

// 监听鼠标移动事件
document.addEventListener("mousemove", (e) => {
    // 处理窗口拖动
    if (isDragging) {
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;

        const newLeft = originalLeft + deltaX;
        const newTop = originalTop + deltaY;

        // 确保窗口不会被拖出屏幕外
        if (newLeft >= 0 && newLeft + aiWindow.offsetWidth <= window.innerWidth) {
            aiWindow.style.left = newLeft + "px";
        }

        if (newTop >= 0 && newTop + aiWindow.offsetHeight <= window.innerHeight) {
            aiWindow.style.top = newTop + "px";
        }
    }

    // 处理窗口大小调整
    if (isResizing) {
        // 计算鼠标移动距离
        const deltaX = e.clientX - originalX;
        const deltaY = e.clientY - originalY;

        // 左上角调整大小时，同时改变位置和大小
        const newWidth = Math.max(200, originalWidth - deltaX);
        const newHeight = Math.max(300, originalHeight - deltaY);

        // 计算新的位置（保持右下角固定）
        const newLeft = originalLeft + originalWidth - newWidth;
        const newTop = originalTop + originalHeight - newHeight;

        // 应用新的尺寸和位置
        aiWindow.style.width = newWidth + "px";
        aiWindow.style.height = newHeight + "px";
        aiWindow.style.left = newLeft + "px";
        aiWindow.style.top = newTop + "px";
    }
});

// 监听鼠标松开事件
document.addEventListener("mouseup", () => {
    if (isDragging) {
        isDragging = false;
        aiHeader.style.cursor = "";
    }

    if (isResizing) {
        isResizing = false;
    }

    document.body.style.userSelect = "";
});

// 监听回车键发送消息
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        sendButton.click();
    }
});

// 数据服务模块
const DataService = {
    // 基础API配置
    baseURL: 'http://localhost:8000/api/v1',

    // 获取股票信息
    async getStockInfo(stockCode) {
        try {
            const response = await fetch(`${this.baseURL}/stocks/${stockCode}`);
            if (!response.ok) throw new Error('获取股票信息失败');
            return await response.json();
        } catch (error) {
            console.error('获取股票信息错误:', error);
            return null;
        }
    },

    // 获取股票实时行情
    async getStockQuote(stockCode) {
        try {
            const response = await fetch(`${this.baseURL}/stocks/${stockCode}/quote`);
            if (!response.ok) throw new Error('获取股票行情失败');
            return await response.json();
        } catch (error) {
            console.error('获取股票行情错误:', error);
            return null;
        }
    },

    // 搜索股票
    async searchStocks(keyword, limit = 10) {
        try {
            // 如果keyword为空，传空字符串
            const searchKeyword = keyword || '';
            const response = await fetch(`${this.baseURL}/stocks/search?keyword=${encodeURIComponent(searchKeyword)}&limit=${limit}`);
            if (!response.ok) throw new Error('搜索股票失败');
            return await response.json();
        } catch (error) {
            console.error('搜索股票错误:', error);
            return [];
        }
    },

    // 获取最新新闻
    async getLatestNews(limit = 20, offset = 0) {
        try {
            const response = await fetch(`${this.baseURL}/news/latest?limit=${limit}&offset=${offset}`);
            if (!response.ok) throw new Error('获取新闻失败');
            return await response.json();
        } catch (error) {
            console.error('获取新闻错误:', error);
            return [];
        }
    },

    // 获取股票相关新闻
    async getStockNews(stockCode, days = 7, limit = 20) {
        try {
            const response = await fetch(`${this.baseURL}/news/stock/${stockCode}?days=${days}&limit=${limit}`);
            if (!response.ok) throw new Error('获取股票新闻失败');
            return await response.json();
        } catch (error) {
            console.error('获取股票新闻错误:', error);
            return [];
        }
    },

    // 获取分析结果
    async getAnalysis(stockCode, query) {
        try {
            const response = await fetch(`${this.baseURL}/analysis/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    stock_code: stockCode,
                    query: query
                }),
            });
            if (!response.ok) throw new Error('获取分析结果失败');
            return await response.json();
        } catch (error) {
            console.error('获取分析结果错误:', error);
            return null;
        }
    },

    // 获取基金列表
    async getFundsList() {
        try {
            const response = await fetch(`${this.baseURL}/stocks/funds/list`);
            if (!response.ok) throw new Error('获取基金数据失败');
            return await response.json();
        } catch (error) {
            console.error('获取基金数据错误:', error);
            return [];
        }
    },

    // 获取指数列表
    async getIndicesList() {
        try {
            const response = await fetch(`${this.baseURL}/stocks/indices/list`);
            if (!response.ok) throw new Error('获取指数数据失败');
            return await response.json();
        } catch (error) {
            console.error('获取指数数据错误:', error);
            return [];
        }
    },

    // 获取市场概览
    async getMarketOverview() {
        try {
            const response = await fetch(`${this.baseURL}/stocks/market/overview`);
            if (!response.ok) throw new Error('获取市场概览失败');
            const data = await response.json();
            
            // 同时获取成交量数据
            try {
                const volumeResponse = await fetch(`${this.baseURL}/stocks/sh-index/volume`);
                if (volumeResponse.ok) {
                    const volumeData = await volumeResponse.json();
                    data.volume_data = volumeData;
                }
            } catch (error) {
                console.error('获取成交量数据失败:', error);
            }
            
            return data;
        } catch (error) {
            console.error('获取市场概览错误:', error);
            return null;
        }
    },

    // AI聊天功能
    async sendChatMessage(message, sessionId = null) {
        try {
            const response = await fetch(`${this.baseURL}/chat/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '发送消息失败');
            }

            return await response.json();
        } catch (error) {
            console.error('发送聊天消息错误:', error);
            
            // 特殊处理网络连接错误
            let errorMessage = `抱歉，发送消息时出现错误: ${error.message}`;
            if (error.message.includes('Failed to fetch')) {
                errorMessage = "抱歉，无法连接到后端服务。请确保：\n1. 后端服务已启动（运行 python quick_start.py）\n2. 后端服务运行在 localhost:8000\n3. 防火墙没有阻止连接";
            }
            
            return {
                success: false,
                response: errorMessage,
                session_id: sessionId
            };
        }
    },

    // RAG知识检索功能
    async searchKnowledge(query, topK = 5, threshold = 0.1) {
        try {
            const response = await fetch(`${this.baseURL}/rag/search?q=${encodeURIComponent(query)}&top_k=${topK}&threshold=${threshold}`);
            if (!response.ok) throw new Error('知识检索失败');
            return await response.json();
        } catch (error) {
            console.error('知识检索错误:', error);
            return [];
        }
    },

    // RAG可信度分析功能
    async analyzeCredibility(content) {
        try {
            const response = await fetch(`${this.baseURL}/rag/analyze?content=${encodeURIComponent(content)}`);
            if (!response.ok) throw new Error('可信度分析失败');
            return await response.json();
        } catch (error) {
            console.error('可信度分析错误:', error);
            return null;
        }
    },

    // 获取RAG知识库统计信息
    async getRAGStats() {
        try {
            const response = await fetch(`${this.baseURL}/rag/stats`);
            if (!response.ok) throw new Error('获取统计信息失败');
            return await response.json();
        } catch (error) {
            console.error('获取RAG统计信息错误:', error);
            return null;
        }
    },

    // 获取特定类型的知识
    async getKnowledgeByType(type, limit = 10) {
        try {
            const response = await fetch(`${this.baseURL}/rag/knowledge/${type}?limit=${limit}`);
            if (!response.ok) throw new Error('获取知识失败');
            return await response.json();
        } catch (error) {
            console.error('获取知识错误:', error);
            return null;
        }
    }
};

// 更新行情数据
async function updateMarketData() {
    const stocks = [
        { code: "600519", name: "贵州茅台" },
        { code: "000001", name: "平安银行" },
        { code: "000858", name: "五粮液" }
    ];

    const marketData = {
        stocks: [],
        funds: [],
        forex: []  // 这里使用指数数据替代外汇
    };

    // 获取股票数据
    for (const stock of stocks) {
        const quote = await DataService.getStockQuote(stock.code);
        if (quote) {
            marketData.stocks.push({
                name: stock.name,
                code: stock.code,
                price: quote.current_price || '--',
                change: quote.change_percent ? `${quote.change_percent > 0 ? '+' : ''}${quote.change_percent}%` : '--'
            });
        }
    }

    // 获取基金数据
    try {
        const funds = await DataService.getFundsList();
        if (funds && funds.length > 0) {
            marketData.funds = funds.map(fund => ({
                name: fund.name,
                code: fund.code,
                price: fund.price || '--',
                change: fund.change || '--'
            }));
        }
    } catch (error) {
        console.error('获取基金数据失败:', error);
    }

    // 获取指数数据（替代外汇）
    try {
        const indices = await DataService.getIndicesList();
        if (indices && indices.length > 0) {
            marketData.forex = indices.map(index => ({
                name: index.name,
                code: index.code,
                price: index.price || '--',
                change: index.change || '--'
            }));
        }
    } catch (error) {
        console.error('获取指数数据失败:', error);
    }

    return marketData;
}

// 市场分析图表（基于baostock数据）
async function initSentimentChart() {
    console.log('开始初始化图表...');

    // 确保ECharts已加载
    if (typeof echarts === 'undefined') {
        console.error('ECharts 未加载');
        return;
    }
    console.log('ECharts 已加载');

    const chartDom = document.getElementById('sentiment-chart');
    if (!chartDom) {
        console.error('找不到图表容器');
        return;
    }
    console.log('找到图表容器，尺寸:', chartDom.offsetWidth, 'x', chartDom.offsetHeight);

    // 显示加载中
    chartDom.innerHTML = '<div class="chart-loading">正在加载市场数据...</div>';

    try {
        console.log('开始获取市场概览数据...');
        // 获取市场概览数据
        const marketOverview = await DataService.getMarketOverview();
        console.log('市场概览数据:', marketOverview);

        let shIndex, szIndex, cyIndex;
        let upCount = 0, downCount = 0, flatCount = 0; // 初始化为0
        let distributionMethod = '加载中...';

        if (marketOverview && marketOverview.major_indices) {
            // 使用市场概览中的指数数据
            shIndex = marketOverview.major_indices.find(idx => idx.code === '000001');
            szIndex = marketOverview.major_indices.find(idx => idx.code === '399001');
            cyIndex = marketOverview.major_indices.find(idx => idx.code === '399006');

            // 使用市场概览中的涨跌分布数据
            upCount = marketOverview.up_stocks || upCount;
            downCount = marketOverview.down_stocks || downCount;
            flatCount = marketOverview.flat_stocks || flatCount;
            
            // 判断数据来源 - 优先使用API返回的method
            if (marketOverview.distribution_method) {
                // 根据API返回的method设置显示名称
                switch (marketOverview.distribution_method) {
                    case 'eastmoney_real_data':
                    case 'eastmoney_real_data_expanded':
                        distributionMethod = '东方财富数据';
                        break;
                    case 'index_estimation':
                        distributionMethod = '基于指数估算';
                        break;
                    case 'default_fallback':
                        distributionMethod = '默认数据';
                        break;
                    case 'non_trading_time':
                        distributionMethod = '非交易时间';
                        break;
                    case 'data_unavailable':
                        distributionMethod = '数据不可用';
                        break;
                    default:
                        distributionMethod = '智能估算';
                }
            } else {
                // 兼容旧版本：根据总数判断
                const total = upCount + downCount + flatCount;
                if (total >= 10000) {
                    distributionMethod = '东方财富数据';
                } else if (total >= 4000 && total <= 6000) {
                    distributionMethod = '交易所数据';
                } else if (marketOverview.up_ratio !== undefined) {
                    distributionMethod = '基于指数估算';
                } else {
                    distributionMethod = '智能估算';
                }
            }
        } else {
            console.log('市场概览数据为空，使用默认数据');
            // 使用默认数据
            shIndex = { current_price: '3100.00', change_percent: '0.5' };
            szIndex = { current_price: '9800.00', change_percent: '-0.3' };
            cyIndex = { current_price: '1800.00', change_percent: '1.2' };
        }

        // 生成模拟的日内走势数据（基于当前涨跌幅）
        const timePoints = ['09:30', '10:30', '11:30', '14:00', '15:00'];
        // 使用默认基准指数3000点，如果current_price为null的话
        const baseIndex = shIndex && shIndex.current_price ? parseFloat(shIndex.current_price) : 3000;
        const baseChange = shIndex && shIndex.change_percent ? parseFloat(shIndex.change_percent) : 0;

        // 生成指数走势数据
        const indexData = timePoints.map((time, index) => {
            const progress = index / (timePoints.length - 1);
            const fluctuation = Math.sin(progress * Math.PI) * baseChange * 0.5 + (Math.random() - 0.5) * 10;
            return Math.round(baseIndex * (1 + baseChange / 100 * progress) + fluctuation);
        });

        // 获取真实成交量数据
        let volumeData;
        if (marketOverview && marketOverview.volume_data) {
            // 使用真实的成交量数据（API返回的已经是万手单位）
            const baseVolume = marketOverview.volume_data.volume;
            
            // 基于真实成交量生成日内分布
            volumeData = timePoints.map((time, index) => {
                const progress = index / (timePoints.length - 1);
                // 成交量通常在开盘和收盘时较高
                const timeFactor = (index === 0 || index === timePoints.length - 1) ? 1.5 : 1.0;
                const randomFactor = 0.8 + Math.random() * 0.4; // 0.8-1.2的随机波动
                return Math.round(baseVolume * timeFactor * randomFactor * (1 + progress * 0.2));
            });
        } else {
            // 如果没有真实数据，使用模拟数据
            volumeData = timePoints.map(() => Math.floor(Math.random() * 300 + 100));
        }

        const totalCount = marketOverview.total_stocks || (upCount + downCount + flatCount);
        const option = {
            title: {
                text: '市场指数走势 (基于实时数据)',
                subtext: `更新时间: ${new Date().toLocaleTimeString('zh-CN')} | 数据源: ${distributionMethod} | 总计: ${totalCount}只（含沪深A股、北交所等）`,
                left: 'center',
                top: 20,
                textStyle: {
                    color: '#333',
                    fontSize: 16
                },
                subtextStyle: {
                    fontSize: 12
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                },
                formatter: function (params) {
                    let result = params[0].name + '<br/>';
                    params.forEach(item => {
                        result += `${item.seriesName}: ${item.value}<br/>`;
                    });
                    return result;
                }
            },
            legend: {
                data: ['上证指数', '成交量'],
                top: 60,
                left: 'center'
            },
            grid: {
                left: '3%',
                right: '5%',
                top: 100,
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: timePoints,
                axisLabel: {
                    formatter: '{value}'
                }
            },
            yAxis: [
                {
                    type: 'value',
                    name: '指数点位',
                    position: 'left',
                    axisLabel: {
                        formatter: '{value}'
                    }
                },
                {
                    type: 'value',
                    name: '成交量',
                    position: 'right',
                    axisLabel: {
                        formatter: '{value}'
                    }
                }
            ],
            series: [
                {
                    name: '上证指数',
                    type: 'line',
                    smooth: true,
                    data: indexData,
                    itemStyle: {
                        color: '#5470c6'
                    },
                    areaStyle: {
                        opacity: 0.3
                    },
                    markLine: {
                        data: [
                            { type: 'average', name: '平均值' }
                        ]
                    }
                },
                {
                    name: '成交量',
                    type: 'bar',
                    yAxisIndex: 1,
                    data: volumeData,
                    itemStyle: {
                        color: '#91cc75'
                    }
                }
            ]
        };

        // 清除加载提示并创建图表
        chartDom.innerHTML = '';
        console.log('清除加载提示，准备创建图表...');
        const myChart = echarts.init(chartDom);
        console.log('ECharts 实例创建成功');
        myChart.setOption(option);
        console.log('图表设置完成');

        // 存储ECharts实例以便清理
        chartDom.echartsInstance = myChart;

        // 响应式调整
        function handleResize() {
            myChart.resize();
        }
        window.addEventListener('resize', handleResize);

        // 存储resize处理器引用以便清理
        chartDom.resizeHandler = handleResize;

        // 定时更新数据（每30秒）
        const chartUpdateInterval = setInterval(async () => {
            try {
                // 重新获取市场概览数据
                const latestMarketOverview = await DataService.getMarketOverview();

                // 使用新的涨跌分布数据
                const newUpCount = latestMarketOverview.up_stocks;
                const newDownCount = latestMarketOverview.down_stocks;
                const newFlatCount = latestMarketOverview.flat_stocks;
                
                // 判断数据来源 - 优先使用API返回的method
                let newDistributionMethod = '默认数据';
                if (latestMarketOverview.distribution_method) {
                    // 根据API返回的method设置显示名称
                    switch (latestMarketOverview.distribution_method) {
                        case 'eastmoney_real_data':
                        case 'eastmoney_real_data_expanded':
                            newDistributionMethod = '东方财富数据';
                            break;
                        case 'index_estimation':
                            newDistributionMethod = '基于指数估算';
                            break;
                        case 'default_fallback':
                            newDistributionMethod = '默认数据';
                            break;
                        case 'non_trading_time':
                            newDistributionMethod = '非交易时间';
                            break;
                        case 'data_unavailable':
                            newDistributionMethod = '数据不可用';
                            break;
                        default:
                            newDistributionMethod = '智能估算';
                    }
                } else {
                    // 兼容旧版本：根据总数判断
                    const total = newUpCount + newDownCount + newFlatCount;
                    if (total >= 10000) {
                        newDistributionMethod = '东方财富数据';
                    } else if (total >= 4000 && total <= 6000) {
                        newDistributionMethod = '交易所数据';
                    } else if (latestMarketOverview.up_ratio !== undefined) {
                        newDistributionMethod = '基于指数估算';
                    } else {
                        newDistributionMethod = '智能估算';
                    }
                }

                // 更新指数和成交量数据
                myChart.setOption({
                    series: [
                        {
                            data: indexData
                        },
                        {
                            data: volumeData
                        }
                    ]
                });

                // 更新时间和数据来源
                const totalCount = latestMarketOverview.total_stocks || (newUpCount + newDownCount + newFlatCount);
                myChart.setOption({
                    title: {
                        subtext: `更新时间: ${new Date().toLocaleTimeString('zh-CN')} | 数据源: ${newDistributionMethod} | 总计: ${totalCount}只（含沪深A股、北交所等）`
                    }
                });

            } catch (error) {
                console.error('更新市场数据失败:', error);
            }
        }, 30000);

        // 存储interval ID以便清理
        chartDom.dataset.updateInterval = chartUpdateInterval;

    } catch (error) {
        console.error('初始化市场分析图表失败:', error);
        chartDom.innerHTML = `
            <div class="error-message">
                <h3>加载失败</h3>
                <p>无法获取市场数据: ${error.message}</p>
                <p>可能的原因：</p>
                <ul>
                    <li>后端服务未启动 (检查 http://localhost:8000)</li>
                    <li>网络连接异常</li>
                    <li>数据库没有数据</li>
                </ul>
                <button onclick="initSentimentChart()" style="margin-top: 10px; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">重试</button>
            </div>
        `;
    }
}

// 新闻滚动功能
async function initNewsTicker() {
    const newsList = document.getElementById('news-list');
    if (!newsList) return;

    try {
        console.log('开始获取新闻数据...');
        // 先尝试获取最新新闻
        const news = await DataService.getLatestNews(10);
        console.log('新闻数据:', news);

        if (news && news.length > 0) {
            newsList.innerHTML = '';
            news.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.title} - ${item.source}`;
                li.title = item.content; // 鼠标悬停显示内容
                newsList.appendChild(li);
            });
            console.log(`成功加载 ${news.length} 条新闻`);
        } else {
            console.log('API返回空数据，使用示例新闻');
            // 使用示例新闻
            const sampleNews = [
                { title: "央行降准释放流动性，A股市场迎来利好", source: "新华社", content: "中国人民银行宣布降准0.5个百分点" },
                { title: "贵州茅台一季度净利润超预期，股价创历史新高", source: "上海证券报", content: "贵州茅台发布一季度财报，净利润同比增长20%" },
                { title: "新能源汽车销量创新高，产业链公司受益", source: "经济参考报", content: "3月新能源汽车销量同比增长超过50%" },
                { title: "医药板块集体回调，创新药企业面临压力", source: "第一财经", content: "受医保谈判政策影响，医药板块今日集体回调" },
                { title: "市场情绪趋于谨慎，投资者观望情绪浓厚", source: "中国证券报", content: "受外围市场波动影响，A股市场今日表现平淡" }
            ];

            newsList.innerHTML = '';
            sampleNews.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.title} - ${item.source}`;
                li.title = item.content;
                newsList.appendChild(li);
            });
        }

        // 启动滚动动画
        startNewsScrolling();

    } catch (error) {
        console.error('加载新闻失败:', error);
        // 使用示例新闻作为后备
        const sampleNews = [
            { title: "【示例】市场动态更新中", source: "财闻智析", content: "正在获取最新市场资讯..." },
            { title: "央行降准释放流动性，A股市场迎来利好", source: "新华社", content: "中国人民银行宣布降准0.5个百分点" },
            { title: "贵州茅台一季度净利润超预期，股价创历史新高", source: "上海证券报", content: "贵州茅台发布一季度财报，净利润同比增长20%" }
        ];

        newsList.innerHTML = '';
        sampleNews.forEach(item => {
            const li = document.createElement('li');
            li.textContent = `${item.title} - ${item.source}`;
            li.title = item.content;
            newsList.appendChild(li);
        });

        startNewsScrolling();
    }
}

// 启动新闻滚动
function startNewsScrolling() {
    const ticker = document.getElementById('news-ticker');
    const newsList = document.getElementById('news-list');

    if (!ticker || !newsList) return;

    // 克隆新闻列表以实现无缝滚动
    const clone = newsList.cloneNode(true);
    newsList.appendChild(clone);

    let scrollPosition = 0;
    const scrollSpeed = 1;
    let animationId = null;
    let isPaused = false;

    function scroll() {
        if (isPaused) {
            animationId = requestAnimationFrame(scroll);
            return;
        }

        scrollPosition -= scrollSpeed;

        // 当滚动到克隆的内容时，重置位置
        if (Math.abs(scrollPosition) >= newsList.offsetHeight / 2) {
            scrollPosition = 0;
        }

        newsList.style.transform = `translateY(${scrollPosition}px)`;
        animationId = requestAnimationFrame(scroll);
    }

    // 鼠标悬停时暂停滚动
    ticker.addEventListener('mouseenter', () => {
        isPaused = true;
    });

    ticker.addEventListener('mouseleave', () => {
        isPaused = false;
    });

    // 开始滚动
    scroll();

    // 存储animation ID以便清理
    ticker.dataset.animationId = animationId;

    // 返回清理函数
    return function () {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
    };
}

// 初始化分析按钮
function initAnalysisButton() {
    const analysisButton = document.querySelector('.cta-button');
    const stockInput = document.querySelector('.search-box input');

    if (!analysisButton || !stockInput) {
        console.log('找不到分析按钮或输入框');
        return;
    }

    // 移除可能存在的旧事件监听器
    analysisButton.removeEventListener('click', handleAnalysisClick);
    
    // 点击分析按钮
    async function handleAnalysisClick() {
        const input = document.querySelector('input[type="text"]').value.trim();
        
        if (!input) {
            const modal = createAnalysisModal();
            modal.querySelector('#analysis-result').innerHTML = '<div class="error">请输入股票代码或基金名称！</div>';
            return;
        }

        // 显示加载中
        const modal = createAnalysisModal();
        const resultDiv = modal.querySelector('#analysis-result');
        resultDiv.innerHTML = '<div class="loading">正在分析中，请稍候...</div>';

        try {
            // 判断输入的是股票代码还是股票名称
            let stockCode = input;

            // 如果输入的是数字（可能是股票代码），直接使用
            // 如果输入的是中文（可能是股票名称），先搜索
            if (/[\u4e00-\u9fa5]/.test(input)) {
                const searchResults = await DataService.searchStocks(input);
                if (searchResults && searchResults.length > 0) {
                    stockCode = searchResults[0].code;
                }
            }

            // 获取分析结果
            const analysisResult = await DataService.getAnalysis(stockCode, input);

            if (analysisResult) {
                // 直接在当前模态框中显示结果
                resultDiv.innerHTML = '';
                showAnalysisResultInContainer(resultDiv, stockCode, analysisResult);
            } else {
                throw new Error('分析结果为空');
            }

        } catch (error) {
            console.error('分析失败:', error);
            resultDiv.innerHTML = `<div class="error">分析失败，请检查股票代码是否正确或稍后再试</div>`;
        }
    }

    // 添加事件监听器
    analysisButton.addEventListener('click', handleAnalysisClick);

    // 支持回车键分析
    stockInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            handleAnalysisClick();
        }
    });
}

// 在指定容器中显示分析结果
function showAnalysisResultInContainer(container, stockCode, result) {
    // 构建结果内容
    let htmlContent = '';
    
    // 显示股票信息
    if (result.stock_info) {
        htmlContent += `
            <div class="stock-info">
                <h3>股票信息</h3>
                <p><strong>股票代码：</strong>${result.stock_info.code || stockCode}</p>
                <p><strong>股票名称：</strong>${result.stock_info.name || '未知'}</p>
                <p><strong>当前价格：</strong>${result.stock_info.current_price || '--'}</p>
                <p><strong>涨跌幅：</strong>${result.stock_info.change_percent ? (result.stock_info.change_percent > 0 ? '+' : '') + result.stock_info.change_percent + '%' : '--'}</p>
            </div>
        `;
    }
    
    // 显示分析结果
    if (result.result && result.result.analysis_result) {
        htmlContent += `
            <div class="analysis-result">
                <h3>智能分析</h3>
                <div class="analysis-content">${result.result.analysis_result.replace(/\n/g, '<br>')}</div>
            </div>
        `;
    } else if (result.analysis || result.content) {
        const analysisText = result.analysis || result.content;
        let displayText = '';
        
        if (typeof analysisText === 'object') {
            // 如果是对象，格式化为友好的展示
            if (analysisText.news_analysis || analysisText.recommendation || analysisText.risk_analysis) {
                displayText = `<div class="analysis-sections">`;
                
                if (analysisText.summary) {
                    displayText += `<div class="analysis-section"><h4>概要</h4><p>${analysisText.summary}</p></div>`;
                }
                
                if (analysisText.news_analysis) {
                    displayText += `<div class="analysis-section"><h4>新闻分析</h4><p>${analysisText.news_analysis}</p></div>`;
                }
                
                if (analysisText.technical_analysis) {
                    displayText += `<div class="analysis-section"><h4>技术分析</h4><p>${analysisText.technical_analysis}</p></div>`;
                }
                
                if (analysisText.risk_analysis) {
                    displayText += `<div class="analysis-section"><h4>风险分析</h4><p>${analysisText.risk_analysis}</p></div>`;
                }
                
                if (analysisText.recommendation) {
                    displayText += `<div class="analysis-section"><h4>投资建议</h4><p>${analysisText.recommendation}</p></div>`;
                }
                
                displayText += `</div>`;
            } else {
                // 其他对象类型，转换为JSON但格式化显示
                displayText = `<pre class="json-result">${JSON.stringify(analysisText, null, 2)}</pre>`;
            }
        } else {
            // 如果是字符串，直接使用
            displayText = analysisText.replace(/\n/g, '<br>');
        }
        
        htmlContent += `
            <div class="analysis-result">
                <h3>分析结果</h3>
                <div class="analysis-content">${displayText}</div>
            </div>
        `;
    } else if (result.result && (result.result.message || result.result.sentiment)) {
        // 处理其他可能的结果格式
        const message = result.result.message || `情感分析: ${result.result.sentiment}`;
        htmlContent += `
            <div class="analysis-result">
                <h3>分析结果</h3>
                <div class="analysis-content">${message.replace(/\n/g, '<br>')}</div>
            </div>
        `;
    }

    // 如果有相关新闻
    if (result.related_news && result.related_news.length > 0) {
        htmlContent += `
            <div class="related-news">
                <h3>相关新闻</h3>
                <ul class="news-list">
        `;

        result.related_news.forEach(news => {
            htmlContent += `
                <li class="news-item">
                    <div class="news-title">${news.title}</div>
                    <div class="news-meta">
                        <span>来源：${news.source}</span>
                        <span>时间：${news.publish_time}</span>
                        <span class="news-sentiment ${news.sentiment}">${news.sentiment === 'positive' ? '利好' : news.sentiment === 'negative' ? '利空' : '中性'}</span>
                    </div>
                </li>
            `;
        });

        htmlContent += `
                </ul>
            </div>
        `;
    }

    container.innerHTML = htmlContent;
}

// 显示分析结果（创建新模态框）
function showAnalysisResult(stockCode, result) {
    const modal = createAnalysisModal();
    const resultContainer = modal.querySelector('#analysis-result');
    showAnalysisResultInContainer(resultContainer, stockCode, result);
}

// 页面加载完成后初始化
document.addEventListener("DOMContentLoaded", () => {
    console.log("页面开始初始化...");
    
    // 设置默认的 active 按钮
    const stocksButton = document.querySelector('.market-button[data-type="stocks"]');
    if (stocksButton) {
        stocksButton.classList.add('active');
        console.log("已设置股票按钮为active");
    }
    
    // 延迟执行以确保所有资源加载完成
    setTimeout(() => {
        updateMarketContent("stocks");
        initSentimentChart();
        initNewsTicker();
        console.log("所有初始化函数已调用");
    }, 100);

    // 初始化分析按钮事件
    initAnalysisButton();

    // 定时更新行情数据（每30秒）
    const marketUpdateInterval = setInterval(() => {
        const activeButton = document.querySelector('.market-button.active');
        if (activeButton) {
            updateMarketContent(activeButton.getAttribute('data-type'));
        }
    }, 30000);

    // 存储interval ID以便清理
    document.body.dataset.marketUpdateInterval = marketUpdateInterval;
});

// 页面卸载时清理资源
window.addEventListener('beforeunload', () => {
    // 清理图表更新定时器
    const chartDom = document.getElementById('sentiment-chart');
    if (chartDom && chartDom.dataset.updateInterval) {
        clearInterval(parseInt(chartDom.dataset.updateInterval));
    }

    // 清理行情数据更新定时器
    if (document.body.dataset.marketUpdateInterval) {
        clearInterval(parseInt(document.body.dataset.marketUpdateInterval));
    }

    // 清理新闻滚动动画
    const ticker = document.getElementById('news-ticker');
    if (ticker && ticker.dataset.animationId) {
        cancelAnimationFrame(parseInt(ticker.dataset.animationId));
    }

    // 清理ECharts实例
    if (chartDom && chartDom.echartsInstance) {
        chartDom.echartsInstance.dispose();
        chartDom.echartsInstance = null;
    }

    // 清理resize事件监听器
    if (chartDom && chartDom.resizeHandler) {
        window.removeEventListener('resize', chartDom.resizeHandler);
        chartDom.resizeHandler = null;
    }
});

// RAG功能函数
// 知识检索功能
async function performRAGSearch() {
    const searchInput = document.getElementById('rag-search-input');
    const resultsContainer = document.getElementById('rag-search-results');
    const query = searchInput.value.trim();
    
    if (!query) {
        resultsContainer.innerHTML = '<p style="color: #666;">请输入搜索关键词</p>';
        return;
    }
    
    resultsContainer.innerHTML = '<p style="color: #666;">正在检索中...</p>';
    
    try {
        const results = await DataService.searchKnowledge(query, 5, 0.1);
        
        if (results && results.length > 0) {
            let html = '';
            results.forEach((result, index) => {
                html += `
                    <div class="rag-result-item">
                        <div class="rag-result-title">${result.title || '无标题'}</div>
                        <div class="rag-result-meta">
                            类型: ${result.type} | 
                            相似度: ${(result.similarity * 100).toFixed(1)}% | 
                            来源: ${result.source}
                        </div>
                        <div class="rag-result-content">${result.content}</div>
                    </div>
                `;
            });
            resultsContainer.innerHTML = html;
        } else {
            resultsContainer.innerHTML = '<p style="color: #666;">未找到相关知识</p>';
        }
    } catch (error) {
        console.error('RAG检索失败:', error);
        resultsContainer.innerHTML = '<p style="color: #e74c3c;">检索失败，请稍后重试</p>';
    }
}

// 可信度分析功能
async function performRAGAnalyze() {
    const analyzeInput = document.getElementById('rag-analyze-input');
    const resultsContainer = document.getElementById('rag-analyze-results');
    const content = analyzeInput.value.trim();
    
    if (!content) {
        resultsContainer.innerHTML = '<p style="color: #666;">请输入要分析的内容</p>';
        return;
    }
    
    resultsContainer.innerHTML = '<p style="color: #666;">正在分析中...</p>';
    
    try {
        const result = await DataService.analyzeCredibility(content);
        
        if (result) {
            const scoreClass = result.credibility_score >= 0.6 ? 'credibility-high' : 
                              result.credibility_score >= 0.3 ? 'credibility-medium' : 'credibility-low';
            
            let html = `
                <div style="margin-bottom: 1rem;">
                    <strong>可信度评分:</strong>
                    <span class="credibility-score ${scoreClass}">
                        ${(result.credibility_score * 100).toFixed(1)}%
                    </span>
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>评估结果:</strong> ${result.assessment}
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>风险等级:</strong> ${result.risk_level}
                </div>
            `;
            
            if (result.evidence && result.evidence.length > 0) {
                html += '<div><strong>支撑证据:</strong></div>';
                result.evidence.forEach(evidence => {
                    html += `
                        <div class="evidence-item">
                            <div>类型: ${evidence.type} | 相似度: ${(evidence.similarity * 100).toFixed(1)}%</div>
                            <div>标题: ${evidence.title}</div>
                            ${evidence.result ? `<div>结果: ${evidence.result}</div>` : ''}
                        </div>
                    `;
                });
            }
            
            resultsContainer.innerHTML = html;
        } else {
            resultsContainer.innerHTML = '<p style="color: #666;">分析失败</p>';
        }
    } catch (error) {
        console.error('可信度分析失败:', error);
        resultsContainer.innerHTML = '<p style="color: #e74c3c;">分析失败，请稍后重试</p>';
    }
}

// 加载RAG知识库统计信息
async function loadRAGStats() {
    const statsContainer = document.getElementById('rag-stats');
    
    try {
        const stats = await DataService.getRAGStats();
        
        if (stats) {
            let html = `
                <div class="rag-stat-item">
                    <span class="rag-stat-label">知识总量</span>
                    <span class="rag-stat-value">${stats.total || 0} 条</span>
                </div>
            `;
            
            if (stats.by_type) {
                html += '<div style="margin-top: 1rem; font-weight: bold;">按类型分布:</div>';
                for (const [type, count] of Object.entries(stats.by_type)) {
                    html += `
                        <div class="rag-stat-item">
                            <span class="rag-stat-label">${type}</span>
                            <span class="rag-stat-value">${count} 条</span>
                        </div>
                    `;
                }
            }
            
            if (stats.by_source) {
                html += '<div style="margin-top: 1rem; font-weight: bold;">按来源分布:</div>';
                for (const [source, count] of Object.entries(stats.by_source)) {
                    html += `
                        <div class="rag-stat-item">
                            <span class="rag-stat-label">${source}</span>
                            <span class="rag-stat-value">${count} 条</span>
                        </div>
                    `;
                }
            }
            
            if (stats.vector_dimensions > 0) {
                html += `
                    <div class="rag-stat-item">
                        <span class="rag-stat-label">向量维度</span>
                        <span class="rag-stat-value">${stats.vector_dimensions}</span>
                    </div>
                `;
            }
            
            statsContainer.innerHTML = html;
        } else {
            statsContainer.innerHTML = '<p style="color: #666;">无法加载统计信息</p>';
        }
    } catch (error) {
        console.error('加载RAG统计信息失败:', error);
        statsContainer.innerHTML = '<p style="color: #e74c3c;">加载失败，请稍后重试</p>';
    }
}

// 页面加载完成后加载RAG统计信息
document.addEventListener('DOMContentLoaded', function() {
    loadRAGStats();
});

