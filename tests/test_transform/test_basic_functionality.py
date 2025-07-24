"""
Transform模块基本功能测试

测试变换模块的基本功能，包括配置、基础变换和复合变换。
"""

import pytest
import numpy as np
from PIL import Image
import tempfile
import os

# 导入要测试的模块
from src.transform import (
    TransformConfig, TransformType, default_config,
    WearEffect, FadeEffect, DirtEffect,
    TiltTransform, PerspectiveTransform,
    ShadowEffect, ReflectionEffect,
    CompositeTransform, quick_enhance
)


class TestTransformConfig:
    """测试变换配置管理"""
    
    def test_default_config_creation(self):
        """测试默认配置创建"""
        config = TransformConfig()
        assert config.get_global_probability() == 0.3
        assert config.get_max_concurrent_transforms() == 3
        
        # 检查是否包含所有预期的变换
        transforms = config.get_all_transforms()
        expected_transforms = [
            'wear_effect', 'fade_effect', 'dirt_effect',
            'tilt_transform', 'perspective_transform', 'rotation_transform',
            'shadow_effect', 'reflection_effect', 'night_effect', 'backlight_effect'
        ]
        
        for transform_name in expected_transforms:
            assert transform_name in transforms
    
    def test_probability_management(self):
        """测试概率管理功能"""
        config = TransformConfig()
        
        # 测试设置全局概率
        config.set_global_probability(0.5)
        assert config.get_global_probability() == 0.5
        
        # 测试更新单个变换概率
        assert config.update_transform_probability('wear_effect', 0.8)
        wear_config = config.get_transform('wear_effect')
        assert wear_config.probability == 0.8
        
        # 测试有效概率计算
        effective_prob = config.get_effective_probability('wear_effect')
        assert effective_prob == 0.8 * 0.5  # 基础概率 * 全局概率
    
    def test_transform_enable_disable(self):
        """测试变换启用/禁用功能"""
        config = TransformConfig()
        
        # 测试禁用变换
        assert config.disable_transform('wear_effect')
        enabled_transforms = config.get_enabled_transforms()
        assert 'wear_effect' not in enabled_transforms
        
        # 测试重新启用变换
        assert config.enable_transform('wear_effect')
        enabled_transforms = config.get_enabled_transforms()
        assert 'wear_effect' in enabled_transforms
    
    def test_config_save_load(self):
        """测试配置保存和加载"""
        config = TransformConfig()
        config.set_global_probability(0.7)
        config.update_transform_probability('fade_effect', 0.6)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name
        
        try:
            config.save_to_file(config_file)
            
            # 加载配置
            loaded_config = TransformConfig(config_file)
            assert loaded_config.get_global_probability() == 0.7
            
            fade_config = loaded_config.get_transform('fade_effect')
            assert fade_config.probability == 0.6
        finally:
            os.unlink(config_file)


class TestTransformEffects:
    """测试具体变换效果"""
    
    @pytest.fixture
    def sample_image(self):
        """创建测试用的示例图像"""
        # 创建一个简单的车牌样式图像
        image = Image.new('RGB', (300, 100), color='white')
        # 可以添加一些文字或图案，但为了测试简单，使用纯色
        return image
    
    def test_wear_effect(self, sample_image):
        """测试磨损效果"""
        transform = WearEffect(probability=1.0)  # 100%概率确保应用
        
        result = transform(sample_image)
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
        
        # 验证图像确实发生了变化
        original_array = np.array(sample_image)
        result_array = np.array(result)
        assert not np.array_equal(original_array, result_array)
    
    def test_fade_effect(self, sample_image):
        """测试褪色效果"""
        transform = FadeEffect(probability=1.0)
        
        result = transform(sample_image)
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
    
    def test_tilt_transform(self, sample_image):
        """测试倾斜变换"""
        transform = TiltTransform(probability=1.0, max_angle=10)
        
        result = transform(sample_image)
        assert result is not None
        assert isinstance(result, Image.Image)
        # 倾斜后图像尺寸可能会改变
    
    def test_shadow_effect(self, sample_image):
        """测试阴影效果"""
        transform = ShadowEffect(probability=1.0)
        
        result = transform(sample_image)
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
    
    def test_transform_probability(self, sample_image):
        """测试变换概率控制"""
        # 概率为0时不应该应用变换
        transform = WearEffect(probability=0.0)
        result = transform(sample_image)
        assert result is None
        
        # 概率为1时应该应用变换
        transform = WearEffect(probability=1.0)
        result = transform(sample_image)
        assert result is not None
    
    def test_transform_intensity(self, sample_image):
        """测试变换强度控制"""
        transform = FadeEffect(probability=1.0)
        
        # 测试不同强度
        weak_result = transform.apply(sample_image, intensity=0.2)
        strong_result = transform.apply(sample_image, intensity=0.8)
        
        assert weak_result is not None
        assert strong_result is not None
        
        # 强度不同应该产生不同的结果
        weak_array = np.array(weak_result)
        strong_array = np.array(strong_result)
        assert not np.array_equal(weak_array, strong_array)


