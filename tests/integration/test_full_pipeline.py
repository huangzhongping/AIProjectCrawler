"""
完整流水线集成测试
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, AsyncMock

# 导入主要模块
from utils.config import load_config
from utils.data_cleaner import DataCleaner
from utils.storage import DataStorage
from ai_analysis.classifier import AIProjectClassifier
from ai_analysis.keyword_extractor import KeywordExtractor
from ai_analysis.summarizer import ProjectSummarizer
from visualization.chart_generator import ChartGenerator
from visualization.report_generator import ReportGenerator


class TestFullPipeline:
    """完整流水线测试"""
    
    @pytest.fixture
    def pipeline_config(self, test_config, temp_dir):
        """流水线测试配置"""
        # 确保所有路径都指向临时目录
        config = test_config.copy()
        config['data']['paths'] = {
            'raw_data': str(temp_dir / 'raw'),
            'processed_data': str(temp_dir / 'processed'),
            'archive_data': str(temp_dir / 'archive'),
            'output': str(temp_dir / 'output')
        }
        
        # 创建目录
        for path in config['data']['paths'].values():
            Path(path).mkdir(parents=True, exist_ok=True)
        
        return config
    
    def test_data_processing_pipeline(self, pipeline_config, sample_projects):
        """测试数据处理流水线"""
        # 1. 数据清洗
        cleaner = DataCleaner(pipeline_config)
        cleaned_data = cleaner.clean_and_deduplicate(sample_projects)
        
        assert len(cleaned_data) <= len(sample_projects)  # 可能有去重
        assert all('cleaned_at' in project for project in cleaned_data)
        
        # 2. 数据存储
        storage = DataStorage(pipeline_config)
        storage.save_daily_data(cleaned_data, '2023-12-01')
        
        # 验证数据保存
        saved_data = storage.get_projects_by_date('2023-12-01')
        assert len(saved_data) == len(cleaned_data)
        
        # 验证统计数据
        stats = storage.get_daily_stats('2023-12-01')
        assert stats is not None
        assert stats['total_projects'] == len(cleaned_data)
    
    @pytest.mark.asyncio
    async def test_ai_analysis_pipeline(self, pipeline_config, sample_projects):
        """测试AI分析流水线"""
        # 使用关键词分析（不需要API）
        pipeline_config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'
        
        # 1. AI分类
        classifier = AIProjectClassifier(pipeline_config)
        ai_projects = []
        
        for project in sample_projects:
            classification = await classifier.classify(project)
            if classification['is_ai_related']:
                project['ai_classification'] = classification
                ai_projects.append(project)
        
        assert len(ai_projects) > 0  # 应该有AI项目
        
        # 2. 关键词提取
        extractor = KeywordExtractor(pipeline_config)
        for project in ai_projects:
            keywords = await extractor.extract(project)
            project['keywords'] = keywords
            assert 'keywords' in keywords
            assert isinstance(keywords['keywords'], list)
        
        # 3. 项目总结
        summarizer = ProjectSummarizer(pipeline_config)
        for project in ai_projects:
            summary = await summarizer.summarize(project)
            project['summary'] = summary
            assert 'summary' in summary
            assert len(summary['summary']) > 0
    
    def test_visualization_pipeline(self, pipeline_config, sample_projects):
        """测试可视化流水线"""
        # 准备带有AI分析结果的项目数据
        processed_projects = []
        for project in sample_projects:
            project.update({
                'ai_classification': {
                    'is_ai_related': True,
                    'confidence_score': 0.8,
                    'ai_categories': ['Machine Learning']
                },
                'keywords': {
                    'keywords': ['ai', 'machine learning', 'python'],
                    'categories': {'技术栈': ['python'], '应用领域': ['ai']}
                },
                'summary': {
                    'summary': '这是一个AI项目',
                    'highlights': ['使用机器学习', '开源项目'],
                    'use_cases': ['数据分析', '自动化']
                }
            })
            processed_projects.append(project)
        
        # 1. 图表生成
        chart_generator = ChartGenerator(pipeline_config)
        charts = chart_generator.generate_daily_charts(processed_projects)
        
        assert isinstance(charts, dict)
        assert len(charts) > 0
        
        # 验证图表文件存在
        for chart_name, chart_path in charts.items():
            if chart_path:  # 某些图表可能生成失败
                assert Path(chart_path).exists()
    
    @pytest.mark.asyncio
    async def test_report_generation_pipeline(self, pipeline_config, sample_projects):
        """测试报告生成流水线"""
        # 准备数据
        processed_projects = []
        for project in sample_projects:
            project.update({
                'ai_classification': {
                    'is_ai_related': True,
                    'confidence_score': 0.8,
                    'ai_categories': ['Machine Learning']
                },
                'keywords': {
                    'keywords': ['ai', 'machine learning', 'python'],
                    'categories': {'技术栈': ['python'], '应用领域': ['ai']}
                },
                'summary': {
                    'summary': '这是一个AI项目',
                    'highlights': ['使用机器学习', '开源项目'],
                    'use_cases': ['数据分析', '自动化']
                }
            })
            processed_projects.append(project)
        
        # 生成图表
        chart_generator = ChartGenerator(pipeline_config)
        charts = chart_generator.generate_daily_charts(processed_projects)
        
        # 生成报告
        pipeline_config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'  # 使用基础分析
        report_generator = ReportGenerator(pipeline_config)
        report = await report_generator.generate_daily_report(processed_projects, charts)
        
        assert 'html' in report
        assert 'markdown' in report
        assert 'data' in report
        
        # 验证HTML报告内容
        html_content = report['html']
        assert 'AI爆款项目雷达' in html_content
        assert len(html_content) > 1000  # 应该是完整的HTML
        
        # 验证Markdown报告内容
        md_content = report['markdown']
        assert '# 🚀 AI爆款项目雷达' in md_content
        assert '## 📊 今日概览' in md_content
    
    @pytest.mark.asyncio
    async def test_end_to_end_pipeline(self, pipeline_config, sample_projects):
        """测试端到端流水线"""
        # 模拟完整的每日更新流程
        
        # 1. 数据清洗
        cleaner = DataCleaner(pipeline_config)
        cleaned_data = cleaner.clean_and_deduplicate(sample_projects)
        
        # 2. AI分析（使用关键词分析）
        pipeline_config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'
        
        classifier = AIProjectClassifier(pipeline_config)
        extractor = KeywordExtractor(pipeline_config)
        summarizer = ProjectSummarizer(pipeline_config)
        
        ai_projects = []
        for project in cleaned_data:
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
        
        assert len(ai_projects) > 0
        
        # 3. 数据存储
        storage = DataStorage(pipeline_config)
        storage.save_daily_data(ai_projects, '2023-12-01')
        
        # 4. 可视化
        chart_generator = ChartGenerator(pipeline_config)
        charts = chart_generator.generate_daily_charts(ai_projects)
        
        report_generator = ReportGenerator(pipeline_config)
        report = await report_generator.generate_daily_report(ai_projects, charts)
        
        # 5. 验证最终结果
        assert len(ai_projects) <= len(sample_projects)
        assert all('ai_classification' in p for p in ai_projects)
        assert all('keywords' in p for p in ai_projects)
        assert all('summary' in p for p in ai_projects)
        
        # 验证报告生成
        assert 'html' in report
        assert 'markdown' in report
        assert len(report['html']) > 1000
        assert len(report['markdown']) > 500
        
        # 验证数据库存储
        saved_projects = storage.get_projects_by_date('2023-12-01')
        assert len(saved_projects) == len(ai_projects)
        
        stats = storage.get_daily_stats('2023-12-01')
        assert stats['ai_projects'] == len(ai_projects)
    
    def test_error_handling_pipeline(self, pipeline_config):
        """测试错误处理流水线"""
        # 测试空数据处理
        cleaner = DataCleaner(pipeline_config)
        empty_result = cleaner.clean_and_deduplicate([])
        assert empty_result == []
        
        # 测试无效数据处理
        invalid_data = [
            {'name': ''},  # 无效名称
            {'description': 'test'},  # 缺少名称
            {}  # 空数据
        ]
        
        cleaned = cleaner.clean_and_deduplicate(invalid_data)
        assert len(cleaned) == 0  # 所有数据都应该被过滤掉
        
        # 测试存储错误处理
        storage = DataStorage(pipeline_config)
        
        # 测试获取不存在的数据
        non_existent = storage.get_projects_by_date('1900-01-01')
        assert non_existent == []
        
        stats = storage.get_daily_stats('1900-01-01')
        assert stats is None
    
    def test_configuration_validation(self, temp_dir):
        """测试配置验证"""
        from utils.config import validate_config, create_directories
        
        # 测试有效配置
        valid_config = {
            'api': {'openai': {'api_key': 'test-key'}},
            'crawler': {'request': {'timeout': 30}},
            'data': {'paths': {'raw_data': str(temp_dir / 'raw')}},
            'logging': {'level': 'INFO'}
        }
        
        assert validate_config(valid_config) is True
        
        # 测试创建目录
        create_directories(valid_config)
        assert (temp_dir / 'raw').exists()
        
        # 测试无效配置
        invalid_config = {}
        assert validate_config(invalid_config) is False
