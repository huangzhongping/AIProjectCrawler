"""
历史记录页面生成器
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from loguru import logger

from utils.daily_records import DailyRecordsManager


class HistoryPageGenerator:
    """历史记录页面生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化"""
        self.config = config
        self.records_manager = DailyRecordsManager(config)
        self.output_dir = Path(config.get('data', {}).get('paths', {}).get('output', 'output'))
    
    def generate_history_page(self, days: int = 30) -> str:
        """生成历史记录页面"""
        try:
            # 获取最近的记录
            recent_records = self.records_manager.get_recent_records(days)
            
            # 获取趋势分析数据
            trend_data = self.records_manager.get_trend_analysis(days)
            
            # 生成HTML页面
            html_content = self._generate_html(recent_records, trend_data)
            
            # 保存页面
            output_path = self.output_dir / "history.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"历史记录页面生成成功: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"生成历史记录页面失败: {e}")
            return ""
    
    def _generate_html(self, records: List[Dict[str, Any]], 
                      trend_data: Dict[str, Any]) -> str:
        """生成HTML内容"""
        
        # 生成记录卡片
        records_html = ""
        for record in records:
            records_html += self._generate_record_card(record)
        
        # 生成趋势图表数据
        chart_data = self._prepare_chart_data(trend_data)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI项目雷达 - 历史记录</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="bg-gradient"></div>
    
    <div class="container">
        <header class="header">
            <h1><i class="fas fa-history"></i> AI项目雷达历史记录</h1>
            <p>追踪每日AI项目发现趋势</p>
            <div class="nav-buttons">
                <a href="index.html" class="btn btn-secondary">
                    <i class="fas fa-home"></i> 返回首页
                </a>
                <a href="#trends" class="btn">
                    <i class="fas fa-chart-line"></i> 查看趋势
                </a>
            </div>
        </header>
        
        <!-- 趋势图表区域 -->
        <section id="trends" class="trends-section">
            <h2><i class="fas fa-chart-line"></i> 趋势分析</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>每日AI项目发现数量</h3>
                    <canvas id="dailyChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3>编程语言分布</h3>
                    <canvas id="languageChart"></canvas>
                </div>
            </div>
        </section>
        
        <!-- 历史记录列表 -->
        <section class="records-section">
            <h2><i class="fas fa-calendar-alt"></i> 每日记录</h2>
            <div class="records-grid">
                {records_html}
            </div>
        </section>
        
        <footer class="footer">
            <p>数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>
                <a href="https://github.com/huangzhongping/AIProjectCrawler" target="_blank">
                    <i class="fab fa-github"></i> 项目源码
                </a>
            </p>
        </footer>
    </div>
    
    <script>
        {self._get_javascript(chart_data)}
    </script>
</body>
</html>
        """
        
        return html_template
    
    def _generate_record_card(self, record: Dict[str, Any]) -> str:
        """生成单个记录卡片"""
        date = record.get('date', '')
        total_projects = record.get('total_projects', 0)
        ai_projects = record.get('ai_projects', 0)
        top_project_name = record.get('top_project_name', '')
        top_project_stars = record.get('top_project_stars', 0)
        top_project_url = record.get('top_project_url', '')
        summary = record.get('summary', '')
        
        # 计算AI项目比例
        ai_percentage = (ai_projects / total_projects * 100) if total_projects > 0 else 0
        
        # 格式化日期
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%m月%d日')
            weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
        except:
            formatted_date = date
            weekday = ''
        
        return f"""
        <div class="record-card" data-date="{date}">
            <div class="record-header">
                <div class="record-date">
                    <span class="date-main">{formatted_date}</span>
                    <span class="date-sub">{weekday}</span>
                </div>
                <div class="record-stats">
                    <div class="stat-item">
                        <span class="stat-number">{ai_projects}</span>
                        <span class="stat-label">AI项目</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{ai_percentage:.1f}%</span>
                        <span class="stat-label">占比</span>
                    </div>
                </div>
            </div>
            
            <div class="record-content">
                <div class="record-summary">{summary}</div>
                
                {f'''
                <div class="top-project">
                    <div class="project-label">🏆 今日最热</div>
                    <div class="project-info">
                        <a href="{top_project_url}" target="_blank" class="project-name">
                            {top_project_name}
                        </a>
                        <span class="project-stars">
                            <i class="fas fa-star"></i> {top_project_stars:,}
                        </span>
                    </div>
                </div>
                ''' if top_project_name else ''}
            </div>
            
            <div class="record-actions">
                <button class="btn-small" onclick="viewDetails('{date}')">
                    <i class="fas fa-eye"></i> 查看详情
                </button>
                <span class="record-total">{total_projects} 个项目</span>
            </div>
        </div>
        """
    
    def _prepare_chart_data(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """准备图表数据"""
        daily_counts = trend_data.get('daily_counts', [])
        language_trends = trend_data.get('language_trends', [])
        
        # 每日数量数据
        daily_labels = [item['date'] for item in daily_counts]
        daily_values = [item['ai_projects'] for item in daily_counts]
        
        # 语言分布数据
        language_labels = [item['stat_name'] for item in language_trends[:8]]
        language_values = [item['avg_percentage'] for item in language_trends[:8]]
        
        return {
            'daily': {
                'labels': daily_labels,
                'values': daily_values
            },
            'languages': {
                'labels': language_labels,
                'values': language_values
            }
        }
    
    def _get_css_styles(self) -> str:
        """获取CSS样式"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #fff;
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .bg-gradient {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, #ff006e, #8338ec, #3a86ff, #06ffa5);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            opacity: 0.1;
            z-index: -1;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 60px;
            padding: 60px 0;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #ff006e, #8338ec, #3a86ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        
        .nav-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            background: linear-gradient(45deg, #ff006e, #8338ec);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(255,0,110,0.3);
        }
        
        .btn-secondary {
            background: transparent;
            border: 2px solid rgba(255,255,255,0.3);
        }
        
        .btn-secondary:hover {
            background: rgba(255,255,255,0.1);
        }
        
        .trends-section {
            margin-bottom: 80px;
        }
        
        .trends-section h2 {
            font-size: 2.5rem;
            margin-bottom: 40px;
            text-align: center;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 40px;
        }
        
        .chart-container {
            background: rgba(255,255,255,0.05);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
        }
        
        .chart-container h3 {
            margin-bottom: 20px;
            text-align: center;
            color: #fff;
        }
        
        .chart-container canvas {
            max-height: 300px;
        }
        
        .records-section h2 {
            font-size: 2.5rem;
            margin-bottom: 40px;
            text-align: center;
        }
        
        .records-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }
        
        .record-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 25px;
            backdrop-filter: blur(20px);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .record-card:hover {
            transform: translateY(-5px);
            border-color: rgba(255,0,110,0.5);
            box-shadow: 0 15px 40px rgba(255,0,110,0.2);
        }
        
        .record-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .record-date .date-main {
            font-size: 1.5rem;
            font-weight: 700;
            color: #fff;
        }
        
        .record-date .date-sub {
            font-size: 0.9rem;
            color: rgba(255,255,255,0.6);
            margin-left: 10px;
        }
        
        .record-stats {
            display: flex;
            gap: 20px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            display: block;
            font-size: 1.5rem;
            font-weight: 700;
            color: #06ffa5;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: rgba(255,255,255,0.6);
        }
        
        .record-summary {
            color: rgba(255,255,255,0.8);
            margin-bottom: 15px;
            line-height: 1.6;
        }
        
        .top-project {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        
        .project-label {
            font-size: 0.9rem;
            color: #ffd700;
            margin-bottom: 8px;
        }
        
        .project-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .project-name {
            color: #fff;
            text-decoration: none;
            font-weight: 600;
        }
        
        .project-name:hover {
            color: #06ffa5;
        }
        
        .project-stars {
            color: #ffd700;
            font-size: 0.9rem;
        }
        
        .record-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .btn-small {
            padding: 8px 16px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            color: #fff;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-small:hover {
            background: rgba(255,0,110,0.2);
            border-color: rgba(255,0,110,0.5);
        }
        
        .record-total {
            color: rgba(255,255,255,0.6);
            font-size: 0.9rem;
        }
        
        .footer {
            text-align: center;
            margin-top: 80px;
            padding: 40px 0;
            border-top: 1px solid rgba(255,255,255,0.1);
            color: rgba(255,255,255,0.6);
        }
        
        .footer a {
            color: #06ffa5;
            text-decoration: none;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .records-grid {
                grid-template-columns: 1fr;
            }
            
            .nav-buttons {
                flex-direction: column;
                align-items: center;
            }
        }
        """
    
    def _get_javascript(self, chart_data: Dict[str, Any]) -> str:
        """获取JavaScript代码"""
        return f"""
        // 图表数据
        const chartData = {json.dumps(chart_data)};
        
        // 初始化图表
        document.addEventListener('DOMContentLoaded', function() {{
            initDailyChart();
            initLanguageChart();
        }});
        
        function initDailyChart() {{
            const ctx = document.getElementById('dailyChart');
            if (!ctx) return;
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: chartData.daily.labels,
                    datasets: [{{
                        label: 'AI项目数量',
                        data: chartData.daily.values,
                        borderColor: '#ff006e',
                        backgroundColor: 'rgba(255, 0, 110, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#fff' }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{ color: '#fff' }},
                            grid: {{ color: 'rgba(255,255,255,0.1)' }}
                        }},
                        y: {{
                            ticks: {{ color: '#fff' }},
                            grid: {{ color: 'rgba(255,255,255,0.1)' }}
                        }}
                    }}
                }}
            }});
        }}
        
        function initLanguageChart() {{
            const ctx = document.getElementById('languageChart');
            if (!ctx) return;
            
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: chartData.languages.labels,
                    datasets: [{{
                        data: chartData.languages.values,
                        backgroundColor: [
                            '#ff006e', '#8338ec', '#3a86ff', '#06ffa5',
                            '#ffbe0b', '#fb5607', '#ff006e', '#8338ec'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#fff' }}
                        }}
                    }}
                }}
            }});
        }}
        
        function viewDetails(date) {{
            // 这里可以添加查看详情的功能
            alert('查看 ' + date + ' 的详细记录');
        }}
        """
