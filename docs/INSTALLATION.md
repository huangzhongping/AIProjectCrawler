# 安装指南

## 系统要求

- Python 3.8 或更高版本
- Git
- 至少 2GB 可用内存
- 稳定的网络连接

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ai-trending-radar.git
cd ai-trending-radar
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置设置

```bash
# 复制配置文件模板
cp config/settings.yaml.example config/settings.yaml

# 复制环境变量文件
cp .env.example .env
```

### 5. 设置 API 密钥

编辑 `.env` 文件，添加你的 OpenAI API 密钥：

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

或者直接编辑 `config/settings.yaml` 文件：

```yaml
api:
  openai:
    api_key: "your-openai-api-key-here"
```

### 6. 运行测试

```bash
# 运行基础测试
python -c "
import sys
sys.path.append('src')
from utils.config import load_config
config = load_config()
print('✅ 配置加载成功')
"
```

### 7. 执行首次运行

```bash
# 执行每日更新
python main.py --mode daily
```

## 详细安装步骤

### 环境准备

#### Python 环境

确保你的系统安装了 Python 3.8 或更高版本：

```bash
python --version
```

如果版本过低，请从 [Python 官网](https://www.python.org/) 下载最新版本。

#### Git 安装

确保系统安装了 Git：

```bash
git --version
```

### 依赖安装

项目使用以下主要依赖：

- **网络爬虫**: requests, beautifulsoup4, selenium
- **AI 分析**: openai, tiktoken
- **数据处理**: pandas, numpy
- **可视化**: matplotlib, plotly, seaborn
- **配置管理**: pyyaml, python-dotenv
- **日志记录**: loguru
- **测试**: pytest, pytest-cov

### 配置详解

#### 基础配置 (config/settings.yaml)

```yaml
# API 配置
api:
  openai:
    api_key: "${OPENAI_API_KEY}"  # 从环境变量读取
    model: "gpt-3.5-turbo"
    max_tokens: 1000
    temperature: 0.3

# 爬虫配置
crawler:
  request:
    timeout: 30
    retry_times: 3
    delay_between_requests: 1
  
  github:
    languages: ["python", "javascript", "typescript"]
    time_ranges: ["daily", "weekly"]
    max_pages: 3
  
  producthunt:
    categories: ["artificial-intelligence", "developer-tools"]
    max_items: 50

# 数据配置
data:
  paths:
    raw_data: "data/raw"
    processed_data: "data/processed"
    output: "output"
  retention_days: 30
```

#### 环境变量 (.env)

```bash
# OpenAI API 密钥
OPENAI_API_KEY=your-openai-api-key-here

# 可选：GitHub Token (提高 API 限制)
GITHUB_TOKEN=your-github-token-here

# 日志级别
LOG_LEVEL=INFO

# 运行环境
ENVIRONMENT=production
```

### 目录结构

安装完成后，项目目录结构如下：

```
ai-trending-radar/
├── src/                    # 源代码
│   ├── crawlers/          # 爬虫模块
│   ├── ai_analysis/       # AI分析模块
│   ├── utils/             # 工具函数
│   └── visualization/     # 可视化模块
├── data/                  # 数据存储
│   ├── raw/              # 原始数据
│   ├── processed/        # 处理后数据
│   └── archive/          # 归档数据
├── output/               # 输出文件
│   ├── reports/          # 报告文件
│   ├── charts/           # 图表文件
│   └── web/              # 网页文件
├── config/               # 配置文件
├── tests/                # 测试文件
├── docs/                 # 文档
└── .github/workflows/    # GitHub Actions
```

## 故障排除

### 常见问题

#### 1. 导入错误

```bash
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**：
```bash
pip install -r requirements.txt
```

#### 2. API 密钥错误

```bash
❌ 请设置有效的OpenAI API密钥
```

**解决方案**：
- 检查 `.env` 文件中的 `OPENAI_API_KEY`
- 确保 API 密钥有效且有足够余额
- 检查网络连接

#### 3. 权限错误

```bash
PermissionError: [Errno 13] Permission denied
```

**解决方案**：
```bash
# 确保有写入权限
chmod 755 data/ output/ logs/
```

#### 4. 网络连接问题

```bash
requests.exceptions.ConnectionError
```

**解决方案**：
- 检查网络连接
- 配置代理（如需要）
- 增加超时时间

### 性能优化

#### 1. 减少 API 调用

如果 OpenAI API 调用过多，可以：

```yaml
# 在 config/settings.yaml 中调整
ai_analysis:
  ai_relevance_threshold: 0.8  # 提高阈值
```

#### 2. 调整爬虫频率

```yaml
crawler:
  request:
    delay_between_requests: 2  # 增加延迟
  github:
    max_pages: 1  # 减少页数
```

#### 3. 限制数据量

```yaml
visualization:
  reports:
    max_projects_per_report: 20  # 减少报告项目数
```

## 验证安装

运行以下命令验证安装是否成功：

```bash
# 1. 测试配置加载
python -c "
import sys
sys.path.append('src')
from utils.config import load_config, validate_config
config = load_config()
if validate_config(config):
    print('✅ 配置验证通过')
else:
    print('❌ 配置验证失败')
"

# 2. 测试模块导入
python -c "
import sys
sys.path.append('src')
from crawlers.github_crawler import GitHubCrawler
from ai_analysis.classifier import AIProjectClassifier
from utils.data_cleaner import DataCleaner
print('✅ 所有模块导入成功')
"

# 3. 运行测试套件
pytest tests/ -v

# 4. 执行试运行
python main.py --mode daily
```

如果所有步骤都成功完成，说明安装正确！

## 下一步

- 阅读 [使用指南](USAGE.md)
- 查看 [API 文档](API.md)
- 了解 [部署指南](DEPLOYMENT.md)
