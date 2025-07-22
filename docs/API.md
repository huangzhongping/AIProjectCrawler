# API 文档

## 核心模块 API

### 爬虫模块 (Crawlers)

#### BaseCrawler

基础爬虫抽象类，提供通用的爬虫功能。

```python
from crawlers.base_crawler import BaseCrawler

class BaseCrawler:
    def __init__(self, config: Dict[str, Any])
    async def fetch_page(self, url: str, **kwargs) -> Optional[str]
    def parse_html(self, html: str) -> BeautifulSoup
    def standardize_project_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]
    async def crawl(self) -> List[Dict[str, Any]]  # 抽象方法
```

**参数**：
- `config`: 配置字典

**方法**：
- `fetch_page()`: 获取网页内容
- `parse_html()`: 解析 HTML
- `standardize_project_data()`: 标准化项目数据
- `crawl()`: 执行爬取（需子类实现）

#### GitHubCrawler

GitHub Trending 爬虫。

```python
from crawlers.github_crawler import GitHubCrawler

crawler = GitHubCrawler(config)
projects = await crawler.crawl()
```

**配置参数**：
```yaml
crawler:
  github:
    base_url: "https://github.com/trending"
    languages: ["python", "javascript"]
    time_ranges: ["daily", "weekly"]
    max_pages: 3
```

**返回数据格式**：
```python
{
    'name': 'project-name',
    'description': 'Project description',
    'url': 'https://github.com/user/project',
    'stars': 1234,
    'forks': 567,
    'language': 'Python',
    'author': 'username',
    'source': 'github',
    'language_filter': 'python',
    'time_range': 'daily',
    'crawled_at': '2023-12-01T12:00:00'
}
```

#### ProductHuntCrawler

Product Hunt 爬虫。

```python
from crawlers.producthunt_crawler import ProductHuntCrawler

crawler = ProductHuntCrawler(config)
projects = await crawler.crawl()
```

**配置参数**：
```yaml
crawler:
  producthunt:
    base_url: "https://www.producthunt.com"
    categories: ["artificial-intelligence"]
    max_items: 50
```

### AI 分析模块 (AI Analysis)

#### AIProjectClassifier

AI 项目分类器。

```python
from ai_analysis.classifier import AIProjectClassifier

classifier = AIProjectClassifier(config)
result = await classifier.classify(project)
```

**方法**：
- `classify(project)`: 分类单个项目
- `batch_classify(projects)`: 批量分类项目

**输入格式**：
```python
project = {
    'name': 'project-name',
    'description': 'Project description',
    'tags': ['ai', 'ml'],
    'language': 'Python'
}
```

**输出格式**：
```python
{
    'is_ai_related': True,
    'confidence_score': 0.9,
    'reasoning': '判断理由',
    'ai_categories': ['Machine Learning', 'NLP'],
    'tech_stack': ['Python', 'TensorFlow']
}
```

#### KeywordExtractor

关键词提取器。

```python
from ai_analysis.keyword_extractor import KeywordExtractor

extractor = KeywordExtractor(config)
keywords = await extractor.extract(project)
```

**输出格式**：
```python
{
    'keywords': ['ai', 'machine learning', 'python'],
    'categories': {
        '技术栈': ['python', 'tensorflow'],
        '应用领域': ['nlp', 'computer vision'],
        '趋势词汇': ['transformer', 'llm']
    },
    'extraction_method': 'ai'  # 'ai', 'rules', 'merged'
}
```

#### ProjectSummarizer

项目总结生成器。

```python
from ai_analysis.summarizer import ProjectSummarizer

summarizer = ProjectSummarizer(config)
summary = await summarizer.summarize(project)
```

**输出格式**：
```python
{
    'summary': '项目总结文本',
    'highlights': ['亮点1', '亮点2', '亮点3'],
    'use_cases': ['应用场景1', '应用场景2'],
    'generation_method': 'ai'  # 'ai', 'basic'
}
```

### 数据处理模块 (Utils)

#### DataCleaner

数据清洗器。

```python
from utils.data_cleaner import DataCleaner

cleaner = DataCleaner(config)
cleaned_data = cleaner.clean_and_deduplicate(raw_data)
```

**方法**：
- `clean_and_deduplicate(data)`: 清洗和去重数据
- `clean_single_item(item)`: 清洗单个数据项
- `is_valid_item(item)`: 验证数据项有效性
- `deduplicate(data)`: 去重数据

#### DataStorage

数据存储管理器。

```python
from utils.storage import DataStorage

storage = DataStorage(config)
```

**方法**：
```python
# 保存数据
storage.save_daily_data(projects, '2023-12-01')
storage.save_raw_data(data, 'github', '20231201_120000')

# 加载数据
projects = storage.get_projects_by_date('2023-12-01')
recent = storage.get_recent_projects(days=7)
stats = storage.get_daily_stats('2023-12-01')

# 数据管理
storage.cleanup_old_data()
```

### 可视化模块 (Visualization)

#### ChartGenerator

图表生成器。

```python
from visualization.chart_generator import ChartGenerator

generator = ChartGenerator(config)
charts = generator.generate_daily_charts(projects)
```

**方法**：
- `generate_daily_charts(projects)`: 生成每日图表
- `create_language_distribution_chart(projects)`: 编程语言分布图
- `create_stars_distribution_chart(projects)`: 星标数分布图
- `create_keyword_chart(projects)`: 关键词图表
- `create_dashboard(projects)`: 综合仪表板

**返回格式**：
```python
{
    'language_distribution': '/path/to/chart.html',
    'stars_distribution': '/path/to/chart.html',
    'keyword_cloud': '/path/to/chart.html',
    'dashboard': '/path/to/chart.html'
}
```

#### ReportGenerator

报告生成器。

