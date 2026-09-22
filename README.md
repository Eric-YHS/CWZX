# 财闻智析 - 智能金融决策平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://img.shields.io/github/actions/workflow/status/Eric-YHS/CWZX/ci.yml?branch=master&logo=githubactions&logoColor=white&label=CI)](https://github.com/Eric-YHS/CWZX/actions/workflows/ci.yml)

财闻智析是一个集成了实时股票数据、智能分析、AI助手和RAG知识库的综合性金融信息平台。通过多源数据整合和AI技术，为用户提供全面、准确、及时的金融信息服务。

> **📋 完整技术文档请查看：[财闻智析-完整项目文档.md](./财闻智析-完整项目文档.md)**

## 🚀 主要功能

### 1. 实时股票行情
- **多源数据集成**：整合腾讯股票API、新浪财经、东方财富等多个数据源
- **实时数据更新**：提供股票实时价格、涨跌幅、成交量等关键指标
- **市场指数**：涵盖上证指数、深证成指、创业板指、沪深300等主要指数
- **基金数据**：支持各类基金产品信息查询
- **智能搜索**：快速搜索股票代码、公司名称

### 2. 市场情绪分析
- **新闻影响分析**：结合历史新闻数据，分析新闻事件对股票市场的影响
- **情感分析**：对新闻文本进行情感倾向分析（积极/消极/中性）
- **趋势预测**：基于历史数据和AI算法预测股票未来走势
- **AI驱动**：使用智谱AI GLM-4.5模型进行深度分析

### 3. AI智能助手
- **多模型支持**：集成智谱AI、OpenAI、通义千问、文心一言、讯飞星火等多个AI服务
- **金融专业**：专业的金融投资顾问，擅长股票、基金、投资理财等领域
- **上下文记忆**：支持多轮对话，记住用户的投资偏好和历史问题
- **智能推荐**：根据用户需求提供个性化的投资建议

### 4. 全文搜索功能
- **ElasticSearch集成**：基于ElasticSearch的高性能全文搜索引擎
- **中文分词**：集成IK分词器，支持精准的中文文本搜索
- **多维度筛选**：支持按时间、类型、情感标签等多维度筛选
- **相似新闻推荐**：基于内容相似度的智能推荐系统

### 5. 今日重大新闻
- **实时新闻**：聚合最新的财经新闻和市场动态
- **分类展示**：股票新闻、财务报告、市场分析、政策新闻等分类
- **情感标记**：每条新闻都带有AI分析的情感标签
- **股票关联**：新闻与相关股票的智能关联

### 6. RAG知识库系统
- **可信度验证**：集成专业数据集，验证信息的真实性和可信度
- **智能检索**：基于TF-IDF向量化技术的知识检索
- **谣言识别**：利用中文谣言数据集识别和过滤虚假信息
- **缓存优化**：高效的缓存机制，确保快速响应

## 📊 RAG知识库详细介绍

### 数据集构成

#### 1. 中文谣言数据集 (Chinese_Rumor_Dataset)
- **数据来源**：新浪微博不实信息举报平台
- **数据规模**：31,669条谣言记录（2009年9月-2017年6月）
- **数据字段**：
  - `rumorCode`: 谣言唯一编码
  - `title`: 举报标题
  - `rumorText`: 谣言内容
  - `result`: 审查结果
  - `publishTime`: 发布时间
  - `visitTimes`: 访问次数

#### 2. CED数据集 (CED_Dataset)
- **数据特点**：包含原文、转发和评论的完整数据
- **数据规模**：1,538条谣言 + 1,849条非谣言
- **数据结构**：
  - `original-microblog`: 微博原文
  - `rumor-repost`: 谣言转发/评论
  - `non-rumor-repost`: 非谣言转发/评论

#### 3. Fake/True新闻数据集 (archive)
- **Fake.csv**: 假新闻数据集
- **True.csv**: 真实新闻数据集
- **应用场景**：新闻真实性验证训练和测试

### 技术实现

```python
# 核心技术栈
- 向量化算法：TF-IDF
- 中文分词：jieba
- 相似度计算：余弦相似度
- 缓存机制：pickle序列化
```

### 功能特性

1. **内容可信度分析**
   - 输入文本后，系统会在知识库中检索相似内容
   - 计算可信度分数，提供真实性评估
   - 标注可能的风险和注意事项

2. **智能知识检索**
   - 支持关键词搜索
   - 按内容类型分类检索
   - 提供相关度排序

3. **实时缓存更新**
   - 自动缓存常用查询结果
   - 定期更新知识库内容
   - 优化查询性能

## 🛠️ 技术架构

### 后端技术栈
- **Web框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy
- **搜索引擎**: ElasticSearch
- **AI服务**: 智谱AI GLM-4.5
- **数据源**: 
  - 腾讯股票API
  - 新浪财经API
  - 东方财富API
  - BaoStock

### 前端技术栈
- **框架**: Vue.js 3
- **UI组件**: Element Plus
- **图表库**: ECharts
- **HTTP客户端**: Axios

### 部署架构
```
前端 (Vue.js) ↔ 后端API (FastAPI) ↔ 数据层 (SQLite/ElasticSearch)
                     ↕
                   AI服务 (智谱AI)
                     ↕
                   外部API (股票/新闻数据源)
```

## 📦 安装与使用

### 环境要求
- Python 3.8+
- Node.js 16+
- ElasticSearch 7.x+

### 快速启动

1. **克隆项目**
```bash
git clone https://github.com/yourusername/CWZX.git
cd CWZX
```

2. **安装依赖**
```bash
# 后端依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 前端依赖
cd frontend
npm install
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置API密钥等信息
```

4. **启动服务**
```bash
# 一键启动
python start_app.py

# 或分别启动
python backend/complete_start.py
cd frontend && npm run dev
```

5. **访问应用**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 🔧 配置说明

### AI服务配置
支持多种AI服务，需在.env文件中配置相应的API密钥：

```env
# 智谱AI（推荐）
ZHIPUAI_API_KEY=your_zhipuai_key

# OpenAI
OPENAI_API_KEY=your_openai_key

# 通义千问
DASHSCOPE_API_KEY=your_qwen_key

# 文心一言
BAIDU_API_KEY=your_baidu_key
BAIDU_SECRET_KEY=your_baidu_secret

# 讯飞星火
XUNFEI_APP_ID=your_xunfei_app_id
XUNFEI_API_KEY=your_xunfei_key
XUNFEI_API_SECRET=your_xunfei_secret
```

### 数据源配置
系统会自动使用免费的公开API，无需额外配置。如需更高频率的数据更新，可配置相应的付费API。

## 📖 API文档

启动服务后，访问 http://localhost:8000/docs 查看完整的API文档。

### 主要API端点

- `GET /api/v1/stocks/{code}` - 获取股票实时数据
- `GET /api/v1/stocks/search` - 搜索股票
- `GET /api/v1/market/overview` - 获取市场概览
- `GET /api/v1/news/latest` - 获取最新新闻
- `POST /api/v1/analysis/sentiment` - 情感分析
- `POST /api/v1/chat` - AI对话
- `POST /api/v1/rag/search` - RAG知识检索


## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [智谱AI](https://open.bigmodel.cn/) - 提供强大的AI模型支持
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Web框架
- [ElasticSearch](https://www.elastic.co/) - 强大的搜索引擎
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架

---

**免责声明**: 本平台提供的信息仅供参考，不构成投资建议。投资有风险，决策需谨慎。

> **📋 完整技术文档请查看：[财闻智析-完整项目文档.md](./财闻智析-完整项目文档.md)**
