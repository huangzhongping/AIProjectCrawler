#!/usr/bin/env python3
"""
AI爆款项目雷达 - 快速安装脚本
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("请安装Python 3.8或更高版本")
        return False


def create_directories():
    """创建必要目录"""
    print("📁 创建项目目录...")
    
    directories = [
        'data/raw',
        'data/processed',
        'data/archive', 
        'output/reports',
        'output/charts',
        'output/web',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")
    
    print("✅ 目录创建完成")


def setup_config():
    """设置配置文件"""
    print("⚙️ 设置配置文件...")
    
    # 复制配置文件
    if not Path('config/settings.yaml').exists():
        if Path('config/settings.yaml.example').exists():
            import shutil
            shutil.copy('config/settings.yaml.example', 'config/settings.yaml')
            print("✅ 复制 settings.yaml")
        else:
            print("❌ 找不到 settings.yaml.example")
            return False
    
    # 复制环境变量文件
    if not Path('.env').exists():
        if Path('.env.example').exists():
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ 复制 .env")
        else:
            print("❌ 找不到 .env.example")
            return False
    
    print("⚠️  请编辑 .env 文件，设置你的 OPENAI_API_KEY")
    return True


def install_dependencies():
    """安装Python依赖"""
    print("📦 安装Python依赖...")
    
    # 检查是否在虚拟环境中
    if sys.prefix == sys.base_prefix:
        print("⚠️  建议在虚拟环境中运行")
        response = input("是否继续安装到全局环境？(y/N): ")
        if response.lower() != 'y':
            print("请先创建虚拟环境:")
            print("  python -m venv venv")
            print("  source venv/bin/activate  # Linux/Mac")
            print("  venv\\Scripts\\activate     # Windows")
            return False
    
    # 升级pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip"):
        return False
    
    # 安装依赖
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "安装依赖包"):
        print("❌ 依赖安装失败")
        print("💡 尝试手动安装核心依赖:")
        print("pip install requests beautifulsoup4 openai pandas plotly pyyaml python-dotenv loguru aiohttp")
        return False
    
    return True


def run_verification():
    """运行验证脚本"""
    print("🔍 运行安装验证...")
    
    try:
        result = subprocess.run([sys.executable, 'verify_setup.py'], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("警告:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ 验证超时")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 AI爆款项目雷达 - 快速安装")
    print("=" * 40)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 创建目录
    create_directories()
    
    # 设置配置
    if not setup_config():
        print("❌ 配置设置失败")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        return
    
    # 运行验证
    print("\n" + "=" * 40)
    print("🔍 验证安装...")
    
    if run_verification():
        print("\n🎉 安装成功！")
        print("\n💡 下一步:")
        print("1. 编辑 .env 文件，设置 OPENAI_API_KEY")
        print("2. 运行演示: python demo.py")
        print("3. 执行完整流程: python main.py --mode daily")
    else:
        print("\n⚠️  安装可能存在问题，请检查上面的输出")
        print("💡 手动验证: python verify_setup.py")
    
    print("\n📚 更多帮助:")
    print("- 安装指南: docs/INSTALLATION.md")
    print("- 使用指南: docs/USAGE.md")


if __name__ == "__main__":
    main()
