"""
GitHub Trending爬虫
"""

import re
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urljoin
from loguru import logger

from .base_crawler import BaseCrawler


class GitHubCrawler(BaseCrawler):
    """GitHub Trending爬虫"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化GitHub爬虫
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        
        # GitHub特定配置
        self.github_config = self.crawler_config.get('github', {})
        self.base_url = self.github_config.get('base_url', 'https://github.com/trending')
        self.languages = self.github_config.get('languages', ['python', 'javascript'])
        self.time_ranges = self.github_config.get('time_ranges', ['daily'])
        self.max_pages = self.github_config.get('max_pages', 1)
        
        logger.info(f"GitHub爬虫初始化完成 - 语言: {self.languages}, 时间范围: {self.time_ranges}")
    
    async def crawl(self) -> List[Dict[str, Any]]:
        """
        执行GitHub Trending爬取
        
        Returns:
            项目数据列表
        """
        logger.info("开始爬取GitHub Trending...")
        
        all_projects = []
        
        async with self:  # 使用异步上下文管理器
            # 爬取不同语言和时间范围的组合
            for language in self.languages:
                for time_range in self.time_ranges:
                    logger.info(f"正在爬取 {language} - {time_range}")
                    
                    projects = await self._crawl_language_timerange(language, time_range)
                    all_projects.extend(projects)
                    
                    # 避免请求过于频繁
                    await asyncio.sleep(1)
        
        # 去重（基于URL）
        unique_projects = self._deduplicate_projects(all_projects)
        
        logger.info(f"GitHub爬取完成，共获取 {len(unique_projects)} 个项目")
        return unique_projects
    
    async def _crawl_language_timerange(self, language: str, time_range: str) -> List[Dict[str, Any]]:
        """
        爬取特定语言和时间范围的项目
        
        Args:
            language: 编程语言
            time_range: 时间范围 (daily, weekly, monthly)
        
        Returns:
            项目列表
        """
        projects = []
        
        for page in range(1, self.max_pages + 1):
            url = self._build_url(language, time_range, page)
            
            html = await self.fetch_page(url)
            if not html:
                logger.warning(f"无法获取页面: {url}")
                break
            
            page_projects = self.parse_project_list(html)
            if not page_projects:
                logger.info(f"第 {page} 页没有更多项目，停止爬取")
                break
            
            # 添加元数据
            for project in page_projects:
                project.update({
                    'source': 'github',
                    'language_filter': language,
                    'time_range': time_range,
                    'crawled_at': datetime.now().isoformat()
                })
            
            projects.extend(page_projects)
            logger.debug(f"第 {page} 页获取到 {len(page_projects)} 个项目")
        
        return projects
    
    def _build_url(self, language: str, time_range: str, page: int = 1) -> str:
        """
        构建GitHub Trending URL
        
        Args:
            language: 编程语言
            time_range: 时间范围
            page: 页码
        
        Returns:
            完整URL
        """
        params = []
        
        if language and language != 'all':
            params.append(f"l={language}")
        
        if time_range != 'daily':
            params.append(f"since={time_range}")
        
        if page > 1:
            params.append(f"p={page}")
        
        url = self.base_url
        if params:
            url += "?" + "&".join(params)
        
        return url

    def parse_project_list(self, html: str) -> List[Dict[str, Any]]:
        """
        解析GitHub Trending项目列表页面

        Args:
            html: HTML内容

        Returns:
            项目数据列表
        """
        soup = self.parse_html(html)
        projects = []

        # 查找项目容器
        project_items = soup.find_all('article', class_='Box-row')

        for item in project_items:
            try:
                project_data = self._parse_project_item(item)
                if project_data:
                    projects.append(project_data)
            except Exception as e:
                logger.warning(f"解析项目失败: {str(e)}")
                continue

        return projects

    def _parse_project_item(self, item) -> Dict[str, Any]:
        """
        解析单个项目条目

        Args:
            item: BeautifulSoup项目元素

        Returns:
            项目数据字典
        """
        # 项目名称和URL
        title_elem = item.find('h2', class_='h3')
        if not title_elem:
            return None

        link_elem = title_elem.find('a')
        if not link_elem:
            return None

        name = self.extract_text(link_elem).replace('\n', '').strip()
        url = self.normalize_url(self.extract_attr(link_elem, 'href'), 'https://github.com')

        # 作者信息
        author = ""
        if '/' in name:
            author = name.split('/')[0]
            name = name.split('/')[-1]

        # 项目描述
        desc_elem = item.find('p', class_='col-9')
        description = self.extract_text(desc_elem)

        # 编程语言
        lang_elem = item.find('span', {'itemprop': 'programmingLanguage'})
        language = self.extract_text(lang_elem)

        # 星标数
        stars = 0
        star_elem = item.find('a', href=re.compile(r'/stargazers$'))
        if star_elem:
            star_text = self.extract_text(star_elem)
            stars = self._parse_star_count(star_text)

        # 今日星标数
        today_stars = 0
        today_elem = item.find('span', class_='d-inline-block')
        if today_elem and 'stars today' in self.extract_text(today_elem):
            today_text = self.extract_text(today_elem)
            today_stars = self._parse_star_count(today_text.split()[0])

        # Fork数
        forks = 0
        fork_elem = item.find('a', href=re.compile(r'/forks$'))
        if fork_elem:
            fork_text = self.extract_text(fork_elem)
            forks = self._parse_star_count(fork_text)

        return self.standardize_project_data({
            'name': name,
            'description': description,
            'url': url,
            'stars': stars,
            'forks': forks,
            'today_stars': today_stars,
            'language': language,
            'author': author,
            'tags': [language] if language else [],
            'updated_at': datetime.now().isoformat(),
            'source': 'github'
        })

    def _parse_star_count(self, text: str) -> int:
        """
        解析星标数文本

        Args:
            text: 星标数文本 (如 "1.2k", "15", "3.4m")

        Returns:
            星标数整数
        """
        if not text:
            return 0

        text = text.strip().lower().replace(',', '')

        try:
            if 'k' in text:
                return int(float(text.replace('k', '')) * 1000)
            elif 'm' in text:
                return int(float(text.replace('m', '')) * 1000000)
            else:
                return int(text)
        except (ValueError, TypeError):
            return 0

    def _deduplicate_projects(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于URL去重项目

        Args:
            projects: 项目列表

        Returns:
            去重后的项目列表
        """
        seen_urls = set()
        unique_projects = []

        for project in projects:
            url = project.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_projects.append(project)

        return unique_projects
