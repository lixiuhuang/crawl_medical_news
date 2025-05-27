from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
import asyncio
import logging
from datetime import datetime
# from crawlers import PubMedCrawler, YimaotongCrawler, DingxiangyuanCrawler
from crawlers import  YimaotongCrawler, DingxiangyuanCrawler
from models.schemas import CrawlRequest, CrawlParameters, CrawlResponse, Article
from models.enums import DataSource

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("medical_crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Medical Data Crawler MCP Server",
    description="一个基于MCP协议的医疗数据资讯爬虫工具，支持多数据源采集",
    version="1.0.0"
)

# MCP工具执行器
class MedicalCrawlerExecutor:
    @staticmethod
    async def crawl_medical_news(keywords: List[str], sources: List[DataSource], limit: int = 20, since_date: Optional[str] = None) -> Dict[str, Any]:
        """执行医疗资讯爬虫任务"""
        # 初始化爬虫
        crawlers = {
            # DataSource.PUBMED: PubMedCrawler(),
            DataSource.YIMAOTONG: YimaotongCrawler(),
            DataSource.DINGXIANGYUAN: DingxiangyuanCrawler()
        }
        
        results = {}
        total_articles = 0
        
        # 为每个关键词和数据源组合创建任务
        tasks = []
        for keyword in keywords:
            for source in sources:
                if source in crawlers:
                    tasks.append(crawlers[source].crawl(keyword, limit, since_date))
        
        # 并行执行所有任务
        if tasks:
            all_results = await asyncio.gather(*tasks)
            
            # 整理结果
            for i, keyword in enumerate(keywords):
                for j, source in enumerate(sources):
                    if source in crawlers:
                        source_key = f"{keyword}_{source}"
                        results[source_key] = all_results[i * len(sources) + j]
                        total_articles += len(results[source_key])
        
        #数量 结果 执行时间
        return {
            'total_articles': total_articles,
            'results': results,
            'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
        }

# MCP工具端点
@app.post("/mcp/tool")
async def execute_tool(request: Request, crawl_request: CrawlRequest) -> CrawlResponse:
    try:
        tool_name = crawl_request.tool.lower()
        params = crawl_request.parameters
        
        if tool_name == "crawl_medical_news":
            crawl_params = CrawlParameters(**params)
            result = await MedicalCrawlerExecutor.crawl_medical_news(
                keywords=crawl_params.keywords,
                sources=crawl_params.sources,
                # limit=crawl_params.limit,
                # since_date=crawl_params.since_date
            )
            return CrawlResponse(result=result)
        else:
            # 提供默认的空结果
            return CrawlResponse(
                result={"error": f"工具 {tool_name} 不存在"},
                error=f"工具 {tool_name} 不存在"
            )
            
    except Exception as e:
        logger.error(f"执行工具失败: {str(e)}")
        # 提供默认的空结果
        return CrawlResponse(
            result={"error": str(e)},
            error=str(e)
        )

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)