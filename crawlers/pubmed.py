# import re  # 添加这行
# import asyncio
# import aiohttp
# import requests
# from bs4 import BeautifulSoup
# import random
# import logging
# from typing import List, Optional
# from .base_crawler import BaseCrawler
# from models.enums import DataSource
# from models.schemas import Article
# logger = logging.getLogger(__name__)

# # PubMed爬虫
# class PubMedCrawler(BaseCrawler):
#     def __init__(self):
#         super().__init__(DataSource.PUBMED)
    
#     async def crawl(self, keyword: str, limit: int = 10, since_date: Optional[str] = None) -> List[Article]:
#         articles = []
#         try:
#             # 构建查询URL
#             base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
#             params = {
#                 'db': 'pubmed',
#                 'term': keyword,
#                 'retmax': limit,
#                 'retmode': 'json'
#             }
            
#             # 添加日期筛选条件
#             if since_date:
#                 params['mindate'] = since_date
#                 params['datetype'] = 'pdat'
            
#             # 获取文献ID列表
#             response = self.session.get(base_url, params=params, headers=self.headers)
#             response.raise_for_status()
#             data = response.json()
            
#             if 'esearchresult' not in data or 'idlist' not in data['esearchresult']:
#                 return articles
                
#             id_list = data['esearchresult']['idlist']
#             if not id_list:
#                 return articles
                
#             # 异步获取文献详细信息
#             async with aiohttp.ClientSession(headers=self.headers) as session:
#                 tasks = []
#                 for article_id in id_list:
#                     summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={article_id}&retmode=json"
#                     tasks.append(self._fetch_article_details(session, article_id, summary_url))
                
#                 articles = await asyncio.gather(*tasks)
                
#             # 过滤空结果
#             articles = [a for a in articles if a]
            
#         except Exception as e:
#             logger.error(f"PubMed爬取错误: {str(e)}")
            
#         return articles