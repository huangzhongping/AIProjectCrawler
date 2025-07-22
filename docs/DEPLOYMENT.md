# 部署指南

## GitHub Actions 自动化部署

### 1. 准备 GitHub 仓库

#### 创建仓库

```bash
# 1. 在 GitHub 上创建新仓库
# 2. 克隆到本地
git clone https://github.com/your-username/ai-trending-radar.git
cd ai-trending-radar

# 3. 推送代码
git add .
git commit -m "Initial commit"
git push origin main
```

#### 设置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

1. 进入仓库 → Settings → Secrets and variables → Actions
2. 添加以下 secrets：

```
OPENAI_API_KEY=your-openai-api-key-here
```

可选的 secrets：
```
GITHUB_TOKEN=your-github-token-here  # 提高 API 限制
```

### 2. 启用 GitHub Pages

1. 进入仓库 → Settings → Pages
2. Source 选择 "GitHub Actions"
3. 保存设置

### 3. 配置工作流

项目已包含以下 GitHub Actions 工作流：

#### 每日自动更新 (`.github/workflows/daily-update.yml`)

- **触发时间**: 每天 UTC 8:00（北京时间 16:00）
- **功能**: 执行完整的数据收集和分析流程
- **输出**: 自动部署到 GitHub Pages

#### 手动触发更新 (`.github/workflows/manual-update.yml`)

- **触发方式**: 手动触发
- **功能**: 支持不同运行模式
- **选项**: 
  - 运行模式（daily/analysis）
  - 数据文件路径
  - 是否部署到 Pages

#### 测试工作流 (`.github/workflows/test.yml`)

- **触发时机**: 代码推送和 PR
- **功能**: 运行测试套件，检查代码质量

### 4. 首次部署

#### 手动触发首次运行

1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Manual AI Trends Update"
4. 点击 "Run workflow"
5. 选择参数：
   - Mode: `daily`
   - Deploy to GitHub Pages: `true`
6. 点击 "Run workflow"

#### 验证部署

1. 等待工作流完成（通常 5-10 分钟）
2. 检查 Actions 页面是否显示绿色勾号
3. 访问 `https://your-username.github.io/ai-trending-radar/`
4. 确认页面正常显示

## 本地服务器部署

### 1. 使用 Docker 部署

#### 创建 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p data/{raw,processed,archive} output/{reports,charts,web} logs

# 设置环境变量
ENV PYTHONPATH=/app/src

# 暴露端口（如果需要 web 服务）
EXPOSE 8000

# 默认命令
CMD ["python", "main.py", "--mode", "daily"]
```

#### 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  ai-radar:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./logs:/app/logs
    restart: unless-stopped
    
  # 可选：添加 nginx 服务静态文件
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./output/web:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - ai-radar
    restart: unless-stopped
```

#### 部署步骤

```bash
# 1. 创建环境变量文件
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 2. 构建和启动
docker-compose up -d

# 3. 查看日志
docker-compose logs -f ai-radar

# 4. 手动执行更新
docker-compose exec ai-radar python main.py --mode daily
```

### 2. 使用 systemd 服务

#### 创建服务文件

```bash
sudo nano /etc/systemd/system/ai-radar.service
```

```ini
[Unit]
Description=AI Trending Radar
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/path/to/ai-trending-radar
Environment=OPENAI_API_KEY=your-api-key-here
ExecStart=/path/to/venv/bin/python main.py --mode daily
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 创建定时器

```bash
sudo nano /etc/systemd/system/ai-radar.timer
```

```ini
[Unit]
Description=Run AI Radar daily
Requires=ai-radar.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

#### 启用服务

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启用定时器
sudo systemctl enable ai-radar.timer
sudo systemctl start ai-radar.timer

# 查看状态
sudo systemctl status ai-radar.timer

# 手动运行
sudo systemctl start ai-radar.service

# 查看日志
sudo journalctl -u ai-radar.service -f
```

## 云服务器部署

### 1. AWS EC2 部署

#### 启动 EC2 实例

```bash
# 1. 选择 Ubuntu 20.04 LTS AMI
# 2. 选择 t3.medium 或更高配置
# 3. 配置安全组，开放必要端口
# 4. 创建或选择密钥对
```

#### 配置服务器

```bash
# 连接到服务器
ssh -i your-key.pem ubuntu@your-ec2-ip

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和 Git
sudo apt install python3 python3-pip python3-venv git -y

# 克隆项目
git clone https://github.com/your-username/ai-trending-radar.git
cd ai-trending-radar

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 测试运行
python main.py --mode daily
```

#### 设置自动化

```bash
# 添加到 crontab
crontab -e

