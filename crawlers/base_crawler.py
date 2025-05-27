import re
import requests
from datetime import datetime
import logging
from models.enums import DataSource  
from models.schemas import Article  
from typing import List, Optional
logger = logging.getLogger(__name__)

class BaseCrawler:
    @classmethod
    def run(cls, source: DataSource):
        """MCP工具调用的入口方法"""
        instance = cls(source)
        return instance.crawl()
        
    def __init__(self, source: DataSource):
        self.source = source
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
    
    async def crawl(self, keyword: str, limit: int = 20, since_date: Optional[str] = None) -> List[Article]:
        raise NotImplementedError("子类必须实现此方法")
    
    def _parse_date(self, date_str: str) -> str:
        """将不同格式的日期转换为标准格式"""
        try:
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%B %d, %Y', '%d %B %Y']:
                try:
                    dt = datetime.strptime(date_str.strip(), fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            # 使用正则表达式提取年份（处理不标准的日期格式）
            year_match = re.search(r'\d{4}', date_str)  # 依赖 re 模块
            return year_match.group() if year_match else date_str
        except Exception as e:
            logger.warning(f"日期解析失败: {date_str}, 错误: {str(e)}")
            return date_str
