"""
透视和角度变换模块

实现各种透视变换效果，包括倾斜、透视、旋转等模拟不同拍摄角度的效果。
"""

import numpy as np
from PIL import Image
import cv2
from typing import Tuple, List
import random
import math

from .base_transform import BaseTransform, TransformUtils


class TiltTransform(BaseTransform):
    """
    倾斜变换效果
    
    模拟车牌的水平和垂直倾斜，如不正的安装角度或拍摄角度。
    
    Args:
        probability (float): 应用概率，默认0.4
        **kwargs: 其他参数
            max_angle (float): 最大倾斜角度（度），默认15
            horizontal_tilt (bool): 是否启用水平倾斜，默认True
            vertical_tilt (bool): 是否启用垂直倾斜，默认True
    """
    
    def __init__(self, probability: float = 0.4, **kwargs):
        """
        初始化倾斜变换
        
        Args:
            probability (float): 应用概率，默认0.4
            **kwargs: 其他参数
                max_angle (float): 最大倾斜角度（度），默认15
                horizontal_tilt (bool): 是否启用水平倾斜，默认True
                vertical_tilt (bool): 是否启用垂直倾斜，默认True
        """
        super().__init__(probability, **kwargs)
        self.max_angle = kwargs.get('max_angle', 15)
        self.horizontal_tilt = kwargs.get('horizontal_tilt', True)
        self.vertical_tilt = kwargs.get('vertical_tilt', True)
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用倾斜变换
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用倾斜变换后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        cv_image = TransformUtils.pil_to_cv2(image)
        height, width = cv_image.shape[:2]
        
        # 随机选择倾斜方向和角度
        tilt_angle = self._generate_tilt_angle(intensity)
        
        if abs(tilt_angle) < 1:  # 角度太小，不应用变换
            return image
        
        # 应用倾斜变换
        tilted_image = self._apply_tilt(cv_image, tilt_angle)
        
        return TransformUtils.cv2_to_pil(tilted_image)
    
    def _generate_tilt_angle(self, intensity: float) -> float:
        """
        生成倾斜角度
        
        Args:
            intensity (float): 效果强度
            
        Returns:
            float: 倾斜角度（度）
        """
        max_angle_adjusted = self.max_angle * intensity
        
        # 随机选择倾斜方向
        directions = []
        if self.horizontal_tilt:
            directions.extend(['left', 'right'])
        if self.vertical_tilt:
            directions.extend(['forward', 'backward'])
        
        if not directions:
            return 0.0
        
        direction = random.choice(directions)
        angle = random.uniform(2, max_angle_adjusted)
        
        # 根据方向调整角度符号
        if direction in ['left', 'backward']:
            angle = -angle
        
        return angle
    
    def _apply_tilt(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        应用倾斜变换
        
        Args:
            image (np.ndarray): 输入图像
            angle (float): 倾斜角度（度）
            
        Returns:
            np.ndarray: 倾斜后的图像
        """
        height, width = image.shape[:2]
        
        # 计算旋转中心
        center = (width // 2, height // 2)
        
        # 创建旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 计算新的边界框
        cos_val = abs(rotation_matrix[0, 0])
        sin_val = abs(rotation_matrix[0, 1])
        new_width = int((height * sin_val) + (width * cos_val))
        new_height = int((height * cos_val) + (width * sin_val))
        
        # 调整旋转中心到新图像中心
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]
        
        # 应用变换
        tilted = cv2.warpAffine(image, rotation_matrix, (new_width, new_height), 
                               borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
        
        # 如果新图像太大，需要裁剪回原始尺寸
        if new_width > width * 1.5 or new_height > height * 1.5:
            start_x = (new_width - width) // 2
            start_y = (new_height - height) // 2
            tilted = tilted[start_y:start_y+height, start_x:start_x+width]
        
        return tilted
    
    def get_transform_name(self) -> str:
        return "tilt_transform"


class PerspectiveTransform(BaseTransform):
    """
    透视变换效果
    
    模拟从不同视角观察车牌的透视效果。
    
    Args:
        probability (float): 应用概率，默认0.3
        **kwargs: 其他参数
            perspective_strength (float): 透视强度，默认0.2
            maintain_aspect (bool): 是否保持宽高比，默认True
    """
    
    def __init__(self, probability: float = 0.3, **kwargs):
        """
        初始化透视变换
        
        Args:
            probability (float): 应用概率，默认0.3
            **kwargs: 其他参数
                perspective_strength (float): 透视强度，默认0.2
                maintain_aspect (bool): 是否保持宽高比，默认True
        """
        super().__init__(probability, **kwargs)
        self.perspective_strength = kwargs.get('perspective_strength', 0.2)
        self.maintain_aspect = kwargs.get('maintain_aspect', True)
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用透视变换
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用透视变换后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        cv_image = TransformUtils.pil_to_cv2(image)
        height, width = cv_image.shape[:2]
        
        # 生成透视变换矩阵
        perspective_matrix = self._generate_perspective_matrix(width, height, intensity)
        
        # 应用透视变换
        transformed = cv2.warpPerspective(cv_image, perspective_matrix, (width, height),
                                        borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
        
        return TransformUtils.cv2_to_pil(transformed)
    
    def _generate_perspective_matrix(self, width: int, height: int, intensity: float) -> np.ndarray:
        """
        生成透视变换矩阵
        
        Args:
            width (int): 图像宽度
            height (int): 图像高度
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 透视变换矩阵
        """
        # 原始四个角点
        src_points = np.float32([
            [0, 0],           # 左上
            [width, 0],       # 右上
            [width, height],  # 右下
            [0, height]       # 左下
        ])
        
        # 计算透视变形量
        max_offset_x = width * 0.5 * self.perspective_strength * intensity
        max_offset_y = height * 0.5 * self.perspective_strength * intensity
        
        # 目标点初始化为原始点
        dst_points = src_points.copy()
        
        # 随机选择透视方向
        perspective_type = random.choice(['top', 'bottom', 'left', 'right'])
        
        if perspective_type == 'top':
            # 顶部收缩
            offset = random.uniform(max_offset_x * 0.2, max_offset_x)
            dst_points[0, 0] += offset
            dst_points[1, 0] -= offset
        elif perspective_type == 'bottom':
            # 底部收缩
            offset = random.uniform(max_offset_x * 0.2, max_offset_x)
            dst_points[3, 0] += offset
            dst_points[2, 0] -= offset
        elif perspective_type == 'left':
            # 左侧收缩
            offset = random.uniform(max_offset_y * 0.2, max_offset_y)
            dst_points[0, 1] += offset
            dst_points[3, 1] -= offset
        elif perspective_type == 'right':
            # 右侧收缩
            offset = random.uniform(max_offset_y * 0.2, max_offset_y)
            dst_points[1, 1] += offset
            dst_points[2, 1] -= offset
            
        # 验证点是否有效（防止共线等问题）
        try:
            # 计算透视变换矩阵
            perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
            
            # 验证矩阵是否有效
            if np.any(np.isnan(perspective_matrix)) or np.any(np.isinf(perspective_matrix)):
                raise ValueError("无效的变换矩阵")
                
        except (cv2.error, ValueError):
            # 如果生成失败，使用身份矩阵（无变换）
            perspective_matrix = np.eye(3, dtype=np.float32)
        
        return perspective_matrix
    
    def get_transform_name(self) -> str:
        return "perspective_transform"


class RotationTransform(BaseTransform):
    """
    旋转变换效果
    
    模拟车牌的小角度旋转。
    
    Args:
        probability (float): 应用概率，默认0.2
        **kwargs: 其他参数
            max_rotation (float): 最大旋转角度（度），默认10
    """
    
    def __init__(self, probability: float = 0.2, **kwargs):
        """
        初始化旋转变换
        
        Args:
            probability (float): 应用概率，默认0.2
            **kwargs: 其他参数
                max_rotation (float): 最大旋转角度（度），默认10
        """
        super().__init__(probability, **kwargs)
        self.max_rotation = kwargs.get('max_rotation', 10)
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用旋转变换
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用旋转变换后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        # 生成随机旋转角度
        angle = random.uniform(-self.max_rotation * intensity, self.max_rotation * intensity)
        
        if abs(angle) < 0.5:  # 角度太小，不应用变换
            return image
        
        # 使用PIL进行旋转（保持图像尺寸），并使用双三次插值以减少锯齿
        rotated = image.rotate(angle, resample=Image.BICUBIC, fillcolor='white', expand=False)
        
        return rotated
    
    def get_transform_name(self) -> str:
        return "rotation_transform"


class GeometricDistortion(BaseTransform):
    """
    几何扭曲效果
    
    模拟车牌表面不平或拍摄设备造成的几何扭曲。
    
    Args:
        probability (float): 应用概率，默认0.15
        **kwargs: 其他参数
            distortion_strength (float): 扭曲强度，默认0.1
            grid_size (int): 网格大小，默认4
    """
    
    def __init__(self, probability: float = 0.15, **kwargs):
        """
        初始化几何扭曲
        
        Args:
            probability (float): 应用概率，默认0.15
            **kwargs: 其他参数
                distortion_strength (float): 扭曲强度，默认0.1
                grid_size (int): 网格大小，默认4
        """
        super().__init__(probability, **kwargs)
        self.distortion_strength = kwargs.get('distortion_strength', 0.1)
        self.grid_size = kwargs.get('grid_size', 4)
    
    def apply(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        应用几何扭曲
        
        Args:
            image (Image.Image): 输入图像
            **kwargs: 运行时参数
                intensity (float): 效果强度
                
        Returns:
            Image.Image: 应用几何扭曲后的图像
        """
        intensity = kwargs.get('intensity', 1.0)
        
        cv_image = TransformUtils.pil_to_cv2(image)
        height, width = cv_image.shape[:2]
        
        # 生成扭曲网格
        distorted_image = self._apply_grid_distortion(cv_image, intensity)
        
        return TransformUtils.cv2_to_pil(distorted_image)
    
    def _apply_grid_distortion(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """
        应用网格扭曲
        
        Args:
            image (np.ndarray): 输入图像
            intensity (float): 效果强度
            
        Returns:
            np.ndarray: 扭曲后的图像
        """
        height, width = image.shape[:2]
        
        # 创建规则网格
        grid_x = np.linspace(0, width, self.grid_size + 1)
        grid_y = np.linspace(0, height, self.grid_size + 1)
        
        # 创建扭曲后的网格
        distorted_grid_x = grid_x.copy()
        distorted_grid_y = grid_y.copy()
        
        # 添加随机扭曲
        max_distortion = min(width, height) * self.distortion_strength * intensity
        
        for i in range(1, len(grid_x) - 1):  # 不扭曲边界点
            distorted_grid_x[i] += random.uniform(-max_distortion, max_distortion)
        
        for i in range(1, len(grid_y) - 1):  # 不扭曲边界点
            distorted_grid_y[i] += random.uniform(-max_distortion, max_distortion)
        
        # 确保网格点在图像范围内
        distorted_grid_x = np.clip(distorted_grid_x, 0, width)
        distorted_grid_y = np.clip(distorted_grid_y, 0, height)
        
        # 创建映射网格
        map_x = np.zeros((height, width), dtype=np.float32)
        map_y = np.zeros((height, width), dtype=np.float32)
        
        # 插值生成完整的映射
        for y in range(height):
            for x in range(width):
                # 找到在哪个网格单元中
                grid_x_idx = min(int(x * self.grid_size / width), self.grid_size - 1)
                grid_y_idx = min(int(y * self.grid_size / height), self.grid_size - 1)
                
                # 在网格单元内的相对位置
                local_x = (x * self.grid_size / width) - grid_x_idx
                local_y = (y * self.grid_size / height) - grid_y_idx
                
                # 双线性插值
                x1 = distorted_grid_x[grid_x_idx] + local_x * (distorted_grid_x[grid_x_idx + 1] - distorted_grid_x[grid_x_idx])
                y1 = distorted_grid_y[grid_y_idx] + local_y * (distorted_grid_y[grid_y_idx + 1] - distorted_grid_y[grid_y_idx])
                
                map_x[y, x] = x1
                map_y[y, x] = y1
        
        # 应用重映射
        distorted = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR, 
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
        
        return distorted
    
    def get_transform_name(self) -> str:
        return "geometric_distortion"


# 便利函数，用于快速应用透视变换效果
def apply_perspective_effects(image: Image.Image, tilt_prob: float = 0.4,
                            perspective_prob: float = 0.3, rotation_prob: float = 0.2,
                            distortion_prob: float = 0.15) -> Image.Image:
    """
    快速应用多种透视变换效果的便利函数
    
    Args:
        image (Image.Image): 输入图像
        tilt_prob (float): 倾斜变换概率
        perspective_prob (float): 透视变换概率
        rotation_prob (float): 旋转变换概率
        distortion_prob (float): 几何扭曲概率
        
    Returns:
        Image.Image: 应用透视变换后的图像
    """
    result = image
    
    # 按顺序应用效果（只应用一种主要的几何变换）
    effects = [
        (TiltTransform(probability=tilt_prob), 1.0),
        (PerspectiveTransform(probability=perspective_prob), 0.8),
        (RotationTransform(probability=rotation_prob), 0.6),
        (GeometricDistortion(probability=distortion_prob), 0.4)
    ]
    
    # 随机选择一种主要效果应用
    if random.random() < 0.7:  # 70%概率应用某种几何变换
        effect, weight = random.choices(effects, weights=[e[1] for e in effects])[0]
        enhanced = effect(result)
        if enhanced is not None:
            result = enhanced
    
    return result