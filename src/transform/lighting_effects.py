"""
光照条件模拟模块

实现各种光照效果，包括阴影、反光、夜间、背光等真实的光照条件模拟。
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2
from typing import Tuple, Union
import random
import math

from .base_transform import BaseTransform, TransformUtils


class ShadowEffect(BaseTransform):
    """
    阴影效果
    
    模拟各种阴影情况，包括投影、遮挡阴影等。
    
    Args:
        probability (float): 应用概率，默认0.3
        **kwargs: 其他参数
            shadow_strength (float): 阴影强度，默认0.4
            shadow_blur (int): 阴影模糊程度，默认5
            shadow_offset (tuple): 阴影偏移，默认(3, 3)
    """
    
    def __init__(self, probability: float = 0.3, **kwargs):
        """
        初始化阴影效果
        
        Args:
            probability (float): 应用概率，默认0.3
            **kwargs: 其他参数
                shadow_strength (float): 阴影强度，默认0.4
                shadow_blur (int): 阴影模糊程度，默认5
                shadow_offset (tuple): 阴影偏移，默认(3, 3)
        """
        super().__init__(probability, **kwargs)
        self.shadow_strength = kwargs.get('shadow_strength', 0.4)
        self.shadow_blur = kwargs.get('shadow_blur', 5)
        self.shadow_offset = kwargs.get('shadow_offset', (3, 3))
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用阴影效果
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用阴影效果后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        # 随机选择阴影类型
        shadow_type = random.choice(['directional', 'partial', 'object_shadow'])
        
        if shadow_type == 'directional':
            return self._apply_directional_shadow(image, intensity)
        elif shadow_type == 'partial':
            return self._apply_partial_shadow(image, intensity)
        else:  # object_shadow
            return self._apply_object_shadow(image, intensity)
    
    def _apply_directional_shadow(self, image: Image.Image, intensity: float) -> Image.Image:
        """
        应用方向性阴影（如建筑物或树木的阴影）
        
        Args:
            image (Image.Image): 输入图像
            intensity (float): 效果强度
            
        Returns:
            Image.Image: 应用方向性阴影后的图像
        """
        cv_image = TransformUtils.pil_to_cv2(image)
        height, width = cv_image.shape[:2]
        
        # 创建阴影mask
        shadow_mask = np.zeros((height, width), dtype=np.float32)
        
        # 随机选择阴影方向
        shadow_direction = random.choice(['top', 'bottom', 'left', 'right', 'diagonal'])
        
        if shadow_direction == 'top':
            # 从上方的阴影
            shadow_height = int(height * random.uniform(0.3, 0.7) * intensity)
            gradient = np.linspace(1, 0, shadow_height)
            shadow_mask[:shadow_height, :] = gradient[:, np.newaxis]
        elif shadow_direction == 'bottom':
            # 从下方的阴影
            shadow_height = int(height * random.uniform(0.3, 0.7) * intensity)
            gradient = np.linspace(0, 1, shadow_height)
            shadow_mask[-shadow_height:, :] = gradient[:, np.newaxis]
        elif shadow_direction == 'left':
            # 从左侧的阴影
            shadow_width = int(width * random.uniform(0.3, 0.7) * intensity)
            gradient = np.linspace(1, 0, shadow_width)
            shadow_mask[:, :shadow_width] = gradient[np.newaxis, :]
        elif shadow_direction == 'right':
            # 从右侧的阴影
            shadow_width = int(width * random.uniform(0.3, 0.7) * intensity)
            gradient = np.linspace(0, 1, shadow_width)
            shadow_mask[:, -shadow_width:] = gradient[np.newaxis, :]
        else:  # diagonal
            # 对角阴影
            for y in range(height):
                for x in range(width):
                    distance = np.sqrt((x - width*0.2)**2 + (y - height*0.2)**2)
                    max_distance = np.sqrt(width**2 + height**2) * 0.8
                    shadow_mask[y, x] = min(1.0, distance / max_distance)
        
        # 平滑阴影边缘
        shadow_mask = cv2.GaussianBlur(shadow_mask, (self.shadow_blur*2+1, self.shadow_blur*2+1), 0)
        
        # 应用阴影
        shadow_strength = self.shadow_strength * intensity
        shadow_3d = np.stack([shadow_mask] * 3, axis=-1) * shadow_strength
        
        result = cv_image.astype(np.float32)
        result = result * (1 - shadow_3d)
        
        return TransformUtils.cv2_to_pil(TransformUtils.ensure_uint8(result))
    
    def _apply_partial_shadow(self, image: Image.Image, intensity: float) -> Image.Image:
        """
        应用局部阴影
        
        Args:
            image (Image.Image): 输入图像
            intensity (float): 效果强度
            
        Returns:
            Image.Image: 应用局部阴影后的图像
        """
        cv_image = TransformUtils.pil_to_cv2(image)
        height, width = cv_image.shape[:2]
        
        # 创建不规则阴影区域
        shadow_mask = np.zeros((height, width), dtype=np.float32)
        
        # 添加几个随机阴影区域
        num_shadows = random.randint(1, 3)
        
        for _ in range(num_shadows):
            # 随机阴影中心和大小
            center_x = random.randint(0, width)
            center_y = random.randint(0, height)
            shadow_radius = random.randint(min(width, height)//6, min(width, height)//3)
            
            # 创建椭圆形阴影
            axes = (shadow_radius, random.randint(shadow_radius//2, shadow_radius))
            angle = random.randint(0, 180)
            
            # 创建临时mask
            temp_mask = np.zeros((height, width), dtype=np.uint8)
            cv2.ellipse(temp_mask, (center_x, center_y), axes, angle, 0, 360, 255, -1)
            
            # 转换为浮点数并归一化
            temp_mask_float = temp_mask.astype(np.float32) / 255.0
            
            # 添加到主阴影mask
            shadow_mask = np.maximum(shadow_mask, temp_mask_float * random.uniform(0.3, 0.8))
        
        # 平滑阴影边缘
        shadow_mask = cv2.GaussianBlur(shadow_mask, (self.shadow_blur*2+1, self.shadow_blur*2+1), 0)
        
        # 应用阴影
        shadow_strength = self.shadow_strength * intensity
        shadow_3d = np.stack([shadow_mask] * 3, axis=-1) * shadow_strength
        
        result = cv_image.astype(np.float32)
        result = result * (1 - shadow_3d)
        
        return TransformUtils.cv2_to_pil(TransformUtils.ensure_uint8(result))
    
    def _apply_object_shadow(self, image: Image.Image, intensity: float) -> Image.Image:
        """
        应用物体投影
        
        Args:
            image (Image.Image): 输入图像
            intensity (float): 效果强度
            
        Returns:
            Image.Image: 应用物体投影后的图像
        """
        cv_image = TransformUtils.pil_to_cv2(image)
        height, width = cv_image.shape[:2]
        
        # 创建模拟投影的形状
        shadow_mask = np.zeros((height, width), dtype=np.float32)
        
        # 随机选择投影类型
        shadow_shapes = ['bar', 'leaf', 'irregular']
        shadow_type = random.choice(shadow_shapes)
        
        if shadow_type == 'bar':
            # 栏杆或管道的投影
            num_bars = random.randint(2, 5)
            bar_width = random.randint(3, 8)
            
            for i in range(num_bars):
                x_pos = random.randint(0, width - bar_width)
                shadow_mask[:, x_pos:x_pos+bar_width] = random.uniform(0.4, 0.8)
        
        elif shadow_type == 'leaf':
            # 树叶或植物的投影
            num_leaves = random.randint(3, 8)
            
            for _ in range(num_leaves):
                center_x = random.randint(0, width)
                center_y = random.randint(0, height)
                leaf_size = random.randint(10, 30)
                
                # 创建叶子形状的近似
                cv2.ellipse(shadow_mask, (center_x, center_y), 
                           (leaf_size, leaf_size//2), random.randint(0, 180),
                           0, 360, random.uniform(0.3, 0.7), -1)
        
        else:  # irregular
            # 不规则投影
            num_points = random.randint(4, 8)
            points = []
            
            for _ in range(num_points):
                x = random.randint(0, width)
                y = random.randint(0, height)
                points.append([x, y])
            
            points = np.array(points, dtype=np.int32)
            cv2.fillPoly(shadow_mask, [points], random.uniform(0.3, 0.7))
        
        # 平滑投影边缘
        shadow_mask = cv2.GaussianBlur(shadow_mask, (self.shadow_blur*2+1, self.shadow_blur*2+1), 0)
        
        # 应用投影
        shadow_strength = self.shadow_strength * intensity
        shadow_3d = np.stack([shadow_mask] * 3, axis=-1) * shadow_strength
        
        result = cv_image.astype(np.float32)
        result = result * (1 - shadow_3d)
        
        return TransformUtils.cv2_to_pil(TransformUtils.ensure_uint8(result))
    
    def get_transform_name(self) -> str:
        return "shadow_effect"


class ReflectionEffect(BaseTransform):
    """
    反光效果
    
    模拟车牌表面的镜面反射和局部高光。
    
    Args:
        probability (float): 应用概率，默认0.2
        **kwargs: 其他参数
            reflection_strength (float): 反光强度，默认0.3
            reflection_size (float): 反光区域大小比例，默认0.3
    """
    
    def __init__(self, probability: float = 0.2, **kwargs):
        """
        初始化反光效果
        
        Args:
            probability (float): 应用概率，默认0.2
            **kwargs: 其他参数
                reflection_strength (float): 反光强度，默认0.3
                reflection_size (float): 反光区域大小比例，默认0.3
        """
        super().__init__(probability, **kwargs)
        self.reflection_strength = kwargs.get('reflection_strength', 0.3)
        self.reflection_size = kwargs.get('reflection_size', 0.3)
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用反光效果
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用反光效果后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        # 随机选择反光类型
        reflection_type = random.choice(['spot_light', 'gradient_light', 'multiple_spots'])
        
        if reflection_type == 'spot_light':
            return self._apply_spot_reflection(image, intensity)
        elif reflection_type == 'gradient_light':
            return self._apply_gradient_reflection(image, intensity)
        else:  # multiple_spots
            return self._apply_multiple_reflections(image, intensity)
    
    def _apply_spot_reflection(self, image: Image.Image, intensity: float) -> Image.Image:
        """
        应用单点反光
        
        Args:
            image (Image.Image): 输入图像
            intensity (float): 效果强度
            
        Returns:
            Image.Image: 应用单点反光后的图像
        """
        cv_image = TransformUtils.pil_to_cv2(image)
        height, width = cv_image.shape[:2]
        
        # 创建反光mask
        reflection_mask = np.zeros((height, width), dtype=np.float32)
        
        # 随机反光位置和大小
        center_x = random.randint(int(width * 0.2), int(width * 0.8))
        center_y = random.randint(int(height * 0.2), int(height * 0.8))
        reflection_radius = int(min(width, height) * self.reflection_size * intensity)
        
        # 创建高斯光斑
        for y in range(height):
            for x in range(width):
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                if distance < reflection_radius:
                    reflection_mask[y, x] = np.exp(-(distance**2) / (2 * (reflection_radius/3)**2))
        
        # 应用反光
        reflection_strength = self.reflection_strength * intensity
        reflection_3d = np.stack([reflection_mask] * 3, axis=-1) * reflection_strength
        
        result = cv_image.astype(np.float32)
        result = result + reflection_3d * 255
        
        return TransformUtils.cv2_to_pil(TransformUtils.ensure_uint8(result))
    
    def _apply_gradient_reflection(self, image: Image.Image, intensity: float) -> Image.Image:
        """
        应用渐变反光
        
        Args:
            image (Image.Image): 输入图像
            intensity (float): 效果强度
            
        Returns:
            Image.Image: 应用渐变反光后的图像
        """
        cv_image = TransformUtils.pil_to_cv2(image)
        height, width = cv_image.shape[:2]
        
        # 创建渐变反光mask
        reflection_mask = np.zeros((height, width), dtype=np.float32)
        
        # 随机选择渐变方向
        direction = random.choice(['horizontal', 'vertical', 'diagonal'])
        
        if direction == 'horizontal':
            for x in range(width):
                intensity_val = abs(np.sin(x * np.pi / width)) * intensity
                reflection_mask[:, x] = intensity_val
        elif direction == 'vertical':
            for y in range(height):
                intensity_val = abs(np.sin(y * np.pi / height)) * intensity
                reflection_mask[y, :] = intensity_val
        else:  # diagonal
            for y in range(height):
                for x in range(width):
                    diagonal_pos = (x + y) / (width + height)
                    intensity_val = abs(np.sin(diagonal_pos * np.pi * 2)) * intensity
                    reflection_mask[y, x] = intensity_val
        
        # 平滑渐变
        reflection_mask = cv2.GaussianBlur(reflection_mask, (15, 15), 5)
        
        # 应用反光
        reflection_strength = self.reflection_strength * 0.5  # 渐变反光强度稍低
        reflection_3d = np.stack([reflection_mask] * 3, axis=-1) * reflection_strength
        
        result = cv_image.astype(np.float32)
        result = result + reflection_3d * 255
        
        return TransformUtils.cv2_to_pil(TransformUtils.ensure_uint8(result))
    
    def _apply_multiple_reflections(self, image: Image.Image, intensity: float) -> Image.Image:
        """
        应用多点反光
        
        Args:
            image (Image.Image): 输入图像
            intensity (float): 效果强度
            
        Returns:
            Image.Image: 应用多点反光后的图像
        """
        cv_image = TransformUtils.pil_to_cv2(image)
        height, width = cv_image.shape[:2]
        
        # 创建反光mask
        reflection_mask = np.zeros((height, width), dtype=np.float32)
        
        # 添加多个小反光点
        num_reflections = random.randint(2, 5)
        
        for _ in range(num_reflections):
            center_x = random.randint(0, width)
            center_y = random.randint(0, height)
            reflection_radius = random.randint(5, 20)
            
            # 创建小光斑
            cv2.circle(reflection_mask, (center_x, center_y), reflection_radius,
                      random.uniform(0.3, 0.8) * intensity, -1)
        
        # 平滑反光边缘
        reflection_mask = cv2.GaussianBlur(reflection_mask, (7, 7), 2)
        
        # 应用反光
        reflection_strength = self.reflection_strength * intensity
        reflection_3d = np.stack([reflection_mask] * 3, axis=-1) * reflection_strength
        
        result = cv_image.astype(np.float32)
        result = result + reflection_3d * 255
        
        return TransformUtils.cv2_to_pil(TransformUtils.ensure_uint8(result))
    
    def get_transform_name(self) -> str:
        return "reflection_effect"


class NightEffect(BaseTransform):
    """
    夜间效果
    
    模拟夜间或低光照条件下的图像效果。
    
    Args:
        probability (float): 应用概率，默认0.2
        **kwargs: 其他参数
            darkness_factor (float): 暗度因子，默认0.6
            color_temperature (str): 色温，默认"warm"
    """
    
    def __init__(self, probability: float = 0.2, **kwargs):
        """
        初始化夜间效果
        
        Args:
            probability (float): 应用概率，默认0.2
            **kwargs: 其他参数
                darkness_factor (float): 暗度因子，默认0.6
                color_temperature (str): 色温，默认"warm"
        """
        super().__init__(probability, **kwargs)
        self.darkness_factor = kwargs.get('darkness_factor', 0.6)
        self.color_temperature = kwargs.get('color_temperature', 'warm')
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用夜间效果
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用夜间效果后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        # 降低整体亮度
        enhancer_brightness = ImageEnhance.Brightness(image)
        darkened = enhancer_brightness.enhance(self.darkness_factor + (1 - self.darkness_factor) * (1 - intensity))
        
        # 调整色温
        color_adjusted = self._adjust_color_temperature(darkened, intensity)
        
        # 添加噪声（模拟低光噪点）
        noisy = self._add_low_light_noise(color_adjusted, intensity)
        
        # 轻微模糊（模拟低光条件下的清晰度下降）
        if intensity > 0.5:
            noisy = noisy.filter(ImageFilter.GaussianBlur(radius=0.5 * intensity))
        
        return noisy
    
    def _adjust_color_temperature(self, image: Image.Image, intensity: float) -> Image.Image:
        """
        调整色温
        
        Args:
            image (Image.Image): 输入图像
            intensity (float): 效果强度
            
        Returns:
            Image.Image: 调整色温后的图像
        """
        image_array = np.array(image).astype(np.float32)
        
        if self.color_temperature == 'warm':
            # 暖色调（偏黄橙）
            image_array[:, :, 0] *= (1 + 0.1 * intensity)  # 增加红色
            image_array[:, :, 1] *= (1 + 0.05 * intensity)  # 轻微增加绿色
            image_array[:, :, 2] *= (1 - 0.1 * intensity)  # 减少蓝色
        elif self.color_temperature == 'cool':
            # 冷色调（偏蓝）
            image_array[:, :, 0] *= (1 - 0.05 * intensity)  # 减少红色
            image_array[:, :, 1] *= (1 - 0.02 * intensity)  # 轻微减少绿色
            image_array[:, :, 2] *= (1 + 0.1 * intensity)  # 增加蓝色
        
        return Image.fromarray(TransformUtils.ensure_uint8(image_array))
    
    def _add_low_light_noise(self, image: Image.Image, intensity: float) -> Image.Image:
        """
        添加低光噪声
        
        Args:
            image (Image.Image): 输入图像
            intensity (float): 效果强度
            
        Returns:
            Image.Image: 添加噪声后的图像
        """
        image_array = np.array(image).astype(np.float32)
        
        # 添加高斯噪声
        noise_strength = 10 * intensity
        noise = np.random.normal(0, noise_strength, image_array.shape)
        
        noisy_array = image_array + noise
        
        return Image.fromarray(TransformUtils.ensure_uint8(noisy_array))
    
    def get_transform_name(self) -> str:
        return "night_effect"


class BacklightEffect(BaseTransform):
    """
    背光效果
    
    模拟逆光或背光条件下的图像效果。
    
    Args:
        probability (float): 应用概率，默认0.2
        **kwargs: 其他参数
            backlight_strength (float): 背光强度，默认0.4
            edge_enhancement (bool): 是否增强边缘，默认True
    """
    
    def __init__(self, probability: float = 0.2, **kwargs):
        """
        初始化背光效果
        
        Args:
            probability (float): 应用概率，默认0.2
            **kwargs: 其他参数
                backlight_strength (float): 背光强度，默认0.4
                edge_enhancement (bool): 是否增强边缘，默认True
        """
        super().__init__(probability, **kwargs)
        self.backlight_strength = kwargs.get('backlight_strength', 0.4)
        self.edge_enhancement = kwargs.get('edge_enhancement', True)
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用背光效果
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用背光效果后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        cv_image = TransformUtils.pil_to_cv2(image)
        
        # 创建背光效果
        backlit_image = self._create_backlight_gradient(cv_image, intensity)
        
        # 增强边缘（如果启用）
        if self.edge_enhancement:
            backlit_image = self._enhance_edges(backlit_image, intensity)
        
        # 调整对比度
        backlit_image = self._adjust_backlight_contrast(backlit_image, intensity)
        
        return TransformUtils.cv2_to_pil(backlit_image)
    
    def _create_backlight_gradient(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """
        创建背光渐变效果
        
        Args:
            image (np.ndarray): 输入图像
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 背光渐变后的图像
        """
        height, width = image.shape[:2]
        
        # 创建背光渐变mask
        gradient_mask = np.zeros((height, width), dtype=np.float32)
        
        # 随机选择背光方向
        light_direction = random.choice(['top', 'bottom', 'left', 'right'])
        
        if light_direction == 'top':
            for y in range(height):
                gradient_mask[y, :] = (height - y) / height
        elif light_direction == 'bottom':
            for y in range(height):
                gradient_mask[y, :] = y / height
        elif light_direction == 'left':
            for x in range(width):
                gradient_mask[:, x] = (width - x) / width
        else:  # right
            for x in range(width):
                gradient_mask[:, x] = x / width
        
        # 应用非线性变换使渐变更自然
        gradient_mask = np.power(gradient_mask, 0.7)
        
        # 调整背光强度
        backlight_strength = self.backlight_strength * intensity
        gradient_3d = np.stack([gradient_mask] * 3, axis=-1) * backlight_strength
        
        # 混合原图和背光效果
        result = image.astype(np.float32)
        result = result + gradient_3d * 255
        
        return TransformUtils.ensure_uint8(result)
    
    def _enhance_edges(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """
        增强边缘轮廓
        
        Args:
            image (np.ndarray): 输入图像
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 增强边缘后的图像
        """
        # 转换为灰度图检测边缘
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用Canny边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 扩展边缘
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # 创建边缘增强mask
        edge_mask = edges.astype(np.float32) / 255.0
        edge_mask_3d = np.stack([edge_mask] * 3, axis=-1)
        
        # 应用边缘增强
        enhancement_strength = 30 * intensity
        result = image.astype(np.float32)
        result = result + edge_mask_3d * enhancement_strength
        
        return TransformUtils.ensure_uint8(result)
    
    def _adjust_backlight_contrast(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """
        调整背光条件下的对比度
        
        Args:
            image (np.ndarray): 输入图像
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 调整对比度后的图像
        """
        # 轻微降低对比度，模拟背光条件下的视觉效果
        contrast_factor = 1 - 0.2 * intensity
        mean_val = np.mean(image)
        
        result = image.astype(np.float32)
        result = (result - mean_val) * contrast_factor + mean_val
        
        return TransformUtils.ensure_uint8(result)
    
    def get_transform_name(self) -> str:
        return "backlight_effect"


# 便利函数，用于快速应用光照效果
def apply_lighting_effects(image: Image.Image, shadow_prob: float = 0.3,
                          reflection_prob: float = 0.2, night_prob: float = 0.2,
                          backlight_prob: float = 0.2) -> Image.Image:
    """
    快速应用多种光照效果的便利函数
    
    Args:
        image (Image.Image): 输入图像
        shadow_prob (float): 阴影效果概率
        reflection_prob (float): 反光效果概率
        night_prob (float): 夜间效果概率
        backlight_prob (float): 背光效果概率
        
    Returns:
        Image.Image: 应用光照效果后的图像
    """
    result = image
    
    # 按顺序应用效果
    effects = [
        NightEffect(probability=night_prob),
        ShadowEffect(probability=shadow_prob),
        BacklightEffect(probability=backlight_prob),
        ReflectionEffect(probability=reflection_prob)
    ]
    
    for effect in effects:
        enhanced = effect(result)
        if enhanced is not None:
            result = enhanced
    
    return result