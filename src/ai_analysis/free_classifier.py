"""
免费AI分类器 - 支持多种免费AI服务
"""

import json
import asyncio
import aiohttp
from typing import Dict, Any, List
from loguru import logger


class FreeAIClassifier:
    """免费AI分类器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化免费AI分类器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.provider = config.get('api', {}).get('provider', 'keywords')
        
        # 根据提供商初始化
        if self.provider == 'ollama':
            self._init_ollama()
        elif self.provider == 'huggingface':
            self._init_huggingface()
        else:
            self.provider = 'keywords'
            logger.info("使用关键词分析模式")
        
        # 加载AI关键词
        self.ai_keywords = config.get('ai_analysis', {}).get('ai_keywords', [])
        self.threshold = config.get('ai_analysis', {}).get('ai_relevance_threshold', 0.7)
    
    def _init_ollama(self):
        """初始化Ollama配置"""
        ollama_config = self.config.get('api', {}).get('ollama', {})
        self.base_url = ollama_config.get('base_url', 'http://localhost:11434')
        self.model = ollama_config.get('model', 'llama3.2:3b')
        self.timeout = ollama_config.get('timeout', 60)
        logger.info(f"使用Ollama模型: {self.model}")
    
    def _init_huggingface(self):
        """初始化Hugging Face配置"""
        hf_config = self.config.get('api', {}).get('huggingface', {})
        self.api_key = hf_config.get('api_key', '')
        self.base_url = hf_config.get('base_url', 'https://api-inference.huggingface.co/models')
        self.model = hf_config.get('model', 'microsoft/DialoGPT-medium')
        self.timeout = hf_config.get('timeout', 30)
        
        if not self.api_key or self.api_key.startswith('${'):
            logger.warning("Hugging Face API密钥未设置，降级到关键词模式")
            self.provider = 'keywords'
        else:
            logger.info(f"使用Hugging Face模型: {self.model}")
    
    async def classify(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        分类项目
        
        Args:
            project: 项目数据
        
        Returns:
            分类结果
        """
        try:
            if self.provider == 'ollama':
                return await self._classify_with_ollama(project)
            elif self.provider == 'huggingface':
                return await self._classify_with_huggingface(project)
            else:
                return self._classify_with_keywords(project)
        except Exception as e:
            logger.error(f"AI分类失败，降级到关键词模式: {e}")
            return self._classify_with_keywords(project)
    
    async def _classify_with_ollama(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """使用Ollama进行分类"""
        try:
            # 构建提示词
            prompt = self._build_classification_prompt(project)
            
            # 调用Ollama API
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9
                    }
                }
                
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get('response', '')
                        return self._parse_ai_response(content)
                    else:
                        logger.error(f"Ollama API调用失败: {response.status}")
                        return self._classify_with_keywords(project)
        
        except Exception as e:
            logger.error(f"Ollama分类失败: {e}")
            return self._classify_with_keywords(project)
    
    async def _classify_with_huggingface(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """使用Hugging Face进行分类"""
        try:
            # 构建简单的分类提示
            text = f"Project: {project.get('name', '')} - {project.get('description', '')}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 使用文本分类模型
            payload = {
                "inputs": text,
                "parameters": {
                    "candidate_labels": ["artificial intelligence", "machine learning", "software development", "web development"],
                    "multi_label": False
                }
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                # 使用零样本分类模型
                url = f"{self.base_url}/facebook/bart-large-mnli"
                
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._parse_hf_classification(result)
                    else:
                        logger.error(f"Hugging Face API调用失败: {response.status}")
                        return self._classify_with_keywords(project)
        
        except Exception as e:
            logger.error(f"Hugging Face分类失败: {e}")
            return self._classify_with_keywords(project)
    
    def _classify_with_keywords(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """使用关键词进行分类"""
        name = project.get('name', '').lower()
        description = project.get('description', '').lower()
        tags = [tag.lower() for tag in project.get('tags', [])]
        
        # 计算AI相关性得分
        ai_score = 0
        matched_keywords = []
        
        text_to_check = f"{name} {description} {' '.join(tags)}"
        
        for keyword in self.ai_keywords:
            if keyword.lower() in text_to_check:
                ai_score += 1
                matched_keywords.append(keyword)
        
        # 计算置信度
        confidence = min(ai_score / 3.0, 1.0)  # 最多3个关键词就认为是高置信度
        is_ai_related = confidence >= (self.threshold * 0.7)  # 关键词模式使用较低阈值
        
        return {
            'is_ai_related': is_ai_related,
            'confidence_score': confidence,
            'reasoning': f"基于关键词匹配，发现 {len(matched_keywords)} 个AI相关关键词: {', '.join(matched_keywords[:5])}",
            'ai_categories': self._extract_ai_categories(matched_keywords),
            'tech_stack': self._extract_tech_stack(text_to_check),
            'matched_keywords': matched_keywords,
            'analysis_method': 'keywords'
        }
    
    def _build_classification_prompt(self, project: Dict[str, Any]) -> str:
        """构建分类提示词"""
        return f"""请分析以下项目是否与人工智能相关：

项目名称: {project.get('name', '')}
项目描述: {project.get('description', '')}
编程语言: {project.get('language', '')}
标签: {', '.join(project.get('tags', []))}

请判断这个项目是否与AI、机器学习、深度学习、自然语言处理、计算机视觉等人工智能技术相关。

请以JSON格式回答：
{{
    "is_ai_related": true/false,
    "confidence_score": 0.0-1.0,
    "reasoning": "判断理由",
    "ai_categories": ["相关的AI分类"],
    "tech_stack": ["技术栈"]
}}"""
    
    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """解析AI模型响应"""
        try:
            # 尝试提取JSON
            if '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                return {
                    'is_ai_related': result.get('is_ai_related', False),
                    'confidence_score': result.get('confidence_score', 0.5),
                    'reasoning': result.get('reasoning', ''),
                    'ai_categories': result.get('ai_categories', []),
                    'tech_stack': result.get('tech_stack', []),
                    'analysis_method': 'ai_model'
                }
        except Exception as e:
            logger.warning(f"解析AI响应失败: {e}")
        
        # 如果解析失败，基于文本内容判断
        content_lower = content.lower()
        ai_indicators = ['ai', 'artificial intelligence', 'machine learning', 'neural', 'deep learning']
        
        is_ai = any(indicator in content_lower for indicator in ai_indicators)
        
        return {
            'is_ai_related': is_ai,
            'confidence_score': 0.7 if is_ai else 0.3,
            'reasoning': f"基于模型输出文本分析: {content[:100]}...",
            'ai_categories': [],
            'tech_stack': [],
            'analysis_method': 'text_analysis'
        }
    
    def _parse_hf_classification(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """解析Hugging Face分类结果"""
        try:
            labels = result.get('labels', [])
            scores = result.get('scores', [])
            
            if labels and scores:
                top_label = labels[0]
                top_score = scores[0]
                
                is_ai_related = top_label in ['artificial intelligence', 'machine learning'] and top_score > 0.5
                
                return {
                    'is_ai_related': is_ai_related,
                    'confidence_score': top_score,
                    'reasoning': f"Hugging Face分类结果: {top_label} (置信度: {top_score:.2f})",
                    'ai_categories': [top_label] if is_ai_related else [],
                    'tech_stack': [],
                    'analysis_method': 'huggingface'
                }
        except Exception as e:
            logger.warning(f"解析Hugging Face结果失败: {e}")
        
        return {
            'is_ai_related': False,
            'confidence_score': 0.5,
            'reasoning': "Hugging Face分类解析失败",
            'ai_categories': [],
            'tech_stack': [],
            'analysis_method': 'fallback'
        }
    
    def _extract_ai_categories(self, keywords: List[str]) -> List[str]:
        """从关键词提取AI分类"""
        categories = []
        
        if any(kw in ['nlp', 'natural language processing', 'text', 'language'] for kw in keywords):
            categories.append('Natural Language Processing')
        
        if any(kw in ['computer vision', 'cv', 'image', 'vision'] for kw in keywords):
            categories.append('Computer Vision')
        
        if any(kw in ['machine learning', 'ml', 'classification', 'regression'] for kw in keywords):
            categories.append('Machine Learning')
        
        if any(kw in ['deep learning', 'neural network', 'neural'] for kw in keywords):
            categories.append('Deep Learning')
        
        if any(kw in ['chatbot', 'bot', 'assistant', 'llm', 'gpt'] for kw in keywords):
            categories.append('Conversational AI')
        
        return categories or ['Artificial Intelligence']
    
    def _extract_tech_stack(self, text: str) -> List[str]:
        """从文本提取技术栈"""
        tech_keywords = {
            'python': 'Python',
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'keras': 'Keras',
            'scikit-learn': 'Scikit-learn',
            'opencv': 'OpenCV',
            'transformers': 'Transformers',
            'huggingface': 'Hugging Face',
            'langchain': 'LangChain'
        }
        
        found_tech = []
        for keyword, tech_name in tech_keywords.items():
            if keyword in text:
                found_tech.append(tech_name)
        
        return found_tech
    
    async def batch_classify(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量分类项目"""
        results = []
        
        for project in projects:
            result = await self.classify(project)
            results.append(result)
            
            # 添加小延迟避免API限制
            if self.provider in ['ollama', 'huggingface']:
                await asyncio.sleep(0.1)
        
        return results
