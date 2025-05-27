# models/enums.py
from enum import Enum

class DataSource(str, Enum):
    """数据源枚举"""
    YIMAITONG = "yimaitong"
    DINGXIANGYUAN = "dingxiangyuan"

class CrawlType(str, Enum):
    """爬取类型枚举"""
    NEWS = "news"
    LITERATURE = "literature"
    GUIDELINE = "guideline"