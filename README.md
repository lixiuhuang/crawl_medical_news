python3 -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows

pip install -r requirements.txt

python main.py

crawl_medical_news/
├── main.py                # FastAPI主程序
├── crawlers/              # 爬虫模块
│   ├── pubmed.py          # PubMed爬虫
│   ├── yimaotong.py       # 医脉通爬虫
│   └── dingxiangyuan.py   # 丁香园爬虫
├── models/                # 数据模型
│   ├── schemas.py         # 数据结构定义
│   └── enums.py           # 枚举类型
├── utils/                 # 工具函数
│   ├── logger.py          # 日志配置
│   └── retry.py           # 重试机制
└── requirements.txt       # 依赖文件

