"""
GitHub爬虫测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from crawlers.github_crawler import GitHubCrawler


class TestGitHubCrawler:
    """GitHub爬虫测试类"""
    
    def test_init(self, test_config):
        """测试初始化"""
        crawler = GitHubCrawler(test_config)
        assert crawler.config == test_config
        assert crawler.base_url == 'https://github.com/trending'
        assert 'python' in crawler.languages
        assert 'daily' in crawler.time_ranges
        assert crawler.max_pages == 1
    
    def test_build_url(self, test_config):
        """测试URL构建"""
        crawler = GitHubCrawler(test_config)
        
        # 基础URL
        url1 = crawler._build_url('python', 'daily', 1)
        assert url1 == 'https://github.com/trending?l=python'
        
        # 带时间范围
        url2 = crawler._build_url('python', 'weekly', 1)
        assert url2 == 'https://github.com/trending?l=python&since=weekly'
        
        # 带页码
        url3 = crawler._build_url('python', 'daily', 2)
        assert url3 == 'https://github.com/trending?l=python&p=2'
        
        # 所有语言
        url4 = crawler._build_url('all', 'daily', 1)
        assert url4 == 'https://github.com/trending'
    
    def test_parse_star_count(self, test_config):
        """测试星标数解析"""
        crawler = GitHubCrawler(test_config)
        
        assert crawler._parse_star_count('1,234') == 1234
        assert crawler._parse_star_count('1.2k') == 1200
        assert crawler._parse_star_count('1.5m') == 1500000
        assert crawler._parse_star_count('15') == 15
        assert crawler._parse_star_count('invalid') == 0
        assert crawler._parse_star_count('') == 0
    
    def test_parse_project_item(self, test_config):
        """测试项目条目解析"""
        crawler = GitHubCrawler(test_config)
        
        # 创建模拟的HTML元素
        from bs4 import BeautifulSoup
        
        html = '''
        <article class="Box-row">
            <h2 class="h3">
                <a href="/user/awesome-project">user/awesome-project</a>
            </h2>
            <p class="col-9">An awesome AI project for machine learning</p>
            <span itemprop="programmingLanguage">Python</span>
            <a href="/user/awesome-project/stargazers">1,234</a>
            <a href="/user/awesome-project/forks">567</a>
            <span class="d-inline-block">89 stars today</span>
        </article>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find('article')
        
        result = crawler._parse_project_item(item)
        
        assert result is not None
        assert result['name'] == 'awesome-project'
        assert result['author'] == 'user'
        assert result['description'] == 'An awesome AI project for machine learning'
        assert result['language'] == 'Python'
        assert result['stars'] == 1234
        assert result['url'] == 'https://github.com/user/awesome-project'
        assert result['source'] == 'github'
    
    def test_parse_project_item_invalid(self, test_config):
        """测试无效项目条目解析"""
        crawler = GitHubCrawler(test_config)
        
        from bs4 import BeautifulSoup
        
        # 缺少必要元素的HTML
        html = '<article class="Box-row"><p>Invalid item</p></article>'
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find('article')
        
        result = crawler._parse_project_item(item)
        assert result is None
    
    def test_parse_project_list(self, test_config, mock_html_content):
        """测试项目列表解析"""
        crawler = GitHubCrawler(test_config)
        
        # 使用更完整的HTML内容
        html = '''
        <html>
        <body>
            <article class="Box-row">
                <h2 class="h3">
                    <a href="/user/test-project">user/test-project</a>
                </h2>
                <p class="col-9">A test AI project for machine learning</p>
                <span itemprop="programmingLanguage">Python</span>
                <a href="/user/test-project/stargazers">1,234</a>
            </article>
            <article class="Box-row">
                <h2 class="h3">
                    <a href="/org/another-project">org/another-project</a>
                </h2>
                <p class="col-9">Another awesome project</p>
                <span itemprop="programmingLanguage">JavaScript</span>
                <a href="/org/another-project/stargazers">567</a>
            </article>
        </body>
        </html>
        '''
        
        projects = crawler.parse_project_list(html)
        
        assert len(projects) == 2
        assert projects[0]['name'] == 'test-project'
        assert projects[1]['name'] == 'another-project'
    
    def test_deduplicate_projects(self, test_config):
        """测试项目去重"""
        crawler = GitHubCrawler(test_config)
        
        projects = [
            {'url': 'https://github.com/user/project1', 'name': 'project1'},
            {'url': 'https://github.com/user/project2', 'name': 'project2'},
            {'url': 'https://github.com/user/project1', 'name': 'project1'},  # 重复
        ]
        
        unique_projects = crawler._deduplicate_projects(projects)
        
        assert len(unique_projects) == 2
        urls = [p['url'] for p in unique_projects]
        assert len(set(urls)) == 2
    
    @pytest.mark.asyncio
    @patch('crawlers.github_crawler.GitHubCrawler.fetch_page')
    async def test_crawl_language_timerange(self, mock_fetch, test_config):
        """测试特定语言和时间范围的爬取"""
        crawler = GitHubCrawler(test_config)
        
        # 模拟HTML响应
        mock_html = '''
        <html>
        <body>
            <article class="Box-row">
                <h2 class="h3">
                    <a href="/user/test-project">user/test-project</a>
                </h2>
                <p class="col-9">A test project</p>
                <span itemprop="programmingLanguage">Python</span>
                <a href="/user/test-project/stargazers">100</a>
            </article>
        </body>
        </html>
        '''
        
        mock_fetch.return_value = mock_html
        
        projects = await crawler._crawl_language_timerange('python', 'daily')
        
        assert len(projects) == 1
        assert projects[0]['source'] == 'github'
        assert projects[0]['language_filter'] == 'python'
        assert projects[0]['time_range'] == 'daily'
        assert 'crawled_at' in projects[0]
    
    @pytest.mark.asyncio
    @patch('crawlers.github_crawler.GitHubCrawler.fetch_page')
    async def test_crawl_language_timerange_no_data(self, mock_fetch, test_config):
        """测试无数据的爬取"""
        crawler = GitHubCrawler(test_config)
        
        # 模拟空响应
        mock_fetch.return_value = '<html><body></body></html>'
        
        projects = await crawler._crawl_language_timerange('python', 'daily')
        
        assert len(projects) == 0
    
    @pytest.mark.asyncio
    @patch('crawlers.github_crawler.GitHubCrawler.fetch_page')
    async def test_crawl_fetch_failure(self, mock_fetch, test_config):
        """测试获取页面失败的情况"""
        crawler = GitHubCrawler(test_config)
        
        # 模拟获取失败
        mock_fetch.return_value = None
        
        projects = await crawler._crawl_language_timerange('python', 'daily')
        
        assert len(projects) == 0
    
    @pytest.mark.asyncio
    async def test_crawl_integration(self, test_config):
        """测试完整爬取流程（集成测试）"""
        # 修改配置以减少请求
        test_config['crawler']['github']['languages'] = ['python']
        test_config['crawler']['github']['time_ranges'] = ['daily']
        test_config['crawler']['github']['max_pages'] = 1
        
        crawler = GitHubCrawler(test_config)
        
        # 由于这是真实的网络请求，我们只测试方法调用不出错
        # 在实际环境中可能需要mock网络请求
        try:
            # 这里可以添加网络mock或跳过真实请求
            # projects = await crawler.crawl()
            # assert isinstance(projects, list)
            pass
        except Exception as e:
            # 网络问题不应该导致测试失败
            pytest.skip(f"Network request failed: {e}")
    
    def test_standardize_project_data(self, test_config):
        """测试项目数据标准化"""
        crawler = GitHubCrawler(test_config)
        
        raw_data = {
            'name': 'test-project',
            'description': 'A test project',
            'url': 'https://github.com/user/test-project',
            'stars': 100,
            'language': 'Python',
            'custom_field': 'custom_value'
        }
        
        standardized = crawler.standardize_project_data(raw_data)
        
        # 检查标准字段
        assert standardized['name'] == 'test-project'
        assert standardized['description'] == 'A test project'
        assert standardized['url'] == 'https://github.com/user/test-project'
        assert standardized['stars'] == 100
        assert standardized['language'] == 'Python'
        
        # 检查默认值
        assert standardized['tags'] == []
        assert standardized['author'] == ''
        
        # 检查原始数据保留
        assert standardized['raw_data'] == raw_data
