#!/usr/bin/env python3
"""
验证GitHub Pages部署的脚本
"""

import requests
import time
from pathlib import Path


def check_page_status(url, expected_content=None):
    """检查页面状态"""
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {url} - 状态码: {response.status_code}")
            
            if expected_content:
                if expected_content in response.text:
                    print(f"   ✅ 包含预期内容: {expected_content[:50]}...")
                else:
                    print(f"   ⚠️  未找到预期内容: {expected_content[:50]}...")
            
            return True
        else:
            print(f"❌ {url} - 状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {url} - 请求失败: {e}")
        return False


def main():
    """主函数"""
    print("🔍 验证GitHub Pages部署状态")
    print("=" * 50)
    
    base_url = "https://huangzhongping.github.io/AIProjectCrawler"
    
    # 要检查的页面
    pages_to_check = [
        {
            "url": f"{base_url}/",
            "name": "主页",
            "expected": "AI爆款项目雷达"
        },
        {
            "url": f"{base_url}/history.html",
            "name": "历史记录页面",
            "expected": "历史记录"
        },
        {
            "url": f"{base_url}/reports/ai-trends-2025-07-23.html",
            "name": "今日报告",
            "expected": "AI项目趋势报告"
        }
    ]
    
    print("正在检查页面状态...")
    print()
    
    all_success = True
    
    for page in pages_to_check:
        print(f"🔗 检查 {page['name']}:")
        success = check_page_status(page['url'], page['expected'])
        
        if not success:
            all_success = False
        
        print()
        time.sleep(1)  # 避免请求过快
    
    if all_success:
        print("🎉 所有页面都可以正常访问！")
        print()
        print("📱 访问链接:")
        print(f"- 主页: {base_url}/")
        print(f"- 历史记录: {base_url}/history.html")
        print(f"- 今日报告: {base_url}/reports/ai-trends-2025-07-23.html")
    else:
        print("⚠️  部分页面可能还在部署中，请稍后再试")
        print()
        print("💡 如果问题持续存在:")
        print("1. 检查GitHub Actions是否成功运行")
        print("2. 确认GitHub Pages设置正确")
        print("3. 等待几分钟后重新检查")
    
    # 检查本地文件
    print("\n📁 本地文件检查:")
    local_files = [
        "pages/index.html",
        "pages/history.html",
        "output/history.html"
    ]
    
    for file_path in local_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"✅ {file_path} - 大小: {size:,} 字节")
        else:
            print(f"❌ {file_path} - 文件不存在")


if __name__ == "__main__":
    main()
