#!/usr/bin/env python3
"""
AI爆款项目雷达 - 安装验证脚本
"""

import sys
import os
from pathlib import Path
import importlib.util


def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (满足要求)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (需要3.8+)")
        return False


def check_directories():
    """检查目录结构"""
    print("\n📁 检查目录结构...")
    
    required_dirs = [
        'src',
        'src/crawlers',
        'src/ai_analysis', 
        'src/utils',
        'src/visualization',
        'config',
        'tests',
        'docs',
        '.github/workflows'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0


def check_files():
    """检查关键文件"""
    print("\n📄 检查关键文件...")
    
    required_files = [
        'main.py',
        'demo.py',
        'requirements.txt',
        'README.md',
        'config/settings.yaml.example',
        'config/prompts.yaml',
        '.env.example',
        '.gitignore'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0


def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        'requests',
        'bs4',  # beautifulsoup4 imports as bs4
        'lxml',
        'openai',
        'pandas',
        'numpy',
        'matplotlib',
        'plotly',
        'yaml',  # pyyaml imports as yaml
        'dotenv',  # python-dotenv imports as dotenv
        'loguru',
        'aiohttp'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is not None:
                print(f"✅ {package}")
            else:
                print(f"❌ {package}")
                missing_packages.append(package)
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 安装缺失的包: pip install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0


def check_configuration():
    """检查配置文件"""
    print("\n⚙️  检查配置...")
    
    config_file = Path('config/settings.yaml')
    env_file = Path('.env')
    
    issues = []
    
    if config_file.exists():
        print("✅ config/settings.yaml 存在")
    else:
        print("⚠️  config/settings.yaml 不存在")
        issues.append("需要复制 config/settings.yaml.example 到 config/settings.yaml")
    
    if env_file.exists():
        print("✅ .env 存在")
        
        # 检查API密钥
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=' in content and 'your-openai-api-key-here' not in content:
                print("✅ OpenAI API密钥已配置")
            else:
                print("⚠️  OpenAI API密钥未配置")
                issues.append("需要在 .env 文件中设置有效的 OPENAI_API_KEY")
    else:
        print("⚠️  .env 不存在")
        issues.append("需要复制 .env.example 到 .env 并配置API密钥")
    
    return len(issues) == 0, issues


def check_imports():
    """检查模块导入"""
    print("\n🔧 检查模块导入...")
    
    # 添加src到路径
    sys.path.insert(0, str(Path('src')))
    
    modules_to_test = [
        ('utils.config', 'load_config'),
        ('utils.logger', 'setup_logger'),
        ('utils.data_cleaner', 'DataCleaner'),
        ('crawlers.github_crawler', 'GitHubCrawler'),
        ('crawlers.producthunt_crawler', 'ProductHuntCrawler'),
        ('ai_analysis.classifier', 'AIProjectClassifier'),
        ('ai_analysis.keyword_extractor', 'KeywordExtractor'),
        ('ai_analysis.summarizer', 'ProjectSummarizer'),
        ('visualization.chart_generator', 'ChartGenerator'),
        ('visualization.report_generator', 'ReportGenerator')
    ]
    
    failed_imports = []
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - {str(e)}")
            failed_imports.append(f"{module_name}.{class_name}")
    
    return len(failed_imports) == 0


def check_github_actions():
    """检查GitHub Actions配置"""
    print("\n🚀 检查GitHub Actions...")
    
    workflow_files = [
        '.github/workflows/daily-update.yml',
        '.github/workflows/manual-update.yml',
        '.github/workflows/test.yml'
    ]
    
    missing_workflows = []
    for workflow in workflow_files:
        if Path(workflow).exists():
            print(f"✅ {workflow}")
        else:
            print(f"❌ {workflow}")
            missing_workflows.append(workflow)
    
    return len(missing_workflows) == 0


def create_missing_directories():
    """创建缺失的目录"""
    print("\n📁 创建必要目录...")
    
    dirs_to_create = [
        'data/raw',
        'data/processed', 
        'data/archive',
        'output/reports',
        'output/charts',
        'output/web',
        'logs'
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")


def main():
    """主函数"""
    print("🔍 AI爆款项目雷达 - 安装验证")
    print("=" * 50)
    
    all_checks_passed = True
    
    # 1. 检查Python版本
    if not check_python_version():
        all_checks_passed = False
    
    # 2. 检查目录结构
    if not check_directories():
        all_checks_passed = False
    
    # 3. 检查关键文件
    if not check_files():
        all_checks_passed = False
    
    # 4. 检查依赖包
    if not check_dependencies():
        all_checks_passed = False
    
    # 5. 检查配置
    config_ok, config_issues = check_configuration()
    if not config_ok:
        all_checks_passed = False
    
    # 6. 检查模块导入
    if not check_imports():
        all_checks_passed = False
    
    # 7. 检查GitHub Actions
    if not check_github_actions():
        print("⚠️  GitHub Actions配置不完整（部署时需要）")
    
    # 8. 创建必要目录
    create_missing_directories()
    
    # 总结
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 所有检查通过！系统已准备就绪")
        print("\n💡 下一步:")
        print("1. 运行演示: python demo.py")
        print("2. 执行完整流程: python main.py --mode daily")
        print("3. 运行测试: pytest tests/ -v")
    else:
        print("❌ 发现问题，请解决后重新运行验证")
        print("\n🔧 解决步骤:")
        
        if not Path('config/settings.yaml').exists():
            print("1. cp config/settings.yaml.example config/settings.yaml")
        
        if not Path('.env').exists():
            print("2. cp .env.example .env")
            print("3. 编辑 .env 文件，设置 OPENAI_API_KEY")
        
        print("4. pip install -r requirements.txt")
        
        if config_issues:
            print("\n⚠️  配置问题:")
            for issue in config_issues:
                print(f"   - {issue}")
    
    print("\n📚 更多帮助:")
    print("- 安装指南: docs/INSTALLATION.md")
    print("- 使用指南: docs/USAGE.md")
    print("- 部署指南: docs/DEPLOYMENT.md")


if __name__ == "__main__":
    main()
