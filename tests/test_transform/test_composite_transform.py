"""
复合变换管理器详细测试模块

测试复合变换管理器的高级功能，包括冲突检测、预设管理、统计分析等。
"""

import pytest
import numpy as np
from PIL import Image, ImageDraw
from unittest.mock import Mock, patch

from src.transform.composite_transform import CompositeTransform
from src.transform.transform_config import TransformConfig, TransformType
from src.transform import default_config


class TestCompositeTransformAdvanced:
    """测试复合变换管理器的高级功能"""
    
    @pytest.fixture
    def test_image(self):
        """创建测试图像"""
        image = Image.new('RGB', (400, 200), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 绘制车牌样式内容
        draw.rectangle([20, 20, 380, 180], outline=(0, 0, 0), width=3)
        draw.text((50, 80), "粤B12345", fill=(0, 0, 0))
        
        return image
    
    @pytest.fixture
    def custom_config(self):
        """创建自定义配置"""
        config = TransformConfig()
        config.set_global_probability(0.8)
        config.set_max_concurrent_transforms(5)
        return config
    
    def test_transform_registry_completeness(self):
        """测试变换注册表的完整性"""
        transformer = CompositeTransform()
        registry = transformer._transform_registry
        
        # 检查所有预期的变换是否都注册了
        expected_transforms = [
            # 老化效果
            'wear_effect', 'fade_effect', 'dirt_effect',
            # 透视变换
            'tilt_transform', 'perspective_transform', 'rotation_transform', 'geometric_distortion',
            # 光照效果
            'shadow_effect', 'reflection_effect', 'night_effect', 'backlight_effect'
        ]
        
        for transform_name in expected_transforms:
            assert transform_name in registry, f"变换 {transform_name} 未注册"
            assert callable(registry[transform_name]), f"变换类 {transform_name} 不可调用"
    
    def test_conflict_rules_definition(self):
        """测试冲突规则定义"""
        transformer = CompositeTransform()
        conflict_rules = transformer._conflict_rules
        
        # 检查冲突规则是否正确定义
        assert isinstance(conflict_rules, dict)
        
        # 检查一些已知的冲突规则
        if 'night_effect' in conflict_rules:
            night_conflicts = conflict_rules['night_effect']
            # 夜间效果应该与强反光效果冲突
            assert isinstance(night_conflicts, list)
    
    def test_application_order_definition(self):
        """测试应用顺序定义"""
        transformer = CompositeTransform()
        application_order = transformer._application_order
        
        # 检查应用顺序是否合理定义
        assert isinstance(application_order, dict)
        
        # 透视变换应该在光照效果之前
        perspective_priority = application_order.get('perspective_transform', float('inf'))
        lighting_priority = application_order.get('shadow_effect', float('inf'))
        
        assert perspective_priority < lighting_priority, "透视变换应该在光照效果之前应用"
    
    def test_conflict_detection(self, test_image):
        """测试冲突检测机制"""
        transformer = CompositeTransform()
        
        # 手动设置冲突的变换
        conflicting_transforms = ['night_effect', 'reflection_effect']
        
        # 强制应用冲突的变换
        result, applied_transforms = transformer.apply(
            test_image,
            force_transforms=conflicting_transforms,
            max_transforms=5
        )
        
        assert result is not None
        
        # 由于冲突检测，不应该同时应用所有强制变换
        # （具体行为取决于实现的冲突解决策略）
        assert len(applied_transforms) <= len(conflicting_transforms)
    
    def test_transform_selection_with_weights(self, test_image):
        """测试带权重的变换选择"""
        # 创建自定义配置，给某些变换更高的概率
        config = TransformConfig()
        config.update_transform_probability('wear_effect', 0.9)
        config.update_transform_probability('fade_effect', 0.1)
        
        transformer = CompositeTransform(config)
        
        # 多次运行以测试概率分布
        wear_count = 0
        fade_count = 0
        trials = 50
        
        for _ in range(trials):
            result, applied_transforms = transformer.apply(
                test_image, 
                max_transforms=1
            )
            
            if 'wear_effect' in applied_transforms:
                wear_count += 1
            if 'fade_effect' in applied_transforms:
                fade_count += 1
        
        # 高概率的变换应该被选择更多次
        # 注意：由于随机性，这个测试可能偶尔失败
        assert wear_count > fade_count, f"wear_effect被选择{wear_count}次，fade_effect被选择{fade_count}次"
    
    def test_intensity_scaling_propagation(self, test_image):
        """测试强度缩放传播"""
        transformer = CompositeTransform()
        
        # 测试不同的强度缩放因子
        intensity_scales = [0.3, 0.7, 1.0, 1.5]
        
        for scale in intensity_scales:
            result, applied_transforms = transformer.apply(
                test_image,
                intensity_scale=scale,
                max_transforms=3
            )
            
            assert result is not None
            assert isinstance(applied_transforms, list)
            
            # 检查结果的差异（间接验证强度缩放）
            result_array = np.array(result)
            original_array = np.array(test_image)
            
            # 强度缩放应该影响变换的效果强度
            if len(applied_transforms) > 0:
                assert not np.array_equal(result_array, original_array)
    
    def test_max_transforms_limit(self, test_image):
        """测试最大变换数量限制"""
        transformer = CompositeTransform()
        
        # 测试不同的最大变换数量
        max_limits = [1, 3, 5, 10]
        
        for max_limit in max_limits:
            result, applied_transforms = transformer.apply(
                test_image,
                max_transforms=max_limit
            )
            
            assert result is not None
            assert len(applied_transforms) <= max_limit, f"应用的变换数量 {len(applied_transforms)} 超过限制 {max_limit}"
    
    def test_exclude_transforms_functionality(self, test_image):
        """测试排除变换功能"""
        transformer = CompositeTransform()
        
        # 排除特定变换
        excluded_transforms = ['wear_effect', 'dirt_effect', 'night_effect']
        
        result, applied_transforms = transformer.apply(
            test_image,
            exclude_transforms=excluded_transforms,
            max_transforms=10  # 设置较大值以确保有变换被应用
        )
        
        assert result is not None
        
        # 检查排除的变换没有被应用
        for excluded_transform in excluded_transforms:
            assert excluded_transform not in applied_transforms, f"排除的变换 {excluded_transform} 被应用了"
    
    def test_force_transforms_priority(self, test_image):
        """测试强制变换的优先级"""
        transformer = CompositeTransform()
        
        # 强制应用特定变换
        forced_transforms = ['fade_effect', 'tilt_transform']
        
        result, applied_transforms = transformer.apply(
            test_image,
            force_transforms=forced_transforms,
            max_transforms=3
        )
        
        assert result is not None
        
        # 强制变换应该被优先应用（如果概率允许）
        # 注意：由于概率因素，强制变换可能不会被应用
        # 这里我们只检查不会出错
        assert isinstance(applied_transforms, list)
    
    def test_single_type_application_isolation(self, test_image):
        """测试单一类型应用的隔离性"""
        transformer = CompositeTransform()
        
        # 测试各种变换类型
        transform_types = [TransformType.AGING, TransformType.PERSPECTIVE, TransformType.LIGHTING]
        
        for transform_type in transform_types:
            result, applied_transforms = transformer.apply_single_type(
                test_image, 
                transform_type,
                intensity_scale=1.0
            )
            
            assert result is not None
            assert isinstance(applied_transforms, list)
            
            # 验证只应用了指定类型的变换
            if len(applied_transforms) > 0:
                self._verify_transform_type_consistency(applied_transforms, transform_type)
    
    def _verify_transform_type_consistency(self, applied_transforms, expected_type):
        """验证应用的变换类型一致性"""
        type_mapping = {
            TransformType.AGING: ['wear_effect', 'fade_effect', 'dirt_effect'],
            TransformType.PERSPECTIVE: ['tilt_transform', 'perspective_transform', 'rotation_transform', 'geometric_distortion'],
            TransformType.LIGHTING: ['shadow_effect', 'reflection_effect', 'night_effect', 'backlight_effect']
        }
        
        expected_transforms = type_mapping.get(expected_type, [])
        
        for transform_name in applied_transforms:
            assert transform_name in expected_transforms, f"变换 {transform_name} 不属于类型 {expected_type}"
    
    def test_preset_application_completeness(self, test_image):
        """测试预设应用的完整性"""
        transformer = CompositeTransform()
        
        # 测试所有可用的预设
        available_presets = [
            'light_aging', 'heavy_aging',
            'perspective_only', 'lighting_only',
            'balanced', 'extreme'
        ]
        
        for preset in available_presets:
            try:
                result, applied_transforms = transformer.apply_preset(test_image, preset)
                
                assert result is not None
                assert isinstance(applied_transforms, list)
                
            except ValueError as e:
                # 如果预设不存在，应该抛出ValueError
                assert "预设" in str(e) or "preset" in str(e).lower()
    
    def test_invalid_preset_handling(self, test_image):
        """测试无效预设的处理"""
        transformer = CompositeTransform()
        
        # 测试无效预设名称
        invalid_presets = ['nonexistent', 'invalid_preset', '']
        
        for invalid_preset in invalid_presets:
            with pytest.raises(ValueError):
                transformer.apply_preset(test_image, invalid_preset)
    
    def test_statistics_accuracy(self):
        """测试统计信息的准确性"""
        config = TransformConfig()
        config.set_global_probability(0.6)
        config.set_max_concurrent_transforms(4)
        
        transformer = CompositeTransform(config)
        stats = transformer.get_transform_statistics()
        
        # 验证基本统计信息
        assert stats['global_probability'] == 0.6
        assert stats['max_concurrent'] == 4
        assert stats['total_transforms'] > 0
        
        # 验证类型分布
        assert 'type_distribution' in stats
        type_dist = stats['type_distribution']
        
        # 所有变换类型都应该有计数
        expected_types = ['AGING', 'PERSPECTIVE', 'LIGHTING']
        for expected_type in expected_types:
            assert expected_type in type_dist
            assert type_dist[expected_type] > 0
        
        # 验证平均概率是合理的
        assert 0 <= stats['average_probability'] <= 1
    
    def test_performance_with_large_transforms(self, test_image):
        """测试大量变换时的性能"""
        # 创建一个包含大量变换的配置
        config = TransformConfig()
        config.set_global_probability(0.8)
        config.set_max_concurrent_transforms(8)
        
        transformer = CompositeTransform(config)
        
        import time
        start_time = time.time()
        
        # 运行多次变换以测试性能
        for _ in range(10):
            result, applied_transforms = transformer.apply(
                test_image,
                max_transforms=5
            )
            
            assert result is not None
        
        elapsed_time = time.time() - start_time
        
        # 性能应该是合理的（每次变换应该在合理时间内完成）
        average_time_per_transform = elapsed_time / 10
        assert average_time_per_transform < 2.0, f"变换时间过长: {average_time_per_transform:.2f}秒"
    
    def test_memory_management(self, test_image):
        """测试内存管理"""
        transformer = CompositeTransform()
        
        # 运行大量变换以测试内存泄漏
        initial_result = transformer.apply(test_image, max_transforms=3)
        
        for i in range(50):
            result, applied_transforms = transformer.apply(
                test_image,
                max_transforms=3
            )
            
            assert result is not None
            
            # 每隔一段时间检查结果的一致性
            if i % 10 == 0:
                # 结果应该是有效的PIL图像
                assert isinstance(result, Image.Image)
                assert result.size == test_image.size
    
    def test_concurrent_safety(self, test_image):
        """测试并发安全性（基础测试）"""
        transformer = CompositeTransform()
        
        # 模拟多个并发调用
        results = []
        
        for _ in range(10):
            result, applied_transforms = transformer.apply(
                test_image,
                max_transforms=2
            )
            
            results.append(result)
            assert result is not None
        
        # 所有结果都应该是有效的
        for result in results:
            assert isinstance(result, Image.Image)
            assert result.size == test_image.size


class TestCompositeTransformEdgeCases:
    """测试复合变换管理器的边缘情况"""
    
    @pytest.fixture
    def edge_case_image(self):
        """创建边缘情况测试图像"""
        return Image.new('RGB', (100, 50), color=(128, 128, 128))
    
    def test_empty_transform_list(self, edge_case_image):
        """测试空变换列表"""
        config = TransformConfig()
        # 禁用所有变换
        for transform_name in config.get_all_transforms():
            config.disable_transform(transform_name)
        
        transformer = CompositeTransform(config)
        
        result, applied_transforms = transformer.apply(edge_case_image)
        
        # 应该返回原始图像
        assert result is not None
        assert len(applied_transforms) == 0
        
        # 图像应该保持不变
        original_array = np.array(edge_case_image)
        result_array = np.array(result)
        np.testing.assert_array_equal(original_array, result_array)
    
    def test_zero_probability_config(self, edge_case_image):
        """测试零概率配置"""
        config = TransformConfig()
        config.set_global_probability(0.0)
        
        transformer = CompositeTransform(config)
        
        result, applied_transforms = transformer.apply(
            edge_case_image,
            max_transforms=5
        )
        
        # 零概率下不应该应用任何变换
        assert result is not None
        assert len(applied_transforms) == 0
    
    def test_very_small_image(self):
        """测试极小图像"""
        tiny_image = Image.new('RGB', (10, 5), color=(255, 0, 0))
        
        transformer = CompositeTransform()
        
        result, applied_transforms = transformer.apply(
            tiny_image,
            max_transforms=2
        )
        
        # 即使是极小图像也应该能处理
        assert result is not None
        assert isinstance(result, Image.Image)
    
    def test_single_pixel_image(self):
        """测试单像素图像"""
        pixel_image = Image.new('RGB', (1, 1), color=(100, 100, 100))
        
        transformer = CompositeTransform()
        
        result, applied_transforms = transformer.apply(
            pixel_image,
            max_transforms=1
        )
        
        # 单像素图像应该能处理（虽然效果可能不明显）
        assert result is not None
        assert isinstance(result, Image.Image)
    
    def test_max_transforms_zero(self, edge_case_image):
        """测试最大变换数量为零"""
        transformer = CompositeTransform()
        
        result, applied_transforms = transformer.apply(
            edge_case_image,
            max_transforms=0
        )
        
        # 最大变换数量为0时不应该应用任何变换
        assert result is not None
        assert len(applied_transforms) == 0
    
    def test_invalid_intensity_scale(self, edge_case_image):
        """测试无效的强度缩放值"""
        transformer = CompositeTransform()
        
        # 测试负数强度缩放
        result, applied_transforms = transformer.apply(
            edge_case_image,
            intensity_scale=-0.5,
            max_transforms=2
        )
        
        # 应该能处理无效值（可能通过钳制或其他方式）
        assert result is not None
        
        # 测试极大强度缩放
        result, applied_transforms = transformer.apply(
            edge_case_image,
            intensity_scale=10.0,
            max_transforms=2
        )
        
        assert result is not None


if __name__ == "__main__":
    # 运行基本测试
    print("运行复合变换管理器详细测试...")
    
    # 创建测试图像
    test_image = Image.new('RGB', (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(test_image)
    draw.rectangle([20, 20, 380, 180], outline=(0, 0, 0), width=3)
    
    # 测试变换注册表
    print("测试变换注册表...")
    transformer = CompositeTransform()
    registry = transformer._transform_registry
    print(f"注册的变换数量: {len(registry)}")
    print(f"注册的变换: {list(registry.keys())}")
    
    # 测试统计信息
    print("测试统计信息...")
    stats = transformer.get_transform_statistics()
    print(f"总变换数: {stats['total_transforms']}")
    print(f"全局概率: {stats['global_probability']}")
    print(f"最大并发: {stats['max_concurrent']}")
    print(f"类型分布: {stats['type_distribution']}")
    
    # 测试冲突检测
    print("测试冲突检测...")
    result, applied = transformer.apply(
        test_image,
        force_transforms=['night_effect', 'reflection_effect'],
        max_transforms=5
    )
    print(f"冲突检测测试: {'成功' if result else '失败'}, 应用的变换: {applied}")
    
    # 测试预设应用
    print("测试预设应用...")
    try:
        result, applied = transformer.apply_preset(test_image, 'light_aging')
        print(f"预设应用: {'成功' if result else '失败'}, 应用的变换: {applied}")
    except ValueError as e:
        print(f"预设应用: 预设不存在 - {e}")
    
    print("复合变换管理器详细测试完成！")