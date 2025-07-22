"""
基础爬虫类
"""

import asyncio
import aiohttp
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from loguru import logger


class BaseCrawler(ABC):
    """基础爬虫抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化爬虫
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.crawler_config = config.get('crawler', {})
        self.request_config = self.crawler_config.get('request', {})
        
        # 请求配置
        self.timeout = self.request_config.get('timeout', 30)
        self.retry_times = self.request_config.get('retry_times', 3)
        self.delay = self.request_config.get('delay_between_requests', 1)
        self.user_agent = self.request_config.get('user_agent', 
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # 会话配置
        self.session = None
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str, **kwargs) -> Optional[str]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            **kwargs: 额外的请求参数
        
        Returns:
            网页HTML内容，失败返回None
        """
        for attempt in range(self.retry_times):
            try:
                logger.debug(f"正在获取页面: {url} (尝试 {attempt + 1}/{self.retry_times})")
                
                async with self.session.get(url, **kwargs) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"成功获取页面: {url}")
                        
                        # 请求间延迟
                        if self.delay > 0:
                            await asyncio.sleep(self.delay)
                        
                        return content
                    else:
                        logger.warning(f"HTTP {response.status}: {url}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"请求超时: {url} (尝试 {attempt + 1}/{self.retry_times})")
            except Exception as e:
                logger.warning(f"请求失败: {url} - {str(e)} (尝试 {attempt + 1}/{self.retry_times})")
            
            # 重试前等待
            if attempt < self.retry_times - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
        
        logger.error(f"获取页面失败，已达到最大重试次数: {url}")
        return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        解析HTML内容
        
        Args:
            html: HTML字符串
        
        Returns:
            BeautifulSoup对象
        """
        return BeautifulSoup(html, 'lxml')
    
    def extract_text(self, element, default: str = "") -> str:
        """
        安全提取元素文本
        
        Args:
            element: BeautifulSoup元素
            default: 默认值
        
        Returns:
            文本内容
        """
        if element:
            return element.get_text(strip=True)
        return default
    
    def extract_attr(self, element, attr: str, default: str = "") -> str:
        """
        安全提取元素属性
        
        Args:
            element: BeautifulSoup元素
            attr: 属性名
            default: 默认值
        
        Returns:
            属性值
        """
        if element and element.has_attr(attr):
            return element[attr]
        return default
    
    def normalize_url(self, url: str, base_url: str) -> str:
        """
        标准化URL
        
        Args:
            url: 原始URL
            base_url: 基础URL
        
        Returns:
            标准化后的URL
        """
        if not url:
            return ""
        
        # 如果是相对URL，转换为绝对URL
        if url.startswith('/'):
            parsed_base = urlparse(base_url)
            return f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
        elif not url.startswith('http'):
            return urljoin(base_url, url)
        
        return url
    
    def standardize_project_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化项目数据格式
        
        Args:
            raw_data: 原始数据
        
        Returns:
            标准化后的数据
        """
        return {
            'name': raw_data.get('name', ''),
            'description': raw_data.get('description', ''),
            'url': raw_data.get('url', ''),
            'stars': raw_data.get('stars', 0),
            'language': raw_data.get('language', ''),
            'tags': raw_data.get('tags', []),
            'author': raw_data.get('author', ''),
            'created_at': raw_data.get('created_at', ''),
            'updated_at': raw_data.get('updated_at', ''),
            'source': raw_data.get('source', ''),
            'category': raw_data.get('category', ''),
            'raw_data': raw_data  # 保留原始数据
        }
    
    @abstractmethod
    async def crawl(self) -> List[Dict[str, Any]]:
        """
        执行爬取任务（抽象方法）
        
        Returns:
            项目数据列表
        """
        pass
    
    @abstractmethod
    def parse_project_list(self, html: str) -> List[Dict[str, Any]]:
        """
        解析项目列表页面（抽象方法）
        
        Args:
            html: HTML内容
        
        Returns:
            项目数据列表
        """
        pass
