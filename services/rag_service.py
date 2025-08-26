"""
RAG (Retrieval-Augmented Generation) Service
用于实现检索增强生成功能，结合本地知识库提供更准确的信息
"""

import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path
import hashlib
import pickle
from datetime import datetime

# 用于文本处理
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 设置日志
logger = logging.getLogger(__name__)

class RAGService:
    """RAG检索增强生成服务类"""
    
    def __init__(self, data_path: str = None):
        """
        初始化RAG服务
        
        Args:
            data_path: RAG数据集路径，默认为项目根目录的RAG_datasets
        """
        if data_path is None:
            # 获取项目根目录
            current_dir = Path(__file__).parent.parent
            data_path = current_dir / "RAG_datasets"
        
        self.data_path = Path(data_path)
        self.knowledge_base = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.cache_file = self.data_path / "cache" / "rag_cache.pkl"
        
        # 确保缓存目录存在
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化知识库
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """加载知识库数据"""
        logger.info("开始加载RAG知识库...")
        
        try:
            # 检查缓存是否存在且有效
            if self._load_from_cache():
                logger.info("从缓存加载知识库成功")
                return
            
            # 从原始数据加载
            self._load_raw_data()
            
            # 构建向量索引
            self._build_vector_index()
            
            # 保存到缓存
            self._save_to_cache()
            
            logger.info(f"知识库加载完成，共 {len(self.knowledge_base)} 条记录")
            
        except Exception as e:
            logger.error(f"加载知识库失败: {e}")
            raise
    
    def _load_raw_data(self):
        """加载原始数据文件"""
        self.knowledge_base = []
        
        # 加载中文谣言数据集
        rumors_file = self.data_path / "Chinese_Rumor_Dataset-master" / "rumors_v170613.json"
        if rumors_file.exists():
            logger.info("加载中文谣言数据集...")
            try:
                with open(rumors_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f):
                        if line_num >= 1000:  # 限制加载数量，避免内存问题
                            break
                        try:
                            data = json.loads(line.strip())
                            if data.get('rumorText') and data.get('result'):
                                self.knowledge_base.append({
                                    'id': f"rumor_{line_num}",
                                    'type': 'rumor_detection',
                                    'title': data.get('title', ''),
                                    'content': data.get('rumorText', ''),
                                    'result': data.get('result', ''),
                                    'source': 'Chinese_Rumor_Dataset'
                                })
                        except json.JSONDecodeError:
                            continue
                logger.info(f"加载谣言数据 {len([kb for kb in self.knowledge_base if kb['type'] == 'rumor_detection'])} 条")
            except Exception as e:
                logger.warning(f"加载谣言数据集失败: {e}")
        
        # 加载Fake/True新闻数据集
        fake_file = self.data_path / "archive" / "Fake.csv"
        true_file = self.data_path / "archive" / "True.csv"
        
        if fake_file.exists():
            logger.info("加载虚假新闻数据集...")
            try:
                fake_df = pd.read_csv(fake_file)
                for idx, row in fake_df.head(500).iterrows():  # 限制加载数量
                    if pd.notna(row.get('text')) and pd.notna(row.get('title')):
                        self.knowledge_base.append({
                            'id': f"fake_{idx}",
                            'type': 'news_classification',
                            'title': row.get('title', ''),
                            'content': row.get('text', ''),
                            'label': 'fake',
                            'subject': row.get('subject', ''),
                            'date': row.get('date', ''),
                            'source': 'Fake_News_Dataset'
                        })
                logger.info(f"加载虚假新闻数据 {len([kb for kb in self.knowledge_base if kb.get('label') == 'fake'])} 条")
            except Exception as e:
                logger.warning(f"加载虚假新闻数据集失败: {e}")
        
        if true_file.exists():
            logger.info("加载真实新闻数据集...")
            try:
                true_df = pd.read_csv(true_file)
                for idx, row in true_df.head(500).iterrows():  # 限制加载数量
                    if pd.notna(row.get('text')) and pd.notna(row.get('title')):
                        self.knowledge_base.append({
                            'id': f"true_{idx}",
                            'type': 'news_classification',
                            'title': row.get('title', ''),
                            'content': row.get('text', ''),
                            'label': 'true',
                            'subject': row.get('subject', ''),
                            'date': row.get('date', ''),
                            'source': 'True_News_Dataset'
                        })
                logger.info(f"加载真实新闻数据 {len([kb for kb in self.knowledge_base if kb.get('label') == 'true'])} 条")
            except Exception as e:
                logger.warning(f"加载真实新闻数据集失败: {e}")
    
    def _build_vector_index(self):
        """构建向量索引"""
        if not self.knowledge_base:
            logger.warning("知识库为空，无法构建向量索引")
            return
        
        logger.info("构建向量索引...")
        
        # 准备文本数据
        texts = []
        for kb_item in self.knowledge_base:
            # 组合标题和内容作为检索文本
            text = f"{kb_item.get('title', '')} {kb_item.get('content', '')}"
            # 对中文文本进行分词
            if any('\u4e00' <= char <= '\u9fff' for char in text):
                text = ' '.join(jieba.cut(text))
            texts.append(text)
        
        # 使用TF-IDF向量化
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=None,  # 中英文混合，不使用停用词
            lowercase=True,
            ngram_range=(1, 2)
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        logger.info(f"向量索引构建完成，特征维度: {self.tfidf_matrix.shape}")
    
    def _get_cache_hash(self) -> str:
        """获取数据文件的哈希值用于缓存验证"""
        hash_obj = hashlib.md5()
        
        # 检查主要数据文件的修改时间
        files_to_check = [
            self.data_path / "Chinese_Rumor_Dataset-master" / "rumors_v170613.json",
            self.data_path / "archive" / "Fake.csv",
            self.data_path / "archive" / "True.csv"
        ]
        
        for file_path in files_to_check:
            if file_path.exists():
                stat = file_path.stat()
                hash_obj.update(f"{file_path}_{stat.st_mtime}_{stat.st_size}".encode())
        
        return hash_obj.hexdigest()
    
    def _load_from_cache(self) -> bool:
        """从缓存加载数据"""
        if not self.cache_file.exists():
            return False
        
        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查缓存版本
            current_hash = self._get_cache_hash()
            if cache_data.get('hash') != current_hash:
                logger.info("数据文件已更新，缓存无效")
                return False
            
            # 恢复数据
            self.knowledge_base = cache_data['knowledge_base']
            self.vectorizer = cache_data['vectorizer']
            self.tfidf_matrix = cache_data['tfidf_matrix']
            
            return True
        
        except Exception as e:
            logger.warning(f"加载缓存失败: {e}")
            return False
    
    def _save_to_cache(self):
        """保存数据到缓存"""
        try:
            cache_data = {
                'hash': self._get_cache_hash(),
                'knowledge_base': self.knowledge_base,
                'vectorizer': self.vectorizer,
                'tfidf_matrix': self.tfidf_matrix,
                'created_at': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info("数据已保存到缓存")
        
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        检索相关知识
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            threshold: 相似度阈值
            
        Returns:
            检索结果列表
        """
        if not self.knowledge_base or self.tfidf_matrix is None:
            logger.warning("知识库未初始化")
            return []
        
        try:
            # 对查询文本进行相同的处理
            query_text = query
            if any('\u4e00' <= char <= '\u9fff' for char in query_text):
                query_text = ' '.join(jieba.cut(query_text))
            
            # 向量化查询
            query_vector = self.vectorizer.transform([query_text])
            
            # 计算相似度
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # 获取最相似的结果
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                similarity = similarities[idx]
                if similarity >= threshold:
                    result = self.knowledge_base[idx].copy()
                    result['similarity'] = float(similarity)
                    results.append(result)
            
            logger.info(f"检索查询: '{query}' 返回 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []
    
    def get_knowledge_by_type(self, knowledge_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        根据类型获取知识
        
        Args:
            knowledge_type: 知识类型
            limit: 返回数量限制
            
        Returns:
            知识列表
        """
        try:
            results = [kb for kb in self.knowledge_base if kb.get('type') == knowledge_type]
            return results[:limit]
        except Exception as e:
            logger.error(f"获取知识失败: {e}")
            return []
    
    def analyze_content_credibility(self, content: str) -> Dict[str, Any]:
        """
        分析内容可信度
        
        Args:
            content: 待分析内容
            
        Returns:
            分析结果
        """
        try:
            # 检索相关的谣言和新闻数据
            search_results = self.search(content, top_k=10, threshold=0.3)
            
            # 分析相关性和可信度
            credibility_score = 0.5  # 默认中性
            fake_count = 0
            true_count = 0
            rumor_count = 0
            
            evidence = []
            
            for result in search_results:
                similarity = result.get('similarity', 0)
                
                if result.get('type') == 'news_classification':
                    if result.get('label') == 'fake':
                        fake_count += 1
                        credibility_score -= similarity * 0.3
                        evidence.append({
                            'type': 'fake_news',
                            'similarity': similarity,
                            'title': result.get('title', ''),
                            'source': result.get('source', '')
                        })
                    elif result.get('label') == 'true':
                        true_count += 1
                        credibility_score += similarity * 0.2
                        evidence.append({
                            'type': 'true_news',
                            'similarity': similarity,
                            'title': result.get('title', ''),
                            'source': result.get('source', '')
                        })
                
                elif result.get('type') == 'rumor_detection':
                    rumor_count += 1
                    credibility_score -= similarity * 0.4
                    evidence.append({
                        'type': 'rumor',
                        'similarity': similarity,
                        'title': result.get('title', ''),
                        'result': result.get('result', '')[:100] + '...' if len(result.get('result', '')) > 100 else result.get('result', ''),
                        'source': result.get('source', '')
                    })
            
            # 标准化评分
            credibility_score = max(0, min(1, credibility_score))
            
            # 生成评估结果
            if credibility_score < 0.3:
                assessment = "可信度较低，建议谨慎对待"
                risk_level = "高"
            elif credibility_score < 0.6:
                assessment = "可信度一般，需要进一步验证"
                risk_level = "中"
            else:
                assessment = "可信度较高"
                risk_level = "低"
            
            return {
                'credibility_score': credibility_score,
                'assessment': assessment,
                'risk_level': risk_level,
                'evidence_summary': {
                    'fake_news_count': fake_count,
                    'true_news_count': true_count,
                    'rumor_count': rumor_count,
                    'total_evidence': len(evidence)
                },
                'evidence': evidence[:5],  # 只返回前5条证据
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"可信度分析失败: {e}")
            return {
                'credibility_score': 0.5,
                'assessment': "分析失败，无法评估可信度",
                'risk_level': "未知",
                'evidence_summary': {},
                'evidence': [],
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        if not self.knowledge_base:
            return {'total': 0}
        
        stats = {
            'total': len(self.knowledge_base),
            'by_type': {},
            'by_source': {},
            'vector_dimensions': self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else 0
        }
        
        for kb_item in self.knowledge_base:
            # 按类型统计
            kb_type = kb_item.get('type', 'unknown')
            stats['by_type'][kb_type] = stats['by_type'].get(kb_type, 0) + 1
            
            # 按来源统计
            source = kb_item.get('source', 'unknown')
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
        
        return stats


# 全局RAG服务实例
_rag_service = None

def get_rag_service() -> RAGService:
    """获取RAG服务实例（单例模式）"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


# 便捷函数
def search_knowledge(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """检索知识的便捷函数"""
    service = get_rag_service()
    return service.search(query, top_k)


def analyze_credibility(content: str) -> Dict[str, Any]:
    """分析内容可信度的便捷函数"""
    service = get_rag_service()
    return service.analyze_content_credibility(content)