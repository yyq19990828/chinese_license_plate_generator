"""
车牌图像合成器模块

负责将车牌号码、背景底板和字体资源合成为最终的车牌图像。
支持不同车牌类型的自动布局计算、字符颜色判断和双层车牌处理。
"""

from typing import Tuple, List, Optional, Dict, Any
import numpy as np
import cv2
import os
from dataclasses import dataclass
import logging
from PIL import Image

from .plate_generator import PlateInfo
from ..rules.base_rule import PlateColor
from ..utils.constants import PlateType
from ..core.exceptions import PlateGenerationError
from ..transform.composite_transform import CompositeTransform
from ..transform.transform_config import TransformConfig, default_config



@dataclass
class CharacterPosition:
    """字符位置信息"""
    x1: int
    y1: int  
    x2: int
    y2: int
    is_red: bool = False  # 是否红色字符


@dataclass
class PlateLayout:
    """车牌布局信息"""
    width: int
    height: int
    character_positions: List[CharacterPosition]
    background_path: str
    font_prefix: str  # 字体文件前缀


class ImageComposer:
    """
    图像合成器
    
    负责车牌图像的合成，包括：
    1. 基于车牌类型的自动布局计算
    2. 字符颜色的自动判断
    3. 双层车牌的支持
    4. 图像增强和后处理
    
    Args:
        plate_models_dir: 车牌底板资源目录
        font_models_dir: 字体资源目录
        transform_config: 变换配置，如果为None则使用默认配置
    """
    
    def __init__(self, plate_models_dir: str, font_models_dir: str, 
                 transform_config: Optional[TransformConfig] = None):
        """
        初始化图像合成器
        
        Args:
            plate_models_dir: 车牌底板资源目录
            font_models_dir: 字体资源目录
            transform_config: 变换配置，如果为None则使用默认配置
        """
        self.plate_models_dir = plate_models_dir
        self.font_models_dir = font_models_dir
        
        # 预定义的车牌尺寸和布局参数
        self.layout_configs = self._initialize_layout_configs()
        
        # 初始化变换管理器
        self.transform_manager = CompositeTransform(transform_config or default_config)
        
    def compose_plate_image(self, plate_info: PlateInfo, enhance: bool = False) -> np.ndarray:
        """
        合成车牌图像
        
        Args:
            plate_info: 车牌信息
            enhance: 是否启用图像增强
            
        Returns:
            np.ndarray: 合成的车牌图像
            
        Raises:
            PlateGenerationError: 合成失败时抛出
        """
        logging.info(f"开始合成车牌图像: {plate_info.plate_number}, 类型: {plate_info.plate_type}, 背景: {plate_info.background_color}")
        try:
            # 计算布局
            layout = self._calculate_layout(plate_info)
            logging.info(f"使用布局: 宽度={layout.width}, 高度={layout.height}, 字体前缀='{layout.font_prefix}'")
            
            # 加载底板图像
            background_img = self._load_background_image(layout.background_path, layout.width, layout.height)
            
            # 逐个合成字符
            for i, char in enumerate(plate_info.plate_number):
                if i >= len(layout.character_positions):
                    logging.warning(f"字符 '{char}' 超出布局位置数量，将被忽略。")
                    break
                    
                char_pos = layout.character_positions[i]
                
                # 加载字符图像
                char_img = self._load_character_image(char, layout.font_prefix, plate_info, i)
                
                # 应用图像增强
                if enhance:
                    char_img = self._apply_character_enhancement(char_img)
                
                # 合成到背景上
                # 处理背景颜色类型（可能是PlateColor枚举或字符串）
                bg_color_str = (plate_info.background_color.value 
                               if hasattr(plate_info.background_color, 'value') 
                               else plate_info.background_color)
                
                background_img = self._compose_character(
                    background_img, char_img, char_pos, 
                    bg_color_str, char_pos.is_red
                )
            
            # 最终后处理
            final_img = self._apply_final_processing(background_img)
            
            # 应用变换效果（如果启用增强）
            if enhance:
                final_img = self._apply_transform_effects(final_img)
            
            logging.info(f"车牌图像合成成功: {plate_info.plate_number}")
            return final_img
            
        except Exception as e:
            logging.error(f"图像合成失败: {plate_info.plate_number}", exc_info=True)
            raise PlateGenerationError(f"图像合成失败: {str(e)}")
    
    def _initialize_layout_configs(self) -> Dict[str, Dict]:
        """初始化布局配置"""
        return {
            # 单层车牌配置
            "single_7": {  # 7位单层车牌
                "width": 440,
                "height": 140,
                "char_width": 45,
                "char_height": 90,
                "y_offset": 25,
                "split_gap": 34,  # 分隔符间距
                "char_gap": 12,   # 字符间距
                "split_position": 2  # 分隔符位置(第2位后)
            },
            "single_8": {  # 8位单层车牌(新能源)
                "width": 480,
                "height": 140,
                "char_width": 43,
                "char_height": 90,
                "y_offset": 25,
                "split_gap": 49,
                "char_gap": 9,
                "split_position": 2
            },
            # 双层车牌配置
            "double_7": {  # 7位双层车牌
                "width": 440,
                "height": 220,
                "char_width_top": 80,   # 上层字符宽度
                "char_height_top": 60,  # 上层字符高度
                "char_width_bottom": 65, # 下层字符宽度
                "char_height_bottom": 110, # 下层字符高度
                "top_y_offset": 15,     # 上层Y偏移
                "bottom_y_offset": 90,  # 下层Y偏移
                "char_gap": 15,
                "top_positions": [(110, 250)],  # 上层两个字符的X坐标范围
                "bottom_positions": [27, 107, 187, 267, 347]  # 下层5个字符的X坐标
            }
        }
    
    def _calculate_layout(self, plate_info: PlateInfo) -> PlateLayout:
        """
        计算车牌布局
        
        Args:
            plate_info: 车牌信息
            
        Returns:
            PlateLayout: 布局信息
        """
        plate_length = len(plate_info.plate_number)
        is_double = plate_info.is_double_layer
        
        # 确定配置键
        if is_double:
            config_key = f"double_{plate_length}"
        else:
            config_key = f"single_{plate_length}"
        
        if config_key not in self.layout_configs:
            # 使用默认配置
            logging.warning(f"未找到布局配置 '{config_key}', 将使用 'single_7' 作为默认配置。")
            config_key = "single_7"
        
        config = self.layout_configs[config_key]
        
        # 计算字符位置
        if is_double:
            positions = self._calculate_double_layer_positions(plate_info, config)
        else:
            positions = self._calculate_single_layer_positions(plate_info, config)
        
        # 确定背景图片路径和字体前缀
        bg_path = self._get_background_path(plate_info, config["width"], config["height"])
        font_prefix = self._get_font_prefix(plate_info)
        
        return PlateLayout(
            width=config["width"],
            height=config["height"],
            character_positions=positions,
            background_path=bg_path,
            font_prefix=font_prefix
        )
    
    def _calculate_single_layer_positions(self, plate_info: PlateInfo, config: Dict) -> List[CharacterPosition]:
        """计算单层车牌字符位置"""
        positions = []
        plate_number = plate_info.plate_number
        
        # 确定分隔位置
        split_pos = self._get_split_position(plate_info)
        
        for i, char in enumerate(plate_number):
            # 计算X坐标
            if i == 0:
                x = 15  # 首字符起始位置
            elif i == split_pos:
                x = positions[i-1].x2 + config["split_gap"]
            else:
                x = positions[i-1].x2 + config["char_gap"]
            
            # 新能源车牌第一位后字符宽度调整
            char_width = config["char_width"]
            if len(plate_number) == 8 and i > 0:
                char_width = 43
            
            # 判断是否红色字符
            is_red = self._is_red_character(char, i, plate_info)
            
            position = CharacterPosition(
                x1=x,
                y1=config["y_offset"],
                x2=x + char_width,
                y2=config["y_offset"] + config["char_height"],
                is_red=is_red
            )
            positions.append(position)
        
        return positions
    
    def _calculate_double_layer_positions(self, plate_info: PlateInfo, config: Dict) -> List[CharacterPosition]:
        """计算双层车牌字符位置"""
        positions = []
        plate_number = plate_info.plate_number
        
        for i, char in enumerate(plate_number):
            is_red = self._is_red_character(char, i, plate_info)
            
            if i < 2:  # 上层字符
                x_positions = [110, 250]  # 预定义的上层X坐标
                position = CharacterPosition(
                    x1=x_positions[i],
                    y1=config["top_y_offset"],
                    x2=x_positions[i] + config["char_width_top"],
                    y2=config["top_y_offset"] + config["char_height_top"],
                    is_red=is_red
                )
            else:  # 下层字符
                bottom_index = i - 2
                x_positions = [27, 107, 187, 267, 347]  # 预定义的下层X坐标
                if bottom_index < len(x_positions):
                    x = x_positions[bottom_index]
                else:
                    x = x_positions[-1] + (bottom_index - len(x_positions) + 1) * 80
                
                position = CharacterPosition(
                    x1=x,
                    y1=config["bottom_y_offset"],
                    x2=x + config["char_width_bottom"],
                    y2=config["bottom_y_offset"] + config["char_height_bottom"],
                    is_red=is_red
                )
            
            positions.append(position)
        
        return positions
    
    def _get_split_position(self, plate_info: PlateInfo) -> int:
        """获取分隔符位置"""
        # 直接使用 PlateInfo 中的 split_position 属性
        return plate_info.split_position
    
    def _is_red_character(self, char: str, position: int, plate_info: PlateInfo) -> bool:
        """判断字符是否为红色"""
        # 只有特殊字符 '警' 是红色，'使'和'领'为白色
        if char == '警':
            return True

        # 仅当车牌类型为军牌时，才应用其他红色字符规则
        if plate_info.plate_type == PlateType.MILITARY_WHITE:
            # 军牌的第一个字符（军种字母）是红色
            if position == 0:
                return True
            # 军牌的第二个字符（地区字母）有50%的几率是红色
            if position == 1 and char.isalpha():
                return np.random.random() > 0.5
        
        return False
    
    def _get_background_path(self, plate_info: PlateInfo, width: int, height: int) -> str:
        """获取背景图片路径"""
        plate_number = plate_info.plate_number
        
        # 使用专用底牌模板
        if '使' in plate_number:
            filename = f"black_shi_{height}.PNG"
        elif '领' in plate_number:
            filename = f"black_ling_{height}.PNG"
        else:
            # 使用原始逻辑 - 处理背景颜色类型
            bg_color = plate_info.background_color
            bg_color_str = (bg_color.value 
                           if hasattr(bg_color, 'value') 
                           else bg_color)
            filename = f"{bg_color_str}_{height}.PNG"
        
        return os.path.join(self.plate_models_dir, filename)
    
    def _get_font_prefix(self, plate_info: PlateInfo) -> str:
        """根据车牌信息获取正确的字体文件前缀"""
        if plate_info.plate_type == PlateType.NEW_ENERGY_GREEN:
            return "green"
        
        # 对于黑色背景的车牌（使领馆、港澳），没有特定的字体前缀，使用标准字体
        if plate_info.background_color in ["black", "black_shi"]:
            if plate_info.is_double_layer:
                return "220"
            else:
                return "140"

        if plate_info.is_double_layer:
            return "220"
        else:
            return "140"
    
    def _load_background_image(self, bg_path: str, width: int, height: int) -> np.ndarray:
        """加载并调整背景图像"""
        if not os.path.exists(bg_path):
            raise PlateGenerationError(f"背景图片不存在: {bg_path}")
        
        img = cv2.imread(bg_path)
        if img is None:
            raise PlateGenerationError(f"无法加载背景图片: {bg_path}")
        
        return cv2.resize(img, (width, height))
    
    def _load_character_image(self, char: str, font_prefix: str, plate_info: PlateInfo, position: int) -> np.ndarray:
        """加载字符图像"""
        # 构建字符文件名
        if font_prefix == "220":  # 双层车牌
            if position < 2:
                filename = f"220_up_{char}.jpg"
            else:
                filename = f"220_down_{char}.jpg"
        else:
            filename = f"{font_prefix}_{char}.jpg"
        
        char_path = os.path.join(self.font_models_dir, filename)
        logging.info(f"尝试加载字符图像: {char_path}")
        
        if not os.path.exists(char_path):
            # 如果特定前缀的字体不存在，尝试使用通用的 '140' 字体作为备选
            fallback_filename = f"140_{char}.jpg"
            fallback_path = os.path.join(self.font_models_dir, fallback_filename)
            logging.warning(f"'{char_path}' 不存在，尝试使用备选字体 '{fallback_path}'")
            if not os.path.exists(fallback_path):
                raise PlateGenerationError(f"字符图片及其备选方案均不存在: {char_path}, {fallback_path}")
            char_path = fallback_path

        # 使用中文文件名兼容的读取方式
        char_img = cv2.imdecode(np.fromfile(char_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        
        if char_img is None:
            raise PlateGenerationError(f"无法加载字符图片: {char_path}")
        
        return char_img
    
    def _apply_character_enhancement(self, char_img: np.ndarray) -> np.ndarray:
        """应用字符图像增强"""
        # 随机应用腐蚀或膨胀操作
        kernel_size = np.random.randint(1, 6)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        
        if np.random.random() > 0.5:
            return cv2.erode(char_img, kernel, iterations=1)
        else:
            return cv2.dilate(char_img, kernel, iterations=1)
    
    def _apply_transform_effects(self, image: np.ndarray) -> np.ndarray:
        """
        应用变换效果到最终图像
        
        Args:
            image: 输入图像(numpy array)
            
        Returns:
            np.ndarray: 应用变换后的图像
        """
        try:
            # 转换为PIL图像格式
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 应用复合变换
            transformed_image, applied_transforms = self.transform_manager.apply(pil_image)
            
            # 转换回numpy格式
            result_image = cv2.cvtColor(np.array(transformed_image), cv2.COLOR_RGB2BGR)
            
            if applied_transforms:
                logging.info(f"应用的变换效果: {', '.join(applied_transforms)}")
            else:
                logging.info("未应用任何变换效果")
                
            return result_image
            
        except Exception as e:
            logging.warning(f"变换效果应用失败，返回原始图像: {str(e)}")
            return image
    
    def _compose_character(self, background: np.ndarray, char_img: np.ndarray, 
                          position: CharacterPosition, bg_color: str, is_red: bool) -> np.ndarray:
        """将字符合成到背景上"""
        x1, y1, x2, y2 = position.x1, position.y1, position.x2, position.y2
        
        # 调整字符图像大小
        char_img_resized = cv2.resize(char_img, (x2 - x1, y2 - y1))
        
        # 获取背景区域
        bg_region = background[y1:y2, x1:x2, :]
        
        # 根据字符颜色和背景色设置文字颜色
        if is_red:
            text_color = [0, 0, 255]  # 红色
        elif 'blue' in bg_color or 'black' in bg_color:
            text_color = [255, 255, 255]  # 白色
        else:
            text_color = [0, 0, 0]  # 黑色
        
        # 应用字符到背景(阈值200作为透明度判断)
        mask = char_img_resized < 200
        bg_region[mask] = text_color
        
        return background
    
    def _apply_final_processing(self, img: np.ndarray) -> np.ndarray:
        """应用最终图像处理"""
        # 轻微模糊以模拟真实车牌效果
        return cv2.blur(img, (3, 3))