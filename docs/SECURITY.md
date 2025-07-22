# 🔒 安全使用指南

## 重要提醒

⚠️ **永远不要将API密钥提交到Git仓库中！**

本项目已经配置了完善的安全机制，但请务必遵循以下安全最佳实践。

## 🛡️ 安全配置

### 1. 环境变量配置

**正确做法**：
```bash
# 复制示例文件
cp .env.example .env

# 编辑.env文件，填入真实的API密钥
nano .env
```

**错误做法**：
```bash
# ❌ 不要直接在配置文件中写入API密钥
api_key: "sk-your-real-api-key-here"
```

### 2. 配置文件安全

项目提供了多个安全的配置文件：

- `config/settings_safe.yaml` - 安全版本，使用环境变量
- `config/settings_no_api.yaml` - 无API版本，使用关键词分析
- `config/settings_ollama.yaml` - 本地模型版本

**推荐使用顺序**：
1. 首选：`settings_no_api.yaml`（完全免费，无安全风险）
2. 次选：`settings_ollama.yaml`（本地运行，隐私安全）
3. 最后：`settings_safe.yaml`（需要API密钥，但安全配置）

### 3. Git安全检查

项目已配置`.gitignore`忽略敏感文件：

```gitignore
# 环境变量文件
.env
.env.local
.env.production

# 敏感配置文件
**/api_keys.yaml
**/*_secret.yaml
config/settings_with_keys.yaml
```

## 🔍 安全检查清单

在提交代码前，请检查：

- [ ] `.env`文件是否被`.gitignore`忽略
- [ ] 配置文件中是否包含真实的API密钥
- [ ] 是否使用了环境变量`${OPENAI_API_KEY}`
- [ ] 日志文件是否包含敏感信息

## 🚨 如果意外提交了敏感信息

### 1. 立即撤销API密钥
- 登录OpenAI控制台
- 撤销泄露的API密钥
- 生成新的API密钥

### 2. 清理Git历史
```bash
# 方法1：使用git filter-repo（推荐）
pip install git-filter-repo
git filter-repo --invert-paths --path config/settings_with_keys.yaml

# 方法2：重写历史
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch config/settings_with_keys.yaml' \
--prune-empty --tag-name-filter cat -- --all
```

### 3. 强制推送
```bash
git push origin --force --all
git push origin --force --tags
```

## 🛠️ 推荐的安全实践

### 1. 使用关键词分析模式
```bash
# 完全免费，无安全风险
python3 run_keywords_only.py
```

### 2. 使用本地AI模型
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama3.2:3b

# 运行本地模式
python3 run_free_ai.py
```

### 3. 环境变量管理
```bash
# 使用direnv管理环境变量
echo "export OPENAI_API_KEY=your-key-here" > .envrc
direnv allow
```

## 📋 安全配置模板

### .env文件模板
```bash
# OpenAI API配置（可选）
OPENAI_API_KEY=your-openai-api-key-here

# GitHub Token（可选，提高API限制）
GITHUB_TOKEN=your-github-token-here

# 运行环境
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 安全的配置文件
```yaml
api:
  openai:
    api_key: "${OPENAI_API_KEY}"  # 从环境变量读取
    model: "gpt-3.5-turbo"
    timeout: 30
```

## 🔗 相关资源

- [OpenAI API密钥管理](https://platform.openai.com/api-keys)
- [GitHub Secrets管理](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Git敏感信息清理工具](https://github.com/newren/git-filter-repo)

## 📞 安全问题报告

如果发现安全问题，请通过以下方式报告：

- 创建私有Issue
- 发送邮件到项目维护者
- 不要在公开渠道讨论安全漏洞

---

**记住：安全第一，预防胜于治疗！** 🛡️
