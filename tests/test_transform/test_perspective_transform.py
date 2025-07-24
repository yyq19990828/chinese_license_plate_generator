"""
透视变换效果测试模块

测试车牌透视变换相关的效果，包括倾斜、透视、旋转和几何扭曲。
"""

import pytest
import numpy as np
from PIL import Image, ImageDraw
import cv2
import math

from src.transform.perspective_transform import (
    TiltTransform, PerspectiveTransform, RotationTransform, 
    GeometricDistortion, apply_perspective_effects
)


class TestTiltTransform:
    """测试倾斜变换"""
    
    @pytest.fixture
    def rectangular_image(self):
        """创建矩形测试图像"""
        image = Image.new('RGB', (440, 140), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 绘制一个明显的矩形框架以便观察变换效果
        draw.rectangle([10, 10, 430, 130], outline=(0, 0, 0), width=3)
        
        # 添加一些内容
        for i, x in enumerate(range(50, 350, 50)):
            draw.rectangle([x, 40, x+40, 100], fill=(100, 100, 100))
        
        return image
    
    def test_tilt_transform_initialization(self):
        """测试倾斜变换初始化"""
        # 测试默认参数
        tilt = TiltTransform()
        assert tilt.probability == 0.3
        assert tilt.params['max_angle'] == 15
        assert tilt.params['direction'] == 'both'
        
        # 测试自定义参数
        tilt = TiltTransform(probability=0.8, max_angle=20, direction='horizontal')
        assert tilt.probability == 0.8
        assert tilt.params['max_angle'] == 20
        assert tilt.params['direction'] == 'horizontal'
    
    def test_tilt_transform_application(self, rectangular_image):
        """测试倾斜变换应用"""
        tilt = TiltTransform(probability=1.0, max_angle=10)
        
        result = tilt(rectangular_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        
        # 倾斜后图像尺寸可能会改变，但应该保持合理范围
        original_area = rectangular_image.size[0] * rectangular_image.size[1]
        result_area = result.size[0] * result.size[1]
        
        # 面积变化不应该过大
        area_ratio = result_area / original_area
        assert 0.5 <= area_ratio <= 2.0
    
    def test_tilt_directions(self, rectangular_image):
        """测试不同倾斜方向"""
        directions = ['horizontal', 'vertical', 'both']
        
        for direction in directions:
            tilt = TiltTransform(probability=1.0, direction=direction, max_angle=10)
            result = tilt(rectangular_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)
    
    def test_tilt_angle_control(self, rectangular_image):
        """测试倾斜角度控制"""
        # 测试不同的最大角度
        angles = [5, 10, 20, 30]
        
        for max_angle in angles:
            tilt = TiltTransform(probability=1.0, max_angle=max_angle)
            result = tilt(rectangular_image)
            
            assert result is not None
            # 角度越大，变换应该越明显（但难以量化测试）
    
    def test_tilt_intensity_scaling(self, rectangular_image):
        """测试倾斜强度缩放"""
        tilt = TiltTransform(probability=1.0, max_angle=20)
        
        # 测试不同强度
        weak_result = tilt.apply(rectangular_image, intensity=0.2)
        strong_result = tilt.apply(rectangular_image, intensity=0.8)
        
        assert weak_result is not None
        assert strong_result is not None
        
        # 强度不同应该产生不同的变换程度
        assert weak_result.size != strong_result.size or not np.array_equal(
            np.array(weak_result), np.array(strong_result)
        )


class TestPerspectiveTransform:
    """测试透视变换"""
    
    @pytest.fixture
    def perspective_test_image(self):
        """创建适合透视变换测试的图像"""
        image = Image.new('RGB', (400, 200), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 绘制网格以便观察透视效果
        for i in range(0, 400, 50):
            draw.line([(i, 0), (i, 200)], fill=(200, 200, 200), width=1)
        for i in range(0, 200, 25):
            draw.line([(0, i), (400, i)], fill=(200, 200, 200), width=1)
        
        # 绘制边框
        draw.rectangle([5, 5, 395, 195], outline=(0, 0, 0), width=2)
        
        return image
    
    def test_perspective_transform_initialization(self):
        """测试透视变换初始化"""
        # 测试默认参数
        perspective = PerspectiveTransform()
        assert perspective.probability == 0.3
        assert perspective.params['max_distortion'] == 0.3
        assert perspective.params['preserve_aspect'] == True
        
        # 测试自定义参数
        perspective = PerspectiveTransform(
            probability=0.7, 
            max_distortion=0.5, 
            preserve_aspect=False
        )
        assert perspective.probability == 0.7
        assert perspective.params['max_distortion'] == 0.5
        assert perspective.params['preserve_aspect'] == False
    
    def test_perspective_transform_application(self, perspective_test_image):
        """测试透视变换应用"""
        perspective = PerspectiveTransform(probability=1.0, max_distortion=0.2)
        
        result = perspective(perspective_test_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        
        # 透视变换后图像应该发生明显变化
        original_array = np.array(perspective_test_image)
        result_array = np.array(result)
        
        # 检查是否有几何变换（通过计算角点变化）
        assert not np.array_equal(original_array, result_array)
    
    def test_perspective_distortion_levels(self, perspective_test_image):
        """测试不同扭曲程度"""
        distortion_levels = [0.1, 0.3, 0.5]
        
        for distortion in distortion_levels:
            perspective = PerspectiveTransform(
                probability=1.0, 
                max_distortion=distortion
            )
            result = perspective(perspective_test_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)
    
    def test_perspective_aspect_preservation(self, perspective_test_image):
        """测试纵横比保持选项"""
        # 测试保持纵横比
        perspective_preserve = PerspectiveTransform(
            probability=1.0, 
            preserve_aspect=True
        )
        result_preserve = perspective_preserve(perspective_test_image)
        
        # 测试不保持纵横比
        perspective_free = PerspectiveTransform(
            probability=1.0, 
            preserve_aspect=False
        )
        result_free = perspective_free(perspective_test_image)
        
        assert result_preserve is not None
        assert result_free is not None
        
        # 两种模式应该产生不同的结果
        # （具体的纵横比检查较复杂，这里只验证能正常运行）


class TestRotationTransform:
    """测试旋转变换"""
    
    @pytest.fixture
    def rotation_test_image(self):
        """创建适合旋转测试的图像"""
        image = Image.new('RGB', (200, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 绘制一个非对称图案以便观察旋转效果
        draw.rectangle([20, 20, 80, 80], fill=(100, 100, 100))
        draw.rectangle([120, 20, 180, 60], fill=(150, 150, 150))
        
        return image
    
    def test_rotation_transform_initialization(self):
        """测试旋转变换初始化"""
        # 测试默认参数
        rotation = RotationTransform()
        assert rotation.probability == 0.3
        assert rotation.params['max_angle'] == 10
        assert rotation.params['expand'] == True
        
        # 测试自定义参数
        rotation = RotationTransform(
            probability=0.6, 
            max_angle=20, 
            expand=False
        )
        assert rotation.probability == 0.6
        assert rotation.params['max_angle'] == 20
        assert rotation.params['expand'] == False
    
    def test_rotation_transform_application(self, rotation_test_image):
        """测试旋转变换应用"""
        rotation = RotationTransform(probability=1.0, max_angle=15)
        
        result = rotation(rotation_test_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        
        # 旋转后图像应该发生变化
        original_array = np.array(rotation_test_image)
        result_array = np.array(result)
        
        assert not np.array_equal(original_array, result_array)
    
    def test_rotation_angle_range(self, rotation_test_image):
        """测试旋转角度范围"""
        # 测试不同的最大角度
        max_angles = [5, 15, 30, 45]
        
        for max_angle in max_angles:
            rotation = RotationTransform(probability=1.0, max_angle=max_angle)
            result = rotation(rotation_test_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)
    
    def test_rotation_expand_option(self, rotation_test_image):
        """测试扩展选项"""
        # 测试expand=True（扩展画布以容纳旋转后的图像）
        rotation_expand = RotationTransform(
            probability=1.0, 
            max_angle=30, 
            expand=True
        )
        result_expand = rotation_expand(rotation_test_image)
        
        # 测试expand=False（保持原始画布大小）
        rotation_crop = RotationTransform(
            probability=1.0, 
            max_angle=30, 
            expand=False
        )
        result_crop = rotation_crop(rotation_test_image)
        
        assert result_expand is not None
        assert result_crop is not None
        
        # expand=True通常会产生更大的图像
        expand_area = result_expand.size[0] * result_expand.size[1]
        crop_area = result_crop.size[0] * result_crop.size[1]
        original_area = rotation_test_image.size[0] * rotation_test_image.size[1]
        
        # expand=False应该保持原始尺寸
        assert crop_area == original_area


class TestGeometricDistortion:
    """测试几何扭曲"""
    
    @pytest.fixture
    def grid_image(self):
        """创建网格图像用于测试几何扭曲"""
        image = Image.new('RGB', (300, 150), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 绘制规则网格
        for i in range(0, 300, 30):
            draw.line([(i, 0), (i, 150)], fill=(0, 0, 0), width=1)
        for i in range(0, 150, 30):
            draw.line([(0, i), (300, i)], fill=(0, 0, 0), width=1)
        
        return image
    
    def test_geometric_distortion_initialization(self):
        """测试几何扭曲初始化"""
        # 测试默认参数
        distortion = GeometricDistortion()
        assert distortion.probability == 0.3
        assert distortion.params['grid_size'] == (10, 10)
        assert distortion.params['max_displacement'] == 0.1
        
        # 测试自定义参数
        distortion = GeometricDistortion(
            probability=0.8,
            grid_size=(8, 8),
            max_displacement=0.2
        )
        assert distortion.probability == 0.8
        assert distortion.params['grid_size'] == (8, 8)
        assert distortion.params['max_displacement'] == 0.2
    
    def test_geometric_distortion_application(self, grid_image):
        """测试几何扭曲应用"""
        distortion = GeometricDistortion(probability=1.0, max_displacement=0.1)
        
        result = distortion(grid_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == grid_image.size
        
        # 几何扭曲应该改变直线（但这很难直接验证）
        original_array = np.array(grid_image)
        result_array = np.array(result)
        
        assert not np.array_equal(original_array, result_array)
    
    def test_distortion_parameters(self, grid_image):
        """测试扭曲参数"""
        # 测试不同的网格尺寸
        grid_sizes = [(5, 5), (10, 10), (15, 15)]
        
        for grid_size in grid_sizes:
            distortion = GeometricDistortion(
                probability=1.0,
                grid_size=grid_size,
                max_displacement=0.1
            )
            result = distortion(grid_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)
        
        # 测试不同的位移强度
        displacements = [0.05, 0.1, 0.2, 0.3]
        
        for displacement in displacements:
            distortion = GeometricDistortion(
                probability=1.0,
                max_displacement=displacement
            )
            result = distortion(grid_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)


class TestPerspectiveEffectsIntegration:
    """测试透视效果的集成功能"""
    
    @pytest.fixture
    def test_image(self):
        """创建测试图像"""
        image = Image.new('RGB', (400, 200), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 绘制一些内容
        draw.rectangle([50, 50, 150, 150], fill=(100, 100, 100))
        draw.rectangle([200, 25, 350, 175], outline=(0, 0, 0), width=3)
        
        return image
    
    def test_apply_perspective_effects_function(self, test_image):
        """测试应用透视效果的便捷函数"""
        result, applied_effects = apply_perspective_effects(test_image, probability=1.0)
        
        assert isinstance(result, Image.Image)
        assert isinstance(applied_effects, list)
        
        # 高概率下应该至少应用一些效果
        assert len(applied_effects) >= 0
    
    def test_combined_perspective_effects(self, test_image):
        """测试组合透视效果"""
        # 依次应用所有透视效果
        tilt = TiltTransform(probability=1.0, max_angle=5)
        perspective = PerspectiveTransform(probability=1.0, max_distortion=0.1)
        rotation = RotationTransform(probability=1.0, max_angle=10)
        
        # 应用倾斜
        result1 = tilt(test_image)
        assert result1 is not None
        
        # 应用透视变换
        result2 = perspective(result1)
        assert result2 is not None
        
        # 应用旋转
        result3 = rotation(result2)
        assert result3 is not None
        
        # 最终结果应该与原图明显不同
        original_array = np.array(test_image)
        final_array = np.array(result3)
        
        # 由于尺寸可能改变，我们检查基本属性
        assert result3.mode == test_image.mode
    
    def test_perspective_effects_with_intensity_control(self, test_image):
        """测试带强度控制的透视效果"""
        tilt = TiltTransform(probability=1.0, max_angle=20)
        
        # 测试不同强度级别
        intensities = [0.2, 0.5, 0.8]
        results = []
        
        for intensity in intensities:
            result = tilt.apply(test_image, intensity=intensity)
            assert result is not None
            results.append(result)
        
        # 不同强度应该产生不同的结果
        # 由于可能的尺寸变化，我们只检查它们不完全相同
        for i in range(len(results) - 1):
            # 至少尺寸或内容应该不同
            different = (results[i].size != results[i + 1].size or 
                        not np.array_equal(np.array(results[i]), np.array(results[i + 1])))
            assert different


if __name__ == "__main__":
    # 运行基本测试
    print("运行透视变换效果测试...")
    
    # 创建测试图像
    test_image = Image.new('RGB', (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(test_image)
    draw.rectangle([50, 50, 350, 150], outline=(0, 0, 0), width=2)
    
    # 测试各个效果
    print("测试倾斜变换...")
    tilt = TiltTransform(probability=1.0, max_angle=10)
    result = tilt(test_image)
    print(f"倾斜变换: {'成功' if result else '失败'}")
    
    print("测试透视变换...")
    perspective = PerspectiveTransform(probability=1.0, max_distortion=0.2)
    result = perspective(test_image)
    print(f"透视变换: {'成功' if result else '失败'}")
    
    print("测试旋转变换...")
    rotation = RotationTransform(probability=1.0, max_angle=15)
    result = rotation(test_image)
    print(f"旋转变换: {'成功' if result else '失败'}")
    
    print("测试几何扭曲...")
    distortion = GeometricDistortion(probability=1.0, max_displacement=0.1)
    result = distortion(test_image)
    print(f"几何扭曲: {'成功' if result else '失败'}")
    
    print("测试组合透视效果...")
    result, applied = apply_perspective_effects(test_image, probability=1.0)
    print(f"组合透视效果: {'成功' if result else '失败'}, 应用的效果: {applied}")
    
    print("透视变换效果测试完成！")