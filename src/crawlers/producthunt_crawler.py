"""
Product Hunt爬虫
"""

import re
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urljoin
from loguru import logger

from .base_crawler import BaseCrawler


class ProductHuntCrawler(BaseCrawler):
    """Product Hunt爬虫"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Product Hunt爬虫
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        
        # Product Hunt特定配置
        self.ph_config = self.crawler_config.get('producthunt', {})
        self.base_url = self.ph_config.get('base_url', 'https://www.producthunt.com')
        self.categories = self.ph_config.get('categories', ['artificial-intelligence'])
        self.max_items = self.ph_config.get('max_items', 50)
        
        logger.info(f"Product Hunt爬虫初始化完成 - 分类: {self.categories}")
    
    async def crawl(self) -> List[Dict[str, Any]]:
        """
        执行Product Hunt爬取
        
        Returns:
            项目数据列表
        """
        logger.info("开始爬取Product Hunt...")
        
        all_projects = []
        
        async with self:  # 使用异步上下文管理器
            # 爬取今日热门产品
            today_projects = await self._crawl_today()
            all_projects.extend(today_projects)
            
            # 爬取不同分类
            for category in self.categories:
                logger.info(f"正在爬取分类: {category}")
                
                category_projects = await self._crawl_category(category)
                all_projects.extend(category_projects)
                
                # 避免请求过于频繁
                await asyncio.sleep(2)
        
        # 去重（基于URL）
        unique_projects = self._deduplicate_projects(all_projects)
        
        logger.info(f"Product Hunt爬取完成，共获取 {len(unique_projects)} 个项目")
        return unique_projects
    
    async def _crawl_today(self) -> List[Dict[str, Any]]:
        """
        爬取今日热门产品
        
        Returns:
            项目列表
        """
        url = self.base_url
        
        html = await self.fetch_page(url)
        if not html:
            logger.warning(f"无法获取今日页面: {url}")
            return []
        
        projects = self.parse_project_list(html)
        
        # 添加元数据
        for project in projects:
            project.update({
                'source': 'producthunt',
                'category': 'today',
                'crawled_at': datetime.now().isoformat()
            })
        
        logger.debug(f"今日页面获取到 {len(projects)} 个项目")
        return projects
    
    async def _crawl_category(self, category: str) -> List[Dict[str, Any]]:
        """
        爬取特定分类的产品
        
        Args:
            category: 分类名称
        
        Returns:
            项目列表
        """
        url = f"{self.base_url}/topics/{category}"
        
        html = await self.fetch_page(url)
        if not html:
            logger.warning(f"无法获取分类页面: {url}")
            return []
        
        projects = self.parse_project_list(html)
        
        # 添加元数据
        for project in projects:
            project.update({
                'source': 'producthunt',
                'category': category,
                'crawled_at': datetime.now().isoformat()
            })
        
        logger.debug(f"分类 {category} 获取到 {len(projects)} 个项目")
        return projects
    
    def parse_project_list(self, html: str) -> List[Dict[str, Any]]:
        """
        解析Product Hunt项目列表页面
        
        Args:
            html: HTML内容
        
        Returns:
            项目数据列表
        """
        soup = self.parse_html(html)
        projects = []
        
        # 查找项目容器 - Product Hunt的结构可能会变化，这里提供基础解析
        # 实际使用时可能需要根据页面结构调整选择器
        project_items = soup.find_all('div', {'data-test': 'post-item'}) or \
                       soup.find_all('div', class_=re.compile(r'post|product'))
        
        for item in project_items[:self.max_items]:
            try:
                project_data = self._parse_project_item(item)
                if project_data:
                    projects.append(project_data)
            except Exception as e:
                logger.warning(f"解析Product Hunt项目失败: {str(e)}")
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
        title_elem = item.find('a', href=re.compile(r'/posts/')) or \
                    item.find('h3') or item.find('h2')
        
        if not title_elem:
            return None
        
        name = self.extract_text(title_elem)
        url = self.normalize_url(self.extract_attr(title_elem, 'href'), self.base_url)
        
        # 项目描述
        desc_elem = item.find('p') or item.find('div', class_=re.compile(r'description|tagline'))
        description = self.extract_text(desc_elem)
        
        # 投票数/点赞数
        votes = 0
        vote_elem = item.find('span', class_=re.compile(r'vote|upvote')) or \
                   item.find('div', {'data-test': 'vote-button'})
        if vote_elem:
            vote_text = self.extract_text(vote_elem)
            votes = self._parse_vote_count(vote_text)
        
        # 标签
        tags = []
        tag_elems = item.find_all('span', class_=re.compile(r'tag|topic')) or \
                   item.find_all('a', href=re.compile(r'/topics/'))
        for tag_elem in tag_elems:
            tag = self.extract_text(tag_elem)
            if tag and tag not in tags:
                tags.append(tag)
        
        # 作者/制作者
        author = ""
        author_elem = item.find('a', href=re.compile(r'/@')) or \
                     item.find('span', class_=re.compile(r'maker|author'))
        if author_elem:
            author = self.extract_text(author_elem)
        
        return self.standardize_project_data({
            'name': name,
            'description': description,
            'url': url,
            'stars': votes,  # 使用投票数作为stars
            'votes': votes,
            'language': '',  # Product Hunt通常不显示编程语言
            'author': author,
            'tags': tags,
            'updated_at': datetime.now().isoformat(),
            'source': 'producthunt'
        })
    
    def _parse_vote_count(self, text: str) -> int:
        """
        解析投票数文本
        
        Args:
            text: 投票数文本
        
        Returns:
            投票数整数
        """
        if not text:
            return 0
        
        # 提取数字
        numbers = re.findall(r'\d+', text)
        if numbers:
            try:
                return int(numbers[0])
            except ValueError:
                return 0
        
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
