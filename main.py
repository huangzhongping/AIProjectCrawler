#!/usr/bin/env python3
"""
AI爆款项目雷达 - 主程序入口
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from utils.logger import setup_logger
from utils.config import load_config
from crawlers.github_crawler import GitHubCrawler
from crawlers.producthunt_crawler import ProductHuntCrawler
from ai_analysis.classifier import AIProjectClassifier
from ai_analysis.keyword_extractor import KeywordExtractor
from ai_analysis.summarizer import ProjectSummarizer
from utils.data_cleaner import DataCleaner
from utils.storage import DataStorage
from utils.daily_records import DailyRecordsManager
from visualization.report_generator import ReportGenerator
from visualization.chart_generator import ChartGenerator
from visualization.history_generator import HistoryPageGenerator


class AITrendingRadar:
    """AI爆款项目雷达主类"""
    
    def __init__(self, config_path=None):
        """初始化"""
        self.config = load_config(config_path)
        self.logger = setup_logger()
        
        # 初始化各个模块
        self.github_crawler = GitHubCrawler(self.config)
        self.producthunt_crawler = ProductHuntCrawler(self.config)
        self.ai_classifier = AIProjectClassifier(self.config)
        self.keyword_extractor = KeywordExtractor(self.config)
        self.summarizer = ProjectSummarizer(self.config)
        self.data_cleaner = DataCleaner(self.config)
        self.storage = DataStorage(self.config)
        self.daily_records = DailyRecordsManager(self.config)
        self.report_generator = ReportGenerator(self.config)
        self.chart_generator = ChartGenerator(self.config)
        self.history_generator = HistoryPageGenerator(self.config)
    
    async def run_daily_update(self):
        """执行每日更新流程"""
        self.logger.info("开始执行每日AI项目雷达更新...")
        
        try:
            # 1. 数据抓取
            self.logger.info("步骤1: 开始数据抓取...")
            github_data = await self.github_crawler.crawl()
            producthunt_data = await self.producthunt_crawler.crawl()
            
            # 2. 数据合并和清洗
            self.logger.info("步骤2: 数据清洗和标准化...")
            raw_data = github_data + producthunt_data
            cleaned_data = self.data_cleaner.clean_and_deduplicate(raw_data)
            
            # 3. AI分析
            self.logger.info("步骤3: AI项目分析...")
            ai_projects = []
            for project in cleaned_data:
                # AI相关性判断
                classification = await self.ai_classifier.classify(project)
                if classification['is_ai_related']:
                    # 关键词提取
                    keywords = await self.keyword_extractor.extract(project)
                    # 项目总结
                    summary = await self.summarizer.summarize(project)
                    
                    project.update({
                        'ai_classification': classification,
                        'keywords': keywords,
                        'summary': summary
                    })
                    ai_projects.append(project)
            
            # 4. 数据存储
            self.logger.info("步骤4: 数据存储...")
            today = datetime.now().strftime("%Y-%m-%d")
            self.storage.save_daily_data(ai_projects, today)
            
            # 5. 生成可视化报告
            self.logger.info("步骤5: 生成可视化报告...")
            # 生成图表
            charts = self.chart_generator.generate_daily_charts(ai_projects)
            # 生成报告
            report = await self.report_generator.generate_daily_report(ai_projects, charts)
            
            # 6. 保存输出文件
            self.logger.info("步骤6: 保存输出文件...")
            output_dir = Path(self.config['data']['paths']['output'])
            
            # 保存HTML报告
            html_path = output_dir / "reports" / f"ai-trends-{today}.html"
            html_path.parent.mkdir(parents=True, exist_ok=True)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(report['html'])
            
            # 保存Markdown报告
            md_path = output_dir / "reports" / f"ai-trends-{today}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(report['markdown'])
            
            # 更新最新报告链接
            latest_html = output_dir / "web" / "index.html"
            latest_html.parent.mkdir(parents=True, exist_ok=True)
            with open(latest_html, 'w', encoding='utf-8') as f:
                f.write(report['html'])

            # 保存每日记录
            self.logger.info("步骤6: 保存每日记录...")
            self.daily_records.save_daily_record(today, cleaned_data, ai_projects)

            # 生成历史记录页面
            self.logger.info("步骤7: 生成历史记录页面...")
            history_path = self.history_generator.generate_history_page()

            self.logger.info(f"✅ 每日更新完成！发现 {len(ai_projects)} 个AI相关项目")
            self.logger.info(f"📊 报告已保存到: {html_path}")
            self.logger.info(f"📚 历史记录页面: {history_path}")
            
            return {
                'success': True,
                'ai_projects_count': len(ai_projects),
                'total_projects_count': len(cleaned_data),
                'report_path': str(html_path)
            }
            
        except Exception as e:
            self.logger.error(f"❌ 每日更新失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def run_analysis_only(self, data_file: str):
        """仅运行AI分析（用于测试）"""
        self.logger.info(f"开始分析数据文件: {data_file}")
        
        try:
            # 加载数据
            data = self.storage.load_data(data_file)
            
            # AI分析
            ai_projects = []
            for project in data:
                classification = await self.ai_classifier.classify(project)
                if classification['is_ai_related']:
                    keywords = await self.keyword_extractor.extract(project)
                    summary = await self.summarizer.summarize(project)
                    
                    project.update({
                        'ai_classification': classification,
                        'keywords': keywords,
                        'summary': summary
                    })
                    ai_projects.append(project)
            
            self.logger.info(f"✅ 分析完成！发现 {len(ai_projects)} 个AI相关项目")
            return ai_projects
            
        except Exception as e:
            self.logger.error(f"❌ 分析失败: {str(e)}")
            raise


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI爆款项目雷达")
    parser.add_argument("--mode", choices=["daily", "analysis"], default="daily",
                       help="运行模式: daily=每日更新, analysis=仅分析")
    parser.add_argument("--data-file", help="分析模式下的数据文件路径")
    
    args = parser.parse_args()
    
    radar = AITrendingRadar()
    
    if args.mode == "daily":
        result = await radar.run_daily_update()
        if result['success']:
            print(f"✅ 每日更新成功！发现 {result['ai_projects_count']} 个AI项目")
            print(f"📊 报告路径: {result['report_path']}")
        else:
            print(f"❌ 更新失败: {result['error']}")
            sys.exit(1)
    
    elif args.mode == "analysis":
        if not args.data_file:
            print("❌ 分析模式需要指定 --data-file 参数")
            sys.exit(1)
        
        ai_projects = await radar.run_analysis_only(args.data_file)
        print(f"✅ 分析完成！发现 {len(ai_projects)} 个AI项目")


if __name__ == "__main__":
    asyncio.run(main())
