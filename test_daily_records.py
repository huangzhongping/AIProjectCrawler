#!/usr/bin/env python3
"""
测试每日记录功能
"""

import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from utils.config import load_config
from utils.daily_records import DailyRecordsManager
from visualization.history_generator import HistoryPageGenerator


def create_test_data():
    """创建测试数据"""
    # 模拟项目数据
    projects = [
        {
            'name': 'test-ai-project-1',
            'url': 'https://github.com/test/ai-project-1',
            'stars': 1500,
            'language': 'Python',
            'description': 'A machine learning project for computer vision',
            'tags': ['ai', 'ml', 'computer-vision']
        },
        {
            'name': 'test-ai-project-2',
            'url': 'https://github.com/test/ai-project-2',
            'stars': 2300,
            'language': 'JavaScript',
            'description': 'Natural language processing toolkit',
            'tags': ['nlp', 'ai', 'javascript']
        },
        {
            'name': 'test-web-app',
            'url': 'https://github.com/test/web-app',
            'stars': 450,
            'language': 'React',
            'description': 'A simple web application',
            'tags': ['web', 'react']
        }
    ]
    
    # 模拟AI项目（带分类结果）
    ai_projects = []
    for project in projects[:2]:  # 前两个是AI项目
        project['ai_classification'] = {
            'is_ai_related': True,
            'confidence_score': 0.9,
            'reasoning': 'Contains AI-related keywords',
            'ai_categories': ['Machine Learning', 'Artificial Intelligence'],
            'tech_stack': ['Python', 'TensorFlow'],
            'analysis_method': 'keywords'
        }
        ai_projects.append(project)
    
    return projects, ai_projects


async def test_daily_records():
    """测试每日记录功能"""
    print("🧪 测试每日记录功能")
    print("=" * 50)
    
    try:
        # 加载配置
        config = load_config()
        
        # 创建记录管理器
        records_manager = DailyRecordsManager(config)
        print("✅ 记录管理器初始化成功")
        
        # 创建测试数据
        projects, ai_projects = create_test_data()
        print(f"✅ 测试数据创建成功: {len(projects)} 个项目，{len(ai_projects)} 个AI项目")
        
        # 测试保存记录（最近几天的数据）
        for i in range(7):
            test_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 稍微变化数据
            test_projects = projects.copy()
            test_ai_projects = ai_projects.copy()
            
            # 随机调整星标数
            import random
            for project in test_projects:
                project['stars'] += random.randint(-100, 500)
            
            # 保存记录
            success = records_manager.save_daily_record(test_date, test_projects, test_ai_projects)
            if success:
                print(f"✅ {test_date} 记录保存成功")
            else:
                print(f"❌ {test_date} 记录保存失败")
        
        # 测试获取记录
        print("\n📊 测试获取记录...")
        today = datetime.now().strftime('%Y-%m-%d')
        record = records_manager.get_daily_record(today)
        
        if record:
            print(f"✅ 获取今日记录成功:")
            print(f"   - 总项目数: {record['summary']['total_projects']}")
            print(f"   - AI项目数: {record['summary']['ai_projects']}")
            print(f"   - 最热项目: {record['summary']['top_project_name']}")
            print(f"   - 项目详情: {len(record['projects'])} 个")
        else:
            print("❌ 获取今日记录失败")
        
        # 测试获取最近记录
        print("\n📅 测试获取最近记录...")
        recent_records = records_manager.get_recent_records(7)
        print(f"✅ 获取最近7天记录成功: {len(recent_records)} 条")
        
        for record in recent_records[:3]:  # 显示前3条
            print(f"   - {record['date']}: {record['ai_projects']} 个AI项目")
        
        # 测试趋势分析
        print("\n📈 测试趋势分析...")
        trend_data = records_manager.get_trend_analysis(7)
        
        if trend_data:
            print("✅ 趋势分析数据获取成功:")
            print(f"   - 每日数据: {len(trend_data.get('daily_counts', []))} 天")
            print(f"   - 语言趋势: {len(trend_data.get('language_trends', []))} 种")
            print(f"   - 分类趋势: {len(trend_data.get('category_trends', []))} 类")
        else:
            print("❌ 趋势分析数据获取失败")
        
        # 测试历史页面生成
        print("\n🌐 测试历史页面生成...")
        history_generator = HistoryPageGenerator(config)
        history_path = history_generator.generate_history_page(7)
        
        if history_path and Path(history_path).exists():
            print(f"✅ 历史页面生成成功: {history_path}")
            print(f"   - 文件大小: {Path(history_path).stat().st_size} 字节")
        else:
            print("❌ 历史页面生成失败")
        
        # 测试导出功能
        print("\n💾 测试导出功能...")
        start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        export_path = records_manager.export_records(start_date, end_date, 'json')
        
        if export_path and Path(export_path).exists():
            print(f"✅ 数据导出成功: {export_path}")
            print(f"   - 文件大小: {Path(export_path).stat().st_size} 字节")
        else:
            print("❌ 数据导出失败")
        
        print("\n🎉 所有测试完成！")
        
        return True
        
    except Exception as e:
        print(f"\n💥 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🚀 AI项目雷达 - 每日记录功能测试")
    print("=" * 60)
    
    success = await test_daily_records()
    
    if success:
        print("\n✅ 测试成功！每日记录功能正常工作")
        print("\n💡 下一步:")
        print("1. 运行 python3 main.py 执行完整流程")
        print("2. 查看生成的历史记录页面")
        print("3. 启用GitHub Actions定时任务")
    else:
        print("\n❌ 测试失败，请检查错误信息")


if __name__ == "__main__":
    asyncio.run(main())
