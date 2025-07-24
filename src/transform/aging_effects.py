"""
车牌老化效果模块

实现各种车牌老化效果，包括磨损、褪色、污渍等真实的老化现象。
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import cv2
from typing import Tuple, Optional
import random

from .base_transform import BaseTransform, TransformUtils


class WearEffect(BaseTransform):
    """
    车牌磨损效果
    
    模拟车牌使用过程中的边缘磨损和字符模糊效果。
    
    Args:
        probability (float): 应用概率，默认0.3
        **kwargs: 其他参数
            erosion_kernel_size (tuple): 腐蚀核大小范围，默认(2, 5)
            erosion_iterations (tuple): 腐蚀迭代次数范围，默认(1, 3)
            blur_strength (tuple): 模糊强度范围，默认(0.5, 2.0)
    """
    
    def __init__(self, probability: float = 0.3, **kwargs):
        """
        初始化磨损效果
        
        Args:
            probability (float): 应用概率，默认0.3
            **kwargs: 其他参数
                erosion_kernel_size (tuple): 腐蚀核大小范围，默认(2, 5)
                erosion_iterations (tuple): 腐蚀迭代次数范围，默认(1, 3)
                blur_strength (tuple): 模糊强度范围，默认(0.5, 2.0)
        """
        # 设置默认参数
        default_params = {
            'erosion_kernel_size': (2, 5),
            'erosion_iterations': (1, 3),
            'blur_strength': (0.5, 2.0)
        }
        default_params.update(kwargs)
        
        super().__init__(probability, **default_params)
        
        # 兼容性属性
        self.wear_strength = self.params.get('wear_strength', 0.3)
        self.blur_kernel_size = self.params.get('blur_kernel_size', 3)
        self.erosion_kernel_size = self.params.get('erosion_kernel_size', (2, 5))
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用磨损效果
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度，覆盖默认值
                
        Returns:
            Image.Image: 应用磨损效果后的图像
        """
        intensity = kwargs.get('intensity', self.wear_strength)
        
        # 转换为OpenCV格式
        cv_image = TransformUtils.pil_to_cv2(image)
        
        # 创建磨损mask
        wear_mask = self._create_wear_mask(cv_image.shape[:2], intensity)
        
        # 应用边缘腐蚀效果
        eroded_image = self._apply_erosion(cv_image, intensity)
        
        # 应用局部模糊
        blurred_image = self._apply_local_blur(eroded_image, wear_mask, intensity)
        
        # 混合原图和效果图
        result = self._blend_with_mask(cv_image, blurred_image, wear_mask, intensity)
        
        return TransformUtils.cv2_to_pil(result)
    
    def _create_wear_mask(self, shape: Tuple[int, int], intensity: float) -> np.ndarray:
        """
        创建磨损区域mask
        
        Args:
            shape (Tuple[int, int]): 图像尺寸 (height, width)
            intensity (float): 磨损强度
            
        Returns:
            np.ndarray: 磨损mask
        """
        height, width = shape
        mask = np.zeros((height, width), dtype=np.float32)
        
        # 边缘磨损
        edge_wear_width = int(min(width, height) * intensity * 0.1)
        if edge_wear_width > 0:
            # 随机选择磨损边缘
            edges_to_wear = random.sample(['top', 'bottom', 'left', 'right'], 
                                        random.randint(1, 3))
            
            for edge in edges_to_wear:
                if edge == 'top':
                    mask[:edge_wear_width, :] = np.random.uniform(0.3, 0.8, (edge_wear_width, width))
                elif edge == 'bottom':
                    mask[-edge_wear_width:, :] = np.random.uniform(0.3, 0.8, (edge_wear_width, width))
                elif edge == 'left':
                    mask[:, :edge_wear_width] = np.random.uniform(0.3, 0.8, (height, edge_wear_width))
                elif edge == 'right':
                    mask[:, -edge_wear_width:] = np.random.uniform(0.3, 0.8, (height, edge_wear_width))
        
        # 随机局部磨损点
        num_spots = int(width * height * intensity * 0.0001)
        for _ in range(num_spots):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            spot_size = random.randint(2, 8)
            
            # 创建圆形磨损点
            cv2.circle(mask, (x, y), spot_size, 
                      random.uniform(0.4, 0.9), -1)
        
        # 平滑处理
        mask = cv2.GaussianBlur(mask, (5, 5), 1.0)
        
        return mask
    
    def _apply_erosion(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """
        应用腐蚀效果模拟边缘磨损
        
        Args:
            image (np.ndarray): 输入图像
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 腐蚀后的图像
        """
        # 处理元组参数
        if isinstance(self.erosion_kernel_size, tuple):
            min_size, max_size = self.erosion_kernel_size
            kernel_size = int(min_size + (max_size - min_size) * intensity)
        else:
            kernel_size = max(1, int(self.erosion_kernel_size * intensity))
        
        kernel_size = max(1, kernel_size)
        
        if kernel_size > 1:
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            
            # 处理迭代次数
            if isinstance(self.params.get('erosion_iterations', 1), tuple):
                min_iter, max_iter = self.params['erosion_iterations']
                iterations = int(min_iter + (max_iter - min_iter) * intensity)
            else:
                iterations = 1
                
            iterations = max(1, iterations)
            eroded = cv2.erode(image, kernel, iterations=iterations)
            return eroded
        return image
    
    def _apply_local_blur(self, image: np.ndarray, mask: np.ndarray, intensity: float) -> np.ndarray:
        """
        应用局部模糊效果
        
        Args:
            image (np.ndarray): 输入图像
            mask (np.ndarray): 模糊区域mask
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 应用局部模糊后的图像
        """
        # 处理模糊强度参数
        if isinstance(self.params.get('blur_strength', (0.5, 2.0)), tuple):
            min_blur, max_blur = self.params['blur_strength']
            blur_strength = min_blur + (max_blur - min_blur) * intensity
        else:
            blur_strength = self.blur_kernel_size * intensity
            
        kernel_size = max(1, int(blur_strength * 3))  # 转换为核大小
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        if kernel_size > 1:
            blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
            
            # 根据mask混合原图和模糊图
            mask_3d = np.stack([mask] * 3, axis=-1)
            result = image * (1 - mask_3d) + blurred * mask_3d
            return TransformUtils.ensure_uint8(result)
        
        return image
    
    def _blend_with_mask(self, original: np.ndarray, effect: np.ndarray, 
                        mask: np.ndarray, intensity: float) -> np.ndarray:
        """
        使用mask混合原图和效果图
        
        Args:
            original (np.ndarray): 原始图像
            effect (np.ndarray): 效果图像
            mask (np.ndarray): 混合mask
            intensity (float): 混合强度
            
        Returns:
            np.ndarray: 混合后的图像
        """
        mask_3d = np.stack([mask] * 3, axis=-1) * intensity
        result = original * (1 - mask_3d) + effect * mask_3d
        return TransformUtils.ensure_uint8(result)
    
    def get_transform_name(self) -> str:
        return "wear_effect"


class FadeEffect(BaseTransform):
    """
    车牌褪色效果
    
    模拟车牌长期暴露在阳光下导致的颜色褪色和对比度降低。
    
    Args:
        probability (float): 应用概率，默认0.3
        **kwargs: 其他参数
            fade_factor (tuple): 褪色因子范围，默认(0.7, 0.9)
            color_shift (tuple): 颜色偏移范围，默认(-20, 20)
    """
    
    def __init__(self, probability: float = 0.3, **kwargs):
        """
        初始化褪色效果
        
        Args:
            probability (float): 应用概率，默认0.3
            **kwargs: 其他参数
                fade_factor (tuple): 褪色因子范围，默认(0.7, 0.9)
                color_shift (tuple): 颜色偏移范围，默认(-20, 20)
        """
        # 设置默认参数
        default_params = {
            'fade_factor': (0.7, 0.9),
            'color_shift': (-20, 20)
        }
        default_params.update(kwargs)
        
        super().__init__(probability, **default_params)
        
        # 兼容性属性
        self.fade_factor = self.params.get('fade_factor', (0.7, 0.9))
        self.color_shift = self.params.get('color_shift', (-20, 20))
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用褪色效果
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用褪色效果后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        # 处理褪色因子参数
        if isinstance(self.fade_factor, tuple):
            min_fade, max_fade = self.fade_factor
            fade_value = min_fade + (max_fade - min_fade) * intensity
        else:
            fade_value = self.fade_factor
        
        # 降低饱和度
        enhancer_color = ImageEnhance.Color(image)
        desaturated = enhancer_color.enhance(fade_value)
        
        # 降低对比度
        enhancer_contrast = ImageEnhance.Contrast(desaturated)
        contrast_value = 0.7 + 0.3 * (1 - intensity)
        faded = enhancer_contrast.enhance(contrast_value)
        
        # 添加轻微的颜色偏移（模拟不均匀褪色）
        faded_array = np.array(faded)
        
        # 创建不均匀褪色效果
        fade_pattern = self._create_fade_pattern(faded_array.shape[:2], intensity)
        
        # 应用颜色偏移
        color_shifted = self._apply_color_shift(faded_array, fade_pattern, intensity)
        
        return Image.fromarray(TransformUtils.ensure_uint8(color_shifted))
    
    def _create_fade_pattern(self, shape: Tuple[int, int], intensity: float) -> np.ndarray:
        """
        创建不均匀褪色图案
        
        Args:
            shape (Tuple[int, int]): 图像尺寸 (height, width)
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 褪色图案
        """
        height, width = shape
        
        # 创建渐变褪色效果
        y_gradient = np.linspace(0, 1, height)
        x_gradient = np.linspace(0, 1, width)
        Y, X = np.meshgrid(y_gradient, x_gradient, indexing='ij')
        
        # 组合多种渐变模式
        pattern = 0.5 + 0.3 * np.sin(Y * np.pi) + 0.2 * np.cos(X * np.pi * 2)
        
        # 添加随机噪声
        noise = np.random.normal(0, 0.1, (height, width))
        pattern += noise
        
        # 归一化并调整强度
        pattern = np.clip(pattern, 0, 1)
        pattern = pattern * intensity + (1 - intensity) * 0.5
        
        return pattern
    
    def _apply_color_shift(self, image: np.ndarray, fade_pattern: np.ndarray, intensity: float) -> np.ndarray:
        """
        应用颜色偏移效果
        
        Args:
            image (np.ndarray): 输入图像
            fade_pattern (np.ndarray): 褪色图案
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 应用颜色偏移后的图像
        """
        result = image.copy().astype(np.float32)
        
        # 扩展fade_pattern到三个颜色通道
        fade_3d = np.stack([fade_pattern] * 3, axis=-1)
        
        # 应用亮度调整
        brightness_factor = 0.9 + 0.2 * fade_3d
        result = result * brightness_factor
        
        # 处理颜色偏移参数
        if isinstance(self.color_shift, tuple):
            min_shift, max_shift = self.color_shift
            # 从范围中随机选择一个值
            color_shift_value = np.random.uniform(min_shift, max_shift) / 100.0  # 转换为小数
        else:
            color_shift_value = self.color_shift
        
        # 添加轻微的颜色偏移（偏向黄色，模拟日晒效果）
        color_shift_strength = color_shift_value * intensity
        result[:, :, 0] += color_shift_strength * fade_pattern * 20  # Red channel
        result[:, :, 1] += color_shift_strength * fade_pattern * 15  # Green channel  
        result[:, :, 2] -= color_shift_strength * fade_pattern * 10  # Blue channel
        
        return np.clip(result, 0, 255)
    
    def get_transform_name(self) -> str:
        return "fade_effect"


class DirtEffect(BaseTransform):
    """
    车牌污渍效果
    
    模拟车牌表面的灰尘、泥点和其他污渍。
    
    Args:
        probability (float): 应用概率，默认0.3
        **kwargs: 其他参数
            num_spots (tuple): 污渍数量范围，默认(3, 8)
            spot_size (tuple): 污渍大小范围，默认(5, 20)
            dirt_density (float): 污渍密度，默认0.05
    """
    
    def __init__(self, probability: float = 0.3, **kwargs):
        """
        初始化污渍效果
        
        Args:
            probability (float): 应用概率，默认0.3
            **kwargs: 其他参数
                num_spots (tuple): 污渍数量范围，默认(3, 8)
                spot_size (tuple): 污渍大小范围，默认(5, 20)
                dirt_density (float): 污渍密度，默认0.05
        """
        # 设置默认参数
        default_params = {
            'num_spots': (3, 8),
            'spot_size': (5, 20),
            'dirt_density': 0.05
        }
        default_params.update(kwargs)
        
        super().__init__(probability, **default_params)
        
        # 兼容性属性
        self.dirt_density = self.params.get('dirt_density', 0.05)
        self.spot_size_range = self.params.get('spot_size_range', (5, 20))
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用污渍效果
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用污渍效果后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        cv_image = TransformUtils.pil_to_cv2(image)
        
        # 添加不同类型的污渍
        dirty_image = cv_image.copy()
        
        # 1. 灰尘效果
        dirty_image = self._add_dust(dirty_image, intensity)
        
        # 2. 泥点效果
        dirty_image = self._add_mud_spots(dirty_image, intensity)
        
        # 3. 水渍效果
        dirty_image = self._add_water_stains(dirty_image, intensity)
        
        # 4. 整体灰蒙效果
        dirty_image = self._add_overall_grime(dirty_image, intensity)
        
        return TransformUtils.cv2_to_pil(dirty_image)
    
    def _add_dust(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """
        添加灰尘效果
        
        Args:
            image (np.ndarray): 输入图像
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 添加灰尘后的图像
        """
        height, width = image.shape[:2]
        
        # 创建灰尘层
        dust_layer = np.ones_like(image, dtype=np.float32) * 255
        
        # 添加随机灰尘颗粒
        num_particles = int(width * height * self.dirt_density * intensity)
        
        for _ in range(num_particles):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            size = random.randint(1, 3)
            opacity = random.uniform(0.1, 0.4) * intensity
            
            # 灰色灰尘
            color = random.randint(80, 150)
            cv2.circle(dust_layer, (x, y), size, (color, color, color), -1)
        
        # 混合灰尘层
        dust_alpha = 0.3 * intensity
        result = image * (1 - dust_alpha) + dust_layer * dust_alpha
        
        return TransformUtils.ensure_uint8(result)
    
    def _add_mud_spots(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """
        添加泥点效果
        
        Args:
            image (np.ndarray): 输入图像
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 添加泥点后的图像
        """
        height, width = image.shape[:2]
        mud_layer = image.copy()
        mask = np.zeros((height, width), dtype=np.float32)
        
        # 添加泥点
        num_spots = int(width * height * self.dirt_density * 0.5 * intensity)
        
        for _ in range(num_spots):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            spot_size = int(random.randint(*self.spot_size_range) * intensity)
            if spot_size < 1:
                spot_size = 1
            
            # 泥土颜色（棕色系）
            mud_color = (
                random.randint(30, 80),   # Blue
                random.randint(40, 90),   # Green  
                random.randint(50, 100)   # Red
            )
            
            opacity = random.uniform(0.5, 0.9) * intensity
            
            # 不规则形状的泥点
            if random.random() < 0.5:
                # 圆形泥点
                cv2.circle(mud_layer, (x, y), spot_size, mud_color, -1)
                cv2.circle(mask, (x, y), spot_size, opacity, -1)
            else:
                # 椭圆形泥点
                axes = (spot_size, random.randint(spot_size//2, spot_size))
                angle = random.randint(0, 180)
                cv2.ellipse(mud_layer, (x, y), axes, angle, 0, 360, mud_color, -1)
                cv2.ellipse(mask, (x, y), axes, angle, 0, 360, opacity, -1)
        
        # 平滑mask
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        mask_3d = np.stack([mask] * 3, axis=-1)
        
        # 混合
        result = image * (1 - mask_3d) + mud_layer * mask_3d
        
        return TransformUtils.ensure_uint8(result)
    
    def _add_water_stains(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """
        添加水渍效果
        
        Args:
            image (np.ndarray): 输入图像
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 添加水渍后的图像
        """
        height, width = image.shape[:2]
        
        # 创建水渍图案
        stain_mask = np.zeros((height, width), dtype=np.float32)
        
        # 添加几个大的水渍区域
        num_stains = random.randint(1, 3)
        
        for _ in range(num_stains):
            # 随机位置和大小
            center_x = random.randint(width//4, 3*width//4)
            center_y = random.randint(height//4, 3*height//4)
            stain_size = random.randint(min(width, height)//8, min(width, height)//4)
            
            # 创建不规则水渍形状
            for _ in range(50):
                offset_x = random.randint(-stain_size, stain_size)
                offset_y = random.randint(-stain_size, stain_size)
                x = np.clip(center_x + offset_x, 0, width - 1)
                y = np.clip(center_y + offset_y, 0, height - 1)
                
                distance = np.sqrt(offset_x**2 + offset_y**2)
                if distance < stain_size:
                    stain_strength = (1 - distance / stain_size) * intensity * 0.3
                    stain_mask[y, x] = max(stain_mask[y, x], stain_strength)
        
        # 平滑水渍边界
        stain_mask = cv2.GaussianBlur(stain_mask, (15, 15), 5)
        
        # 应用水渍效果（轻微变暗）
        stain_3d = np.stack([stain_mask] * 3, axis=-1)
        result = image.astype(np.float32)
        result = result * (1 - stain_3d * 0.4)
        
        return TransformUtils.ensure_uint8(result)
    
    def _add_overall_grime(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """
        添加整体灰蒙效果
        
        Args:
            image (np.ndarray): 输入图像
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 添加整体灰蒙后的图像
        """
        # 轻微降低亮度和对比度
        result = image.astype(np.float32)
        
        # 整体变暗
        darkening_factor = 1 - 0.1 * intensity
        result *= darkening_factor
        
        # 添加轻微的灰色调
        gray_tint_strength = 0.05 * intensity
        gray_value = np.mean(result, axis=2, keepdims=True)
        result = result * (1 - gray_tint_strength) + gray_value * gray_tint_strength
        
        return TransformUtils.ensure_uint8(result)
    
    def get_transform_name(self) -> str:
        return "dirt_effect"


# 便利函数，用于快速创建和应用老化效果
def apply_aging_effects(image: Image.Image, wear_prob: float = 0.3, 
                       fade_prob: float = 0.3, dirt_prob: float = 0.2) -> Image.Image:
    """
    快速应用多种老化效果的便利函数
    
    Args:
        image (Image.Image): 输入图像
        wear_prob (float): 磨损效果概率
        fade_prob (float): 褪色效果概率  
        dirt_prob (float): 污渍效果概率
        
    Returns:
        Image.Image: 应用老化效果后的图像
    """
    result = image
    
    # 按顺序应用效果
    effects = [
        FadeEffect(probability=fade_prob),
        WearEffect(probability=wear_prob), 
        DirtEffect(probability=dirt_prob)
    ]
    
    for effect in effects:
        enhanced = effect(result)
        if enhanced is not None:
            result = enhanced
    
    return result