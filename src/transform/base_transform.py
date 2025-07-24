"""
基础变换类模块

提供所有车牌增强变换效果的基类和接口定义。
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import numpy as np
from PIL import Image
import cv2


class BaseTransform(ABC):
    """
    车牌变换效果基类
    
    所有具体的变换效果都应该继承此类并实现其抽象方法。
    
    Args:
        probability (float): 应用此变换的概率，默认0.3
        **kwargs: 其他变换参数
    """
    
    def __init__(self, probability: float = 0.3, **kwargs):
        """
        初始化基础变换类
        
        Args:
            probability (float): 应用此变换的概率，默认0.3
            **kwargs: 其他变换参数
        """
        if not 0.0 <= probability <= 1.0:
            raise ValueError("Probability must be between 0.0 and 1.0")
        
        self.probability = probability
        self.params = kwargs
        
    @abstractmethod
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用变换效果到图像
        
        Args:
            image (Image.Image): 输入的车牌图像
            **kwargs: 运行时参数
            
        Returns:
            Image.Image: 变换后的图像
        """
        pass
    
    @abstractmethod
    def get_transform_name(self) -> str:
        """
        获取变换效果名称
        
        Returns:
            str: 变换效果的唯一标识名称
        """
        pass
    
    def should_apply(self) -> bool:
        """
        根据概率判断是否应该应用此变换
        
        Returns:
            bool: True表示应该应用变换
        """
        return np.random.random() < self.probability
    
    def set_probability(self, probability: float) -> None:
        """
        设置变换概率
        
        Args:
            probability (float): 新的概率值
        """
        if not 0.0 <= probability <= 1.0:
            raise ValueError("Probability must be between 0.0 and 1.0")
        self.probability = probability
    
    def get_probability(self) -> float:
        """
        获取当前变换概率
        
        Returns:
            float: 当前概率值
        """
        return self.probability
    
    def validate_image(self, image: Image.Image) -> None:
        """
        验证输入图像的有效性
        
        Args:
            image (Image.Image): 待验证的图像
            
        Raises:
            ValueError: 当图像无效时
        """
        if not isinstance(image, Image.Image):
            raise ValueError("Input must be a PIL Image")
        
        if image.size[0] == 0 or image.size[1] == 0:
            raise ValueError("Image dimensions cannot be zero")
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取变换配置信息
        
        Returns:
            Dict[str, Any]: 包含变换名称、概率和参数的配置字典
        """
        return {
            'name': self.get_transform_name(),
            'probability': self.probability,
            'params': self.params.copy()
        }
    
    def __call__(self, image: Image.Image, **kwargs) -> Optional[Image.Image]:
        """
        使对象可调用，根据概率决定是否应用变换
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
            
        Returns:
            Optional[Image.Image]: 变换后的图像，如果不应用变换则返回None
        """
        self.validate_image(image)
        
        if not self.should_apply():
            return None
            
        return self.apply(image, **kwargs)


class TransformUtils:
    """
    变换工具类，提供常用的图像处理辅助方法
    """
    
    @staticmethod
    def pil_to_cv2(image: Image.Image) -> np.ndarray:
        """
        PIL图像转换为OpenCV格式
        
        Args:
            image (Image.Image): PIL图像
            
        Returns:
            np.ndarray: OpenCV格式图像
        """
        # 转换为RGB模式（如果不是的话）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # PIL使用RGB，OpenCV使用BGR
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return opencv_image
    
    @staticmethod
    def cv2_to_pil(image: np.ndarray) -> Image.Image:
        """
        OpenCV图像转换为PIL格式
        
        Args:
            image (np.ndarray): OpenCV格式图像
            
        Returns:
            Image.Image: PIL图像
        """
        # OpenCV使用BGR，PIL使用RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)
    
    @staticmethod
    def ensure_uint8(image: np.ndarray) -> np.ndarray:
        """
        确保图像数据类型为uint8
        
        Args:
            image (np.ndarray): 输入图像
            
        Returns:
            np.ndarray: uint8类型图像
        """
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        return image
    
    @staticmethod
    def add_noise(image: np.ndarray, noise_factor: float = 0.1) -> np.ndarray:
        """
        为图像添加随机噪声
        
        Args:
            image (np.ndarray): 输入图像
            noise_factor (float): 噪声强度因子
            
        Returns:
            np.ndarray: 添加噪声后的图像
        """
        noise = np.random.normal(0, noise_factor * 255, image.shape)
        noisy_image = image + noise
        return TransformUtils.ensure_uint8(noisy_image)
    
    @staticmethod
    def adjust_brightness(image: np.ndarray, factor: float) -> np.ndarray:
        """
        调整图像亮度
        
        Args:
            image (np.ndarray): 输入图像
            factor (float): 亮度调整因子（1.0保持不变，>1.0变亮，<1.0变暗）
            
        Returns:
            np.ndarray: 调整亮度后的图像
        """
        adjusted = image * factor
        return TransformUtils.ensure_uint8(adjusted)
    
    @staticmethod
    def adjust_contrast(image: np.ndarray, factor: float) -> np.ndarray:
        """
        调整图像对比度
        
        Args:
            image (np.ndarray): 输入图像
            factor (float): 对比度调整因子（1.0保持不变，>1.0增加对比度，<1.0降低对比度）
            
        Returns:
            np.ndarray: 调整对比度后的图像
        """
        mean = np.mean(image)
        adjusted = (image - mean) * factor + mean
        return TransformUtils.ensure_uint8(adjusted)
    
    @staticmethod
    def get_random_point_in_bounds(width: int, height: int, margin: int = 0) -> Tuple[int, int]:
        """
        在指定边界内获取随机点
        
        Args:
            width (int): 边界宽度
            height (int): 边界高度
            margin (int): 边距
            
        Returns:
            Tuple[int, int]: 随机点坐标(x, y)
        """
        x = np.random.randint(margin, width - margin)
        y = np.random.randint(margin, height - margin)
        return x, y