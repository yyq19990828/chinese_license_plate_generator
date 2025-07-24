"""
复合变换管理器模块

提供多种变换效果的组合管理，支持智能选择、冲突避免和效果优化。
"""

import random
from typing import List, Dict, Any, Optional, Type, Union, Tuple
from PIL import Image
import numpy as np

from .base_transform import BaseTransform
from .transform_config import TransformConfig, TransformType, default_config
from .aging_effects import WearEffect, FadeEffect, DirtEffect
from .perspective_transform import TiltTransform, PerspectiveTransform, RotationTransform, GeometricDistortion
from .lighting_effects import ShadowEffect, ReflectionEffect, NightEffect, BacklightEffect


class CompositeTransform:
    """
    复合变换管理器
    
    负责管理和协调多种变换效果的应用，确保效果组合的合理性和视觉质量。
    
    Args:
        config (Optional[TransformConfig]): 变换配置，如果为None则使用默认配置
    """
    
    def __init__(self, config: Optional[TransformConfig] = None):
        """
        初始化复合变换管理器
        
        Args:
            config (Optional[TransformConfig]): 变换配置，如果为None则使用默认配置
        """
        self.config = config or default_config
        self._transform_registry = self._build_transform_registry()
        self._conflict_rules = self._define_conflict_rules()
        self._application_order = self._define_application_order()
    
    def _build_transform_registry(self) -> Dict[str, Type[BaseTransform]]:
        """
        构建变换类注册表
        
        Returns:
            Dict[str, Type[BaseTransform]]: 变换名称到类的映射
        """
        return {
            # 老化效果
            'wear_effect': WearEffect,
            'fade_effect': FadeEffect,
            'dirt_effect': DirtEffect,
            
            # 透视变换
            'tilt_transform': TiltTransform,
            'perspective_transform': PerspectiveTransform,
            'rotation_transform': RotationTransform,
            'geometric_distortion': GeometricDistortion,
            
            # 光照效果
            'shadow_effect': ShadowEffect,
            'reflection_effect': ReflectionEffect,
            'night_effect': NightEffect,
            'backlight_effect': BacklightEffect,
        }
    
    def _define_conflict_rules(self) -> Dict[str, List[str]]:
        """
        定义变换之间的冲突规则
        
        Returns:
            Dict[str, List[str]]: 变换名称到冲突变换列表的映射
        """
        return {
            # 几何变换冲突（同时应用多种几何变换可能导致过度扭曲）
            'tilt_transform': ['perspective_transform', 'geometric_distortion'],
            'perspective_transform': ['tilt_transform', 'rotation_transform', 'geometric_distortion'],
            'rotation_transform': ['perspective_transform', 'geometric_distortion'],
            'geometric_distortion': ['tilt_transform', 'perspective_transform', 'rotation_transform'],
            
            # 光照效果冲突（某些光照效果不宜同时出现）
            'night_effect': ['reflection_effect', 'backlight_effect'],
            'reflection_effect': ['night_effect'],
            'backlight_effect': ['night_effect', 'shadow_effect'],
            'shadow_effect': ['backlight_effect'],
        }
    
    def _define_application_order(self) -> List[str]:
        """
        定义变换应用顺序
        
        Returns:
            List[str]: 按应用顺序排列的变换名称列表
        """
        return [
            # 1. 几何变换（最先应用，影响后续效果的空间分布）
            'geometric_distortion',
            'perspective_transform',
            'tilt_transform', 
            'rotation_transform',
            
            # 2. 基础光照效果
            'night_effect',
            'backlight_effect',
            
            # 3. 老化效果
            'fade_effect',
            'wear_effect',
            
            # 4. 环境效果
            'shadow_effect',
            'dirt_effect',
            
            # 5. 表面效果（最后应用）
            'reflection_effect',
        ]
    
    def apply(self, image: Image.Image, 
              max_transforms: Optional[int] = None,
              force_transforms: Optional[List[str]] = None,
              exclude_transforms: Optional[List[str]] = None,
              intensity_scale: float = 1.0) -> Tuple[Image.Image, List[str]]:
        """
        应用复合变换效果
        
        Args:
            image (Image.Image): 输入图像
            max_transforms (Optional[int]): 最大变换数量，如果为None则使用配置值
            force_transforms (Optional[List[str]]): 强制应用的变换列表
            exclude_transforms (Optional[List[str]]): 排除的变换列表
            intensity_scale (float): 整体强度缩放因子，默认1.0
            
        Returns:
            Tuple[Image.Image, List[str]]: 变换后的图像和应用的变换名称列表
        """
        if max_transforms is None:
            max_transforms = self.config.get_max_concurrent_transforms()
        
        # 选择要应用的变换
        selected_transforms = self._select_transforms(
            max_transforms, force_transforms, exclude_transforms
        )
        
        # 按顺序应用变换
        result_image = image
        applied_transforms = []
        
        for transform_name in self._application_order:
            if transform_name in selected_transforms:
                transform_instance = self._create_transform_instance(transform_name, intensity_scale)
                
                enhanced_image = transform_instance(result_image)
                if enhanced_image is not None:
                    result_image = enhanced_image
                    applied_transforms.append(transform_name)
        
        return result_image, applied_transforms
    
    def _select_transforms(self, max_transforms: int,
                          force_transforms: Optional[List[str]] = None,
                          exclude_transforms: Optional[List[str]] = None) -> List[str]:
        """
        智能选择要应用的变换
        
        Args:
            max_transforms (int): 最大变换数量
            force_transforms (Optional[List[str]]): 强制应用的变换
            exclude_transforms (Optional[List[str]]): 排除的变换
            
        Returns:
            List[str]: 选中的变换名称列表
        """
        selected = []
        
        # 添加强制变换
        if force_transforms:
            for transform_name in force_transforms:
                if (transform_name in self._transform_registry and 
                    transform_name not in selected and
                    (not exclude_transforms or transform_name not in exclude_transforms)):
                    selected.append(transform_name)
        
        # 获取可用的变换（排除已选中的和冲突的）
        available_transforms = self._get_available_transforms(selected, exclude_transforms)
        
        # 按概率和类型平衡选择其余变换
        while len(selected) < max_transforms and available_transforms:
            # 按类型分组，确保不同类型的变换都有机会被选中
            type_groups = self._group_by_type(available_transforms)
            
            # 随机选择一个类型
            if type_groups:
                selected_type = random.choice(list(type_groups.keys()))
                candidates = type_groups[selected_type]
                
                # 在该类型中按概率选择
                transform_name = self._weighted_random_choice(candidates)
                
                if transform_name:
                    selected.append(transform_name)
                    
                    # 更新可用变换列表（移除冲突的变换）
                    available_transforms = self._get_available_transforms(selected, exclude_transforms)
        
        return selected
    
    def _get_available_transforms(self, selected: List[str], 
                                 excluded: Optional[List[str]] = None) -> List[str]:
        """
        获取当前可用的变换列表
        
        Args:
            selected (List[str]): 已选中的变换
            excluded (Optional[List[str]]): 排除的变换
            
        Returns:
            List[str]: 可用变换列表
        """
        available = []
        enabled_transforms = self.config.get_enabled_transforms()
        
        for transform_name in enabled_transforms:
            # 检查是否已被选中
            if transform_name in selected:
                continue
            
            # 检查是否被排除
            if excluded and transform_name in excluded:
                continue
            
            # 检查是否与已选中的变换冲突
            if self._has_conflicts(transform_name, selected):
                continue
            
            available.append(transform_name)
        
        return available
    
    def _has_conflicts(self, transform_name: str, selected: List[str]) -> bool:
        """
        检查变换是否与已选中的变换冲突
        
        Args:
            transform_name (str): 要检查的变换名称
            selected (List[str]): 已选中的变换列表
            
        Returns:
            bool: 是否存在冲突
        """
        conflicts = self._conflict_rules.get(transform_name, [])
        return any(conflict in selected for conflict in conflicts)
    
    def _group_by_type(self, transform_names: List[str]) -> Dict[TransformType, List[str]]:
        """
        按变换类型分组
        
        Args:
            transform_names (List[str]): 变换名称列表
            
        Returns:
            Dict[TransformType, List[str]]: 按类型分组的变换
        """
        groups = {}
        
        for transform_name in transform_names:
            transform_config = self.config.get_transform(transform_name)
            if transform_config:
                transform_type = transform_config.transform_type
                if transform_type not in groups:
                    groups[transform_type] = []
                groups[transform_type].append(transform_name)
        
        return groups
    
    def _weighted_random_choice(self, candidates: List[str]) -> Optional[str]:
        """
        按权重随机选择变换
        
        Args:
            candidates (List[str]): 候选变换列表
            
        Returns:
            Optional[str]: 选中的变换名称，如果没有合适的则返回None
        """
        if not candidates:
            return None
        
        # 计算每个候选变换的有效概率
        weights = []
        valid_candidates = []
        
        for transform_name in candidates:
            effective_prob = self.config.get_effective_probability(transform_name)
            if effective_prob > 0:
                weights.append(effective_prob)
                valid_candidates.append(transform_name)
        
        if not valid_candidates:
            return None
        
        # 按权重随机选择
        if random.random() < max(weights):  # 使用最大概率作为触发条件
            return random.choices(valid_candidates, weights=weights)[0]
        
        return None
    
    def _create_transform_instance(self, transform_name: str, 
                                  intensity_scale: float = 1.0) -> BaseTransform:
        """
        创建变换实例
        
        Args:
            transform_name (str): 变换名称
            intensity_scale (float): 强度缩放因子
            
        Returns:
            BaseTransform: 变换实例
        """
        transform_class = self._transform_registry[transform_name]
        transform_config = self.config.get_transform(transform_name)
        
        # 应用强度缩放
        probability = transform_config.probability * intensity_scale
        probability = max(0.0, min(1.0, probability))  # 确保在[0,1]范围内
        
        # 创建实例
        return transform_class(
            probability=probability,
            **transform_config.custom_params
        )
    
    def apply_single_type(self, image: Image.Image, transform_type: TransformType,
                         intensity_scale: float = 1.0) -> Tuple[Image.Image, List[str]]:
        """
        只应用指定类型的变换效果
        
        Args:
            image (Image.Image): 输入图像
            transform_type (TransformType): 变换类型
            intensity_scale (float): 强度缩放因子
            
        Returns:
            Tuple[Image.Image, List[str]]: 变换后的图像和应用的变换名称列表
        """
        # 获取该类型的所有变换
        type_transforms = self.config.get_transforms_by_type(transform_type)
        transform_names = [t.name for t in type_transforms]
        
        # 只从该类型中选择
        selected = self._select_transforms(
            max_transforms=2,  # 限制同类型变换数量
            force_transforms=None,
            exclude_transforms=[name for name in self._transform_registry.keys() 
                              if name not in transform_names]
        )
        
        # 应用选中的变换
        result_image = image
        applied_transforms = []
        
        for transform_name in self._application_order:
            if transform_name in selected:
                transform_instance = self._create_transform_instance(transform_name, intensity_scale)
                
                enhanced_image = transform_instance(result_image)
                if enhanced_image is not None:
                    result_image = enhanced_image
                    applied_transforms.append(transform_name)
        
        return result_image, applied_transforms
    
    def apply_preset(self, image: Image.Image, preset_name: str) -> Tuple[Image.Image, List[str]]:
        """
        应用预设的变换组合
        
        Args:
            image (Image.Image): 输入图像
            preset_name (str): 预设名称
            
        Returns:
            Tuple[Image.Image, List[str]]: 变换后的图像和应用的变换名称列表
        """
        presets = {
            'light_aging': {
                'force_transforms': ['fade_effect'],
                'max_transforms': 2,
                'intensity_scale': 0.5
            },
            'heavy_aging': {
                'force_transforms': ['fade_effect', 'wear_effect', 'dirt_effect'],
                'max_transforms': 3,
                'intensity_scale': 0.8
            },
            'perspective_only': {
                'force_transforms': ['tilt_transform'],
                'exclude_transforms': ['fade_effect', 'wear_effect', 'dirt_effect'],
                'max_transforms': 2,
                'intensity_scale': 0.7
            },
            'low_light': {
                'force_transforms': ['night_effect', 'shadow_effect'],
                'max_transforms': 3,
                'intensity_scale': 0.6
            },
            'harsh_conditions': {
                'force_transforms': ['wear_effect', 'dirt_effect', 'shadow_effect'],
                'max_transforms': 4,
                'intensity_scale': 0.9
            }
        }
        
        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}. Available presets: {list(presets.keys())}")
        
        preset_config = presets[preset_name]
        
        return self.apply(
            image,
            max_transforms=preset_config.get('max_transforms', 3),
            force_transforms=preset_config.get('force_transforms'),
            exclude_transforms=preset_config.get('exclude_transforms'),
            intensity_scale=preset_config.get('intensity_scale', 1.0)
        )
    
    def get_transform_statistics(self) -> Dict[str, Any]:
        """
        获取变换统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        enabled_transforms = self.config.get_enabled_transforms()
        
        type_counts = {}
        total_probability = 0
        
        for transform_name, transform_params in enabled_transforms.items():
            transform_type = transform_params.transform_type
            if transform_type not in type_counts:
                type_counts[transform_type] = 0
            type_counts[transform_type] += 1
            total_probability += transform_params.probability
        
        return {
            'total_transforms': len(enabled_transforms),
            'type_distribution': {t.value: count for t, count in type_counts.items()},
            'average_probability': total_probability / len(enabled_transforms) if enabled_transforms else 0,
            'max_concurrent': self.config.get_max_concurrent_transforms(),
            'global_probability': self.config.get_global_probability()
        }


# 便利函数
def create_composite_transform(config_dict: Optional[Dict[str, Any]] = None) -> CompositeTransform:
    """
    创建复合变换管理器的便利函数
    
    Args:
        config_dict (Optional[Dict[str, Any]]): 配置字典
        
    Returns:
        CompositeTransform: 复合变换管理器实例
    """
    if config_dict:
        from .transform_config import create_config_from_dict
        config = create_config_from_dict(config_dict)
    else:
        config = default_config
    
    return CompositeTransform(config)


def quick_enhance(image: Image.Image, 
                 intensity: str = "medium",
                 style: str = "balanced") -> Tuple[Image.Image, List[str]]:
    """
    快速增强图像的便利函数
    
    Args:
        image (Image.Image): 输入图像
        intensity (str): 强度级别 ("light", "medium", "heavy")
        style (str): 增强风格 ("balanced", "aging", "perspective", "lighting")
        
    Returns:
        Tuple[Image.Image, List[str]]: 增强后的图像和应用的变换列表
    """
    intensity_scales = {
        "light": 0.4,
        "medium": 0.7,
        "heavy": 1.0
    }
    
    style_configs = {
        "balanced": {"max_transforms": 3},
        "aging": {"force_transforms": ["fade_effect"], "max_transforms": 3},
        "perspective": {"force_transforms": ["tilt_transform"], "max_transforms": 2},
        "lighting": {"force_transforms": ["shadow_effect"], "max_transforms": 3}
    }
    
    transformer = CompositeTransform()
    
    intensity_scale = intensity_scales.get(intensity, 0.7)
    style_config = style_configs.get(style, {"max_transforms": 3})
    
    return transformer.apply(
        image,
        intensity_scale=intensity_scale,
        **style_config
    )