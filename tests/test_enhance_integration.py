"""
enhance参数集成测试

测试新的enhance参数在整个系统中的集成情况。
"""

import pytest
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch

from src.generator.integrated_generator import IntegratedPlateGenerator
from src.generator.plate_generator import PlateGenerationConfig
from src.generator.image_composer import ImageComposer
from src.core.enhance_config import EnhanceConfig
from src.transform.transform_config import TransformConfig, TransformParams, TransformType
from src.utils.constants import PlateType


class TestEnhanceIntegration:
    """测试enhance参数的集成功能"""
    
    @pytest.fixture
    def mock_generator(self):
        """创建模拟生成器"""
        with patch('src.generator.integrated_generator.IntegratedPlateGenerator._validate_resources'):
            generator = IntegratedPlateGenerator("test_plate_models", "test_font_models")
            return generator
    
    @pytest.fixture
    def mock_plate_info(self):
        """创建模拟车牌信息"""
        from src.generator.plate_generator import PlateInfo
        from src.rules.base_rule import PlateColor
        
        return PlateInfo(
            plate_number="京A12345",
            plate_type=PlateType.ORDINARY_BLUE,
            background_color=PlateColor.BLUE,
            is_double_layer=False
        )
    
    def test_generate_with_false_enhance(self, mock_generator, mock_plate_info):
        """测试使用 enhance=False 生成车牌"""
        with patch.object(mock_generator.plate_generator, 'generate_random_plate', return_value=mock_plate_info), \
             patch.object(mock_generator.image_composer, 'compose_plate_image', return_value=np.zeros((100, 300, 3), dtype=np.uint8)) as mock_compose:
            
            plate_info, plate_image = mock_generator.generate_plate_with_image(enhance=False)
            
            # 验证调用参数
            mock_compose.assert_called_once()
            args, kwargs = mock_compose.call_args
            enhance_config = args[1]  # 第二个参数是 enhance_config
            
            assert isinstance(enhance_config, EnhanceConfig)
            assert not enhance_config.enabled
    
    def test_generate_with_true_enhance(self, mock_generator, mock_plate_info):
        """测试使用 enhance=True 生成车牌"""
        with patch.object(mock_generator.plate_generator, 'generate_random_plate', return_value=mock_plate_info), \
             patch.object(mock_generator.image_composer, 'compose_plate_image', return_value=np.zeros((100, 300, 3), dtype=np.uint8)) as mock_compose:
            
            plate_info, plate_image = mock_generator.generate_plate_with_image(enhance=True)
            
            # 验证调用参数
            mock_compose.assert_called_once()
            args, kwargs = mock_compose.call_args
            enhance_config = args[1]
            
            assert isinstance(enhance_config, EnhanceConfig)
            assert enhance_config.enabled
            assert enhance_config.is_using_default_config()
    
    def test_generate_with_custom_transform_config(self, mock_generator, mock_plate_info):
        """测试使用自定义 TransformConfig 生成车牌"""
        # 创建自定义配置
        custom_config = TransformConfig()
        custom_config._transforms.clear()
        custom_config.add_transform(TransformParams(
            name="test_aging",
            transform_type=TransformType.AGING,
            probability=1.0,
            intensity_range=(0.5, 0.8)
        ))
        
        with patch.object(mock_generator.plate_generator, 'generate_random_plate', return_value=mock_plate_info), \
             patch.object(mock_generator.image_composer, 'compose_plate_image', return_value=np.zeros((100, 300, 3), dtype=np.uint8)) as mock_compose:
            
            plate_info, plate_image = mock_generator.generate_plate_with_image(enhance=custom_config)
            
            # 验证调用参数
            mock_compose.assert_called_once()
            args, kwargs = mock_compose.call_args
            enhance_config = args[1]
            
            assert isinstance(enhance_config, EnhanceConfig)
            assert enhance_config.enabled
            assert not enhance_config.is_using_default_config()
            assert enhance_config.transform_config is custom_config
    
    def test_generate_specific_plate_with_enhance(self, mock_generator, mock_plate_info):
        """测试生成指定车牌号码时的enhance参数"""
        with patch.object(mock_generator.plate_generator, 'generate_specific_plate', return_value=mock_plate_info), \
             patch.object(mock_generator.image_composer, 'compose_plate_image', return_value=np.zeros((100, 300, 3), dtype=np.uint8)) as mock_compose:
            
            plate_info, plate_image = mock_generator.generate_specific_plate_with_image("京A12345", enhance=True)
            
            # 验证调用参数
            mock_compose.assert_called_once()
            args, kwargs = mock_compose.call_args
            enhance_config = args[1]
            
            assert isinstance(enhance_config, EnhanceConfig)
            assert enhance_config.enabled
    
    def test_batch_generate_with_enhance(self, mock_generator, mock_plate_info):
        """测试批量生成时的enhance参数"""
        with patch.object(mock_generator.plate_generator, 'generate_random_plate', return_value=mock_plate_info), \
             patch.object(mock_generator.image_composer, 'compose_plate_image', return_value=np.zeros((100, 300, 3), dtype=np.uint8)) as mock_compose:
            
            results = mock_generator.generate_batch_plates_with_images(count=3, enhance=True)
            
            assert len(results) == 3
            # 验证每次调用都正确传递了enhance配置
            assert mock_compose.call_count == 3
            
            for call in mock_compose.call_args_list:
                args, kwargs = call
                enhance_config = args[1]
                assert isinstance(enhance_config, EnhanceConfig)
                assert enhance_config.enabled


