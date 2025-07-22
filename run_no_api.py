#!/usr/bin/env python3
"""
AI爆款项目雷达 - 无API模式运行脚本
专门用于在没有OpenAI API配额的情况下运行
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

# 强制禁用API
os.environ.pop('OPENAI_API_KEY', None)

from main import AITrendingRadar


async def main():
    """主函数"""
    print("🚀 AI爆款项目雷达 - 无API模式")
    print("=" * 50)
    print("此模式使用关键词分析，不需要OpenAI API")
    print()
    
    try:
        # 使用无API配置文件
        config_path = "config/settings_no_api.yaml"
        
        if not Path(config_path).exists():
            print(f"❌ 配置文件不存在: {config_path}")
            print("使用默认配置...")
            config_path = None
        
        # 创建雷达实例
        radar = AITrendingRadar(config_path=config_path)
        
        # 确保API密钥为空
        radar.config['api']['openai']['api_key'] = ""
        
        print("🔧 配置信息:")
        print(f"   - API模式: 禁用 (使用关键词分析)")
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
    
    print("\n💡 提示:")
    print("- 此模式不需要OpenAI API，完全基于关键词分析")
    print("- 如需更精确的AI分析，请充值OpenAI账户后使用API模式")
    print("- 可以通过修改 config/settings_no_api.yaml 调整关键词和阈值")


if __name__ == "__main__":
    asyncio.run(main())
