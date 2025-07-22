"""
关键词提取器
"""

import json
import re
from typing import Dict, Any, List, Set
from openai import AsyncOpenAI
from loguru import logger


class KeywordExtractor:
    """关键词提取器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化关键词提取器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # OpenAI配置
        api_config = config.get('api', {}).get('openai', {})
        self.api_key = api_config.get('api_key')
        self.model = api_config.get('model', 'gpt-3.5-turbo')
        self.max_tokens = api_config.get('max_tokens', 1000)
        self.temperature = api_config.get('temperature', 0.3)
        
        # 关键词提取配置
        keyword_config = config.get('ai_analysis', {}).get('keyword_extraction', {})
        self.max_keywords = keyword_config.get('max_keywords', 10)
        self.min_keyword_length = keyword_config.get('min_keyword_length', 3)
        
        # 初始化OpenAI客户端
        if not self.api_key or self.api_key.startswith('${'):
            logger.warning("OpenAI API密钥未设置，将使用基础关键词提取")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("关键词提取器初始化完成")
        
        # 加载提示词
        self.prompt_template = self._load_extraction_prompt()
        
        # 预定义的技术关键词
        self.tech_keywords = self._load_tech_keywords()
    
    def _load_extraction_prompt(self) -> str:
        """
        加载关键词提取提示词模板
        
        Returns:
            提示词模板
        """
        try:
            import yaml
            from pathlib import Path
            
            prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"
            if prompts_path.exists():
                with open(prompts_path, 'r', encoding='utf-8') as f:
                    prompts = yaml.safe_load(f)
                    return prompts.get('keyword_extraction_prompt', self._get_default_prompt())
        except Exception as e:
            logger.warning(f"加载提示词文件失败: {e}")
        
        return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """
        获取默认关键词提取提示词
        
        Returns:
            默认提示词
        """
        return """请从以下AI项目描述中提取最重要的技术关键词和趋势词汇。

项目描述：{description}

要求：
1. 提取5-10个最相关的关键词
2. 关键词应该反映技术特点和应用领域
3. 优先提取AI/ML相关的专业术语
4. 包含新兴技术趋势词汇