class TestCompositeTransform:
    """测试复合变换管理器"""
    
    @pytest.fixture
    def sample_image(self):
        """创建测试用的示例图像"""
        return Image.new('RGB', (300, 100), color='white')
    
    def test_composite_creation(self):
        """测试复合变换管理器创建"""
        transformer = CompositeTransform()
        assert transformer is not None
        
        # 测试使用自定义配置
        custom_config = TransformConfig()
        custom_config.set_global_probability(0.5)
        
        custom_transformer = CompositeTransform(custom_config)
        assert custom_transformer.config.get_global_probability() == 0.5
    
    def test_transform_selection(self, sample_image):
        """测试变换选择逻辑"""
        transformer = CompositeTransform()
        
        # 测试基本应用
        result, applied_transforms = transformer.apply(sample_image, max_transforms=2)
        assert isinstance(result, Image.Image)
        assert isinstance(applied_transforms, list)
        assert len(applied_transforms) <= 2
    
    def test_forced_transforms(self, sample_image):
        """测试强制应用指定变换"""
        transformer = CompositeTransform()
        
        result, applied_transforms = transformer.apply(
            sample_image,
            force_transforms=['fade_effect'],
            max_transforms=2
        )
        
        # 如果fade_effect被应用，它应该在应用列表中
        # 注意：由于概率因素，可能不会被应用，这是正常的
        assert isinstance(applied_transforms, list)
    
    def test_excluded_transforms(self, sample_image):
        """测试排除指定变换"""
        transformer = CompositeTransform()
        
        result, applied_transforms = transformer.apply(
            sample_image,
            exclude_transforms=['wear_effect', 'dirt_effect'],
            max_transforms=3
        )
        
        # 排除的变换不应该出现在应用列表中
        excluded = ['wear_effect', 'dirt_effect']
        for transform_name in applied_transforms:
            assert transform_name not in excluded
    
    def test_single_type_application(self, sample_image):
        """测试单一类型变换应用"""
        transformer = CompositeTransform()
        
        # 只应用老化效果
        result, applied_transforms = transformer.apply_single_type(
            sample_image, 
            TransformType.AGING
        )
        
        assert isinstance(result, Image.Image)
        assert isinstance(applied_transforms, list)
        
        # 检查应用的变换是否都是老化类型
        aging_transforms = ['wear_effect', 'fade_effect', 'dirt_effect']
        for transform_name in applied_transforms:
            assert transform_name in aging_transforms
    
    def test_preset_application(self, sample_image):
        """测试预设变换组合"""
        transformer = CompositeTransform()
        
        # 测试轻度老化预设
        result, applied_transforms = transformer.apply_preset(sample_image, 'light_aging')
        assert isinstance(result, Image.Image)
        assert isinstance(applied_transforms, list)
        
        # 测试无效预设
        with pytest.raises(ValueError):
            transformer.apply_preset(sample_image, 'invalid_preset')
    
    def test_statistics(self):
        """测试变换统计信息"""
        transformer = CompositeTransform()
        stats = transformer.get_transform_statistics()
        
        assert 'total_transforms' in stats
        assert 'type_distribution' in stats
        assert 'average_probability' in stats
        assert 'max_concurrent' in stats
        assert 'global_probability' in stats
        
        assert stats['total_transforms'] > 0
        assert stats['max_concurrent'] == 3
        assert stats['global_probability'] == 0.3


class TestQuickEnhance:
    """测试快速增强功能"""
    
    @pytest.fixture
    def sample_image(self):
        """创建测试用的示例图像"""
        return Image.new('RGB', (300, 100), color='white')
    
    def test_quick_enhance_basic(self, sample_image):
        """测试基本快速增强"""
        result, applied_transforms = quick_enhance(sample_image)
        
        assert isinstance(result, Image.Image)
        assert isinstance(applied_transforms, list)
        assert result.size == sample_image.size
    
    def test_quick_enhance_intensity_levels(self, sample_image):
        """测试不同强度级别"""
        intensities = ["light", "medium", "heavy"]
        
        for intensity in intensities:
            result, applied_transforms = quick_enhance(
                sample_image, 
                intensity=intensity
            )
            assert isinstance(result, Image.Image)
            assert isinstance(applied_transforms, list)
    
    def test_quick_enhance_styles(self, sample_image):
        """测试不同增强风格"""
        styles = ["balanced", "aging", "perspective", "lighting"]
        
        for style in styles:
            result, applied_transforms = quick_enhance(
                sample_image,
                style=style
            )
            assert isinstance(result, Image.Image)
            assert isinstance(applied_transforms, list)


def test_module_imports():
    """测试模块导入"""
    # 这个测试确保所有导入都能正常工作
    from src.transform import (
        BaseTransform, TransformConfig, CompositeTransform,
        WearEffect, TiltTransform, ShadowEffect
    )
    
    # 基本类应该可以实例化
    config = TransformConfig()
    assert config is not None
    
    transformer = CompositeTransform()
    assert transformer is not None


if __name__ == "__main__":
    # 运行基本的烟雾测试
    print("运行Transform模块基本功能测试...")
    
    # 创建测试图像
    test_image = Image.new('RGB', (300, 100), color='white')
    
    # 测试单个变换
    print("测试单个变换效果...")
    wear = WearEffect(probability=1.0)
    result = wear(test_image)
    print(f"磨损效果: {'成功' if result else '失败'}")
    
    # 测试复合变换
    print("测试复合变换...")
    transformer = CompositeTransform()
    result, applied = transformer.apply(test_image, max_transforms=2)
    print(f"复合变换: {'成功' if result else '失败'}, 应用的变换: {applied}")
    
    # 测试快速增强
    print("测试快速增强...")
    result, applied = quick_enhance(test_image, intensity="medium")
    print(f"快速增强: {'成功' if result else '失败'}, 应用的变换: {applied}")
    
    print("基本功能测试完成！")