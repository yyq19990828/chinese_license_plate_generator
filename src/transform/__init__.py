"""
车牌增强变换模块

提供车牌图像的各种增强变换效果，包括老化效果、透视变换和光照模拟。

主要组件:
- BaseTransform: 基础变换类和接口
- TransformConfig: 变换配置管理
- AgingEffects: 车牌老化效果
- PerspectiveTransform: 透视和角度变换
- LightingEffects: 光照条件模拟
- CompositeTransform: 复合变换管理器

使用示例:
    >>> from src.transform import default_config, CompositeTransform
    >>> from PIL import Image
    >>> 
    >>> # 加载车牌图像
    >>> plate_image = Image.open("plate.png")
    >>> 
    >>> # 创建复合变换器
    >>> transformer = CompositeTransform(config=default_config)
    >>> 
    >>> # 应用变换效果
    >>> enhanced_image = transformer.apply(plate_image)
"""

from .base_transform import BaseTransform, TransformUtils
from .transform_config import (
    TransformConfig, 
    TransformParams, 
    TransformType,
    default_config,
    get_default_config,
    create_config_from_dict
)

# 导入具体变换效果
from .aging_effects import WearEffect, FadeEffect, DirtEffect, apply_aging_effects
from .perspective_transform import (
    TiltTransform, PerspectiveTransform, RotationTransform, GeometricDistortion,
    apply_perspective_effects
)
from .lighting_effects import (
    ShadowEffect, ReflectionEffect, NightEffect, BacklightEffect,
    apply_lighting_effects
)
from .composite_transform import CompositeTransform, create_composite_transform, quick_enhance

# 定义模块公开接口
__all__ = [
    # 基础类
    'BaseTransform',
    'TransformUtils',
    
    # 配置管理
    'TransformConfig',
    'TransformParams', 
    'TransformType',
    'default_config',
    'get_default_config',
    'create_config_from_dict',
    
    # 老化效果
    'WearEffect',
    'FadeEffect', 
    'DirtEffect',
    'apply_aging_effects',
    
    # 透视变换
    'TiltTransform',
    'PerspectiveTransform',
    'RotationTransform',
    'GeometricDistortion',
    'apply_perspective_effects',
    
    # 光照效果
    'ShadowEffect',
    'ReflectionEffect',
    'NightEffect', 
    'BacklightEffect',
    'apply_lighting_effects',
    
    # 复合变换管理
    'CompositeTransform',
    'create_composite_transform',
    'quick_enhance'
]

# 模块版本信息
__version__ = "1.0.0"
__author__ = "Chinese License Plate Generator Team"
__description__ = "车牌增强变换模块，提供多种真实场景效果"


def get_version() -> str:
    """
    获取模块版本信息
    
    Returns:
        str: 版本号
    """
    return __version__


def get_available_transforms() -> list:
    """
    获取可用的变换效果列表
    
    Returns:
        list: 可用变换效果的名称列表
    """
    return list(default_config.get_enabled_transforms().keys())


def get_transform_types() -> list:
    """
    获取所有变换类型
    
    Returns:
        list: 变换类型列表
    """
    return [transform_type.value for transform_type in TransformType]


def quick_config(probability: float = 0.3, max_concurrent: int = 3) -> TransformConfig:
    """
    快速创建配置实例
    
    Args:
        probability (float): 全局概率，默认0.3
        max_concurrent (int): 最大并发变换数，默认3
        
    Returns:
        TransformConfig: 配置实例
    """
    config = TransformConfig()
    config.set_global_probability(probability)
    config.set_max_concurrent_transforms(max_concurrent)
    return config