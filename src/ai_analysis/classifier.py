"""
AI项目分类器
"""

import json
import asyncio
from typing import Dict, Any, List
from openai import AsyncOpenAI
from loguru import logger

try:
    from ..utils.config import get_config_value
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.config import get_config_value


class AIProjectClassifier:
    """AI项目分类器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化分类器
        
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
        self.timeout = api_config.get('timeout', 30)
        
        # AI分析配置
        ai_config = config.get('ai_analysis', {})
        self.threshold = ai_config.get('ai_relevance_threshold', 0.7)
        self.ai_keywords = ai_config.get('ai_keywords', [])
        
        # 强制禁用OpenAI API，始终使用关键词分析
        logger.info("使用关键词分析模式（已禁用OpenAI API调用）")
        self.client = None
        
        # 加载提示词
        self.prompt_template = self._load_classification_prompt()
    
    def _load_classification_prompt(self) -> str:
        """
        加载分类提示词模板
        
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
                    return prompts.get('ai_classification_prompt', self._get_default_prompt())
        except Exception as e:
            logger.warning(f"加载提示词文件失败: {e}")
        
        return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """
        获取默认分类提示词
        
        Returns:
            默认提示词
        """
        return """你是一个专业的AI项目分析师。请分析以下项目信息，判断它是否与人工智能相关。

项目信息：
- 名称：{name}
- 描述：{description}
- 标签：{tags}
- 编程语言：{language}

请从以下几个维度进行分析：
1. 项目是否直接使用了AI/ML技术
2. 项目是否为AI工具或平台
3. 项目是否解决AI相关问题
4. 项目描述中是否包含AI相关关键词

请返回JSON格式的结果：
{
    "is_ai_related": true/false,
    "confidence_score": 0.0-1.0,
    "reasoning": "判断理由",
    "ai_categories": ["机器学习", "自然语言处理", "计算机视觉", "等"],
    "tech_stack": ["使用的AI技术栈"]
}"""
    
    async def classify(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        分类项目是否为AI相关
        
        Args:
            project: 项目数据
        
        Returns:
            分类结果
        """
        if not self.client:
            # 如果没有API密钥，使用关键词匹配作为后备方案
            return self._classify_by_keywords(project)
        
        try:
            # 准备输入数据
            name = project.get('name', '')
            description = project.get('description', '')
            tags = project.get('tags', [])
            language = project.get('language', '')
            
            # 构建提示词
            prompt = self.prompt_template.format(
                name=name,
                description=description,
                tags=', '.join(tags) if tags else '无',
                language=language or '未知'
            )
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI项目分析师。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            
            # 解析响应
            content = response.choices[0].message.content
            result = self._parse_classification_result(content)
            
            logger.debug(f"AI分类完成: {name} -> {result['is_ai_related']}")
            return result
            
        except Exception as e:
            logger.error(f"AI分类失败: {str(e)}")
            # 降级到关键词匹配
            return self._classify_by_keywords(project)
    
    def _parse_classification_result(self, content: str) -> Dict[str, Any]:
        """
        解析AI分类结果
        
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
                
                # 验证必需字段
                if 'is_ai_related' in result and 'confidence_score' in result:
                    return {
                        'is_ai_related': bool(result.get('is_ai_related', False)),
                        'confidence_score': float(result.get('confidence_score', 0.0)),
                        'reasoning': result.get('reasoning', ''),
                        'ai_categories': result.get('ai_categories', []),
                        'tech_stack': result.get('tech_stack', [])
                    }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"解析AI分类结果失败: {e}")
        
        # 如果解析失败，尝试从文本中提取信息
        is_ai_related = any(keyword in content.lower() for keyword in ['true', 'ai', 'artificial intelligence'])
        
        return {
            'is_ai_related': is_ai_related,
            'confidence_score': 0.5,
            'reasoning': '解析失败，使用文本匹配',
            'ai_categories': [],
            'tech_stack': []
        }
    
    def _classify_by_keywords(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于关键词的分类（后备方案）
        
        Args:
            project: 项目数据
        
        Returns:
            分类结果
        """
        name = project.get('name', '').lower()
        description = project.get('description', '').lower()
        tags = [tag.lower() for tag in project.get('tags', [])]
        
        # 合并所有文本
        all_text = f"{name} {description} {' '.join(tags)}"
        
        # 计算匹配的AI关键词数量
        matched_keywords = []
        for keyword in self.ai_keywords:
            if keyword.lower() in all_text:
                matched_keywords.append(keyword)
        
        # 计算置信度
        confidence = min(len(matched_keywords) / 3.0, 1.0)  # 最多3个关键词达到100%置信度
        is_ai_related = confidence >= (self.threshold * 0.7)  # 降低阈值
        
        logger.debug(f"关键词分类: {project.get('name')} -> {is_ai_related} (匹配: {matched_keywords})")
        
        return {
            'is_ai_related': is_ai_related,
            'confidence_score': confidence,
            'reasoning': f'基于关键词匹配: {matched_keywords}',
            'ai_categories': ['AI相关'] if is_ai_related else [],
            'tech_stack': matched_keywords
        }
    
    async def batch_classify(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量分类项目
        
        Args:
            projects: 项目列表
        
        Returns:
            分类结果列表
        """
        logger.info(f"开始批量AI分类，共 {len(projects)} 个项目")
        
        # 并发处理，但限制并发数
        semaphore = asyncio.Semaphore(5)  # 最多5个并发请求
        
        async def classify_with_semaphore(project):
            async with semaphore:
                return await self.classify(project)
        
        tasks = [classify_with_semaphore(project) for project in projects]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"项目 {i} 分类失败: {result}")
                # 使用关键词分类作为后备
                valid_results.append(self._classify_by_keywords(projects[i]))
            else:
                valid_results.append(result)
        
        ai_count = sum(1 for r in valid_results if r['is_ai_related'])
        logger.info(f"批量AI分类完成，发现 {ai_count} 个AI相关项目")
        
        return valid_results
