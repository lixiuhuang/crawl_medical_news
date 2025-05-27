import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from .base_crawler import BaseCrawler
from models.enums import DataSource
from models.schemas import Article
from typing import List, Optional
logger = logging.getLogger(__name__)

class DingxiangyuanCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(DataSource.DINGXIANGYUAN)
    
    async def crawl(self, keyword: str, limit: int = 20, since_date: Optional[str] = None) -> List[Article]:
        articles = []
        try:
            # 构建搜索URL
            encoded_keyword = aiohttp.helpers.quote(keyword)
            #url = f"https://search.dxy.cn/api/search/home/list?age=&orderType=&searchType=&autoSpellCorrect=true&pageNum=1&keyword={encoded_keyword}&pageSize=1"
            url = f"https://search.dxy.cn/api/search/home/list?age=&orderType=&searchType=&autoSpellCorrect=true&keyword={encoded_keyword}&pageNum=1&pageSize=40"
            
            # 发送HTTP请求获取JSON数据
            if hasattr(self.session, 'get') and not asyncio.iscoroutinefunction(self.session.get):
                # 同步requests.Session
                response = self.session.get(url, headers=self.headers)
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    logger.error(f"非JSON响应: {response.text[:200]}")
                    raise ValueError(f"无效的响应类型1: {content_type}")
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {response.text[:200]}")
                    raise ValueError("API返回无效JSON") from e
            else:
                # 异步aiohttp.ClientSession
                async with self.session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' not in content_type:
                        text = await response.text()
                        logger.error(f"非JSON响应: {text[:200]}")
                        raise ValueError(f"无效的响应类型2: {content_type}")
                    try:
                        data = await response.json()
                    except json.JSONDecodeError as e:
                        text = await response.text()
                        logger.error(f"JSON解析失败: {text[:200]}")
                        raise ValueError("API返回无效JSON") from e
            
            logger.debug(f"API响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if not data or not isinstance(data, dict):
                raise ValueError("无效的API响应格式")
            
            # 获取结果列表并过滤数据
            results = data.get('data', {}).get('result', [])
            results = [item for item in results if item and( item.get('source') == 'clinicalDecision' or item.get('source') == 'post')]
            if not results:
                logger.warning(f"未找到关键词'{keyword}'的搜索结果")
                return articles
            for item in results[:limit]:
                try:
                    # 提取文章信息
                    title = item.get('title', '').strip()
                    source_type = item.get('source', '')
                    article_id = item.get('id', '')
                    
                    # 根据source类型生成不同链接
                    if source_type == 'clinicalDecision':  #临床
                        article_url = f"https://drugs.dxy.cn/pc/clinicalDecision/{article_id}?ky={encoded_keyword}"
                    elif source_type == 'post':
                        article_url = f"https://www.dxy.cn/bbs/newweb/pc/post/{article_id}?keywords={encoded_keyword}"
                    elif source_type == 'drug':
                        article_url = f"https://drugs.dxy.cn/drug/{article_id}?ky={encoded_keyword}"
                    elif source_type == 'guide':
                        article_url = f"https://guide.dxy.cn/article/{article_id}?keywords={encoded_keyword}"
                    else:
                        article_url = f"https://www.dxy.cn/bbs/newweb/pc/post/{article_id}?keywords={encoded_keyword}"
                    
                    # 提取发布日期
                    publish_date = item.get('publishDate')
                    if not publish_date:
                        create_time = item.get('createtime')
                        if create_time:
                            # 处理Unix时间戳(可能是毫秒或秒)
                            try:
                                timestamp = int(create_time)
                                # 先尝试毫秒级
                                try:
                                    publish_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                                except ValueError:
                                    # 再尝试秒级
                                    publish_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                            except Exception as e:
                                logger.warning(f"时间戳转换失败: {str(e)}")
                                publish_date = datetime.now().strftime('%Y-%m-%d')
                        else:
                            publish_date = datetime.now().strftime('%Y-%m-%d')
                    
                    # 提取摘要 (根据实际字段调整)
                    content = item.get('content', '')
                    # 如果有日期筛选条件，检查是否符合
                    if since_date and publish_date < since_date:
                        continue
                    # 构建文章对象
                    articles.append(Article(
                        title=title,
                        url=article_url,
                        source=self.source,
                        publish_date=self._parse_date(publish_date),
                        content=content
                    ))
                    
                except Exception as e:
                    logger.warning(f"解析丁香园文章失败: {str(e)}")
            
        except Exception as e:
            logger.error(f"丁香园爬取错误: {str(e)}")
        return articles
