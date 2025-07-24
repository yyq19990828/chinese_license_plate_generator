"""
变换配置管理模块

提供变换效果的配置管理、概率控制和参数设置功能。
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import os


class TransformType(Enum):
    """变换类型枚举"""
    AGING = "aging"           # 老化效果
    PERSPECTIVE = "perspective"  # 透视变换
    LIGHTING = "lighting"     # 光照效果
    COMPOSITE = "composite"   # 复合变换


@dataclass
class TransformParams:
    """
    单个变换的参数配置
    """
    name: str
    transform_type: TransformType
    probability: float = 0.3
    intensity_range: tuple = (0.1, 0.8)
    enabled: bool = True
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """验证参数有效性"""
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(f"Probability must be between 0.0 and 1.0, got {self.probability}")
        
        if len(self.intensity_range) != 2 or self.intensity_range[0] >= self.intensity_range[1]:
            raise ValueError(f"Invalid intensity_range: {self.intensity_range}")


class TransformConfig:
    """
    变换配置管理器
    
    管理所有变换效果的配置、概率和参数设置。
    
    Args:
        config_file (Optional[str]): 配置文件路径，如果为None则使用默认配置
    """
    
    DEFAULT_PROBABILITY = 0.3
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file (Optional[str]): 配置文件路径，如果为None则使用默认配置
        """
        self._transforms: Dict[str, TransformParams] = {}
        self._global_probability = self.DEFAULT_PROBABILITY
        self._max_concurrent_transforms = 3
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        else:
            self._load_default_config()
    
    def _load_default_config(self) -> None:
        """加载默认配置"""
        
        # 老化效果配置
        self.add_transform(TransformParams(
            name="wear_effect",
            transform_type=TransformType.AGING,
            probability=0.3,
            intensity_range=(0.1, 0.6),
            custom_params={
                "wear_strength": 0.3,
                "blur_kernel_size": 3,
                "erosion_kernel_size": 2
            }
        ))
        
        self.add_transform(TransformParams(
            name="fade_effect", 
            transform_type=TransformType.AGING,
            probability=0.3,
            intensity_range=(0.1, 0.5),
            custom_params={
                "fade_factor": 0.7,
                "color_shift": 0.1
            }
        ))
        
        self.add_transform(TransformParams(
            name="dirt_effect",
            transform_type=TransformType.AGING,
            probability=0.2,
            intensity_range=(0.1, 0.4),
            custom_params={
                "dirt_density": 0.05,
                "spot_size_range": (2, 8)
            }
        ))
        
        # 透视变换配置
        self.add_transform(TransformParams(
            name="tilt_transform",
            transform_type=TransformType.PERSPECTIVE,
            probability=0.4,
            intensity_range=(0.1, 0.3),
            custom_params={
                "max_angle": 15,  # 最大倾斜角度（度）
                "horizontal_tilt": True,
                "vertical_tilt": True
            }
        ))
        
        self.add_transform(TransformParams(
            name="perspective_transform",
            transform_type=TransformType.PERSPECTIVE,
            probability=0.3,
            intensity_range=(0.1, 0.4),
            custom_params={
                "perspective_strength": 0.2,
                "maintain_aspect": True
            }
        ))
        
        self.add_transform(TransformParams(
            name="rotation_transform",
            transform_type=TransformType.PERSPECTIVE,
            probability=0.2,
            intensity_range=(0.1, 0.2),
            custom_params={
                "max_rotation": 10  # 最大旋转角度（度）
            }
        ))
        
        # 光照效果配置
        self.add_transform(TransformParams(
            name="shadow_effect",
            transform_type=TransformType.LIGHTING,
            probability=0.3,
            intensity_range=(0.2, 0.6),
            custom_params={
                "shadow_strength": 0.4,
                "shadow_blur": 5,
                "shadow_offset": (3, 3)
            }
        ))
        
        self.add_transform(TransformParams(
            name="reflection_effect",
            transform_type=TransformType.LIGHTING,
            probability=0.2,
            intensity_range=(0.1, 0.4),
            custom_params={
                "reflection_strength": 0.3,
                "reflection_size": 0.3
            }
        ))
        
        self.add_transform(TransformParams(
            name="night_effect",
            transform_type=TransformType.LIGHTING,
            probability=0.2,
            intensity_range=(0.2, 0.7),
            custom_params={
                "darkness_factor": 0.6,
                "color_temperature": "warm"
            }
        ))
        
        self.add_transform(TransformParams(
            name="backlight_effect",
            transform_type=TransformType.LIGHTING,
            probability=0.2,
            intensity_range=(0.1, 0.5),
            custom_params={
                "backlight_strength": 0.4,
                "edge_enhancement": True
            }
        ))
    
    def add_transform(self, transform_params: TransformParams) -> None:
        """
        添加变换配置
        
        Args:
            transform_params (TransformParams): 变换参数配置
        """
        self._transforms[transform_params.name] = transform_params
    
    def remove_transform(self, name: str) -> bool:
        """
        移除变换配置
        
        Args:
            name (str): 变换名称
            
        Returns:
            bool: 是否成功移除
        """
        if name in self._transforms:
            del self._transforms[name]
            return True
        return False
    
    def get_transform(self, name: str) -> Optional[TransformParams]:
        """
        获取指定变换的配置
        
        Args:
            name (str): 变换名称
            
        Returns:
            Optional[TransformParams]: 变换配置，如果不存在则返回None
        """
        return self._transforms.get(name)
    
    def get_transforms_by_type(self, transform_type: TransformType) -> List[TransformParams]:
        """
        获取指定类型的所有变换配置
        
        Args:
            transform_type (TransformType): 变换类型
            
        Returns:
            List[TransformParams]: 该类型的所有变换配置
        """
        return [
            transform for transform in self._transforms.values()
            if transform.transform_type == transform_type and transform.enabled
        ]
    
    def get_all_transforms(self) -> Dict[str, TransformParams]:
        """
        获取所有变换配置
        
        Returns:
            Dict[str, TransformParams]: 所有变换配置的字典
        """
        return self._transforms.copy()
    
    def get_enabled_transforms(self) -> Dict[str, TransformParams]:
        """
        获取所有启用的变换配置
        
        Returns:
            Dict[str, TransformParams]: 所有启用的变换配置
        """
        return {
            name: transform for name, transform in self._transforms.items()
            if transform.enabled
        }
    
    def enable_transform(self, name: str) -> bool:
        """
        启用指定变换
        
        Args:
            name (str): 变换名称
            
        Returns:
            bool: 是否成功启用
        """
        if name in self._transforms:
            self._transforms[name].enabled = True
            return True
        return False
    
    def disable_transform(self, name: str) -> bool:
        """
        禁用指定变换
        
        Args:
            name (str): 变换名称
            
        Returns:
            bool: 是否成功禁用
        """
        if name in self._transforms:
            self._transforms[name].enabled = False
            return True
        return False
    
    def set_global_probability(self, probability: float) -> None:
        """
        设置全局概率乘子
        
        Args:
            probability (float): 全局概率值
        """
        if not 0.0 <= probability <= 1.0:
            raise ValueError("Global probability must be between 0.0 and 1.0")
        self._global_probability = probability
    
    def get_global_probability(self) -> float:
        """
        获取全局概率乘子
        
        Returns:
            float: 全局概率值
        """
        return self._global_probability
    
    def set_max_concurrent_transforms(self, max_count: int) -> None:
        """
        设置最大并发变换数量
        
        Args:
            max_count (int): 最大并发数量
        """
        if max_count <= 0:
            raise ValueError("Max concurrent transforms must be positive")
        self._max_concurrent_transforms = max_count
    
    def get_max_concurrent_transforms(self) -> int:
        """
        获取最大并发变换数量
        
        Returns:
            int: 最大并发数量
        """
        return self._max_concurrent_transforms
    
    def update_transform_probability(self, name: str, probability: float) -> bool:
        """
        更新指定变换的概率
        
        Args:
            name (str): 变换名称
            probability (float): 新的概率值
            
        Returns:
            bool: 是否成功更新
        """
        if name in self._transforms:
            if not 0.0 <= probability <= 1.0:
                raise ValueError("Probability must be between 0.0 and 1.0")
            self._transforms[name].probability = probability
            return True
        return False
    
    def update_all_probabilities(self, probability: float) -> None:
        """
        批量更新所有变换的概率
        
        Args:
            probability (float): 新的概率值
        """
        if not 0.0 <= probability <= 1.0:
            raise ValueError("Probability must be between 0.0 and 1.0")
        
        for transform in self._transforms.values():
            transform.probability = probability
    
    def get_effective_probability(self, transform_name: str) -> float:
        """
        获取变换的有效概率（考虑全局概率乘子）
        
        Args:
            transform_name (str): 变换名称
            
        Returns:
            float: 有效概率值
        """
        if transform_name not in self._transforms:
            return 0.0
        
        base_probability = self._transforms[transform_name].probability
        return base_probability * self._global_probability
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典格式
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        transforms_dict = {}
        for name, transform in self._transforms.items():
            transforms_dict[name] = {
                'transform_type': transform.transform_type.value,
                'probability': transform.probability,
                'intensity_range': transform.intensity_range,
                'enabled': transform.enabled,
                'custom_params': transform.custom_params
            }
        
        return {
            'global_probability': self._global_probability,
            'max_concurrent_transforms': self._max_concurrent_transforms,
            'transforms': transforms_dict
        }
    
    def save_to_file(self, file_path: str) -> None:
        """
        保存配置到文件
        
        Args:
            file_path (str): 保存路径
        """
        config_dict = self.to_dict()
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, file_path: str) -> None:
        """
        从文件加载配置
        
        Args:
            file_path (str): 配置文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        self._global_probability = config_dict.get('global_probability', self.DEFAULT_PROBABILITY)
        self._max_concurrent_transforms = config_dict.get('max_concurrent_transforms', 3)
        
        self._transforms.clear()
        
        transforms_dict = config_dict.get('transforms', {})
        for name, transform_data in transforms_dict.items():
            transform_params = TransformParams(
                name=name,
                transform_type=TransformType(transform_data['transform_type']),
                probability=transform_data['probability'],
                intensity_range=tuple(transform_data['intensity_range']),
                enabled=transform_data['enabled'],
                custom_params=transform_data['custom_params']
            )
            self.add_transform(transform_params)


# 全局默认配置实例
default_config = TransformConfig()


def get_default_config() -> TransformConfig:
    """
    获取默认配置实例
    
    Returns:
        TransformConfig: 默认配置实例
    """
    return default_config


def create_config_from_dict(config_dict: Dict[str, Any]) -> TransformConfig:
    """
    从字典创建配置实例
    
    Args:
        config_dict (Dict[str, Any]): 配置字典
        
    Returns:
        TransformConfig: 配置实例
    """
    config = TransformConfig()
    
    config._global_probability = config_dict.get('global_probability', TransformConfig.DEFAULT_PROBABILITY)
    config._max_concurrent_transforms = config_dict.get('max_concurrent_transforms', 3)
    
    config._transforms.clear()
    
    transforms_dict = config_dict.get('transforms', {})
    for name, transform_data in transforms_dict.items():
        transform_params = TransformParams(
            name=name,
            transform_type=TransformType(transform_data['transform_type']),
            probability=transform_data['probability'],
            intensity_range=tuple(transform_data['intensity_range']),
            enabled=transform_data['enabled'],
            custom_params=transform_data['custom_params']
        )
        config.add_transform(transform_params)
    
    return config