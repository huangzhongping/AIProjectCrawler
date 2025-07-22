"""
报告生成器
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter
from openai import AsyncOpenAI
from loguru import logger


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化报告生成器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # OpenAI配置（用于生成趋势分析）
        api_config = config.get('api', {}).get('openai', {})
        self.api_key = api_config.get('api_key')
        self.model = api_config.get('model', 'gpt-3.5-turbo')
        
        if not self.api_key or self.api_key.startswith('${'):
            logger.warning("OpenAI API密钥未设置，将使用基础报告生成")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
        
        # 报告配置
        report_config = config.get('visualization', {}).get('reports', {})
        self.max_projects = report_config.get('max_projects_per_report', 50)
        
        # 模板路径
        self.template_path = Path(__file__).parent / "templates"
        self.template_path.mkdir(exist_ok=True)
        
        # 加载提示词
        self.trend_prompt = self._load_trend_analysis_prompt()
        
        logger.info("报告生成器初始化完成")
    
    def _load_trend_analysis_prompt(self) -> str:
        """
        加载趋势分析提示词
        
        Returns:
            提示词模板
        """
        try:
            import yaml
            
            prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"
            if prompts_path.exists():
                with open(prompts_path, 'r', encoding='utf-8') as f:
                    prompts = yaml.safe_load(f)
                    return prompts.get('trend_analysis_prompt', self._get_default_trend_prompt())
        except Exception as e:
            logger.warning(f"加载趋势分析提示词失败: {e}")
        
        return self._get_default_trend_prompt()
    
    def _get_default_trend_prompt(self) -> str:
        """
        获取默认趋势分析提示词
        
        Returns:
            默认提示词
        """
        return """基于以下AI项目数据，分析当前的技术趋势和热点方向。

项目数据概览：
{projects_summary}

请分析：
1. 最热门的AI技术方向
2. 新兴的技术趋势
3. 开发者关注的重点领域
4. 技术发展的变化趋势

