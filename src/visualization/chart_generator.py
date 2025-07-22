"""
图表生成器
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from loguru import logger


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化图表生成器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # 图表配置
        chart_config = config.get('visualization', {}).get('charts', {})
        self.theme = chart_config.get('theme', 'plotly_white')
        self.width = chart_config.get('width', 1200)
        self.height = chart_config.get('height', 800)
        self.font_size = chart_config.get('font_size', 12)
        
        # 输出路径
        output_path = config.get('data', {}).get('paths', {}).get('output', 'output')
        self.charts_path = Path(output_path) / "charts"
        self.charts_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("图表生成器初始化完成")
    
    def generate_daily_charts(self, projects: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        生成每日图表
        
        Args:
            projects: 项目列表
        
        Returns:
            图表文件路径字典
        """
        logger.info(f"开始生成图表，共 {len(projects)} 个项目")
        
        charts = {}
        
        try:
            # 1. 编程语言分布图
            charts['language_distribution'] = self.create_language_distribution_chart(projects)
            
            # 2. 星标数分布图
            charts['stars_distribution'] = self.create_stars_distribution_chart(projects)
            
            # 3. 关键词云图
            charts['keyword_cloud'] = self.create_keyword_chart(projects)
            
            # 4. AI分类分布图
            charts['ai_categories'] = self.create_ai_categories_chart(projects)
            
            # 5. 数据源分布图
            charts['source_distribution'] = self.create_source_distribution_chart(projects)
            
            # 6. 综合仪表板
            charts['dashboard'] = self.create_dashboard(projects)
            
            logger.info(f"图表生成完成，共生成 {len(charts)} 个图表")
            
        except Exception as e:
            logger.error(f"图表生成失败: {e}")
        
        return charts
    
    def create_language_distribution_chart(self, projects: List[Dict[str, Any]]) -> str:
        """
        创建编程语言分布图
        
        Args:
            projects: 项目列表
        
        Returns:
            图表文件路径
        """
        # 统计编程语言
        languages = [p.get('language', '未知') for p in projects if p.get('language')]
        language_counts = Counter(languages)
        
        # 取前10个
        top_languages = dict(language_counts.most_common(10))
        
        # 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=list(top_languages.keys()),
            values=list(top_languages.values()),
            hole=0.3,
            textinfo='label+percent',
            textfont_size=self.font_size
        )])
        
        fig.update_layout(
            title={
                'text': 'AI项目编程语言分布',
                'x': 0.5,
                'font': {'size': self.font_size + 4}
            },
            template=self.theme,
            width=self.width // 2,
            height=self.height // 2,
            showlegend=True
        )
        
        # 保存图表
        filepath = self.charts_path / "language_distribution.html"
        fig.write_html(str(filepath))
        
        return str(filepath)
    
    def create_stars_distribution_chart(self, projects: List[Dict[str, Any]]) -> str:
        """
        创建星标数分布图
        
        Args:
            projects: 项目列表
        
        Returns:
            图表文件路径
        """
        # 获取星标数据
        stars_data = [p.get('stars', 0) for p in projects]
        
        # 创建直方图
        fig = go.Figure(data=[go.Histogram(
            x=stars_data,
            nbinsx=20,
            opacity=0.7,
            marker_color='skyblue'
        )])
        
        fig.update_layout(
            title={
                'text': 'AI项目星标数分布',
                'x': 0.5,
                'font': {'size': self.font_size + 4}
            },
            xaxis_title='星标数',
            yaxis_title='项目数量',
            template=self.theme,
            width=self.width // 2,
            height=self.height // 2
        )
        
        # 保存图表
        filepath = self.charts_path / "stars_distribution.html"
        fig.write_html(str(filepath))
        
        return str(filepath)
    
    def create_keyword_chart(self, projects: List[Dict[str, Any]]) -> str:
        """
        创建关键词图表
        
        Args:
            projects: 项目列表
        
        Returns:
            图表文件路径
        """
        # 收集所有关键词
        all_keywords = []
        for project in projects:
            keywords = project.get('keywords', {}).get('keywords', [])
            all_keywords.extend(keywords)
        
        # 统计关键词频率
        keyword_counts = Counter(all_keywords)
        top_keywords = dict(keyword_counts.most_common(20))
        
        # 创建条形图
        fig = go.Figure(data=[go.Bar(
            x=list(top_keywords.values()),
            y=list(top_keywords.keys()),
            orientation='h',
            marker_color='lightcoral'
        )])
        
        fig.update_layout(
            title={
                'text': '热门AI技术关键词',
                'x': 0.5,
                'font': {'size': self.font_size + 4}
            },
            xaxis_title='出现次数',
            yaxis_title='关键词',
            template=self.theme,
            width=self.width,
            height=self.height // 2
        )
        
        # 保存图表
        filepath = self.charts_path / "keyword_chart.html"
        fig.write_html(str(filepath))
        
        return str(filepath)
    
    def create_ai_categories_chart(self, projects: List[Dict[str, Any]]) -> str:
        """
        创建AI分类分布图
        
        Args:
            projects: 项目列表
        
        Returns:
            图表文件路径
        """
        # 收集AI分类
        all_categories = []
        for project in projects:
            ai_classification = project.get('ai_classification', {})
            categories = ai_classification.get('ai_categories', [])
            all_categories.extend(categories)
        
        # 统计分类
        category_counts = Counter(all_categories)
        
        if not category_counts:
            # 如果没有分类数据，创建一个默认图表
            fig = go.Figure()
            fig.add_annotation(
                text="暂无AI分类数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
        else:
            # 创建条形图
            fig = go.Figure(data=[go.Bar(
                x=list(category_counts.keys()),
                y=list(category_counts.values()),
                marker_color='lightgreen'
            )])
        
        fig.update_layout(
            title={
                'text': 'AI项目分类分布',
                'x': 0.5,
                'font': {'size': self.font_size + 4}
            },
            xaxis_title='AI分类',
            yaxis_title='项目数量',
            template=self.theme,
            width=self.width // 2,
            height=self.height // 2
        )
        
        # 保存图表
        filepath = self.charts_path / "ai_categories.html"
        fig.write_html(str(filepath))
        
        return str(filepath)
    
    def create_source_distribution_chart(self, projects: List[Dict[str, Any]]) -> str:
        """
        创建数据源分布图
        
        Args:
            projects: 项目列表
        
        Returns:
            图表文件路径
        """
        # 统计数据源
        sources = [p.get('source', '未知') for p in projects]
        source_counts = Counter(sources)
        
        # 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=list(source_counts.keys()),
            values=list(source_counts.values()),
            textinfo='label+value',
            textfont_size=self.font_size
        )])
        
        fig.update_layout(
            title={
                'text': '数据源分布',
                'x': 0.5,
                'font': {'size': self.font_size + 4}
            },
            template=self.theme,
            width=self.width // 2,
            height=self.height // 2
        )
        
        # 保存图表
        filepath = self.charts_path / "source_distribution.html"
        fig.write_html(str(filepath))
        
        return str(filepath)
    
    def create_dashboard(self, projects: List[Dict[str, Any]]) -> str:
        """
        创建综合仪表板
        
        Args:
            projects: 项目列表
        
        Returns:
            图表文件路径
        """
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('编程语言分布', '星标数分布', '数据源分布', '项目统计'),
            specs=[[{"type": "pie"}, {"type": "histogram"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # 1. 编程语言分布
        languages = [p.get('language', '未知') for p in projects if p.get('language')]
        language_counts = Counter(languages)
        top_languages = dict(language_counts.most_common(5))
        
        fig.add_trace(go.Pie(
            labels=list(top_languages.keys()),
            values=list(top_languages.values()),
            name="编程语言"
        ), row=1, col=1)
        
        # 2. 星标数分布
        stars_data = [p.get('stars', 0) for p in projects]
        fig.add_trace(go.Histogram(
            x=stars_data,
            name="星标数",
            nbinsx=10
        ), row=1, col=2)
        
        # 3. 数据源分布
        sources = [p.get('source', '未知') for p in projects]
        source_counts = Counter(sources)
        
        fig.add_trace(go.Pie(
            labels=list(source_counts.keys()),
            values=list(source_counts.values()),
            name="数据源"
        ), row=2, col=1)
        
        # 4. 项目统计
        total_projects = len(projects)
        avg_stars = sum(p.get('stars', 0) for p in projects) / len(projects) if projects else 0
        
        fig.add_trace(go.Bar(
            x=['总项目数', '平均星标数'],
            y=[total_projects, avg_stars],
            name="统计"
        ), row=2, col=2)
        
        fig.update_layout(
            title={
                'text': 'AI项目趋势仪表板',
                'x': 0.5,
                'font': {'size': self.font_size + 6}
            },
            template=self.theme,
            width=self.width,
            height=self.height,
            showlegend=False
        )
        
        # 保存图表
        filepath = self.charts_path / "dashboard.html"
        fig.write_html(str(filepath))
        
        return str(filepath)
