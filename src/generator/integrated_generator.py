"""
集成车牌生成器

整合车牌生成器、图像合成器和字体管理器，提供完整的车牌生成解决方案。
"""

from typing import Optional, List, Tuple
import numpy as np
import os

from .plate_generator import PlateGenerator, PlateInfo, PlateGenerationConfig
from .image_composer import ImageComposer  
from .font_manager import FontManager
from ..core.exceptions import PlateGenerationError


class IntegratedPlateGenerator:
    """
    集成车牌生成器
    
    整合了号码生成、图像合成和字体管理的完整解决方案。
    """
    
    def __init__(self, plate_models_dir: str = "plate_model", 
                 font_models_dir: str = "font_model", 
                 enable_font_cache: bool = True):
        """
        初始化集成生成器
        
        Args:
            plate_models_dir: 车牌底板资源目录
            font_models_dir: 字体资源目录  
            enable_font_cache: 是否启用字体缓存
        """
        # 初始化各个组件
        self.plate_generator = PlateGenerator()
        self.image_composer = ImageComposer(plate_models_dir, font_models_dir)
        self.font_manager = FontManager(font_models_dir, enable_font_cache)
        
        # 验证资源完整性
        self._validate_resources()
    
    def generate_plate_with_image(self, config: Optional[PlateGenerationConfig] = None, 
                                enhance: bool = False) -> Tuple[PlateInfo, np.ndarray]:
        """
        生成车牌号码和对应图像
        
        Args:
            config: 生成配置
            enhance: 是否启用图像增强
            
        Returns:
            Tuple[PlateInfo, np.ndarray]: 车牌信息和图像
        """
        try:
            # 生成车牌信息
            plate_info = self.plate_generator.generate_random_plate(config)
            
            # 生成车牌图像
            plate_image = self.image_composer.compose_plate_image(plate_info, enhance)
            
            return plate_info, plate_image
            
        except Exception as e:
            raise PlateGenerationError(f"集成生成失败: {str(e)}")
    
    def generate_specific_plate_with_image(self, plate_number: str, 
                                         enhance: bool = False) -> Tuple[PlateInfo, np.ndarray]:
        """
        生成指定号码的车牌和图像
        
        Args:
            plate_number: 车牌号码
            enhance: 是否启用图像增强
            
        Returns:
            Tuple[PlateInfo, np.ndarray]: 车牌信息和图像
        """
        try:
            # 生成车牌信息
            plate_info = self.plate_generator.generate_specific_plate(plate_number)
            
            # 生成车牌图像
            plate_image = self.image_composer.compose_plate_image(plate_info, enhance)
            
            return plate_info, plate_image
            
        except Exception as e:
            raise PlateGenerationError(f"指定车牌生成失败: {str(e)}")
    
    def generate_batch_plates_with_images(self, count: int, 
                                        config: Optional[PlateGenerationConfig] = None,
                                        enhance: bool = False) -> List[Tuple[PlateInfo, np.ndarray]]:
        """
        批量生成车牌和图像
        
        Args:
            count: 生成数量
            config: 生成配置
            enhance: 是否启用图像增强
            
        Returns:
            List[Tuple[PlateInfo, np.ndarray]]: 车牌信息和图像列表
        """
        results = []
        
        for i in range(count):
            try:
                plate_info, plate_image = self.generate_plate_with_image(config, enhance)
                results.append((plate_info, plate_image))
                
                # 每100张进行一次内存优化
                if (i + 1) % 100 == 0:
                    self.font_manager.optimize_memory()
                    
            except PlateGenerationError:
                # 跳过失败的生成
                continue
        
        return results
    
    def save_plate_image(self, plate_image: np.ndarray, plate_info: PlateInfo, 
                        save_dir: str, filename_template: str = "{plate_number}_{bg_color}_{is_double}.jpg") -> str:
        """
        保存车牌图像
        
        Args:
            plate_image: 车牌图像
            plate_info: 车牌信息
            save_dir: 保存目录
            filename_template: 文件名模板
            
        Returns:
            str: 保存的文件路径
        """
        import cv2
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件名
        filename = filename_template.format(
            plate_number=plate_info.plate_number,
            bg_color=plate_info.background_color,
            is_double=plate_info.is_double_layer,
            plate_type=plate_info.plate_type
        )
        
        # 保存文件
        filepath = os.path.join(save_dir, filename)
        cv2.imwrite(filepath, plate_image)
        
        return filepath
    
    def get_system_stats(self) -> dict:
        """获取系统统计信息"""
        stats = {
            'font_cache_stats': self.font_manager.get_cache_stats(),
            'supported_characters': len(self.font_manager.get_supported_characters()),
        }
        return stats
    
    def optimize_memory(self) -> None:
        """优化内存使用"""
        self.font_manager.optimize_memory()
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.font_manager.clear_cache()
    
    def _validate_resources(self) -> None:
        """验证资源完整性"""
        # 验证字体资源
        validation_result = self.font_manager.validate_font_resources()
        
        if validation_result['missing_chars']:
            print(f"警告: 缺少 {len(validation_result['missing_chars'])} 个字符图像")
        
        if validation_result['invalid_files']:
            print(f"警告: {len(validation_result['invalid_files'])} 个字体文件无法加载")
    
    def get_plate_types_info(self) -> dict:
        """获取支持的车牌类型信息"""
        from ..utils.constants import PlateType
        
        return {
            'ordinary_plates': [
                PlateType.ORDINARY_BLUE,
                PlateType.ORDINARY_YELLOW, 
                PlateType.POLICE_WHITE,
                PlateType.ORDINARY_COACH,
                PlateType.ORDINARY_TRAILER
            ],
            'new_energy_plates': [
                PlateType.NEW_ENERGY_GREEN
            ],
            'special_plates': [
                PlateType.EMBASSY_BLACK,
                PlateType.MILITARY_WHITE,
                PlateType.HONGKONG_BLACK,
                PlateType.MACAO_BLACK
            ]
        }


def create_generator(plate_models_dir: str = "plate_model",
                    font_models_dir: str = "font_model") -> IntegratedPlateGenerator:
    """
    创建集成生成器的便利函数
    
    Args:
        plate_models_dir: 车牌底板资源目录
        font_models_dir: 字体资源目录
        
    Returns:
        IntegratedPlateGenerator: 集成生成器实例
    """
    return IntegratedPlateGenerator(plate_models_dir, font_models_dir)