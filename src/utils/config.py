"""
配置管理模块
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，默认为 config/settings.yaml
    
    Returns:
        配置字典
    """
    # 加载环境变量
    load_dotenv()
    
    # 确定配置文件路径
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    # 读取YAML配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 替换环境变量
    config = _replace_env_vars(config)
    
    return config


def _replace_env_vars(obj: Any) -> Any:
    """
    递归替换配置中的环境变量
    
    Args:
        obj: 配置对象
    
    Returns:
        替换后的配置对象
    """
    if isinstance(obj, dict):
        return {key: _replace_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_replace_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        # 提取环境变量名
        env_var = obj[2:-1]
        return os.getenv(env_var, obj)  # 如果环境变量不存在，返回原值
    else:
        return obj


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    通过点分隔的路径获取配置值
    
    Args:
        config: 配置字典
        key_path: 配置路径，如 "api.openai.api_key"
        default: 默认值
    
    Returns:
        配置值
    """
    keys = key_path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置的有效性
    
    Args:
        config: 配置字典
    
    Returns:
        是否有效
    """
    required_keys = [
        "api.openai.api_key",
        "crawler.request.timeout",
        "data.paths.raw_data",
        "logging.level"
    ]
    
    for key_path in required_keys:
        value = get_config_value(config, key_path)
        if value is None:
            print(f"❌ 缺少必需的配置项: {key_path}")
            return False
    
    # 检查OpenAI API密钥
    api_key = get_config_value(config, "api.openai.api_key")
    if not api_key or api_key.startswith("${"):
        print("❌ 请设置有效的OpenAI API密钥")
        return False
    
    return True


def create_directories(config: Dict[str, Any]) -> None:
    """
    根据配置创建必要的目录
    
    Args:
        config: 配置字典
    """
    paths_to_create = [
        get_config_value(config, "data.paths.raw_data"),
        get_config_value(config, "data.paths.processed_data"),
        get_config_value(config, "data.paths.archive_data"),
        get_config_value(config, "data.paths.output"),
        "logs",
        "output/reports",
        "output/charts",
        "output/web"
    ]
    
    for path in paths_to_create:
        if path:
            Path(path).mkdir(parents=True, exist_ok=True)
