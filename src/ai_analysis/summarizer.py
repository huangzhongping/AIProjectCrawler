"""
项目总结生成器
"""

import json
from typing import Dict, Any
from openai import AsyncOpenAI
from loguru import logger


class ProjectSummarizer:
    """项目总结生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化总结生成器
        
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
        
        # 初始化OpenAI客户端
        if not self.api_key or self.api_key.startswith('${'):
            logger.warning("OpenAI API密钥未设置，将使用基础总结生成")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("项目总结生成器初始化完成")
        
        # 加载提示词
        self.prompt_template = self._load_summary_prompt()
    
    def _load_summary_prompt(self) -> str:
        """
        加载总结提示词模板
        
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
                    return prompts.get('project_summary_prompt', self._get_default_prompt())
        except Exception as e:
            logger.warning(f"加载提示词文件失败: {e}")
        
        return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """
        获取默认总结提示词
        
        Returns:
            默认提示词
        """
        return """请为以下AI项目生成一个简洁而全面的中文总结。

项目信息：
- 名称：{name}
- 描述：{description}
- 星标数：{stars}
- 编程语言：{language}
- 最近更新：{updated_at}

总结要求：
1. 100-200字的简洁描述
2. 突出项目的AI技术特点
3. 说明项目的实用价值
4. 使用通俗易懂的语言

请返回JSON格式：
{
    "summary": "项目总结",
    "highlights": ["亮点1", "亮点2", "亮点3"],
    "use_cases": ["应用场景1", "应用场景2"]
}"""
    
    async def summarize(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成项目总结
        
        Args:
            project: 项目数据
        
        Returns:
            总结结果
        """
        if not self.client:
            # 如果没有API密钥，使用基础总结生成
            return self._generate_basic_summary(project)
        
        try:
            # 准备输入数据
            name = project.get('name', '')
            description = project.get('description', '')
            stars = project.get('stars', 0)
            language = project.get('language', '')
            updated_at = project.get('updated_at', '')
            
            # 构建提示词
            prompt = self.prompt_template.format(
                name=name,
                description=description,
                stars=stars,
                language=language or '未知',
                updated_at=updated_at or '未知'
            )
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的技术项目分析师，擅长用简洁明了的语言总结AI项目。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # 解析响应
            content = response.choices[0].message.content
            result = self._parse_summary_result(content)
            
            logger.debug(f"项目总结生成完成: {name}")
            return result
            
        except Exception as e:
            logger.error(f"项目总结生成失败: {str(e)}")
            # 降级到基础总结
            return self._generate_basic_summary(project)
    
    def _parse_summary_result(self, content: str) -> Dict[str, Any]:
        """
        解析总结结果
        
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
                
                return {
                    'summary': result.get('summary', ''),
                    'highlights': result.get('highlights', []),
                    'use_cases': result.get('use_cases', []),
                    'generation_method': 'ai'
                }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"解析总结结果失败: {e}")
        
        # 如果解析失败，使用原始内容作为总结
        return {
            'summary': content[:200] + '...' if len(content) > 200 else content,
            'highlights': [],
            'use_cases': [],
            'generation_method': 'text_fallback'
        }
    
    def _generate_basic_summary(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成基础总结（后备方案）
        
        Args:
            project: 项目数据
        
        Returns:
            总结结果
        """
        name = project.get('name', '')
        description = project.get('description', '')
        stars = project.get('stars', 0)
        language = project.get('language', '')
        
        # 生成基础总结
        summary_parts = []
        
        if name:
            summary_parts.append(f"{name}是一个")
        
        if language:
            summary_parts.append(f"基于{language}的")
        
        summary_parts.append("AI相关项目")
        
        if description:
            # 截取描述的前100个字符
            desc_short = description[:100] + '...' if len(description) > 100 else description
            summary_parts.append(f"，{desc_short}")
        
        if stars > 0:
            summary_parts.append(f"。该项目已获得{stars}个星标")
        
        summary = ''.join(summary_parts)
        
        # 生成亮点
        highlights = []
        if stars > 1000:
            highlights.append("高人气项目")
        if language:
            highlights.append(f"使用{language}开发")
        if 'ai' in description.lower() or 'ml' in description.lower():
            highlights.append("AI/ML技术应用")
        
        # 生成应用场景
        use_cases = []
        if 'chatbot' in description.lower():
            use_cases.append("聊天机器人")
        if 'image' in description.lower() or 'vision' in description.lower():
            use_cases.append("图像处理")
        if 'text' in description.lower() or 'nlp' in description.lower():
            use_cases.append("文本处理")
        if 'data' in description.lower():
            use_cases.append("数据分析")
        
        return {
            'summary': summary,
            'highlights': highlights,
            'use_cases': use_cases,
            'generation_method': 'basic'
        }
