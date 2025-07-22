#!/usr/bin/env python3
"""
AI爆款项目雷达 - 免费AI模型运行脚本
支持多种免费AI服务
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from utils.config import load_config
from utils.logger import setup_logger
from utils.data_cleaner import DataCleaner
from crawlers.github_crawler import GitHubCrawler
from ai_analysis.free_classifier import FreeAIClassifier
from visualization.report_generator import ReportGenerator
from datetime import datetime


class FreeAITrendingRadar:
    """免费AI趋势雷达"""
    
    def __init__(self, provider='keywords'):
        """
        初始化
        
        Args:
            provider: AI提供商 ('keywords', 'ollama', 'huggingface')
        """
        self.provider = provider
        
        # 根据提供商选择配置文件
        if provider == 'ollama':
            config_path = 'config/settings_ollama.yaml'
        elif provider == 'huggingface':
            config_path = 'config/settings_huggingface.yaml'
        else:
            config_path = 'config/settings_no_api.yaml'
        
        self.config = load_config(config_path)
        self.config['api']['provider'] = provider
        
        self.logger = setup_logger()
        
        # 初始化组件
        self.github_crawler = GitHubCrawler(self.config)
        self.data_cleaner = DataCleaner(self.config)
        self.ai_classifier = FreeAIClassifier(self.config)
        self.report_generator = ReportGenerator(self.config)
    
    async def run_daily_update(self):
        """执行每日更新"""
        try:
            self.logger.info(f"开始每日更新 - 使用 {self.provider} 模式")
            
            # 1. 爬取数据
            self.logger.info("🕷️ 开始爬取GitHub数据...")
            github_data = await self.github_crawler.crawl()
            self.logger.info(f"GitHub爬取完成: {len(github_data)} 个项目")
            
            # 2. 数据清洗
            self.logger.info("🧹 开始数据清洗...")
            cleaned_data = self.data_cleaner.clean_and_deduplicate(github_data)
            self.logger.info(f"数据清洗完成: {len(cleaned_data)} 个有效项目")
            
            # 3. AI分析
            self.logger.info(f"🤖 开始AI分析 ({self.provider} 模式)...")
            ai_projects = []
            
            for i, project in enumerate(cleaned_data, 1):
                self.logger.info(f"分析项目 {i}/{len(cleaned_data)}: {project['name']}")
                
                classification = await self.ai_classifier.classify(project)
                
                if classification['is_ai_related']:
                    project['ai_classification'] = classification
                    ai_projects.append(project)
                    self.logger.info(f"✅ AI项目: {project['name']} (置信度: {classification['confidence_score']:.2f})")
            
            self.logger.info(f"AI分析完成: 发现 {len(ai_projects)} 个AI项目")
            
            # 4. 生成报告
            self.logger.info("📝 生成报告...")
            report = await self.report_generator.generate_daily_report(ai_projects, {})
            
            # 保存报告
            today = datetime.now().strftime("%Y-%m-%d")
            output_dir = Path("output/reports")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # HTML报告
            html_path = output_dir / f"free-ai-trends-{today}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(report['html'])
            
            # Markdown报告
            md_path = output_dir / f"free-ai-trends-{today}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(report['markdown'])
            
            self.logger.info(f"报告生成完成: {html_path}")
            
            return {
                'success': True,
                'total_projects_count': len(cleaned_data),
                'ai_projects_count': len(ai_projects),
                'report_path': str(html_path),
                'provider': self.provider
            }
            
        except Exception as e:
            self.logger.error(f"运行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': self.provider
            }


async def main():
    """主函数"""
    print("🚀 AI爆款项目雷达 - 免费AI模式")
    print("=" * 50)
    
    # 选择AI提供商
    print("请选择AI分析模式:")
    print("1. 关键词分析 (推荐，无需安装)")
    print("2. Ollama本地模型 (需要安装Ollama)")
    print("3. Hugging Face免费API (需要注册)")
    
    choice = input("请输入选择 (1-3，默认1): ").strip() or "1"
    
    if choice == "2":
        provider = "ollama"
        print("\n📋 Ollama使用说明:")
        print("1. 安装Ollama: https://ollama.ai/")
        print("2. 下载模型: ollama pull llama3.2:3b")
        print("3. 启动服务: ollama serve")
        
        confirm = input("确认Ollama已安装并运行? (y/N): ").strip().lower()
        if confirm != 'y':
            print("请先安装并启动Ollama")
            return
            
    elif choice == "3":
        provider = "huggingface"
        print("\n📋 Hugging Face使用说明:")
        print("1. 注册账户: https://huggingface.co/")
        print("2. 获取API Token: https://huggingface.co/settings/tokens")
        print("3. 设置环境变量: export HUGGINGFACE_API_KEY=your_token")
        
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            print("❌ 请设置HUGGINGFACE_API_KEY环境变量")
            return
    else:
        provider = "keywords"
        print("\n✅ 使用关键词分析模式")
    
    print(f"\n🔧 启动 {provider} 模式...")
    
    # 创建雷达实例
    radar = FreeAITrendingRadar(provider=provider)
    
    # 执行更新
    result = await radar.run_daily_update()
    
    # 显示结果
    print("\n" + "=" * 50)
    if result['success']:
        print("🎉 运行成功！")
        print(f"   - AI分析模式: {result['provider']}")
        print(f"   - 总项目数: {result['total_projects_count']}")
        print(f"   - AI项目数: {result['ai_projects_count']}")
        print(f"   - 报告文件: {result['report_path']}")
        
        if result['ai_projects_count'] > 0:
            print(f"\n🏆 发现了 {result['ai_projects_count']} 个AI项目！")
            print("查看详细报告:")
            print(f"   - HTML: {result['report_path']}")
            print(f"   - Markdown: {result['report_path'].replace('.html', '.md')}")
    else:
        print(f"❌ 运行失败: {result['error']}")
    
    print("\n💡 免费AI模式说明:")
    print("- 关键词模式: 基于90+个AI关键词，准确率高")
    print("- Ollama模式: 本地运行，隐私安全，需要安装")
    print("- Hugging Face模式: 云端免费API，需要注册")


if __name__ == "__main__":
    asyncio.run(main())
