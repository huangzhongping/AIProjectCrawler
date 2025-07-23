#!/usr/bin/env python3
"""
手动部署GitHub Pages的脚本
确保所有文件都被正确复制到pages目录
"""

import shutil
import os
from pathlib import Path


def deploy_to_pages():
    """部署文件到pages目录"""
    print("🚀 开始部署GitHub Pages...")
    
    # 创建pages目录
    pages_dir = Path("pages")
    if pages_dir.exists():
        shutil.rmtree(pages_dir)
    pages_dir.mkdir(exist_ok=True)
    
    print("✅ 创建pages目录")
    
    # 复制主页文件
    docs_dir = Path("docs")
    if (docs_dir / "index.html").exists():
        shutil.copy2(docs_dir / "index.html", pages_dir / "index.html")
        print("✅ 复制主页文件")
    
    if (docs_dir / "_config.yml").exists():
        shutil.copy2(docs_dir / "_config.yml", pages_dir / "_config.yml")
        print("✅ 复制配置文件")
    
    # 复制输出文件
    output_dir = Path("output")
    if output_dir.exists():
        # 复制历史记录页面
        if (output_dir / "history.html").exists():
            shutil.copy2(output_dir / "history.html", pages_dir / "history.html")
            print("✅ 复制历史记录页面")
        
        # 复制报告文件
        reports_dir = output_dir / "reports"
        if reports_dir.exists():
            pages_reports_dir = pages_dir / "reports"
            pages_reports_dir.mkdir(exist_ok=True)
            
            for file in reports_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, pages_reports_dir / file.name)
            print(f"✅ 复制报告文件: {len(list(reports_dir.glob('*')))} 个文件")
        
        # 复制图表文件
        charts_dir = output_dir / "charts"
        if charts_dir.exists():
            pages_charts_dir = pages_dir / "charts"
            pages_charts_dir.mkdir(exist_ok=True)
            
            for file in charts_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, pages_charts_dir / file.name)
            print(f"✅ 复制图表文件: {len(list(charts_dir.glob('*')))} 个文件")
        
        # 复制其他HTML和JSON文件
        for file in output_dir.glob("*.html"):
            shutil.copy2(file, pages_dir / file.name)
        
        for file in output_dir.glob("*.json"):
            shutil.copy2(file, pages_dir / file.name)
        
        print("✅ 复制其他输出文件")
    
    # 检查结果
    pages_files = list(pages_dir.glob("**/*"))
    print(f"\n📁 Pages目录内容 ({len(pages_files)} 个文件):")
    for file in sorted(pages_files):
        if file.is_file():
            print(f"   - {file.relative_to(pages_dir)}")
    
    # 验证关键文件
    required_files = ["index.html", "history.html"]
    missing_files = []
    
    for file in required_files:
        if not (pages_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 缺少关键文件: {missing_files}")
        return False
    else:
        print(f"\n✅ 所有关键文件都已准备就绪")
        return True


def main():
    """主函数"""
    print("🌐 GitHub Pages 部署脚本")
    print("=" * 40)
    
    try:
        success = deploy_to_pages()
        
        if success:
            print("\n🎉 部署准备完成！")
            print("\n💡 下一步:")
            print("1. 提交pages目录到Git")
            print("2. 推送到GitHub触发Actions")
            print("3. 等待GitHub Pages更新")
            print("\n🔗 预期访问地址:")
            print("- 主页: https://huangzhongping.github.io/AIProjectCrawler/")
            print("- 历史: https://huangzhongping.github.io/AIProjectCrawler/history.html")
        else:
            print("\n❌ 部署准备失败，请检查文件")
            
    except Exception as e:
        print(f"\n💥 部署失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
