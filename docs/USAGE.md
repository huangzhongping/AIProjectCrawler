# 使用指南

## 基本用法

### 命令行界面

AI爆款项目雷达提供简单的命令行界面：

```bash
# 执行每日更新（完整流程）
python main.py --mode daily

# 仅分析已有数据
python main.py --mode analysis --data-file data/processed/ai_projects_2023-12-01.json
```

### 运行模式

#### 1. 每日更新模式 (daily)

完整的数据收集和分析流程：

```bash
python main.py --mode daily
```

**执行步骤**：
1. 爬取 GitHub Trending 和 Product Hunt 数据
2. 数据清洗和去重
3. AI 项目分类和分析
4. 关键词提取和项目总结
5. 生成可视化图表
6. 生成 HTML 和 Markdown 报告
7. 保存数据到数据库

**输出文件**：
- `output/reports/ai-trends-YYYY-MM-DD.html` - HTML 报告
- `output/reports/ai-trends-YYYY-MM-DD.md` - Markdown 报告
- `output/web/index.html` - 最新报告（用于 GitHub Pages）
- `output/charts/` - 各种图表文件
- `data/processed/ai_projects_YYYY-MM-DD.json` - 处理后的数据

#### 2. 分析模式 (analysis)

仅对已有数据进行 AI 分析：

```bash
python main.py --mode analysis --data-file data/raw/github_20231201_120000.json
```

**适用场景**：
- 重新分析历史数据
- 测试 AI 分析效果
- 调试分析算法

## 配置选项

### 爬虫配置

#### GitHub Trending 配置

```yaml
crawler:
  github:
    languages: ["python", "javascript", "typescript", "go", "rust"]
    time_ranges: ["daily", "weekly", "monthly"]
    max_pages: 3
```

**参数说明**：
- `languages`: 要爬取的编程语言列表
- `time_ranges`: 时间范围（daily/weekly/monthly）
- `max_pages`: 每个语言+时间范围组合的最大页数

#### Product Hunt 配置

```yaml
crawler:
  producthunt:
    categories: ["artificial-intelligence", "developer-tools", "tech"]
    max_items: 50
```

**参数说明**：
- `categories`: 要爬取的产品分类
- `max_items`: 每个分类的最大项目数

### AI 分析配置

```yaml
ai_analysis:
  ai_relevance_threshold: 0.7
  keyword_extraction:
    max_keywords: 10
    min_keyword_length: 3
  ai_keywords:
    - "artificial intelligence"
    - "machine learning"
    - "deep learning"
    # ... 更多关键词
```

**参数说明**：
- `ai_relevance_threshold`: AI 相关性判断阈值（0-1）
- `max_keywords`: 每个项目提取的最大关键词数
- `min_keyword_length`: 关键词最小长度
- `ai_keywords`: 预定义的 AI 相关关键词列表

### 可视化配置

```yaml
visualization:
  charts:
    theme: "plotly_white"
    width: 1200
    height: 800
    font_size: 12
  reports:
    max_projects_per_report: 50
    include_charts: true
```

## 高级用法

### 自定义数据源

你可以扩展爬虫来支持新的数据源：

1. 创建新的爬虫类：

```python
# src/crawlers/custom_crawler.py
from .base_crawler import BaseCrawler

class CustomCrawler(BaseCrawler):
    async def crawl(self):
        # 实现你的爬虫逻辑
        pass
    
    def parse_project_list(self, html):
        # 实现HTML解析逻辑
        pass
```

2. 在主程序中集成：

```python
# 在 main.py 中添加
from crawlers.custom_crawler import CustomCrawler

# 在 AITrendingRadar 类中
self.custom_crawler = CustomCrawler(self.config)

# 在 run_daily_update 方法中
custom_data = await self.custom_crawler.crawl()
```

### 自定义 AI 分析

#### 添加新的分类维度

```python
# 扩展 ai_analysis/classifier.py
class AIProjectClassifier:
    def classify_by_domain(self, project):
        """按应用领域分类"""
        # 实现领域分类逻辑
        pass
    
    def classify_by_maturity(self, project):
        """按项目成熟度分类"""
        # 实现成熟度分类逻辑
        pass
```

#### 自定义关键词提取

```python
# 扩展 ai_analysis/keyword_extractor.py
class KeywordExtractor:
    def extract_technical_keywords(self, project):
        """提取技术关键词"""
        # 实现技术关键词提取
        pass
    
    def extract_business_keywords(self, project):
        """提取商业关键词"""
        # 实现商业关键词提取
        pass
```

### 自定义可视化

#### 添加新的图表类型

