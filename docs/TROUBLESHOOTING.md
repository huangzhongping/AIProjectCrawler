# 故障排除指南

## 常见安装问题

### 1. sqlite3 安装错误

**错误信息**:
```
ERROR: Could not find a version that satisfies the requirement sqlite3
```

**解决方案**:
`sqlite3` 是 Python 的内置模块，不需要通过 pip 安装。如果你看到这个错误，说明 requirements.txt 文件有问题。

```bash
# 重新下载最新的 requirements.txt
curl -O https://raw.githubusercontent.com/your-repo/ai-trending-radar/main/requirements.txt

# 或者手动安装核心依赖
pip install requests beautifulsoup4 openai pandas plotly pyyaml python-dotenv loguru aiohttp
```

### 2. Python 版本问题

**错误信息**:
```
SyntaxError: invalid syntax
```

**解决方案**:
确保使用 Python 3.8 或更高版本：

```bash
# 检查 Python 版本
python --version
python3 --version

# 如果版本过低，使用 python3
python3 -m pip install -r requirements.txt
python3 demo.py
```

### 3. 虚拟环境问题

**错误信息**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:
确保在正确的虚拟环境中：

```bash
# 创建新的虚拟环境
python -m venv ai-radar-env

# 激活虚拟环境
# Linux/Mac:
source ai-radar-env/bin/activate
# Windows:
ai-radar-env\Scripts\activate

# 重新安装依赖
pip install -r requirements.txt
```

### 4. OpenAI API 密钥问题

**错误信息**:
```
❌ 请设置有效的OpenAI API密钥
```

**解决方案**:

1. **获取 API 密钥**:
   - 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
   - 创建新的 API 密钥

2. **设置环境变量**:
   ```bash
   # 方法1: 编辑 .env 文件
   echo "OPENAI_API_KEY=''" > .env
   
   # 方法2: 设置系统环境变量
   export OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. **验证设置**:
   ```bash
   python -c "import os; print('API Key:', os.getenv('OPENAI_API_KEY', 'Not set'))"
   ```

### 5. 网络连接问题

**错误信息**:
```
requests.exceptions.ConnectionError
```

**解决方案**:

1. **检查网络连接**:
   ```bash
   ping github.com
   ping api.openai.com
   ```

2. **配置代理**（如果需要）:
   ```bash
   export HTTP_PROXY=http://your-proxy:port
   export HTTPS_PROXY=http://your-proxy:port
   ```

3. **增加超时时间**:
   编辑 `config/settings.yaml`:
   ```yaml
   crawler:
     request:
       timeout: 60  # 增加到60秒
   ```

### 6. 权限问题

**错误信息**:
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**:

```bash
# Linux/Mac: 修改目录权限
chmod -R 755 data/ output/ logs/

# Windows: 以管理员身份运行命令提示符
```

### 7. 内存不足

**错误信息**:
```
MemoryError
```

**解决方案**:

1. **减少数据量**:
   编辑 `config/settings.yaml`:
   ```yaml
   crawler:
     github:
       max_pages: 1  # 减少页数
   visualization:
     reports:
       max_projects_per_report: 20  # 减少项目数
   ```

2. **关闭其他程序**释放内存

### 8. 图表生成失败

**错误信息**:
```
plotly.graph_objects module not found
```

**解决方案**:

```bash
# 重新安装 plotly
pip uninstall plotly
pip install plotly>=5.17.0

# 如果还有问题，安装额外依赖
pip install kaleido  # 用于静态图片导出
```

## 依赖问题解决

### 最小依赖安装

如果完整安装有问题，可以尝试最小依赖：

```bash
# 核心依赖
pip install requests beautifulsoup4 pyyaml python-dotenv loguru

# AI 功能（可选）
pip install openai

# 数据处理（可选）
pip install pandas numpy

# 可视化（可选）
pip install matplotlib plotly
```

### 替代安装方法

```bash
# 使用 conda
conda install requests beautifulsoup4 pandas matplotlib
pip install openai plotly pyyaml python-dotenv loguru

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 运行时问题

### 1. 爬虫被限制

**症状**: 大量 HTTP 403/429 错误

**解决方案**:
```yaml
# 在 config/settings.yaml 中调整
crawler:
  request:
    delay_between_requests: 3  # 增加延迟
    retry_times: 5            # 增加重试
```

### 2. AI 分析失败

**症状**: 所有项目都被标记为非 AI 相关

**解决方案**:
1. 检查 API 密钥是否正确
2. 检查网络连接
3. 降低阈值：
   ```yaml
   ai_analysis:
     ai_relevance_threshold: 0.5  # 降低阈值
   ```

### 3. 数据库锁定

**错误信息**:
```
sqlite3.OperationalError: database is locked
```

**解决方案**:
```bash
# 删除数据库文件重新开始
rm data/processed/projects.db

# 或者等待一段时间后重试
```

## 调试技巧

### 1. 启用详细日志

```bash
# 设置环境变量
export LOG_LEVEL=DEBUG

# 或在 config/settings.yaml 中设置
logging:
  level: "DEBUG"
```

### 2. 单步测试

```bash
# 测试配置加载
python -c "
import sys
sys.path.append('src')
from utils.config import load_config
config = load_config()
print('配置加载成功')
"

# 测试爬虫
python -c "
import sys, asyncio
sys.path.append('src')
from crawlers.github_crawler import GitHubCrawler
from utils.config import load_config

async def test():
    config = load_config()
    crawler = GitHubCrawler(config)
    print('爬虫初始化成功')

asyncio.run(test())
"
```

### 3. 使用演示模式

```bash
# 运行演示脚本，使用示例数据
python demo.py
```

## 获取帮助

### 1. 检查日志文件

```bash
# 查看最新日志
tail -f logs/app.log

# 搜索错误
grep "ERROR" logs/app.log
```

### 2. 运行诊断

```bash
# 运行完整诊断
python verify_setup.py

# 检查系统信息
python -c "
import sys, platform
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.architecture()}')
"
```

### 3. 社区支持

- 📧 **邮件**: your-email@example.com
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-username/ai-trending-radar/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/your-username/ai-trending-radar/discussions)

### 4. 提交问题时请包含

1. **系统信息**: 操作系统、Python 版本
2. **错误信息**: 完整的错误堆栈
3. **配置文件**: 相关的配置设置（隐藏敏感信息）
4. **重现步骤**: 如何重现问题
5. **日志文件**: 相关的日志输出

## 常见解决方案总结

| 问题类型 | 快速解决方案 |
|---------|-------------|
| 依赖安装失败 | `pip install --upgrade pip` 然后重新安装 |
| 模块找不到 | 检查虚拟环境是否激活 |
| API 密钥错误 | 检查 `.env` 文件和环境变量 |
| 网络连接问题 | 检查防火墙和代理设置 |
| 权限错误 | 修改文件夹权限或使用管理员权限 |
| 内存不足 | 减少数据量或关闭其他程序 |
| 图表生成失败 | 重新安装 plotly 和相关依赖 |

记住：大多数问题都可以通过重新安装依赖或检查配置来解决！
