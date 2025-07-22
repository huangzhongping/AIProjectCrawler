#!/usr/bin/env python3
"""
AI爆款项目雷达演示脚本
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from utils.logger import setup_logger
from utils.config import load_config, validate_config, create_directories
from utils.data_cleaner import DataCleaner
from ai_analysis.classifier import AIProjectClassifier
from ai_analysis.keyword_extractor import KeywordExtractor
from ai_analysis.summarizer import ProjectSummarizer
from visualization.chart_generator import ChartGenerator
from visualization.report_generator import ReportGenerator


def create_demo_data():
    """创建演示数据"""
    return [
        {
            'name': 'awesome-ai-chatbot',
            'description': 'An advanced AI chatbot powered by large language models and natural language processing',
            'url': 'https://github.com/demo/awesome-ai-chatbot',
            'stars': 2500,
            'forks': 450,
            'language': 'Python',
            'author': 'ai-researcher',
            'tags': ['ai', 'chatbot', 'nlp', 'llm'],
            'source': 'github',
            'created_at': '2023-01-15T10:00:00Z',
            'updated_at': '2023-12-01T15:30:00Z'
        },
        {
            'name': 'ml-vision-toolkit',
            'description': 'A comprehensive computer vision toolkit for machine learning with deep learning models',
            'url': 'https://github.com/demo/ml-vision-toolkit',
            'stars': 1800,
            'forks': 320,
            'language': 'Python',
            'author': 'vision-lab',
            'tags': ['machine-learning', 'computer-vision', 'deep-learning'],
            'source': 'github',
            'created_at': '2023-03-20T14:00:00Z',
            'updated_at': '2023-11-28T09:15:00Z'
        },
        {
            'name': 'neural-network-framework',
            'description': 'A lightweight neural network framework for building and training AI models',
            'url': 'https://github.com/demo/neural-network-framework',
            'stars': 3200,
            'forks': 680,
            'language': 'JavaScript',
            'author': 'ml-team',
            'tags': ['neural-networks', 'ai', 'framework'],
            'source': 'github',
            'created_at': '2023-02-10T08:30:00Z',
            'updated_at': '2023-12-01T11:45:00Z'
        },
        {
            'name': 'data-science-platform',
            'description': 'An integrated platform for data science and machine learning workflows',
            'url': 'https://producthunt.com/posts/data-science-platform',
            'stars': 150,
            'votes': 89,
            'language': 'TypeScript',
            'author': 'data-startup',
            'tags': ['data-science', 'ml', 'platform'],
            'source': 'producthunt',
            'created_at': '2023-06-01T12:00:00Z',
            'updated_at': '2023-11-30T16:20:00Z'
        },
        {
            'name': 'simple-web-app',
            'description': 'A simple web application for managing tasks and projects',
            'url': 'https://github.com/demo/simple-web-app',
            'stars': 45,
            'forks': 12,
            'language': 'JavaScript',
            'author': 'web-dev',
            'tags': ['web', 'app', 'productivity'],
            'source': 'github',
            'created_at': '2023-08-15T09:00:00Z',
            'updated_at': '2023-11-25T14:30:00Z'
        }
    ]


async def run_demo():
    """运行演示"""
    print("🚀 AI爆款项目雷达演示开始")
    print("=" * 50)
    
    try:
        # 1. 加载配置
        print("📋 1. 加载配置...")
        config = load_config()
        
        if not validate_config(config):
            print("❌ 配置验证失败，使用演示模式")
            # 使用演示配置
            config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'
        
        create_directories(config)
        
        # 设置日志
        logger = setup_logger(
            log_level="INFO",
            log_file="logs/demo.log"
        )
        
        print("✅ 配置加载完成")
        
        # 2. 创建演示数据
        print("\n📊 2. 准备演示数据...")
        demo_projects = create_demo_data()
        print(f"✅ 创建了 {len(demo_projects)} 个演示项目")
        
        # 3. 数据清洗
        print("\n🧹 3. 数据清洗...")
        cleaner = DataCleaner(config)
        cleaned_projects = cleaner.clean_and_deduplicate(demo_projects)
        print(f"✅ 清洗完成，有效项目: {len(cleaned_projects)}")
        
        # 4. AI分析
        print("\n🤖 4. AI分析...")
        classifier = AIProjectClassifier(config)
        extractor = KeywordExtractor(config)
        summarizer = ProjectSummarizer(config)
        
        ai_projects = []
        for i, project in enumerate(cleaned_projects, 1):
            print(f"   分析项目 {i}/{len(cleaned_projects)}: {project['name']}")
            
            # AI分类
            classification = await classifier.classify(project)
            
            if classification['is_ai_related']:
                # 关键词提取
                keywords = await extractor.extract(project)
                
                # 项目总结
                summary = await summarizer.summarize(project)
                
                project.update({
                    'ai_classification': classification,
                    'keywords': keywords,
                    'summary': summary
                })
                ai_projects.append(project)
                
                print(f"      ✅ AI相关 (置信度: {classification['confidence_score']:.2f})")
            else:
                print(f"      ❌ 非AI项目")
        
        print(f"✅ AI分析完成，发现 {len(ai_projects)} 个AI项目")
        
        # 5. 生成可视化
        print("\n📈 5. 生成可视化...")
        chart_generator = ChartGenerator(config)
        
        try:
            charts = chart_generator.generate_daily_charts(ai_projects)
            print(f"✅ 生成了 {len(charts)} 个图表")
            
            for chart_name, chart_path in charts.items():
                if chart_path and Path(chart_path).exists():
                    print(f"   📊 {chart_name}: {chart_path}")
                else:
                    print(f"   ❌ {chart_name}: 生成失败")
        except Exception as e:
            print(f"⚠️  图表生成部分失败: {e}")
            charts = {}
        
        # 6. 生成报告
        print("\n📝 6. 生成报告...")
        report_generator = ReportGenerator(config)
        
        try:
            report = await report_generator.generate_daily_report(ai_projects, charts)
            
            # 保存报告
            today = datetime.now().strftime("%Y-%m-%d")
            output_dir = Path("output/reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # HTML报告
            html_path = output_dir / f"demo-report-{today}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(report['html'])
            
            # Markdown报告
            md_path = output_dir / f"demo-report-{today}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(report['markdown'])
            
            print(f"✅ 报告生成完成")
            print(f"   📄 HTML报告: {html_path}")
            print(f"   📄 Markdown报告: {md_path}")
            
        except Exception as e:
            print(f"⚠️  报告生成失败: {e}")
        
        # 7. 显示结果摘要
        print("\n📋 7. 结果摘要")
        print("=" * 30)
        print(f"总项目数: {len(demo_projects)}")
        print(f"有效项目数: {len(cleaned_projects)}")
        print(f"AI项目数: {len(ai_projects)}")
        
        if ai_projects:
            print("\n🏆 发现的AI项目:")
            for i, project in enumerate(ai_projects, 1):
                classification = project.get('ai_classification', {})
                confidence = classification.get('confidence_score', 0)
                print(f"   {i}. {project['name']} (置信度: {confidence:.2f})")
                print(f"      {project['description'][:80]}...")
                
                keywords = project.get('keywords', {}).get('keywords', [])
                if keywords:
                    print(f"      关键词: {', '.join(keywords[:5])}")
                print()
        
        print("🎉 演示完成！")
        
        # 8. 提供下一步建议
        print("\n💡 下一步建议:")
        print("1. 设置OpenAI API密钥以获得更好的AI分析效果")
        print("2. 运行 'python main.py --mode daily' 执行完整流程")
        print("3. 查看生成的报告文件")
        print("4. 配置GitHub Actions实现自动化")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        print("请检查配置和依赖是否正确安装")
        return False
    
    return True


def main():
    """主函数"""
    print("AI爆款项目雷达 - 演示模式")
    print("这个演示将展示系统的主要功能")
    print()
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return
    
    # 检查必要目录
    required_dirs = ['src', 'config']
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"❌ 缺少必要目录: {dir_name}")
            return
    
    # 运行演示
    try:
        success = asyncio.run(run_demo())
        if success:
            print("\n✅ 演示成功完成！")
        else:
            print("\n❌ 演示未能完全成功")
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n💥 演示失败: {e}")


if __name__ == "__main__":
    main()
