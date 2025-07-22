"""
日志管理模块
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "1 day",
    retention: str = "7 days"
) -> logger:
    """
    设置日志记录器
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
        rotation: 日志轮转设置
        retention: 日志保留时间
    
    Returns:
        配置好的logger实例
    """
    # 移除默认的handler
    logger.remove()
    
    # 控制台输出格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件输出格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台handler
    logger.add(
        sys.stdout,
        format=console_format,
        level=log_level,
        colorize=True
    )
    
    # 添加文件handler（如果指定了文件路径）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format=file_format,
            level=log_level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8"
        )
    
    return logger


def get_logger(name: str = None) -> logger:
    """
    获取logger实例
    
    Args:
        name: logger名称
    
    Returns:
        logger实例
    """
    if name:
        return logger.bind(name=name)
    return logger
