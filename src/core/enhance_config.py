"""
增强配置模块

提供增强参数的统一接口，支持bool值和TransformConfig自定义配置。
"""

from typing import Union, Optional
from ..transform.transform_config import TransformConfig


class EnhanceConfig:
    """
    增强配置管理器
    
    统一管理增强参数，支持：
    1. 简单bool值：True/False 控制是否启用默认增强
    2. 自定义TransformConfig：高度自定义的变换配置
    """
    
    def __init__(self, enhance: Union[bool, TransformConfig, None] = False):
        """
        初始化增强配置
        
        Args:
            enhance: 增强配置
                - bool: True启用默认增强，False禁用增强
                - TransformConfig: 使用自定义变换配置
                - None: 禁用增强
        """
        self._enabled = False
        self._transform_config: Optional[TransformConfig] = None
        
        self._parse_enhance_config(enhance)
    
    def _parse_enhance_config(self, enhance: Union[bool, TransformConfig, None]) -> None:
        """
        解析增强配置参数
        
        Args:
            enhance: 增强配置参数
        """
        if enhance is None or enhance is False:
            # 禁用增强
            self._enabled = False
            self._transform_config = None
            
        elif enhance is True:
            # 启用默认增强配置
            self._enabled = True
            self._transform_config = TransformConfig()  # 使用默认配置
            
        elif isinstance(enhance, TransformConfig):
            # 使用自定义变换配置
            self._enabled = True
            self._transform_config = enhance
            
        elif isinstance(enhance, EnhanceConfig):
            # 如果已经是EnhanceConfig对象，直接复制其状态
            self._enabled = enhance._enabled
            self._transform_config = enhance._transform_config
            
        else:
            raise TypeError(
                f"enhance参数必须是bool、TransformConfig或EnhanceConfig类型，获得: {type(enhance)}"
            )
    
    @property
    def enabled(self) -> bool:
        """是否启用增强"""
        return self._enabled
    
    @property
    def transform_config(self) -> Optional[TransformConfig]:
        """获取变换配置"""
        return self._transform_config
    
    def is_using_default_config(self) -> bool:
        """是否使用默认配置"""
        if not self._enabled or self._transform_config is None:
            return False
        
        # 检查是否为默认配置（通过比较配置数量来简单判断）
        default_config = TransformConfig()
        return len(self._transform_config.get_all_transforms()) == len(default_config.get_all_transforms())
    
    def update_config(self, enhance: Union[bool, TransformConfig, None]) -> None:
        """
        更新增强配置
        
        Args:
            enhance: 新的增强配置
        """
        self._parse_enhance_config(enhance)
    
    def __bool__(self) -> bool:
        """支持bool()转换"""
        return self._enabled
    
    def __repr__(self) -> str:
        """字符串表示"""
        if not self._enabled:
            return "EnhanceConfig(disabled)"
        elif self.is_using_default_config():
            return "EnhanceConfig(enabled=True, using_default_config=True)"
        else:
            transform_count = len(self._transform_config.get_all_transforms()) if self._transform_config else 0
            return f"EnhanceConfig(enabled=True, custom_transforms={transform_count})"


def create_enhance_config(enhance: Union[bool, TransformConfig, None] = False) -> EnhanceConfig:
    """
    创建增强配置的便利函数
    
    Args:
        enhance: 增强配置参数
        
    Returns:
        EnhanceConfig: 增强配置实例
    """
    return EnhanceConfig(enhance)


def create_custom_enhance_config(**kwargs) -> EnhanceConfig:
    """
    创建自定义增强配置的便利函数
    
    Args:
        **kwargs: TransformConfig的初始化参数
        
    Returns:
        EnhanceConfig: 带有自定义变换配置的增强配置实例
        
    Examples:
        >>> # 创建启用所有变换的配置
        >>> config = create_custom_enhance_config()
        >>> enhance_config = EnhanceConfig(config)
        
        >>> # 创建从文件加载的配置
        >>> config = TransformConfig('my_config.json')  
        >>> enhance_config = EnhanceConfig(config)
    """
    transform_config = TransformConfig(**kwargs)
    return EnhanceConfig(transform_config)