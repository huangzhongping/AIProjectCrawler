"""
AI分类器测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from ai_analysis.classifier import AIProjectClassifier


class TestAIProjectClassifier:
    """AI分类器测试类"""
    
    def test_init_with_api_key(self, test_config):
        """测试带API密钥的初始化"""
        classifier = AIProjectClassifier(test_config)
        assert classifier.config == test_config
        assert classifier.api_key == 'test-key'
        assert classifier.model == 'gpt-3.5-turbo'
        assert classifier.threshold == 0.7
    
    def test_init_without_api_key(self, test_config):
        """测试无API密钥的初始化"""
        test_config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'
        classifier = AIProjectClassifier(test_config)
        assert classifier.client is None
    
    def test_parse_classification_result_valid_json(self, test_config):
        """测试解析有效JSON结果"""
        classifier = AIProjectClassifier(test_config)
        
        json_content = '''
        {
            "is_ai_related": true,
            "confidence_score": 0.9,
            "reasoning": "This is an AI project",
            "ai_categories": ["Machine Learning"],
            "tech_stack": ["Python", "TensorFlow"]
        }
        '''
        
        result = classifier._parse_classification_result(json_content)
        
        assert result['is_ai_related'] is True
        assert result['confidence_score'] == 0.9
        assert result['reasoning'] == "This is an AI project"
        assert "Machine Learning" in result['ai_categories']
        assert "Python" in result['tech_stack']
    
    def test_parse_classification_result_invalid_json(self, test_config):
        """测试解析无效JSON结果"""
        classifier = AIProjectClassifier(test_config)
        
        invalid_content = "This is not JSON but mentions AI and true"
        result = classifier._parse_classification_result(invalid_content)
        
        assert isinstance(result['is_ai_related'], bool)
        assert result['confidence_score'] == 0.5
        assert result['reasoning'] == '解析失败，使用文本匹配'
    
    def test_classify_by_keywords(self, test_config):
        """测试基于关键词的分类"""
        classifier = AIProjectClassifier(test_config)
        
        # AI相关项目
        ai_project = {
            'name': 'awesome-ai-project',
            'description': 'A machine learning project using artificial intelligence',
            'tags': ['ai', 'ml'],
            'language': 'Python'
        }
        
        result = classifier._classify_by_keywords(ai_project)
        assert result['is_ai_related'] is True
        assert result['confidence_score'] > 0
        assert len(result['tech_stack']) > 0
    
    def test_classify_by_keywords_non_ai(self, test_config):
        """测试非AI项目的关键词分类"""
        classifier = AIProjectClassifier(test_config)
        
        non_ai_project = {
            'name': 'web-server',
            'description': 'A simple web server built with Node.js',
            'tags': ['web', 'server'],
            'language': 'JavaScript'
        }
        
        result = classifier._classify_by_keywords(non_ai_project)
        assert result['is_ai_related'] is False
        assert result['confidence_score'] < classifier.threshold * 0.7
    
    @pytest.mark.asyncio
    async def test_classify_without_client(self, test_config):
        """测试无客户端时的分类"""
        test_config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'
        classifier = AIProjectClassifier(test_config)
        
        project = {
            'name': 'ai-project',
            'description': 'An artificial intelligence project',
            'tags': ['ai'],
            'language': 'Python'
        }
        
        result = await classifier.classify(project)
        assert 'is_ai_related' in result
        assert 'confidence_score' in result
    
    @pytest.mark.asyncio
    @patch('ai_analysis.classifier.AsyncOpenAI')
    async def test_classify_with_api_success(self, mock_openai, test_config, mock_openai_response):
        """测试API调用成功的分类"""
        # 设置mock
        mock_client = AsyncMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        classifier = AIProjectClassifier(test_config)
        classifier.client = mock_client
        
        project = {
            'name': 'ai-project',
            'description': 'An artificial intelligence project',
            'tags': ['ai'],
            'language': 'Python'
        }
        
        result = await classifier.classify(project)
        
        assert result['is_ai_related'] is True
        assert result['confidence_score'] == 0.9
        assert mock_client.chat.completions.create.called
    
    @pytest.mark.asyncio
    @patch('ai_analysis.classifier.AsyncOpenAI')
    async def test_classify_with_api_failure(self, mock_openai, test_config):
        """测试API调用失败的分类"""
        # 设置mock抛出异常
        mock_client = AsyncMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        classifier = AIProjectClassifier(test_config)
        classifier.client = mock_client
        
        project = {
            'name': 'ai-project',
            'description': 'An artificial intelligence project',
            'tags': ['ai'],
            'language': 'Python'
        }
        
        result = await classifier.classify(project)
        
        # 应该降级到关键词匹配
        assert 'is_ai_related' in result
        assert 'confidence_score' in result
    
    @pytest.mark.asyncio
    async def test_batch_classify(self, test_config, sample_projects):
        """测试批量分类"""
        test_config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'  # 使用关键词分类
        classifier = AIProjectClassifier(test_config)
        
        results = await classifier.batch_classify(sample_projects)
        
        assert len(results) == len(sample_projects)
        for result in results:
            assert 'is_ai_related' in result
            assert 'confidence_score' in result
            assert 'reasoning' in result
    
    def test_load_classification_prompt(self, test_config):
        """测试加载分类提示词"""
        classifier = AIProjectClassifier(test_config)
        prompt = classifier._load_classification_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert '{name}' in prompt
        assert '{description}' in prompt
    
    def test_get_default_prompt(self, test_config):
        """测试获取默认提示词"""
        classifier = AIProjectClassifier(test_config)
        prompt = classifier._get_default_prompt()
        
        assert isinstance(prompt, str)
        assert 'AI项目分析师' in prompt
        assert 'JSON格式' in prompt
        assert 'is_ai_related' in prompt
