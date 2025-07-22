#!/usr/bin/env python3
"""
AI爆款项目雷达 - 纯关键词模式
强制禁用所有API调用，仅使用关键词分析
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

# 强制清除所有API密钥环境变量
os.environ.pop('OPENAI_API_KEY', None)
os.environ.pop('HUGGINGFACE_API_KEY', None)

from main import AITrendingRadar


async def main():
    """主函数"""
    print("🚀 AI爆款项目雷达 - 纯关键词模式")
    print("=" * 50)
    print("此模式完全禁用API调用，仅使用关键词分析")
    print("✅ 完全免费，无配额限制")
    print("✅ 速度快，准确率高")
    print()
    
    try:
        # 创建雷达实例
        radar = AITrendingRadar()
        
        # 强制禁用API
        radar.config['api']['openai']['api_key'] = ""
        
        # 确保AI分类器使用关键词模式
        if hasattr(radar, 'ai_classifier'):
            radar.ai_classifier.client = None
            radar.ai_classifier.api_key = ""
        
        print("🔧 配置信息:")
        print("   - API模式: 完全禁用")
        print("   - 分析方式: 关键词匹配")
        print(f"   - AI关键词数量: {len(radar.config.get('ai_analysis', {}).get('ai_keywords', []))}")
        print(f"   - 相关性阈值: {radar.config.get('ai_analysis', {}).get('ai_relevance_threshold', 0.7)}")
        print()
        
        # 执行每日更新
        print("🚀 开始执行每日更新...")
        result = await radar.run_daily_update()
        
        if result.get('success', False):
            print("\n🎉 运行成功！")
            print(f"   - 总项目数: {result.get('total_projects_count', 0)}")
            print(f"   - AI项目数: {result.get('ai_projects_count', 0)}")
            
            report_path = result.get('report_path')
            if report_path:
                print(f"   - 报告文件: {report_path}")
            
            # 显示发现的AI项目
            if result.get('ai_projects_count', 0) > 0:
                print(f"\n🏆 发现了 {result.get('ai_projects_count')} 个AI项目！")
                print("查看详细报告:")
                print(f"   - HTML: output/reports/ai-trends-{result.get('date', 'today')}.html")
                print(f"   - Markdown: output/reports/ai-trends-{result.get('date', 'today')}.md")
            else:
                print("\n⚠️  未发现AI项目，可能需要调整关键词或阈值")
        else:
            print(f"\n❌ 运行失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"\n💥 运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n💡 关键词分析模式说明:")
    print("- 基于90+个精选AI关键词进行智能匹配")
    print("- 分析项目名称、描述、标签等多个维度")
    print("- 完全本地运行，无需网络API调用")
    print("- 识别准确率高，适合日常使用")
    print("\n🔧 如需调整:")
    print("- 修改 config/settings.yaml 中的 ai_keywords 列表")
    print("- 调整 ai_relevance_threshold 阈值（0.1-1.0）")


if __name__ == "__main__":
    asyncio.run(main())
