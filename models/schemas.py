import re  # 必须在文件顶部
# models/schemas.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from .enums import DataSource

class Article(BaseModel):
    """文章数据模型"""
    title: str
    url: str
    source: DataSource
    publish_date: str
    content: Optional[str] = None
    summary: Optional[str] = None
    authors: Optional[List[str]] = []
    keywords: Optional[List[str]] = []

class CrawlParameters(BaseModel):
    """爬虫参数模型"""
    keywords: List[str] = Field(..., description="搜索关键词列表")
    sources: List[DataSource] = Field([DataSource.YIMAITONG], description="数据源列表")
    limit: int = Field(10, description="每个关键词的最大结果数")
    since_date: Optional[str] = Field(None, description="起始日期，格式: YYYY-MM-DD")
    
    @validator("since_date")
    def validate_date_format(cls, v):
        if v and not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError("日期格式必须为YYYY-MM-DD")
        return v

class CrawlRequest(BaseModel):
    """MCP工具请求模型"""
    tool: str = Field(..., description="工具名称")
    parameters: Dict[str, Any] = Field(..., description="工具参数")

class CrawlResponse(BaseModel):
    """MCP工具响应模型"""
    result: Dict[str, Any] = Field(default_factory=dict)  # 设置默认值
    error: Optional[str] = None