```python
# 扩展 visualization/chart_generator.py
class ChartGenerator:
    def create_trend_timeline(self, projects):
        """创建趋势时间线图"""
        # 实现时间线图表
        pass
    
    def create_network_graph(self, projects):
        """创建项目关系网络图"""
        # 实现网络图表
        pass
```

#### 自定义报告模板

1. 创建新的 HTML 模板：

```html
<!-- src/visualization/templates/custom_report.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <!-- 自定义样式 -->
</head>
<body>
    <!-- 自定义内容 -->
</body>
</html>
```

2. 在报告生成器中使用：

```python
# 扩展 visualization/report_generator.py
def generate_custom_report(self, data):
    # 使用自定义模板生成报告
    pass
```

## 数据管理

### 数据存储结构

```
data/
├── raw/                    # 原始爬取数据
│   ├── github_YYYYMMDD_HHMMSS.json
│   └── producthunt_YYYYMMDD_HHMMSS.json
├── processed/              # 处理后数据
│   └── ai_projects_YYYY-MM-DD.json
└── archive/                # 归档数据
    └── old_data_files.json
```

### 数据库操作

```python
from utils.storage import DataStorage

storage = DataStorage(config)

# 获取指定日期的项目
projects = storage.get_projects_by_date('2023-12-01')

# 获取最近7天的项目
recent_projects = storage.get_recent_projects(days=7)

# 获取统计数据
stats = storage.get_daily_stats('2023-12-01')

# 清理旧数据
storage.cleanup_old_data()
```

### 数据导出

```python
# 导出为 CSV
import pandas as pd

projects = storage.get_projects_by_date('2023-12-01')
df = pd.DataFrame(projects)
df.to_csv('ai_projects_2023-12-01.csv', index=False)

# 导出为 Excel
df.to_excel('ai_projects_2023-12-01.xlsx', index=False)
```

## 监控和日志

### 日志配置

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file_path: "logs/app.log"
  rotation: "1 day"
  retention: "7 days"
```

### 查看日志

```bash
# 查看实时日志
tail -f logs/app.log

# 查看错误日志
grep "ERROR" logs/app.log

# 查看特定模块日志
grep "crawler" logs/app.log
```

### 性能监控

```python
# 在代码中添加性能监控
import time
from loguru import logger

start_time = time.time()
# 执行操作
end_time = time.time()

logger.info(f"操作耗时: {end_time - start_time:.2f}秒")
```

## 故障排除

### 常见问题

#### 1. 爬虫被限制

**症状**: 大量 HTTP 403/429 错误

**解决方案**:
```yaml
crawler:
  request:
    delay_between_requests: 3  # 增加延迟
    retry_times: 5            # 增加重试次数
```

#### 2. AI 分析失败

**症状**: AI 分类结果全部为 False

**解决方案**:
- 检查 OpenAI API 密钥
- 降低相关性阈值
- 检查网络连接

#### 3. 内存不足

**症状**: MemoryError 或程序崩溃

**解决方案**:
```yaml
crawler:
  github:
    max_pages: 1  # 减少数据量
visualization:
  reports:
    max_projects_per_report: 20  # 减少报告项目数
```

#### 4. 图表生成失败

**症状**: 图表文件为空或报错

**解决方案**:
- 检查数据格式
- 确保有足够的数据点
- 检查 Plotly 依赖

### 调试技巧

#### 1. 启用调试模式

```bash
# 设置环境变量
export LOG_LEVEL=DEBUG

# 或在配置文件中
logging:
  level: "DEBUG"
```

#### 2. 单步调试

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用 IPython
import IPython; IPython.embed()
```

#### 3. 测试单个模块

```bash
# 测试爬虫
python -c "
import sys
sys.path.append('src')
import asyncio
from crawlers.github_crawler import GitHubCrawler
from utils.config import load_config

async def test():
    config = load_config()
    crawler = GitHubCrawler(config)
    # 测试爬虫功能

asyncio.run(test())
"
```

## 最佳实践

### 1. 定期备份数据

```bash
# 创建备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_$DATE.tar.gz data/ output/
```

### 2. 监控 API 使用量

```python
# 记录 API 调用次数
api_calls = 0
def track_api_call():
    global api_calls
    api_calls += 1
    logger.info(f"API 调用次数: {api_calls}")
```

### 3. 优化性能

- 使用异步处理
- 合理设置并发数
- 缓存重复计算结果
- 定期清理旧数据

### 4. 安全考虑

- 不要在代码中硬编码 API 密钥
- 使用环境变量或配置文件
- 定期轮换 API 密钥
- 限制网络访问权限
