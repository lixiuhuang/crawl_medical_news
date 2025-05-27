import asyncio
import logging
import requests
from datetime import datetime
from typing import List, Optional
from playwright.async_api import async_playwright
from .base_crawler import BaseCrawler
from models.enums import DataSource
from models.schemas import Article
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class YimaotongCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(DataSource.YIMAOTONG)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        }

    async def crawl(self, keyword: str, limit: int = 20, since_date: Optional[str] = None) -> List[Article]:
        articles = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # 采集前5页数据
                for page_num in range(1, 6):
                    url = f"https://so.medlive.cn/result?type=all&keyword={keyword}&page={page_num}"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    report_lst = soup.find('div', class_='results_cont')
                    print(report_lst)
                    if report_lst:
                        for item in report_lst.find_all('a', class_='results_block'):
                            try:
                                title = item.find('div', class_='results_name').get_text(strip=True) if item.find('div', class_='results_name') else ''
                                content = item.find('div', class_='results_infor').get_text(strip=True) if item.find('div', class_='results_infor') else ''
                                article_url = item['href']
                                # 日期筛选
                                if since_date and publish_date < since_date:
                                    continue
                                    
                                articles.append(Article(
                                    title=title,
                                    url=article_url,
                                    source=self.source,
                                    publish_date='',
                                    content=content
                                ))
                                
                                if len(articles) >= limit:
                                    break
                                    
                            except Exception as e:
                                logger.warning(f"解析医脉通文章失败: {str(e)}")
                        
                if len(articles) >= limit:
                    pass
                
        except Exception as e:
            logger.error(f"医脉通爬取错误: {str(e)}")
            
        return articles[:limit]
