"""
EnhanceConfig 单元测试
"""

import pytest
import tempfile
import os

from src.core.enhance_config import EnhanceConfig, create_enhance_config, create_custom_enhance_config
from src.transform.transform_config import TransformConfig, TransformParams, TransformType


class TestEnhanceConfig:
    """测试 EnhanceConfig 类"""
    
    def test_init_with_false(self):
        """测试用 False 初始化"""
        config = EnhanceConfig(False)
        assert not config.enabled
        assert config.transform_config is None
    
    def test_init_with_none(self):
        """测试用 None 初始化"""
        config = EnhanceConfig(None)
        assert not config.enabled
        assert config.transform_config is None
    
    def test_init_with_true(self):
        """测试用 True 初始化"""
        config = EnhanceConfig(True)
        assert config.enabled
        assert config.transform_config is not None
        assert isinstance(config.transform_config, TransformConfig)
        assert config.is_using_default_config()
    
    def test_init_with_transform_config(self):
        """测试用 TransformConfig 初始化"""
        transform_config = TransformConfig()
        config = EnhanceConfig(transform_config)
        assert config.enabled
        assert config.transform_config is transform_config
        assert config.is_using_default_config()  # 因为是默认配置
    
    def test_init_with_custom_transform_config(self):
        """测试用自定义 TransformConfig 初始化"""
        transform_config = TransformConfig()
        transform_config._transforms.clear()  # 清空变换
        transform_config.add_transform(TransformParams(
            name="test_transform",
            transform_type=TransformType.AGING,
            probability=0.5
        ))
        
        config = EnhanceConfig(transform_config)
        assert config.enabled
        assert config.transform_config is transform_config
        assert not config.is_using_default_config()  # 因为是自定义配置
    
    def test_init_with_enhance_config(self):
        """测试用另一个EnhanceConfig对象初始化"""
        # 创建原始配置
        original = EnhanceConfig(True)
        
        # 用原始配置创建新配置
        copied = EnhanceConfig(original)
        
        assert copied.enabled == original.enabled
        assert copied.transform_config is not None
        assert copied.is_using_default_config()
    
    def test_init_with_invalid_type(self):
        """测试用无效类型初始化"""
        with pytest.raises(TypeError, match="enhance参数必须是bool、TransformConfig或EnhanceConfig类型"):
            EnhanceConfig("invalid")
    
    def test_bool_conversion(self):
        """测试 bool() 转换"""
        assert not bool(EnhanceConfig(False))
        assert bool(EnhanceConfig(True))
        
        transform_config = TransformConfig()
        assert bool(EnhanceConfig(transform_config))
    
    def test_update_config(self):
        """测试更新配置"""
        config = EnhanceConfig(False)
        assert not config.enabled
        
        # 更新为 True
        config.update_config(True)
        assert config.enabled
        assert config.is_using_default_config()
        
        # 更新为自定义配置
        custom_config = TransformConfig()
        custom_config._transforms.clear()
        config.update_config(custom_config)
        assert config.enabled
        assert not config.is_using_default_config()
        
        # 更新为 False
        config.update_config(False)
        assert not config.enabled
    
    def test_repr(self):
        """测试字符串表示"""
        # 禁用状态
        config = EnhanceConfig(False)
        assert "disabled" in repr(config)
        
        # 默认配置
        config = EnhanceConfig(True)
        assert "enabled=True" in repr(config)
        assert "using_default_config=True" in repr(config)
        
        # 自定义配置
        transform_config = TransformConfig()
        transform_config._transforms.clear()
        transform_config.add_transform(TransformParams(
            name="test", 
            transform_type=TransformType.AGING,
            probability=0.5
        ))
        config = EnhanceConfig(transform_config)
        assert "enabled=True" in repr(config)
        assert "custom_transforms=1" in repr(config)


class TestEnhanceConfigHelpers:
    """测试 EnhanceConfig 辅助函数"""
    
    def test_create_enhance_config(self):
        """测试 create_enhance_config 函数"""
        # 使用默认参数
        config = create_enhance_config()
        assert not config.enabled
        
        # 使用 True
        config = create_enhance_config(True)
        assert config.enabled
        assert config.is_using_default_config()
        
        # 使用 TransformConfig
        transform_config = TransformConfig()
        config = create_enhance_config(transform_config)
        assert config.enabled
        assert config.transform_config is transform_config
    
    def test_create_custom_enhance_config(self):
        """测试 create_custom_enhance_config 函数"""
        config = create_custom_enhance_config()
        assert config.enabled
        assert isinstance(config.transform_config, TransformConfig)


class TestEnhanceConfigIntegration:
    """测试 EnhanceConfig 与其他组件的集成"""
    
    def test_with_file_config(self):
        """测试与文件配置的集成"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                'global_probability': 0.5,
                'max_concurrent_transforms': 2,
                'transforms': {
                    'test_transform': {
                        'transform_type': 'aging',
                        'probability': 0.8,
                        'intensity_range': [0.1, 0.5],
                        'enabled': True,
                        'custom_params': {}
                    }
                }
            }
            import json
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            # 从文件创建配置
            transform_config = TransformConfig(temp_file)
            enhance_config = EnhanceConfig(transform_config)
            
            assert enhance_config.enabled
            assert enhance_config.transform_config is not None
            assert enhance_config.transform_config.get_global_probability() == 0.5
            assert len(enhance_config.transform_config.get_all_transforms()) == 1
        finally:
            # 清理临时文件
            os.unlink(temp_file)
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 空的变换配置
        empty_config = TransformConfig()
        empty_config._transforms.clear()
        enhance_config = EnhanceConfig(empty_config)
        
        assert enhance_config.enabled
        assert not enhance_config.is_using_default_config()
        
        # 检查变换配置为空时的行为
        assert len(enhance_config.transform_config.get_all_transforms()) == 0
    
    def test_property_access(self):
        """测试属性访问"""
        config = EnhanceConfig(True)
        
        # 测试 enabled 属性
        assert config.enabled is True
        
        # 测试 transform_config 属性
        assert config.transform_config is not None
        assert isinstance(config.transform_config, TransformConfig)
        
        # 禁用状态测试
        config = EnhanceConfig(False)
        assert config.enabled is False
        assert config.transform_config is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])