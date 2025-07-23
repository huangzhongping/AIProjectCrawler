"""
每日推荐记录管理模块
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger


class DailyRecordsManager:
    """每日推荐记录管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化记录管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.data_dir = Path(config.get('data', {}).get('paths', {}).get('processed_data', 'data/processed'))
        self.output_dir = Path(config.get('data', {}).get('paths', {}).get('output', 'output'))
        
        # 创建必要的目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据库文件路径
        self.db_path = self.data_dir / "daily_records.db"
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建每日记录表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS daily_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT UNIQUE NOT NULL,
                        total_projects INTEGER DEFAULT 0,
                        ai_projects INTEGER DEFAULT 0,
                        top_project_name TEXT,
                        top_project_stars INTEGER DEFAULT 0,
                        top_project_url TEXT,
                        summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建项目详情表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS daily_projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        project_name TEXT NOT NULL,
                        project_url TEXT NOT NULL,
                        stars INTEGER DEFAULT 0,
                        language TEXT,
                        description TEXT,
                        ai_categories TEXT,  -- JSON格式存储
                        confidence_score REAL DEFAULT 0.0,
                        rank_in_day INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (date) REFERENCES daily_records (date)
                    )
                """)
                
                # 创建趋势统计表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trend_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        stat_type TEXT NOT NULL,  -- 'language', 'category', 'keyword'
                        stat_name TEXT NOT NULL,
                        stat_value INTEGER DEFAULT 0,
                        percentage REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def save_daily_record(self, date: str, projects: List[Dict[str, Any]], 
                         ai_projects: List[Dict[str, Any]]) -> bool:
        """
        保存每日记录
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)
            projects: 所有项目列表
            ai_projects: AI项目列表
        
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 准备每日汇总数据
                total_projects = len(projects)
                ai_projects_count = len(ai_projects)
                
                # 找出最热门的AI项目
                top_project = None
                if ai_projects:
                    top_project = max(ai_projects, key=lambda x: x.get('stars', 0))
                
                # 生成每日总结
                summary = self._generate_daily_summary(projects, ai_projects)
                
                # 插入或更新每日记录
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_records 
                    (date, total_projects, ai_projects, top_project_name, 
                     top_project_stars, top_project_url, summary, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    date,
                    total_projects,
                    ai_projects_count,
                    top_project['name'] if top_project else None,
                    top_project.get('stars', 0) if top_project else 0,
                    top_project.get('url', '') if top_project else '',
                    summary
                ))
                
                # 删除当天的旧项目记录
                cursor.execute("DELETE FROM daily_projects WHERE date = ?", (date,))
                
                # 插入AI项目详情
                for rank, project in enumerate(ai_projects, 1):
                    ai_classification = project.get('ai_classification', {})
                    cursor.execute("""
                        INSERT INTO daily_projects 
                        (date, project_name, project_url, stars, language, description,
                         ai_categories, confidence_score, rank_in_day)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        date,
                        project.get('name', ''),
                        project.get('url', ''),
                        project.get('stars', 0),
                        project.get('language', ''),
                        project.get('description', ''),
                        json.dumps(ai_classification.get('ai_categories', []), ensure_ascii=False),
                        ai_classification.get('confidence_score', 0.0),
                        rank
                    ))
                
                # 保存趋势统计
                self._save_trend_stats(cursor, date, ai_projects)
                
                conn.commit()
                logger.info(f"每日记录保存成功: {date}")
                return True
                
        except Exception as e:
            logger.error(f"保存每日记录失败: {e}")
            return False
    
    def _generate_daily_summary(self, projects: List[Dict[str, Any]], 
                               ai_projects: List[Dict[str, Any]]) -> str:
        """生成每日总结"""
        try:
            total_count = len(projects)
            ai_count = len(ai_projects)
            ai_percentage = (ai_count / total_count * 100) if total_count > 0 else 0
            
            # 统计编程语言
            languages = {}
            for project in ai_projects:
                lang = project.get('language', 'Unknown')
                languages[lang] = languages.get(lang, 0) + 1
            
            top_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown"
            
            # 计算平均星标数
            avg_stars = sum(p.get('stars', 0) for p in ai_projects) / len(ai_projects) if ai_projects else 0
            
            summary = f"今日发现 {total_count} 个项目，其中 {ai_count} 个AI相关项目（{ai_percentage:.1f}%）。"
            summary += f"主要编程语言为 {top_language}，平均星标数 {avg_stars:.0f}。"
            
            if ai_projects:
                top_project = max(ai_projects, key=lambda x: x.get('stars', 0))
                summary += f"最热门项目：{top_project['name']}（{top_project.get('stars', 0)}⭐）。"
            
            return summary
            
        except Exception as e:
            logger.error(f"生成每日总结失败: {e}")
            return "数据处理中遇到问题，无法生成总结。"
    
    def _save_trend_stats(self, cursor, date: str, ai_projects: List[Dict[str, Any]]):
        """保存趋势统计数据"""
        try:
            # 删除当天的旧统计数据
            cursor.execute("DELETE FROM trend_stats WHERE date = ?", (date,))
            
            # 统计编程语言
            languages = {}
            categories = {}
            
            for project in ai_projects:
                # 编程语言统计
                lang = project.get('language', 'Unknown')
                languages[lang] = languages.get(lang, 0) + 1
                
                # AI分类统计
                ai_classification = project.get('ai_classification', {})
                for category in ai_classification.get('ai_categories', []):
                    categories[category] = categories.get(category, 0) + 1
            
            total_projects = len(ai_projects)
            
            # 保存语言统计
            for lang, count in languages.items():
                percentage = (count / total_projects * 100) if total_projects > 0 else 0
                cursor.execute("""
                    INSERT INTO trend_stats (date, stat_type, stat_name, stat_value, percentage)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, 'language', lang, count, percentage))
            
            # 保存分类统计
            for category, count in categories.items():
                percentage = (count / total_projects * 100) if total_projects > 0 else 0
                cursor.execute("""
                    INSERT INTO trend_stats (date, stat_type, stat_name, stat_value, percentage)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, 'category', category, count, percentage))
                
        except Exception as e:
            logger.error(f"保存趋势统计失败: {e}")
    
    def get_daily_record(self, date: str) -> Optional[Dict[str, Any]]:
        """获取指定日期的记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 获取每日汇总
                cursor.execute("""
                    SELECT * FROM daily_records WHERE date = ?
                """, (date,))
                
                record = cursor.fetchone()
                if not record:
                    return None
                
                # 获取项目详情
                cursor.execute("""
                    SELECT * FROM daily_projects WHERE date = ? 
                    ORDER BY rank_in_day ASC
                """, (date,))
                
                projects = [dict(row) for row in cursor.fetchall()]
                
                # 获取趋势统计
                cursor.execute("""
                    SELECT * FROM trend_stats WHERE date = ?
                """, (date,))
                
                stats = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'summary': dict(record),
                    'projects': projects,
                    'stats': stats
                }
                
        except Exception as e:
            logger.error(f"获取每日记录失败: {e}")
            return None
    
    def get_recent_records(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近几天的记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 计算日期范围
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days-1)
                
                cursor.execute("""
                    SELECT * FROM daily_records 
                    WHERE date >= ? AND date <= ?
                    ORDER BY date DESC
                """, (start_date.isoformat(), end_date.isoformat()))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"获取最近记录失败: {e}")
            return []
    
    def get_trend_analysis(self, days: int = 30) -> Dict[str, Any]:
        """获取趋势分析数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 计算日期范围
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days-1)
                
                # 获取每日AI项目数量趋势
                cursor.execute("""
                    SELECT date, ai_projects FROM daily_records 
                    WHERE date >= ? AND date <= ?
                    ORDER BY date ASC
                """, (start_date.isoformat(), end_date.isoformat()))
                
                daily_counts = [dict(row) for row in cursor.fetchall()]
                
                # 获取语言趋势
                cursor.execute("""
                    SELECT stat_name, AVG(percentage) as avg_percentage
                    FROM trend_stats 
                    WHERE date >= ? AND date <= ? AND stat_type = 'language'
                    GROUP BY stat_name
                    ORDER BY avg_percentage DESC
                    LIMIT 10
                """, (start_date.isoformat(), end_date.isoformat()))
                
                language_trends = [dict(row) for row in cursor.fetchall()]
                
                # 获取分类趋势
                cursor.execute("""
                    SELECT stat_name, AVG(percentage) as avg_percentage
                    FROM trend_stats 
                    WHERE date >= ? AND date <= ? AND stat_type = 'category'
                    GROUP BY stat_name
                    ORDER BY avg_percentage DESC
                    LIMIT 10
                """, (start_date.isoformat(), end_date.isoformat()))
                
                category_trends = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'daily_counts': daily_counts,
                    'language_trends': language_trends,
                    'category_trends': category_trends,
                    'period': f"{start_date} to {end_date}"
                }
                
        except Exception as e:
            logger.error(f"获取趋势分析失败: {e}")
            return {}
    
    def export_records(self, start_date: str, end_date: str, 
                      format: str = 'json') -> Optional[str]:
        """导出记录数据"""
        try:
            records = []
            current_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            while current_date <= end_date_obj:
                record = self.get_daily_record(current_date.isoformat())
                if record:
                    records.append(record)
                current_date += timedelta(days=1)
            
            # 生成导出文件
            export_dir = self.output_dir / "exports"
            export_dir.mkdir(exist_ok=True)
            
            filename = f"ai_trends_{start_date}_to_{end_date}.{format}"
            file_path = export_dir / filename
            
            if format == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
            
            logger.info(f"记录导出成功: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"导出记录失败: {e}")
            return None