# 添加以下行（每天 8:00 执行）
0 8 * * * cd /home/ubuntu/ai-trending-radar && /home/ubuntu/ai-trending-radar/venv/bin/python main.py --mode daily >> /home/ubuntu/ai-radar.log 2>&1
```

### 2. Google Cloud Platform 部署

#### 使用 Cloud Run

```bash
# 1. 创建 Dockerfile（见上文）
# 2. 构建镜像
gcloud builds submit --tag gcr.io/your-project-id/ai-radar

# 3. 部署到 Cloud Run
gcloud run deploy ai-radar \
  --image gcr.io/your-project-id/ai-radar \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=your-api-key-here
```

#### 使用 Cloud Scheduler

```bash
# 创建定时任务
gcloud scheduler jobs create http ai-radar-daily \
  --schedule="0 8 * * *" \
  --uri="https://your-cloud-run-url/trigger" \
  --http-method=POST
```

### 3. Heroku 部署

#### 准备文件

创建 `Procfile`：
```
worker: python main.py --mode daily
```

创建 `runtime.txt`：
```
python-3.9.18
```

#### 部署步骤

```bash
# 1. 安装 Heroku CLI
# 2. 登录
heroku login

# 3. 创建应用
heroku create your-app-name

# 4. 设置环境变量
heroku config:set OPENAI_API_KEY=your-api-key-here

# 5. 部署
git push heroku main

# 6. 设置定时任务（需要付费插件）
heroku addons:create scheduler:standard
heroku addons:open scheduler
```

## 监控和维护

### 1. 日志监控

#### 设置日志轮转

```bash
# 创建 logrotate 配置
sudo nano /etc/logrotate.d/ai-radar
```

```
/path/to/ai-trending-radar/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 your-username your-username
}
```

#### 监控关键指标

```bash
# 检查磁盘使用
df -h

# 检查内存使用
free -h

# 检查进程状态
ps aux | grep python

# 检查网络连接
netstat -an | grep ESTABLISHED
```

### 2. 错误告警

#### 使用邮件告警

```python
# 在 main.py 中添加错误处理
import smtplib
from email.mime.text import MIMEText

def send_error_email(error_msg):
    msg = MIMEText(f"AI Radar Error: {error_msg}")
    msg['Subject'] = 'AI Radar Error Alert'
    msg['From'] = 'your-email@example.com'
    msg['To'] = 'admin@example.com'
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@example.com', 'your-password')
    server.send_message(msg)
    server.quit()

# 在异常处理中调用
try:
    result = await radar.run_daily_update()
except Exception as e:
    send_error_email(str(e))
    raise
```

### 3. 性能优化

#### 数据库优化

```python
# 定期清理旧数据
from utils.storage import DataStorage

storage = DataStorage(config)
storage.cleanup_old_data()  # 清理超过保留期的数据
```

#### 缓存优化

```python
# 添加缓存机制
import functools
import time

@functools.lru_cache(maxsize=128)
def cached_ai_analysis(project_hash):
    # 缓存 AI 分析结果
    pass
```

### 4. 备份策略

#### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/ai-radar"
PROJECT_DIR="/path/to/ai-trending-radar"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据
tar -czf $BACKUP_DIR/data_$DATE.tar.gz $PROJECT_DIR/data/
tar -czf $BACKUP_DIR/output_$DATE.tar.gz $PROJECT_DIR/output/

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

#### 设置定时备份

```bash
# 添加到 crontab
0 2 * * * /path/to/backup.sh >> /var/log/ai-radar-backup.log 2>&1
```

## 故障排除

### 常见部署问题

#### 1. GitHub Actions 失败

**检查步骤**：
- 验证 Secrets 设置
- 检查工作流语法
- 查看 Actions 日志

#### 2. 权限问题

```bash
# 设置正确的文件权限
chmod +x main.py
chmod -R 755 data/ output/ logs/
```

#### 3. 依赖冲突

```bash
# 重新创建虚拟环境
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. 内存不足

```bash
# 检查系统资源
htop
free -h

# 优化配置
# 减少并发数、数据量等
```

### 性能调优

#### 1. 减少 API 调用

```yaml
# 调整配置以减少 OpenAI API 调用
ai_analysis:
  ai_relevance_threshold: 0.8  # 提高阈值
```

#### 2. 优化爬虫性能

```yaml
crawler:
  request:
    delay_between_requests: 0.5  # 减少延迟（注意不要被限制）
  github:
    max_pages: 2  # 减少页数
```

#### 3. 数据库优化

```python
# 定期重建索引
# 清理旧数据
# 使用批量操作
```
