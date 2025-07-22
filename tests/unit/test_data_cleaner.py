"""
数据清洗器测试
"""

import pytest
from utils.data_cleaner import DataCleaner


class TestDataCleaner:
    """数据清洗器测试类"""
    
    def test_init(self, test_config):
        """测试初始化"""
        cleaner = DataCleaner(test_config)
        assert cleaner.config == test_config
        assert cleaner.similarity_threshold == 0.9
        assert 'name' in cleaner.compare_fields
    
    def test_clean_text(self, test_config):
        """测试文本清洗"""
        cleaner = DataCleaner(test_config)
        
        # 测试基本清洗
        assert cleaner.clean_text("  Hello World  ") == "Hello World"
        assert cleaner.clean_text("Hello\n\nWorld") == "Hello World"
        assert cleaner.clean_text("") == ""
        
        # 测试特殊字符清洗
        text_with_special = "Hello@#$%World!"
        cleaned = cleaner.clean_text(text_with_special)
        assert "@#$%" not in cleaned
        assert "Hello" in cleaned and "World" in cleaned
    
    def test_clean_url(self, test_config):
        """测试URL清洗"""
        cleaner = DataCleaner(test_config)
        
        # 测试基本URL
        assert cleaner.clean_url("https://github.com/user/repo") == "https://github.com/user/repo"
        
        # 测试添加协议
        assert cleaner.clean_url("github.com/user/repo") == "https://github.com/user/repo"
        assert cleaner.clean_url("//github.com/user/repo") == "https://github.com/user/repo"
        
        # 测试移除跟踪参数
        url_with_tracking = "https://github.com/user/repo?utm_source=test&ref=homepage"
        cleaned_url = cleaner.clean_url(url_with_tracking)
        assert "utm_source" not in cleaned_url
        assert "ref=" not in cleaned_url
    
    def test_clean_number(self, test_config):
        """测试数字清洗"""
        cleaner = DataCleaner(test_config)
        
        assert cleaner.clean_number(123) == 123
        assert cleaner.clean_number("456") == 456
        assert cleaner.clean_number("1,234") == 1234
        assert cleaner.clean_number("abc") == 0
        assert cleaner.clean_number(-10) == 0  # 负数转为0
    
    def test_clean_language(self, test_config):
        """测试编程语言清洗"""
        cleaner = DataCleaner(test_config)
        
        assert cleaner.clean_language("python") == "Python"
        assert cleaner.clean_language("JavaScript") == "Javascript"
        assert cleaner.clean_language("js") == "javascript"
        assert cleaner.clean_language("c++") == "c++"
        assert cleaner.clean_language("") == ""
    
    def test_clean_tags(self, test_config):
        """测试标签清洗"""
        cleaner = DataCleaner(test_config)
        
        tags = ["AI", "Machine Learning", "ai", "python", ""]
        cleaned = cleaner.clean_tags(tags)
        
        assert "ai" in cleaned
        assert "machine learning" in cleaned
        assert "python" in cleaned
        assert "" not in cleaned
        assert len(set(cleaned)) == len(cleaned)  # 无重复
    
    def test_is_valid_item(self, test_config):
        """测试数据项有效性验证"""
        cleaner = DataCleaner(test_config)
        
        # 有效项目
        valid_item = {
            'name': 'Test Project',
            'description': 'A test project',
            'url': 'https://github.com/test/test'
        }
        assert cleaner.is_valid_item(valid_item) is True
        
        # 无名称
        invalid_item1 = {
            'description': 'A test project',
            'url': 'https://github.com/test/test'
        }
        assert cleaner.is_valid_item(invalid_item1) is False
        
        # 无URL和描述
        invalid_item2 = {
            'name': 'Test Project'
        }
        assert cleaner.is_valid_item(invalid_item2) is False
        
        # 名称过短
        invalid_item3 = {
            'name': 'A',
            'description': 'A test project'
        }
        assert cleaner.is_valid_item(invalid_item3) is False
    
    def test_clean_single_item(self, test_config):
        """测试单个数据项清洗"""
        cleaner = DataCleaner(test_config)
        
        raw_item = {
            'name': '  Test Project  ',
            'description': 'A test\n\nproject',
            'url': 'github.com/test/test',
            'stars': '1,234',
            'language': 'python',
            'tags': ['AI', 'ML', 'ai'],
            'author': '  testuser  '
        }
        
        cleaned = cleaner.clean_single_item(raw_item)
        
        assert cleaned['name'] == 'Test Project'
        assert cleaned['description'] == 'A test project'
        assert cleaned['url'] == 'https://github.com/test/test'
        assert cleaned['stars'] == 1234
        assert cleaned['language'] == 'Python'
        assert 'ai' in cleaned['tags']
        assert len(set(cleaned['tags'])) == len(cleaned['tags'])  # 无重复标签
        assert cleaned['author'] == 'testuser'
        assert 'cleaned_at' in cleaned
    
    def test_calculate_item_hash(self, test_config):
        """测试项目哈希计算"""
        cleaner = DataCleaner(test_config)
        
        item1 = {'url': 'https://github.com/test/test', 'name': 'Test'}
        item2 = {'url': 'https://github.com/test/test', 'name': 'Different'}
        item3 = {'name': 'Test', 'description': 'A test project'}
        
        # 相同URL应该有相同哈希
        assert cleaner.calculate_item_hash(item1) == cleaner.calculate_item_hash(item2)
        
        # 不同URL应该有不同哈希
        hash1 = cleaner.calculate_item_hash(item1)
        hash3 = cleaner.calculate_item_hash(item3)
        assert hash1 != hash3
    
    def test_is_similar(self, test_config):
        """测试相似性判断"""
        cleaner = DataCleaner(test_config)
        
        item1 = {
            'name': 'awesome-ai-project',
            'description': 'An awesome AI project',
            'url': 'https://github.com/user/awesome-ai-project'
        }
        
        item2 = {
            'name': 'awesome-ai-project',
            'description': 'An awesome AI project for machine learning',
            'url': 'https://github.com/user/awesome-ai-project'
        }
        
        item3 = {
            'name': 'completely-different-project',
            'description': 'A completely different project',
            'url': 'https://github.com/other/different'
        }
        
        # 相似项目
        assert cleaner.is_similar(item1, item2) is True
        
        # 不相似项目
        assert cleaner.is_similar(item1, item3) is False
    
    def test_deduplicate(self, test_config):
        """测试去重功能"""
        cleaner = DataCleaner(test_config)
        
        projects = [
            {
                'name': 'project1',
                'description': 'First project',
                'url': 'https://github.com/user/project1',
                'stars': 100
            },
            {
                'name': 'project1',
                'description': 'First project with more details',
                'url': 'https://github.com/user/project1',
                'stars': 150  # 更高的星数
            },
            {
                'name': 'project2',
                'description': 'Second project',
                'url': 'https://github.com/user/project2',
                'stars': 200
            }
        ]
        
        deduplicated = cleaner.deduplicate(projects)
        
        # 应该只有2个项目（project1被合并）
        assert len(deduplicated) == 2
        
        # 合并后的project1应该有更高的星数
        project1 = next(p for p in deduplicated if p['name'] == 'project1')
        assert project1['stars'] == 150
    
    def test_clean_and_deduplicate(self, test_config, sample_projects):
        """测试完整的清洗和去重流程"""
        cleaner = DataCleaner(test_config)
        
        # 添加一些需要清洗的数据
        dirty_projects = sample_projects + [
            {
                'name': '  awesome-ai-project  ',  # 重复项目，需要清洗
                'description': 'An awesome artificial intelligence project using machine learning!!!',
                'url': 'github.com/user/awesome-ai-project?utm_source=test',
                'stars': '1500',
                'language': 'python',
                'tags': ['AI', 'ML', 'ai'],
                'source': 'github'
            }
        ]
        
        result = cleaner.clean_and_deduplicate(dirty_projects)
        
        # 应该去重了重复的项目
        assert len(result) == len(sample_projects)
        
        # 检查数据是否被正确清洗
        for project in result:
            assert project['name'].strip() == project['name']  # 无前后空格
            assert isinstance(project['stars'], int)  # 星数为整数
            if project.get('url'):
                assert project['url'].startswith('http')  # URL有协议
