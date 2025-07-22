"""
测试配置文件
"""

import pytest
import sys
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def test_config():
    """测试配置"""
    return {
        'api': {
            'openai': {
                'api_key': 'test-key',
                'model': 'gpt-3.5-turbo',
                'max_tokens': 1000,
                'temperature': 0.3,
                'timeout': 30
            }
        },
        'crawler': {
            'request': {
                'timeout': 30,
                'retry_times': 3,
                'delay_between_requests': 0.1,  # 测试时减少延迟
                'user_agent': 'Test-Agent'
            },
            'github': {
                'base_url': 'https://github.com/trending',
                'languages': ['python'],
                'time_ranges': ['daily'],
                'max_pages': 1
            },
            'producthunt': {
                'base_url': 'https://www.producthunt.com',
                'categories': ['artificial-intelligence'],
                'max_items': 10
            }
        },
        'ai_analysis': {
            'ai_relevance_threshold': 0.7,
            'keyword_extraction': {
                'max_keywords': 10,
                'min_keyword_length': 3
            },
            'ai_keywords': [
                'artificial intelligence', 'machine learning', 'ai', 'ml'
            ]
        },
        'data': {
            'paths': {
                'raw_data': 'test_data/raw',
                'processed_data': 'test_data/processed',
                'archive_data': 'test_data/archive',
                'output': 'test_output'
            },
            'retention_days': 7,
            'deduplication': {
                'similarity_threshold': 0.9,
                'fields_to_compare': ['name', 'description', 'url']
            }
        },
        'visualization': {
            'charts': {
                'theme': 'plotly_white',
                'width': 800,
                'height': 600,
                'font_size': 12
            },
            'reports': {
                'template_path': 'src/visualization/templates',
                'output_format': ['html', 'markdown'],
                'include_charts': True,
                'max_projects_per_report': 20
            }
        },
        'logging': {
            'level': 'DEBUG',
            'format': '{time} | {level} | {message}',
            'file_path': 'test_logs/app.log'
        }
    }


@pytest.fixture
def temp_dir():
    """临时目录"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_projects():
    """示例项目数据"""
    return [
        {
            'name': 'awesome-ai-project',
            'description': 'An awesome artificial intelligence project using machine learning',
            'url': 'https://github.com/user/awesome-ai-project',
            'stars': 1500,
            'forks': 200,
            'language': 'Python',
            'author': 'user',
            'tags': ['ai', 'machine-learning', 'python'],
            'source': 'github',
            'created_at': '2023-01-01T00:00:00Z',
            'updated_at': '2023-12-01T00:00:00Z'
        },
        {
            'name': 'ml-toolkit',
            'description': 'A comprehensive machine learning toolkit for data scientists',
            'url': 'https://github.com/org/ml-toolkit',
            'stars': 800,
            'forks': 150,
            'language': 'Python',
            'author': 'org',
            'tags': ['ml', 'data-science', 'toolkit'],
            'source': 'github',
            'created_at': '2023-02-01T00:00:00Z',
            'updated_at': '2023-11-01T00:00:00Z'
        },
        {
            'name': 'chatbot-framework',
            'description': 'A modern chatbot framework powered by large language models',
            'url': 'https://producthunt.com/posts/chatbot-framework',
            'stars': 300,
            'votes': 150,
            'language': 'JavaScript',
            'author': 'startup',
            'tags': ['chatbot', 'llm', 'framework'],
            'source': 'producthunt',
            'created_at': '2023-03-01T00:00:00Z',
            'updated_at': '2023-10-01T00:00:00Z'
        }
    ]


@pytest.fixture
def mock_openai_response():
    """模拟OpenAI API响应"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '''
    {
        "is_ai_related": true,
        "confidence_score": 0.9,
        "reasoning": "This project uses machine learning and AI technologies",
        "ai_categories": ["Machine Learning", "Artificial Intelligence"],
        "tech_stack": ["Python", "TensorFlow", "PyTorch"]
    }
    '''
    return mock_response


@pytest.fixture
def mock_html_content():
    """模拟HTML内容"""
    return '''
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
    </body>
    </html>
    '''


@pytest.fixture(autouse=True)
def setup_test_environment(temp_dir, test_config):
    """设置测试环境"""
    # 创建测试目录
    for path in test_config['data']['paths'].values():
        (temp_dir / path).mkdir(parents=True, exist_ok=True)
    
    # 创建日志目录
    (temp_dir / "test_logs").mkdir(exist_ok=True)
    
    # 更新配置中的路径为临时目录
    for key, path in test_config['data']['paths'].items():
        test_config['data']['paths'][key] = str(temp_dir / path)
    
    test_config['logging']['file_path'] = str(temp_dir / "test_logs" / "app.log")
    
    yield
    
    # 清理工作在temp_dir fixture中完成
