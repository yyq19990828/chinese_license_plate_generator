"""
车牌生成器包

提供车牌生成、图像合成和字体管理功能。
"""

from .plate_generator import PlateGenerator, PlateInfo, PlateGenerationConfig
from .image_composer import ImageComposer
from .font_manager import FontManager
from .integrated_generator import IntegratedPlateGenerator, create_generator

__all__ = [
    'PlateGenerator',
    'PlateInfo', 
    'PlateGenerationConfig',
    'ImageComposer',
    'FontManager',
    'IntegratedPlateGenerator',
    'create_generator'
]