请返回JSON格式：
{
    "keywords": ["关键词1", "关键词2", ...],
    "categories": {
        "技术栈": ["技术关键词"],
        "应用领域": ["应用关键词"],
        "趋势词汇": ["趋势关键词"]
    }
}"""
    
    def _load_tech_keywords(self) -> Set[str]:
        """
        加载预定义的技术关键词
        
        Returns:
            技术关键词集合
        """
        ai_keywords = self.config.get('ai_analysis', {}).get('ai_keywords', [])
        
        # 扩展关键词列表
        extended_keywords = ai_keywords + [
            # 机器学习
            'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'xgboost',
            'random forest', 'svm', 'neural network', 'deep learning',
            
            # 自然语言处理
            'nlp', 'bert', 'gpt', 'transformer', 'llm', 'chatbot',
            'sentiment analysis', 'text mining', 'language model',
            
            # 计算机视觉
            'opencv', 'yolo', 'cnn', 'image recognition', 'object detection',
            'face recognition', 'image processing', 'computer vision',
            
            # 数据科学
            'pandas', 'numpy', 'matplotlib', 'jupyter', 'data science',
            'data analysis', 'visualization', 'big data',
            
            # AI工具和平台
            'hugging face', 'openai', 'anthropic', 'langchain', 'vector database',
            'embedding', 'fine-tuning', 'prompt engineering',
            
            # 新兴技术
            'rag', 'multimodal', 'generative ai', 'diffusion', 'stable diffusion',
            'midjourney', 'dall-e', 'whisper', 'copilot'
        ]
        
        return set(keyword.lower() for keyword in extended_keywords)
    
    async def extract(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取项目关键词
        
        Args:
            project: 项目数据
        
        Returns:
            关键词提取结果
        """
        if not self.client:
            # 如果没有API密钥，使用基础关键词提取
            return self._extract_by_rules(project)
        
        try:
            description = project.get('description', '')
            if not description:
                return self._extract_by_rules(project)
            
            # 构建提示词
            prompt = self.prompt_template.format(description=description)
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的技术关键词提取专家。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # 解析响应
            content = response.choices[0].message.content
            result = self._parse_extraction_result(content)
            
            # 与基础提取结果合并
            basic_result = self._extract_by_rules(project)
            merged_result = self._merge_results(result, basic_result)
            
            logger.debug(f"关键词提取完成: {project.get('name')} -> {len(merged_result['keywords'])} 个关键词")
            return merged_result
            
        except Exception as e:
            logger.error(f"关键词提取失败: {str(e)}")
            # 降级到基础提取
            return self._extract_by_rules(project)
    
    def _parse_extraction_result(self, content: str) -> Dict[str, Any]:
        """
        解析关键词提取结果
        
        Args:
            content: API响应内容
        
        Returns:
            解析后的结果
        """
        try:
            # 尝试解析JSON
            if '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                keywords = result.get('keywords', [])
                categories = result.get('categories', {})
                
                return {
                    'keywords': keywords[:self.max_keywords],
                    'categories': categories,
                    'extraction_method': 'ai'
                }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"解析关键词提取结果失败: {e}")
        
        # 如果解析失败，从文本中提取
        keywords = self._extract_keywords_from_text(content)
        
        return {
            'keywords': keywords[:self.max_keywords],
            'categories': {'提取失败': keywords},
            'extraction_method': 'text_fallback'
        }
    
    def _extract_by_rules(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于规则的关键词提取（后备方案）
        
        Args:
            project: 项目数据
        
        Returns:
            关键词提取结果
        """
        name = project.get('name', '').lower()
        description = project.get('description', '').lower()
        tags = [tag.lower() for tag in project.get('tags', [])]
        language = project.get('language', '').lower()
        
        # 合并所有文本
        all_text = f"{name} {description} {' '.join(tags)} {language}"
        
        # 提取技术关键词
        tech_keywords = []
        for keyword in self.tech_keywords:
            if keyword in all_text:
                tech_keywords.append(keyword)
        
        # 提取其他关键词
        other_keywords = self._extract_keywords_from_text(all_text)
        
        # 合并并去重
        all_keywords = list(set(tech_keywords + other_keywords))
        
        # 按相关性排序（技术关键词优先）
        sorted_keywords = tech_keywords + [k for k in other_keywords if k not in tech_keywords]
        
        # 分类
        categories = {
            '技术栈': [k for k in sorted_keywords if k in self.tech_keywords],
            '应用领域': tags,
            '编程语言': [language] if language else []
        }
        
        return {
            'keywords': sorted_keywords[:self.max_keywords],
            'categories': categories,
            'extraction_method': 'rules'
        }
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
        
        Returns:
            关键词列表
        """
        # 简单的关键词提取：找出常见的技术词汇
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # 过滤短词和常见词
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'a', 'an'}
        
        keywords = []
        for word in words:
            if (len(word) >= self.min_keyword_length and 
                word not in stop_words and 
                word not in keywords):
                keywords.append(word)
        
        return keywords[:self.max_keywords]
    
    def _merge_results(self, ai_result: Dict[str, Any], basic_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并AI提取和基础提取的结果
        
        Args:
            ai_result: AI提取结果
            basic_result: 基础提取结果
        
        Returns:
            合并后的结果
        """
        # 合并关键词
        all_keywords = ai_result.get('keywords', []) + basic_result.get('keywords', [])
        unique_keywords = []
        seen = set()
        
        for keyword in all_keywords:
            if keyword.lower() not in seen:
                seen.add(keyword.lower())
                unique_keywords.append(keyword)
        
        # 合并分类
        ai_categories = ai_result.get('categories', {})
        basic_categories = basic_result.get('categories', {})
        
        merged_categories = {}
        for category, keywords in {**basic_categories, **ai_categories}.items():
            if category not in merged_categories:
                merged_categories[category] = []
            merged_categories[category].extend(keywords)
            # 去重
            merged_categories[category] = list(set(merged_categories[category]))
        
        return {
            'keywords': unique_keywords[:self.max_keywords],
            'categories': merged_categories,
            'extraction_method': 'merged'
        }