class TestImageComposerEnhance:
    """测试ImageComposer中的enhance参数处理"""
    
    @pytest.fixture
    def mock_composer(self):
        """创建模拟图像合成器"""
        with patch('src.generator.image_composer.ImageComposer._validate_resources'):
            composer = ImageComposer("test_plates", "test_fonts")
            return composer
    
    @pytest.fixture  
    def mock_plate_info(self):
        """创建模拟车牌信息"""
        from src.generator.plate_generator import PlateInfo
        from src.rules.base_rule import PlateColor
        
        return PlateInfo(
            plate_number="京A12345",
            plate_type=PlateType.ORDINARY_BLUE,
            background_color=PlateColor.BLUE,
            is_double_layer=False
        )
    
    def test_compose_with_bool_enhance(self, mock_composer, mock_plate_info):
        """测试使用bool类型的enhance参数合成图像"""
        mock_image = np.zeros((100, 300, 3), dtype=np.uint8)
        
        with patch.object(mock_composer, '_calculate_layout'), \
             patch.object(mock_composer, '_load_background_image', return_value=mock_image), \
             patch.object(mock_composer, '_load_character_image', return_value=mock_image), \
             patch.object(mock_composer, '_compose_character', return_value=mock_image), \
             patch.object(mock_composer, '_apply_final_processing', return_value=mock_image), \
             patch.object(mock_composer, '_apply_character_enhancement', return_value=mock_image) as mock_char_enhance, \
             patch.object(mock_composer, '_apply_transform_effects', return_value=mock_image) as mock_transform:
            
            # 测试 enhance=False
            result = mock_composer.compose_plate_image(mock_plate_info, enhance=False)
            assert isinstance(result, np.ndarray)
            mock_char_enhance.assert_not_called()
            mock_transform.assert_not_called()
            
            # 重置mock
            mock_char_enhance.reset_mock()
            mock_transform.reset_mock()
            
            # 测试 enhance=True
            result = mock_composer.compose_plate_image(mock_plate_info, enhance=True)
            assert isinstance(result, np.ndarray)
            mock_char_enhance.assert_called()
            mock_transform.assert_called()
    
    def test_compose_with_enhance_config(self, mock_composer, mock_plate_info):
        """测试使用EnhanceConfig类型的enhance参数合成图像"""
        mock_image = np.zeros((100, 300, 3), dtype=np.uint8)
        
        # 创建自定义增强配置
        custom_config = TransformConfig()
        enhance_config = EnhanceConfig(custom_config)
        
        with patch.object(mock_composer, '_calculate_layout'), \
             patch.object(mock_composer, '_load_background_image', return_value=mock_image), \
             patch.object(mock_composer, '_load_character_image', return_value=mock_image), \
             patch.object(mock_composer, '_compose_character', return_value=mock_image), \
             patch.object(mock_composer, '_apply_final_processing', return_value=mock_image), \
             patch.object(mock_composer, '_apply_character_enhancement', return_value=mock_image) as mock_char_enhance, \
             patch.object(mock_composer, '_apply_transform_effects', return_value=mock_image) as mock_transform:
            
            result = mock_composer.compose_plate_image(mock_plate_info, enhance=enhance_config)
            assert isinstance(result, np.ndarray)
            
            # 验证正确调用了增强方法
            mock_char_enhance.assert_called()
            mock_transform.assert_called()
            
            # 验证transform_effects被调用时传递了正确的配置
            args, kwargs = mock_transform.call_args
            passed_config = args[1] if len(args) > 1 else None
            assert passed_config is custom_config
    
    def test_apply_transform_effects_with_custom_config(self, mock_composer):
        """测试_apply_transform_effects方法使用自定义配置"""
        mock_image = np.zeros((100, 300, 3), dtype=np.uint8)
        custom_config = TransformConfig()
        
        with patch('src.generator.image_composer.CompositeTransform') as mock_composite_class, \
             patch('src.generator.image_composer.Image') as mock_image_class, \
             patch('src.generator.image_composer.cv2'):
            
            mock_transform_manager = Mock()
            mock_transform_manager.apply.return_value = (Mock(), [])
            mock_composite_class.return_value = mock_transform_manager
            
            # 调用方法
            result = mock_composer._apply_transform_effects(mock_image, custom_config)
            
            # 验证使用自定义配置创建了临时变换管理器
            mock_composite_class.assert_called_with(custom_config)
            mock_transform_manager.apply.assert_called_once()


class TestEnhanceConfigCompatibility:
    """测试enhance参数的向后兼容性"""
    
    def test_backward_compatibility(self):
        """测试与旧代码的向后兼容性"""
        # 确保原有的 enhance=True/False 用法仍然有效
        config_true = EnhanceConfig(True)
        config_false = EnhanceConfig(False)
        
        assert config_true.enabled
        assert not config_false.enabled
        
        # 确保可以正确转换为bool
        assert bool(config_true)
        assert not bool(config_false)
    
    def test_type_checking(self):
        """测试类型检查"""
        # 正确的类型
        EnhanceConfig(True)
        EnhanceConfig(False)
        EnhanceConfig(None)
        EnhanceConfig(TransformConfig())
        
        # 错误的类型
        with pytest.raises(TypeError):
            EnhanceConfig("invalid")
        
        with pytest.raises(TypeError):
            EnhanceConfig(123)
        
        with pytest.raises(TypeError):
            EnhanceConfig([])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])