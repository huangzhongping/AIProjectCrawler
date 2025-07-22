"""
数据清洗模块
"""

import re
import hashlib
from typing import List, Dict, Any, Set
from datetime import datetime
from difflib import SequenceMatcher
from loguru import logger


class DataCleaner:
    """数据清洗器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据清洗器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # 去重配置
        dedup_config = config.get('data', {}).get('deduplication', {})
        self.similarity_threshold = dedup_config.get('similarity_threshold', 0.9)
        self.compare_fields = dedup_config.get('fields_to_compare', ['name', 'description', 'url'])
        
        logger.info("数据清洗器初始化完成")
    
    def clean_and_deduplicate(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        清洗和去重数据
        
        Args:
            raw_data: 原始数据列表
        
        Returns:
            清洗后的数据列表
        """
        logger.info(f"开始数据清洗，原始数据 {len(raw_data)} 条")
        
        # 1. 基础清洗
        cleaned_data = []
        for item in raw_data:
            cleaned_item = self.clean_single_item(item)
            if cleaned_item and self.is_valid_item(cleaned_item):
                cleaned_data.append(cleaned_item)
        
        logger.info(f"基础清洗完成，有效数据 {len(cleaned_data)} 条")
        
        # 2. 去重
        deduplicated_data = self.deduplicate(cleaned_data)
        
        logger.info(f"去重完成，最终数据 {len(deduplicated_data)} 条")
        
        return deduplicated_data
    
    def clean_single_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗单个数据项
        
        Args:
            item: 原始数据项
        
        Returns:
            清洗后的数据项
        """
        cleaned = {}
        
        # 清洗名称
        name = item.get('name', '').strip()
        cleaned['name'] = self.clean_text(name)
        
        # 清洗描述
        description = item.get('description', '').strip()
        cleaned['description'] = self.clean_text(description)
        
        # 清洗URL
        url = item.get('url', '').strip()
        cleaned['url'] = self.clean_url(url)
        
        # 清洗数字字段
        cleaned['stars'] = self.clean_number(item.get('stars', 0))
        cleaned['forks'] = self.clean_number(item.get('forks', 0))
        cleaned['votes'] = self.clean_number(item.get('votes', 0))
        
        # 清洗语言
        language = item.get('language', '').strip()
        cleaned['language'] = self.clean_language(language)
        
        # 清洗标签
        tags = item.get('tags', [])
        cleaned['tags'] = self.clean_tags(tags)
        
        # 清洗作者
        author = item.get('author', '').strip()
        cleaned['author'] = self.clean_text(author)
        
        # 保留其他字段
        for key, value in item.items():
            if key not in cleaned:
                cleaned[key] = value
        
        # 添加清洗时间戳
        cleaned['cleaned_at'] = datetime.now().isoformat()
        
        return cleaned
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本内容
        
        Args:
            text: 原始文本
        
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 移除特殊字符（保留基本标点）
        text = re.sub(r'[^\w\s\-.,!?()[\]{}:;"\'/]', '', text)
        
        # 移除emoji（简单处理）
        text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', '', text)
        
        return text.strip()
    
    def clean_url(self, url: str) -> str:
        """
        清洗URL
        
        Args:
            url: 原始URL
        
        Returns:
            清洗后的URL
        """
        if not url:
            return ""
        
        # 移除空白字符
        url = url.strip()
        
        # 确保URL格式正确
        if not url.startswith(('http://', 'https://')):
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                # 相对URL，需要根据来源补全
                pass
            else:
                url = 'https://' + url
        
        # 移除URL中的跟踪参数
        url = re.sub(r'[?&](utm_|ref=|source=)[^&]*', '', url)
        
        return url
    
    def clean_number(self, value: Any) -> int:
        """
        清洗数字字段
        
        Args:
            value: 原始值
        
        Returns:
            清洗后的整数
        """
        if isinstance(value, int):
            return max(0, value)
        
        if isinstance(value, str):
            # 移除非数字字符
            numbers = re.findall(r'\d+', value)
            if numbers:
                return int(numbers[0])
        
        return 0
    
    def clean_language(self, language: str) -> str:
        """
        清洗编程语言字段
        
        Args:
            language: 原始语言
        
        Returns:
            标准化的语言名称
        """
        if not language:
            return ""
        
        language = language.strip().lower()
        
        # 语言名称标准化映射
        language_mapping = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'cpp': 'c++',
            'c#': 'csharp',
            'c sharp': 'csharp',
            'golang': 'go',
            'node': 'javascript',
            'nodejs': 'javascript',
            'react': 'javascript',
            'vue': 'javascript',
            'angular': 'javascript'
        }
        
        return language_mapping.get(language, language.title())
    
    def clean_tags(self, tags: List[str]) -> List[str]:
        """
        清洗标签列表
        
        Args:
            tags: 原始标签列表
        
        Returns:
            清洗后的标签列表
        """
        if not tags:
            return []
        
        cleaned_tags = []
        for tag in tags:
            if isinstance(tag, str):
                cleaned_tag = self.clean_text(tag.lower())
                if cleaned_tag and len(cleaned_tag) > 1 and cleaned_tag not in cleaned_tags:
                    cleaned_tags.append(cleaned_tag)
        
        return cleaned_tags[:10]  # 限制标签数量
    
    def is_valid_item(self, item: Dict[str, Any]) -> bool:
        """
        验证数据项是否有效
        
        Args:
            item: 数据项
        
        Returns:
            是否有效
        """
        # 必须有名称
        if not item.get('name'):
            return False
        
        # 必须有URL或描述
        if not item.get('url') and not item.get('description'):
            return False
        
        # 名称长度检查
        name = item.get('name', '')
        if len(name) < 2 or len(name) > 200:
            return False
        
        return True
    
    def deduplicate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去重数据
        
        Args:
            data: 数据列表
        
        Returns:
            去重后的数据列表
        """
        if not data:
            return []
        
        unique_data = []
        seen_hashes = set()
        
        for item in data:
            # 计算项目的哈希值
            item_hash = self.calculate_item_hash(item)
            
            if item_hash not in seen_hashes:
                # 检查是否与已有项目相似
                is_duplicate = False
                for existing_item in unique_data:
                    if self.is_similar(item, existing_item):
                        is_duplicate = True
                        # 合并信息（保留更完整的数据）
                        merged_item = self.merge_similar_items(existing_item, item)
                        # 替换原有项目
                        idx = unique_data.index(existing_item)
                        unique_data[idx] = merged_item
                        break
                
                if not is_duplicate:
                    unique_data.append(item)
                    seen_hashes.add(item_hash)
        
        return unique_data
    
    def calculate_item_hash(self, item: Dict[str, Any]) -> str:
        """
        计算项目的哈希值
        
        Args:
            item: 项目数据
        
        Returns:
            哈希值
        """
        # 使用URL作为主要标识符
        url = item.get('url', '')
        if url:
            return hashlib.md5(url.encode()).hexdigest()
        
        # 如果没有URL，使用名称和描述
        name = item.get('name', '')
        description = item.get('description', '')
        combined = f"{name}|{description}"
        
        return hashlib.md5(combined.encode()).hexdigest()
    
    def is_similar(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """
        判断两个项目是否相似
        
        Args:
            item1: 项目1
            item2: 项目2
        
        Returns:
            是否相似
        """
        similarities = []
        
        for field in self.compare_fields:
            value1 = str(item1.get(field, '')).lower()
            value2 = str(item2.get(field, '')).lower()
            
            if value1 and value2:
                similarity = SequenceMatcher(None, value1, value2).ratio()
                similarities.append(similarity)
        
        if not similarities:
            return False
        
        # 平均相似度
        avg_similarity = sum(similarities) / len(similarities)
        
        return avg_similarity >= self.similarity_threshold
    
    def merge_similar_items(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并相似的项目
        
        Args:
            item1: 项目1
            item2: 项目2
        
        Returns:
            合并后的项目
        """
        merged = item1.copy()
        
        # 选择更完整的信息
        for key, value in item2.items():
            if key not in merged or not merged[key]:
                merged[key] = value
            elif key in ['stars', 'forks', 'votes']:
                # 数字字段取最大值
                merged[key] = max(merged.get(key, 0), value)
            elif key == 'tags':
                # 合并标签
                existing_tags = merged.get('tags', [])
                new_tags = value if isinstance(value, list) else []
                merged['tags'] = list(set(existing_tags + new_tags))
        
        # 添加合并标记
        merged['merged_from'] = [item1.get('source', ''), item2.get('source', '')]
        
        return merged
