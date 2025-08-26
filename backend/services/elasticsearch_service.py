from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import json

load_dotenv()

class ElasticSearchService:
    """ElasticSearch服务"""
    
    def __init__(self):
        self.es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.index_name = os.getenv("ELASTICSEARCH_INDEX", "financial_news")
        self.client = None
    
    async def connect(self):
        """连接ElasticSearch"""
        try:
            self.client = AsyncElasticsearch([self.es_url])
            # 检查连接
            if await self.client.ping():
                print("成功连接到ElasticSearch")
                # 创建索引（如果不存在）
                await self._create_index()
                return True
            else:
                print("无法连接到ElasticSearch")
                return False
        except Exception as e:
            print(f"连接ElasticSearch时出错: {e}")
            return False
    
    async def close(self):
        """关闭连接"""
        if self.client:
            await self.client.close()
    
    async def _create_index(self):
        """创建索引"""
        if not await self.client.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_smart"
                        },
                        "content": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_smart"
                        },
                        "source": {"type": "keyword"},
                        "publish_time": {"type": "date"},
                        "news_type": {"type": "keyword"},
                        "stock_codes": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "url": {"type": "keyword"},
                        "sentiment": {"type": "keyword"},
                        "impact_analysis": {"type": "text"},
                        "created_at": {"type": "date"}
                    }
                }
            }
            
            await self.client.indices.create(index=self.index_name, body=mapping)
            print(f"创建索引 {self.index_name} 成功")
    
    async def index_news(self, news_data: Dict[str, Any]):
        """索引单条新闻"""
        try:
            doc = {
                **news_data,
                "created_at": news_data.get("created_at", datetime.now())
            }
            
            await self.client.index(
                index=self.index_name,
                id=news_data["id"],
                body=doc
            )
            return True
        except Exception as e:
            print(f"索引新闻时出错: {e}")
            return False
    
    async def bulk_index_news(self, news_list: List[Dict[str, Any]]):
        """批量索引新闻"""
        if not self.client:
            return False
        
        def generate_actions():
            for news in news_list:
                yield {
                    "_index": self.index_name,
                    "_id": news["id"],
                    "_source": {
                        **news,
                        "created_at": news.get("created_at", datetime.now())
                    }
                }
        
        try:
            success_count, errors = await async_bulk(
                self.client,
                generate_actions()
            )
            
            if errors:
                print(f"批量索引时出现错误: {errors}")
            
            print(f"成功索引 {success_count} 条新闻")
            return True
        except Exception as e:
            print(f"批量索引新闻时出错: {e}")
            return False
    
    async def search_news(
        self,
        query: str,
        stock_code: Optional[str] = None,
        news_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        size: int = 20,
        from_: int = 0
    ) -> List[Dict[str, Any]]:
        """搜索新闻"""
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^3", "content"],
                                "type": "best_fields"
                            }
                        }
                    ],
                    "filter": []
                }
            },
            "sort": [
                {"publish_time": {"order": "desc"}}
            ],
            "size": size,
            "from": from_
        }
        
        # 添加过滤条件
        if stock_code:
            search_body["query"]["bool"]["filter"].append(
                {"term": {"stock_codes": stock_code}}
            )
        
        if news_type:
            search_body["query"]["bool"]["filter"].append(
                {"term": {"news_type": news_type}}
            )
        
        if start_date or end_date:
            range_filter = {"range": {"publish_time": {}}}
            if start_date:
                range_filter["range"]["publish_time"]["gte"] = start_date.isoformat()
            if end_date:
                range_filter["range"]["publish_time"]["lte"] = end_date.isoformat()
            search_body["query"]["bool"]["filter"].append(range_filter)
        
        try:
            response = await self.client.search(index=self.index_name, body=search_body)
            
            hits = response["hits"]["hits"]
            results = []
            
            for hit in hits:
                source = hit["_source"]
                results.append({
                    "id": source["id"],
                    "title": source["title"],
                    "content": source["content"],
                    "source": source["source"],
                    "publish_time": source["publish_time"],
                    "news_type": source["news_type"],
                    "stock_codes": source.get("stock_codes", []),
                    "tags": source.get("tags", []),
                    "url": source.get("url"),
                    "sentiment": source.get("sentiment"),
                    "impact_analysis": source.get("impact_analysis"),
                    "score": hit["_score"]
                })
            
            return results
        except Exception as e:
            print(f"搜索新闻时出错: {e}")
            return []
    
    async def get_similar_news(
        self,
        news_id: str,
        size: int = 5
    ) -> List[Dict[str, Any]]:
        """获取相似新闻"""
        try:
            # 首先获取原新闻
            original_news = await self.client.get(index=self.index_name, id=news_id)
            original_content = original_news["_source"]["content"]
            
            # 使用more_like_this查询
            search_body = {
                "query": {
                    "more_like_this": {
                        "fields": ["title", "content"],
                        "like": original_content,
                        "min_term_freq": 1,
                        "min_doc_freq": 1
                    }
                },
                "size": size
            }
            
            response = await self.client.search(index=self.index_name, body=search_body)
            
            hits = response["hits"]["hits"]
            results = []
            
            for hit in hits:
                if hit["_id"] != news_id:  # 排除原新闻
                    source = hit["_source"]
                    results.append({
                        "id": source["id"],
                        "title": source["title"],
                        "content": source["content"][:200] + "...",
                        "source": source["source"],
                        "publish_time": source["publish_time"],
                        "score": hit["_score"]
                    })
            
            return results
        except Exception as e:
            print(f"获取相似新闻时出错: {e}")
            return []
    
    async def delete_news(self, news_id: str):
        """删除新闻"""
        try:
            await self.client.delete(index=self.index_name, id=news_id)
            return True
        except Exception as e:
            print(f"删除新闻时出错: {e}")
            return False
    
    async def get_news_statistics(self) -> Dict[str, Any]:
        """获取新闻统计信息"""
        try:
            # 总数统计
            total_count = await self.client.count(index=self.index_name)
            
            # 情感分布
            sentiment_agg = {
                "size": 0,
                "aggs": {
                    "sentiment_distribution": {
                        "terms": {
                            "field": "sentiment",
                            "size": 10
                        }
                    }
                }
            }
            
            sentiment_response = await self.client.search(index=self.index_name, body=sentiment_agg)
            
            # 新闻类型分布
            type_agg = {
                "size": 0,
                "aggs": {
                    "type_distribution": {
                        "terms": {
                            "field": "news_type",
                            "size": 10
                        }
                    }
                }
            }
            
            type_response = await self.client.search(index=self.index_name, body=type_agg)
            
            # 时间分布（最近7天）
            time_agg = {
                "size": 0,
                "query": {
                    "range": {
                        "publish_time": {
                            "gte": "now-7d/d"
                        }
                    }
                },
                "aggs": {
                    "time_distribution": {
                        "date_histogram": {
                            "field": "publish_time",
                            "calendar_interval": "1d"
                        }
                    }
                }
            }
            
            time_response = await self.client.search(index=self.index_name, body=time_agg)
            
            return {
                "total_count": total_count["count"],
                "sentiment_distribution": sentiment_response["aggregations"]["sentiment_distribution"]["buckets"],
                "type_distribution": type_response["aggregations"]["type_distribution"]["buckets"],
                "time_distribution": time_response["aggregations"]["time_distribution"]["buckets"]
            }
        except Exception as e:
            print(f"获取统计信息时出错: {e}")
            return {}