```python
from visualization.report_generator import ReportGenerator

generator = ReportGenerator(config)
report = await generator.generate_daily_report(projects, charts)
```

**输出格式**：
```python
{
    'html': 'HTML报告内容',
    'markdown': 'Markdown报告内容',
    'data': {
        'date': '2023-12-01',
        'total_projects': 100,
        'top_projects': [...],
        'trend_analysis': {...}
    }
}
```

## 配置 API

### 配置加载

```python
from utils.config import load_config, validate_config, get_config_value

# 加载配置
config = load_config('config/settings.yaml')

# 验证配置
is_valid = validate_config(config)

# 获取配置值
api_key = get_config_value(config, 'api.openai.api_key')
```

### 配置结构

```python
config = {
    'api': {
        'openai': {
            'api_key': 'your-key',
            'model': 'gpt-3.5-turbo',
            'max_tokens': 1000,
            'temperature': 0.3
        }
    },
    'crawler': {
        'request': {
            'timeout': 30,
            'retry_times': 3,
            'delay_between_requests': 1
        },
        'github': {...},
        'producthunt': {...}
    },
    'ai_analysis': {
        'ai_relevance_threshold': 0.7,
        'keyword_extraction': {...},
        'ai_keywords': [...]
    },
    'data': {
        'paths': {...},
        'retention_days': 30,
        'deduplication': {...}
    },
    'visualization': {
        'charts': {...},
        'reports': {...}
    },
    'logging': {...}
}
```

## 主程序 API

### AITrendingRadar

主程序类。

```python
from main import AITrendingRadar

radar = AITrendingRadar()
```

**方法**：
```python
# 执行每日更新
result = await radar.run_daily_update()

# 仅运行分析
projects = await radar.run_analysis_only('data.json')
```

**返回格式**：
```python
# run_daily_update 返回
{
    'success': True,
    'ai_projects_count': 50,
    'total_projects_count': 200,
    'report_path': '/path/to/report.html'
}

# 失败时返回
{
    'success': False,
    'error': '错误信息'
}
```

## 数据格式规范

### 标准项目数据格式

```python
project = {
    # 基础信息
    'name': str,           # 项目名称
    'description': str,    # 项目描述
    'url': str,           # 项目URL
    'author': str,        # 作者/组织
    'source': str,        # 数据源 ('github', 'producthunt')
    
    # 统计信息
    'stars': int,         # 星标数
    'forks': int,         # Fork数
    'votes': int,         # 投票数（Product Hunt）
    
    # 技术信息
    'language': str,      # 编程语言
    'tags': List[str],    # 标签列表
    
    # 时间信息
    'created_at': str,    # 创建时间 (ISO格式)
    'updated_at': str,    # 更新时间 (ISO格式)
    'crawled_at': str,    # 爬取时间 (ISO格式)
    
    # AI分析结果（可选）
    'ai_classification': Dict,  # AI分类结果
    'keywords': Dict,          # 关键词提取结果
    'summary': Dict,           # 项目总结
    
    # 元数据
    'raw_data': Dict      # 原始数据
}
```

### AI 分析结果格式

```python
ai_classification = {
    'is_ai_related': bool,        # 是否AI相关
    'confidence_score': float,    # 置信度 (0-1)
    'reasoning': str,             # 判断理由
    'ai_categories': List[str],   # AI分类
    'tech_stack': List[str]       # 技术栈
}

keywords = {
    'keywords': List[str],        # 关键词列表
    'categories': Dict[str, List[str]],  # 分类关键词
    'extraction_method': str      # 提取方法
}

summary = {
    'summary': str,               # 项目总结
    'highlights': List[str],      # 项目亮点
    'use_cases': List[str],       # 应用场景
    'generation_method': str      # 生成方法
}
```

## 错误处理

### 异常类型

```python
# 配置错误
class ConfigError(Exception):
    pass

# 网络错误
class NetworkError(Exception):
    pass

# API错误
class APIError(Exception):
    pass

# 数据错误
class DataError(Exception):
    pass
```

### 错误处理示例

```python
try:
    result = await classifier.classify(project)
except APIError as e:
    logger.error(f"API调用失败: {e}")
    # 降级到关键词分类
    result = classifier._classify_by_keywords(project)
except Exception as e:
    logger.error(f"未知错误: {e}")
    # 返回默认结果
    result = {'is_ai_related': False, 'confidence_score': 0.0}
```

## 扩展开发

### 添加新的爬虫

```python
from crawlers.base_crawler import BaseCrawler

class CustomCrawler(BaseCrawler):
    async def crawl(self) -> List[Dict[str, Any]]:
        # 实现爬取逻辑
        pass
    
    def parse_project_list(self, html: str) -> List[Dict[str, Any]]:
        # 实现解析逻辑
        pass
```

### 添加新的分析器

```python
class CustomAnalyzer:
    def __init__(self, config):
        self.config = config
    
    async def analyze(self, project):
        # 实现分析逻辑
        return analysis_result
```

### 添加新的可视化

```python
class CustomVisualizer:
    def generate_custom_chart(self, data):
        # 实现图表生成逻辑
        return chart_path
```

## 性能优化

### 异步处理

```python
import asyncio

# 并发处理
async def process_batch(projects):
    tasks = [classifier.classify(p) for p in projects]
    results = await asyncio.gather(*tasks)
    return results

# 限制并发数
semaphore = asyncio.Semaphore(5)

async def limited_classify(project):
    async with semaphore:
        return await classifier.classify(project)
```

### 缓存机制

```python
import functools

@functools.lru_cache(maxsize=128)
def cached_analysis(project_hash):
    # 缓存分析结果
    pass
```

### 批量操作

```python
# 批量数据库操作
storage.batch_save(projects)

# 批量API调用
results = await classifier.batch_classify(projects)
```