请返回JSON格式：
{
    "hot_trends": ["热门趋势1", "热门趋势2", ...],
    "emerging_tech": ["新兴技术1", "新兴技术2", ...],
    "focus_areas": ["重点领域1", "重点领域2", ...],
    "trend_analysis": "详细的趋势分析文本"
}"""
    
    async def generate_daily_report(self, projects: List[Dict[str, Any]], charts: Dict[str, str]) -> Dict[str, str]:
        """
        生成每日报告
        
        Args:
            projects: 项目列表
            charts: 图表文件路径字典
        
        Returns:
            报告内容字典 (html, markdown)
        """
        logger.info(f"开始生成每日报告，共 {len(projects)} 个项目")
        
        # 生成报告数据
        report_data = await self._prepare_report_data(projects)
        
        # 生成HTML报告
        html_report = self._generate_html_report(report_data, charts)
        
        # 生成Markdown报告
        markdown_report = self._generate_markdown_report(report_data)
        
        logger.info("每日报告生成完成")
        
        return {
            'html': html_report,
            'markdown': markdown_report,
            'data': report_data
        }
    
    async def _prepare_report_data(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        准备报告数据
        
        Args:
            projects: 项目列表
        
        Returns:
            报告数据字典
        """
        # 基础统计
        total_projects = len(projects)
        
        # 按星标数排序，取前N个
        top_projects = sorted(projects, key=lambda x: x.get('stars', 0), reverse=True)[:self.max_projects]
        
        # 统计编程语言
        languages = [p.get('language', '') for p in projects if p.get('language')]
        language_stats = dict(Counter(languages).most_common(10))
        
        # 统计关键词
        all_keywords = []
        for project in projects:
            keywords = project.get('keywords', {}).get('keywords', [])
            all_keywords.extend(keywords)
        keyword_stats = dict(Counter(all_keywords).most_common(20))
        
        # 统计数据源
        sources = [p.get('source', '') for p in projects]
        source_stats = dict(Counter(sources))
        
        # 生成趋势分析
        trend_analysis = await self._generate_trend_analysis(projects)
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_projects': total_projects,
            'top_projects': top_projects,
            'language_stats': language_stats,
            'keyword_stats': keyword_stats,
            'source_stats': source_stats,
            'trend_analysis': trend_analysis,
            'generated_at': datetime.now().isoformat()
        }
    
    async def _generate_trend_analysis(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成趋势分析
        
        Args:
            projects: 项目列表
        
        Returns:
            趋势分析结果
        """
        if not self.client:
            return self._generate_basic_trend_analysis(projects)
        
        try:
            # 准备项目概览数据
            projects_summary = self._prepare_projects_summary(projects)
            
            # 构建提示词
            prompt = self.trend_prompt.format(projects_summary=projects_summary)
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI技术趋势分析师。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # 解析响应
            content = response.choices[0].message.content
            result = self._parse_trend_analysis(content)
            
            logger.debug("AI趋势分析生成完成")
            return result
            
        except Exception as e:
            logger.error(f"AI趋势分析生成失败: {e}")
            return self._generate_basic_trend_analysis(projects)
    
    def _prepare_projects_summary(self, projects: List[Dict[str, Any]]) -> str:
        """
        准备项目概览数据
        
        Args:
            projects: 项目列表
        
        Returns:
            项目概览字符串
        """
        # 统计信息
        total_count = len(projects)
        
        # 热门语言
        languages = [p.get('language', '') for p in projects if p.get('language')]
        top_languages = dict(Counter(languages).most_common(5))
        
        # 热门关键词
        all_keywords = []
        for project in projects:
            keywords = project.get('keywords', {}).get('keywords', [])
            all_keywords.extend(keywords)
        top_keywords = dict(Counter(all_keywords).most_common(10))
        
        # 高星项目
        high_star_projects = [p for p in projects if p.get('stars', 0) > 100]
        
        summary = f"""
总项目数: {total_count}
高星项目数 (>100 stars): {len(high_star_projects)}

热门编程语言:
{json.dumps(top_languages, ensure_ascii=False, indent=2)}

热门技术关键词:
{json.dumps(top_keywords, ensure_ascii=False, indent=2)}

代表性项目:
"""
        
        # 添加代表性项目
        for i, project in enumerate(projects[:5]):
            summary += f"{i+1}. {project.get('name', 'Unknown')} - {project.get('description', '')[:100]}...\n"
        
        return summary
    
    def _parse_trend_analysis(self, content: str) -> Dict[str, Any]:
        """
        解析趋势分析结果
        
        Args:
            content: API响应内容
        
        Returns:
            解析后的结果
        """
        try:
            # 尝试解析JSON
            if '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                return {
                    'hot_trends': result.get('hot_trends', []),
                    'emerging_tech': result.get('emerging_tech', []),
                    'focus_areas': result.get('focus_areas', []),
                    'trend_analysis': result.get('trend_analysis', ''),
                    'analysis_method': 'ai'
                }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"解析趋势分析结果失败: {e}")
        
        # 如果解析失败，使用原始内容
        return {
            'hot_trends': [],
            'emerging_tech': [],
            'focus_areas': [],
            'trend_analysis': content,
            'analysis_method': 'text_fallback'
        }
    
    def _generate_basic_trend_analysis(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成基础趋势分析（后备方案）
        
        Args:
            projects: 项目列表
        
        Returns:
            基础趋势分析结果
        """
        # 统计热门技术
        all_keywords = []
        for project in projects:
            keywords = project.get('keywords', {}).get('keywords', [])
            all_keywords.extend(keywords)
        
        keyword_counts = Counter(all_keywords)
        hot_trends = [kw for kw, count in keyword_counts.most_common(5)]
        
        # 统计编程语言
        languages = [p.get('language', '') for p in projects if p.get('language')]
        language_counts = Counter(languages)
        focus_areas = [lang for lang, count in language_counts.most_common(3)]
        
        # 生成基础分析文本
        analysis_text = f"""
基于今日收集的 {len(projects)} 个AI项目数据分析：

🔥 热门技术趋势：
{', '.join(hot_trends[:5]) if hot_trends else '暂无数据'}

💻 主要编程语言：
{', '.join(focus_areas) if focus_areas else '暂无数据'}

📊 项目分布：
- 总项目数：{len(projects)}
- 高星项目（>100 stars）：{len([p for p in projects if p.get('stars', 0) > 100])}
- 平均星标数：{sum(p.get('stars', 0) for p in projects) // len(projects) if projects else 0}

这些数据反映了当前AI技术发展的热点方向和开发者关注的重点领域。
"""
        
        return {
            'hot_trends': hot_trends,
            'emerging_tech': hot_trends[:3],
            'focus_areas': focus_areas,
            'trend_analysis': analysis_text,
            'analysis_method': 'basic'
        }

    def _generate_html_report(self, report_data: Dict[str, Any], charts: Dict[str, str]) -> str:
        """
        生成HTML报告

        Args:
            report_data: 报告数据
            charts: 图表文件路径字典

        Returns:
            HTML报告内容
        """
        date = report_data['date']
        total_projects = report_data['total_projects']
        top_projects = report_data['top_projects']
        trend_analysis = report_data['trend_analysis']

        # 生成项目列表HTML
        projects_html = ""
        for i, project in enumerate(top_projects[:20], 1):
            stars = project.get('stars', 0)
            language = project.get('language', '未知')
            description = project.get('description', '')[:200] + '...' if len(project.get('description', '')) > 200 else project.get('description', '')
            url = project.get('url', '#')

            projects_html += f"""
            <div class="project-item">
                <h3>#{i} <a href="{url}" target="_blank">{project.get('name', 'Unknown')}</a></h3>
                <div class="project-meta">
                    <span class="stars">⭐ {stars}</span>
                    <span class="language">💻 {language}</span>
                    <span class="source">📊 {project.get('source', 'Unknown')}</span>
                </div>
                <p class="description">{description}</p>
            </div>
            """

        # 生成趋势分析HTML
        trends_html = ""
        if trend_analysis.get('hot_trends'):
            trends_html += "<h3>🔥 热门趋势</h3><ul>"
            for trend in trend_analysis['hot_trends'][:5]:
                trends_html += f"<li>{trend}</li>"
            trends_html += "</ul>"

        if trend_analysis.get('emerging_tech'):
            trends_html += "<h3>🚀 新兴技术</h3><ul>"
            for tech in trend_analysis['emerging_tech'][:5]:
                trends_html += f"<li>{tech}</li>"
            trends_html += "</ul>"

        # 生成图表嵌入HTML
        charts_html = ""
        for chart_name, chart_path in charts.items():
            if Path(chart_path).exists():
                with open(chart_path, 'r', encoding='utf-8') as f:
                    chart_content = f.read()
                    # 提取图表的div内容
                    if '<div' in chart_content and '</div>' in chart_content:
                        start = chart_content.find('<div')
                        end = chart_content.rfind('</div>') + 6
                        chart_div = chart_content[start:end]
                        charts_html += f'<div class="chart-container">{chart_div}</div>'

        # HTML模板
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI爆款项目雷达 - {date}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .section-header {{
            background: #667eea;
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: bold;
        }}
        .section-content {{
            padding: 20px;
        }}
        .project-item {{
            border-bottom: 1px solid #eee;
            padding: 20px 0;
        }}
        .project-item:last-child {{
            border-bottom: none;
        }}
        .project-item h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .project-item h3 a {{
            color: #667eea;
            text-decoration: none;
        }}
        .project-item h3 a:hover {{
            text-decoration: underline;
        }}
        .project-meta {{
            margin-bottom: 10px;
        }}
        .project-meta span {{
            display: inline-block;
            margin-right: 15px;
            padding: 4px 8px;
            background: #f1f3f4;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .description {{
            color: #666;
            margin: 0;
        }}
        .trend-analysis {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 40px;
        }}
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="header">
        <h1>🚀 AI爆款项目雷达</h1>
        <p>发现最新最热的AI项目趋势 | {date}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{total_projects}</div>
            <div>AI项目总数</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len([p for p in top_projects if p.get('stars', 0) > 100])}</div>
            <div>高星项目</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{sum(p.get('stars', 0) for p in top_projects) // len(top_projects) if top_projects else 0}</div>
            <div>平均星标数</div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">📈 趋势分析</div>
        <div class="section-content">
            <div class="trend-analysis">
                {trends_html}
                <div style="margin-top: 20px;">
                    <h3>📊 详细分析</h3>
                    <p>{trend_analysis.get('trend_analysis', '暂无详细分析')}</p>
                </div>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">📊 数据可视化</div>
        <div class="section-content">
            {charts_html}
        </div>
    </div>

    <div class="section">
        <div class="section-header">🏆 热门AI项目</div>
        <div class="section-content">
            {projects_html}
        </div>
    </div>

    <div class="footer">
        <p>📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>🤖 由AI爆款项目雷达自动生成</p>
    </div>
</body>
</html>
        """

        return html_template

    def _generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """
        生成Markdown报告

        Args:
            report_data: 报告数据

        Returns:
            Markdown报告内容
        """
        date = report_data['date']
        total_projects = report_data['total_projects']
        top_projects = report_data['top_projects']
        trend_analysis = report_data['trend_analysis']
        language_stats = report_data['language_stats']
        keyword_stats = report_data['keyword_stats']

        # 生成项目列表
        projects_md = ""
        for i, project in enumerate(top_projects[:20], 1):
            name = project.get('name', 'Unknown')
            url = project.get('url', '#')
            stars = project.get('stars', 0)
            language = project.get('language', '未知')
            description = project.get('description', '')

            projects_md += f"""
### {i}. [{name}]({url})

- ⭐ **星标数**: {stars}
- 💻 **语言**: {language}
- 📊 **来源**: {project.get('source', 'Unknown')}
- 📝 **描述**: {description}

---
"""

        # 生成趋势分析
        trends_md = ""
        if trend_analysis.get('hot_trends'):
            trends_md += "#### 🔥 热门趋势\n\n"
            for trend in trend_analysis['hot_trends'][:5]:
                trends_md += f"- {trend}\n"
            trends_md += "\n"

        if trend_analysis.get('emerging_tech'):
            trends_md += "#### 🚀 新兴技术\n\n"
            for tech in trend_analysis['emerging_tech'][:5]:
                trends_md += f"- {tech}\n"
            trends_md += "\n"

        # 生成统计信息
        lang_stats_md = ""
        for lang, count in list(language_stats.items())[:5]:
            lang_stats_md += f"- {lang}: {count} 个项目\n"

        keyword_stats_md = ""
        for keyword, count in list(keyword_stats.items())[:10]:
            keyword_stats_md += f"- {keyword}: {count} 次\n"

        # Markdown模板
        markdown_template = f"""# 🚀 AI爆款项目雷达

> 发现最新最热的AI项目趋势 | {date}

## 📊 今日概览

- 🎯 **AI项目总数**: {total_projects}
- ⭐ **高星项目** (>100 stars): {len([p for p in top_projects if p.get('stars', 0) > 100])}
- 📈 **平均星标数**: {sum(p.get('stars', 0) for p in top_projects) // len(top_projects) if top_projects else 0}
- 📅 **报告日期**: {date}

## 📈 趋势分析

{trends_md}

### 📊 详细分析

{trend_analysis.get('trend_analysis', '暂无详细分析')}

## 💻 编程语言分布

{lang_stats_md}

## 🔥 热门关键词

{keyword_stats_md}

## 🏆 热门AI项目

{projects_md}

## 📝 说明

- 数据来源：GitHub Trending、Product Hunt
- 更新频率：每日自动更新
- 筛选标准：AI相关性分析 + 热度排序
- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*🤖 本报告由AI爆款项目雷达自动生成*
"""

        return markdown_template
