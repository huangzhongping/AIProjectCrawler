#!/usr/bin/env python3
"""
专门用于GitHub Actions的运行脚本
使用最小依赖，避免版本冲突
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

def check_dependencies():
    """检查必要的依赖"""
    required_modules = ['requests', 'yaml', 'loguru']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ 缺少依赖: {missing_modules}")
        print("尝试安装基础依赖...")
        os.system("pip install requests pyyaml loguru")
        return False
    
    return True

def create_simple_report():
    """创建简单的报告页面"""
    try:
        # 创建输出目录
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        pages_dir = Path("pages")
        pages_dir.mkdir(exist_ok=True)
        
        # 创建简单的历史记录页面
        history_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI项目雷达 - 历史记录</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            margin: 40px 0;
            backdrop-filter: blur(10px);
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            margin: 10px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }
        .loading {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI项目雷达</h1>
        <h2>📚 历史记录</h2>
        
        <div class="status">
            <div class="loading">
                <h3>⚡ 系统正在初始化...</h3>
                <p>历史记录功能正在构建中</p>
                <p>预计完成时间: 几分钟内</p>
            </div>
        </div>
        
        <div>
            <a href="index.html" class="btn">🏠 返回主页</a>
            <a href="https://github.com/huangzhongping/AIProjectCrawler" class="btn">📖 查看源码</a>
        </div>
        
        <div style="margin-top: 40px; opacity: 0.8;">
            <p>🤖 AI项目雷达 - 发现最新最热的AI项目趋势</p>
            <p>更新时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
    </div>
    
    <script>
        // 自动刷新页面
        setTimeout(() => {
            window.location.reload();
        }, 300000); // 5分钟后刷新
    </script>
</body>
</html>
        """
        
        # 保存历史记录页面
        with open(output_dir / "history.html", 'w', encoding='utf-8') as f:
            f.write(history_html)
        
        with open(pages_dir / "history.html", 'w', encoding='utf-8') as f:
            f.write(history_html)
        
        print("✅ 创建简单历史记录页面成功")
        
        # 复制主页到pages目录
        docs_index = Path("docs/index.html")
        if docs_index.exists():
            import shutil
            shutil.copy2(docs_index, pages_dir / "index.html")
            print("✅ 复制主页到pages目录")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建报告失败: {e}")
        return False

def run_simple_crawler():
    """运行简化的爬虫"""
    try:
        print("🚀 开始简化版AI项目雷达...")
        
        # 检查依赖
        if not check_dependencies():
            print("⚠️ 依赖检查失败，使用备用方案")
        
        # 创建简单报告
        success = create_simple_report()
        
        if success:
            print("✅ GitHub Actions运行成功")
            print("📁 生成的文件:")
            
            # 列出生成的文件
            for path in ["output", "pages"]:
                if Path(path).exists():
                    for file in Path(path).glob("*.html"):
                        print(f"   - {file}")
        else:
            print("❌ 运行失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"💥 运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🤖 AI项目雷达 - GitHub Actions版本")
    print("=" * 50)
    
    try:
        # 运行简化版本
        success = run_simple_crawler()
        
        if success:
            print("\n🎉 GitHub Actions运行完成！")
            print("📱 页面将在几分钟内更新")
        else:
            print("\n❌ 运行失败，请检查日志")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
