"""
数据存储模块
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger


class DataStorage:
    """数据存储管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据存储
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # 存储路径配置
        paths_config = config.get('data', {}).get('paths', {})
        self.raw_data_path = Path(paths_config.get('raw_data', 'data/raw'))
        self.processed_data_path = Path(paths_config.get('processed_data', 'data/processed'))
        self.archive_data_path = Path(paths_config.get('archive_data', 'data/archive'))
        
        # 数据保留配置
        self.retention_days = config.get('data', {}).get('retention_days', 30)
        
        # 创建目录
        self._create_directories()
        
        # 初始化数据库
        self.db_path = self.processed_data_path / "projects.db"
        self._init_database()
        
        logger.info("数据存储管理器初始化完成")
    
    def _create_directories(self):
        """创建必要的目录"""
        for path in [self.raw_data_path, self.processed_data_path, self.archive_data_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """初始化SQLite数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建项目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    url TEXT UNIQUE,
                    stars INTEGER DEFAULT 0,
                    forks INTEGER DEFAULT 0,
                    votes INTEGER DEFAULT 0,
                    language TEXT,
                    author TEXT,
                    source TEXT,
                    category TEXT,
                    tags TEXT,  -- JSON格式存储
                    ai_classification TEXT,  -- JSON格式存储
                    keywords TEXT,  -- JSON格式存储
                    summary TEXT,  -- JSON格式存储
                    created_at TEXT,
                    updated_at TEXT,
                    crawled_at TEXT,
                    UNIQUE(url)
                )
            ''')
            
            # 创建每日统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE,
                    total_projects INTEGER,
                    ai_projects INTEGER,
                    top_languages TEXT,  -- JSON格式存储
                    top_keywords TEXT,  -- JSON格式存储
                    created_at TEXT
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_source ON projects(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_date ON projects(crawled_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_ai ON projects(ai_classification)')
            
            conn.commit()
    
    def save_raw_data(self, data: List[Dict[str, Any]], source: str, timestamp: str = None) -> str:
        """
        保存原始数据
        
        Args:
            data: 原始数据列表
            source: 数据源名称
            timestamp: 时间戳，默认为当前时间
        
        Returns:
            保存的文件路径
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{source}_{timestamp}.json"
        filepath = self.raw_data_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"原始数据已保存: {filepath} ({len(data)} 条记录)")
        return str(filepath)
    
    def save_daily_data(self, projects: List[Dict[str, Any]], date: str) -> None:
        """
        保存每日处理后的数据
        
        Args:
            projects: 项目列表
            date: 日期字符串 (YYYY-MM-DD)
        """
        # 保存到JSON文件
        filename = f"ai_projects_{date}.json"
        filepath = self.processed_data_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        
        # 保存到数据库
        self._save_to_database(projects)
        
        # 生成每日统计
        self._generate_daily_stats(projects, date)
        
        logger.info(f"每日数据已保存: {filepath} ({len(projects)} 个AI项目)")
    
    def _save_to_database(self, projects: List[Dict[str, Any]]) -> None:
        """
        保存项目到数据库
        
        Args:
            projects: 项目列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for project in projects:
                try:
                    # 准备数据
                    data = (
                        project.get('name', ''),
                        project.get('description', ''),
                        project.get('url', ''),
                        project.get('stars', 0),
                        project.get('forks', 0),
                        project.get('votes', 0),
                        project.get('language', ''),
                        project.get('author', ''),
                        project.get('source', ''),
                        project.get('category', ''),
                        json.dumps(project.get('tags', []), ensure_ascii=False),
                        json.dumps(project.get('ai_classification', {}), ensure_ascii=False),
                        json.dumps(project.get('keywords', {}), ensure_ascii=False),
                        json.dumps(project.get('summary', {}), ensure_ascii=False),
                        project.get('created_at', ''),
                        project.get('updated_at', ''),
                        project.get('crawled_at', datetime.now().isoformat())
                    )
                    
                    # 插入或更新
                    cursor.execute('''
                        INSERT OR REPLACE INTO projects 
                        (name, description, url, stars, forks, votes, language, author, 
                         source, category, tags, ai_classification, keywords, summary,
                         created_at, updated_at, crawled_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', data)
                    
                except Exception as e:
                    logger.warning(f"保存项目到数据库失败: {project.get('name', 'Unknown')} - {e}")
            
            conn.commit()
    
    def _generate_daily_stats(self, projects: List[Dict[str, Any]], date: str) -> None:
        """
        生成每日统计数据
        
        Args:
            projects: 项目列表
            date: 日期字符串
        """
        # 统计编程语言
        languages = {}
        for project in projects:
            lang = project.get('language', '').lower()
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 统计关键词
        keywords = {}
        for project in projects:
            project_keywords = project.get('keywords', {}).get('keywords', [])
            for keyword in project_keywords:
                if keyword:
                    keywords[keyword] = keywords.get(keyword, 0) + 1
        
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # 保存统计数据
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats 
                (date, total_projects, ai_projects, top_languages, top_keywords, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                date,
                len(projects),
                len(projects),  # 这里的projects已经是AI项目了
                json.dumps(top_languages, ensure_ascii=False),
                json.dumps(top_keywords, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def load_data(self, filepath: str) -> List[Dict[str, Any]]:
        """
        加载数据文件
        
        Args:
            filepath: 文件路径
        
        Returns:
            数据列表
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"数据文件不存在: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"数据加载成功: {filepath} ({len(data)} 条记录)")
            return data
            
        except Exception as e:
            logger.error(f"数据加载失败: {filepath} - {e}")
            return []
    
    def get_projects_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        获取指定日期的项目
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)
        
        Returns:
            项目列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM projects 
                WHERE DATE(crawled_at) = ?
                ORDER BY stars DESC
            ''', (date,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            projects = []
            for row in rows:
                project = dict(zip(columns, row))
                
                # 解析JSON字段
                for field in ['tags', 'ai_classification', 'keywords', 'summary']:
                    if project.get(field):
                        try:
                            project[field] = json.loads(project[field])
                        except json.JSONDecodeError:
                            project[field] = {}
                
                projects.append(project)
            
            return projects
    
    def get_recent_projects(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取最近几天的项目
        
        Args:
            days: 天数
        
        Returns:
            项目列表
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM projects 
                WHERE DATE(crawled_at) >= ?
                ORDER BY crawled_at DESC, stars DESC
            ''', (start_date,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            projects = []
            for row in rows:
                project = dict(zip(columns, row))
                
                # 解析JSON字段
                for field in ['tags', 'ai_classification', 'keywords', 'summary']:
                    if project.get(field):
                        try:
                            project[field] = json.loads(project[field])
                        except json.JSONDecodeError:
                            project[field] = {}
                
                projects.append(project)
            
            return projects
    
    def get_daily_stats(self, date: str) -> Optional[Dict[str, Any]]:
        """
        获取指定日期的统计数据
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)
        
        Returns:
            统计数据字典
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM daily_stats WHERE date = ?
            ''', (date,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [description[0] for description in cursor.description]
            stats = dict(zip(columns, row))
            
            # 解析JSON字段
            for field in ['top_languages', 'top_keywords']:
                if stats.get(field):
                    try:
                        stats[field] = json.loads(stats[field])
                    except json.JSONDecodeError:
                        stats[field] = []
            
            return stats
    
    def cleanup_old_data(self) -> None:
        """清理过期数据"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        # 归档旧的JSON文件
        for data_path in [self.raw_data_path, self.processed_data_path]:
            for file_path in data_path.glob("*.json"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    # 移动到归档目录
                    archive_path = self.archive_data_path / file_path.name
                    file_path.rename(archive_path)
                    logger.info(f"文件已归档: {file_path} -> {archive_path}")
        
        # 清理数据库中的旧数据
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
            
            cursor.execute('''
                DELETE FROM projects WHERE DATE(crawled_at) < ?
            ''', (cutoff_date_str,))
            
            cursor.execute('''
                DELETE FROM daily_stats WHERE date < ?
            ''', (cutoff_date_str,))
            
            conn.commit()
        
        logger.info(f"清理完成，删除 {cutoff_date_str} 之前的数据")
