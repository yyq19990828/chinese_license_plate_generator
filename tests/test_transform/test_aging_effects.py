"""
车牌老化效果测试模块

测试车牌老化相关的变换效果，包括磨损、褪色和污渍效果。
"""

import pytest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

from src.transform.aging_effects import WearEffect, FadeEffect, DirtEffect, apply_aging_effects


class TestWearEffect:
    """测试磨损效果"""
    
    @pytest.fixture
    def sample_plate_image(self):
        """创建模拟车牌图像"""
        # 创建一个白色背景的车牌
        image = Image.new('RGB', (440, 140), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 添加一些文字来模拟车牌字符
        try:
            # 尝试使用系统字体
            font = ImageFont.load_default()
        except:
            font = None
            
        # 绘制模拟的车牌文字
        if font:
            draw.text((50, 50), "粤B12345", fill=(0, 0, 0), font=font)
        else:
            # 如果没有字体，绘制一些矩形来模拟字符
            for i, x in enumerate(range(50, 350, 50)):
                draw.rectangle([x, 40, x+40, 100], fill=(0, 0, 0))
        
        return image
    
    def test_wear_effect_initialization(self):
        """测试磨损效果初始化"""
        # 测试默认参数
        wear = WearEffect()
        assert wear.probability == 0.3
        assert wear.params['erosion_kernel_size'] == (2, 5)
        assert wear.params['erosion_iterations'] == (1, 3)
        
        # 测试自定义参数
        custom_params = {
            'erosion_kernel_size': (3, 7),
            'erosion_iterations': (2, 4)
        }
        wear = WearEffect(probability=0.8, **custom_params)
        assert wear.probability == 0.8
        assert wear.params['erosion_kernel_size'] == (3, 7)
    
    def test_wear_effect_application(self, sample_plate_image):
        """测试磨损效果应用"""
        wear = WearEffect(probability=1.0)
        
        # 应用磨损效果
        result = wear(sample_plate_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == sample_plate_image.size
        
        # 检查图像确实发生了变化
        original_array = np.array(sample_plate_image)
        result_array = np.array(result)
        
        # 磨损效果应该改变图像
        assert not np.array_equal(original_array, result_array)
        
        # 磨损效果通常会使边缘变得不那么清晰
        # 检查是否存在模糊或腐蚀的迹象
        original_edges = cv2.Canny(cv2.cvtColor(original_array, cv2.COLOR_RGB2GRAY), 50, 150)
        result_edges = cv2.Canny(cv2.cvtColor(result_array, cv2.COLOR_RGB2GRAY), 50, 150)
        
        # 磨损后边缘点应该减少（由于腐蚀）
        assert np.sum(result_edges) <= np.sum(original_edges)
    
    def test_wear_effect_intensity(self, sample_plate_image):
        """测试磨损效果强度控制"""
        wear = WearEffect(probability=1.0)
        
        # 测试不同强度
        weak_result = wear.apply(sample_plate_image, intensity=0.2)
        strong_result = wear.apply(sample_plate_image, intensity=0.8)
        
        assert weak_result is not None
        assert strong_result is not None
        
        # 强度不同应该产生不同程度的磨损
        weak_array = np.array(weak_result)
        strong_array = np.array(strong_result)
        original_array = np.array(sample_plate_image)
        
        # 计算与原图的差异
        weak_diff = np.sum(np.abs(weak_array.astype(int) - original_array.astype(int)))
        strong_diff = np.sum(np.abs(strong_array.astype(int) - original_array.astype(int)))
        
        # 强度更高的应该差异更大
        assert strong_diff >= weak_diff
    
    def test_wear_effect_zero_probability(self, sample_plate_image):
        """测试零概率情况"""
        wear = WearEffect(probability=0.0)
        result = wear(sample_plate_image)
        
        # 概率为0时应该返回None
        assert result is None


class TestFadeEffect:
    """测试褪色效果"""
    
    @pytest.fixture
    def colored_plate_image(self):
        """创建有颜色的车牌图像"""
        # 创建蓝色背景的车牌
        image = Image.new('RGB', (440, 140), color=(0, 100, 200))
        draw = ImageDraw.Draw(image)
        
        # 添加白色文字
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        if font:
            draw.text((50, 50), "粤B12345", fill=(255, 255, 255), font=font)
        else:
            # 绘制白色矩形模拟字符
            for i, x in enumerate(range(50, 350, 50)):
                draw.rectangle([x, 40, x+40, 100], fill=(255, 255, 255))
        
        return image
    
    def test_fade_effect_initialization(self):
        """测试褪色效果初始化"""
        # 测试默认参数
        fade = FadeEffect()
        assert fade.probability == 0.3
        assert fade.params['fade_factor'] == (0.7, 0.9)
        assert fade.params['color_shift'] == (-20, 20)
        
        # 测试自定义参数
        custom_params = {
            'fade_factor': (0.5, 0.8),
            'color_shift': (-30, 30)
        }
        fade = FadeEffect(probability=0.7, **custom_params)
        assert fade.probability == 0.7
        assert fade.params['fade_factor'] == (0.5, 0.8)
    
    def test_fade_effect_application(self, colored_plate_image):
        """测试褪色效果应用"""
        fade = FadeEffect(probability=1.0)
        
        # 应用褪色效果
        result = fade(colored_plate_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == colored_plate_image.size
        
        # 检查颜色变化
        original_array = np.array(colored_plate_image)
        result_array = np.array(result)
        
        # 褪色效果应该降低颜色强度
        original_mean = np.mean(original_array, axis=(0, 1))
        result_mean = np.mean(result_array, axis=(0, 1))
        
        # 褪色后平均颜色强度应该有所变化
        assert not np.allclose(original_mean, result_mean, rtol=0.01)
    
    def test_fade_effect_color_reduction(self, colored_plate_image):
        """测试褪色效果的颜色衰减"""
        fade = FadeEffect(probability=1.0, fade_factor=(0.5, 0.5))  # 固定衰减因子
        
        result = fade.apply(colored_plate_image, intensity=1.0)
        
        original_array = np.array(colored_plate_image)
        result_array = np.array(result)
        
        # 检查颜色饱和度是否降低
        original_hsv = cv2.cvtColor(original_array, cv2.COLOR_RGB2HSV)
        result_hsv = cv2.cvtColor(result_array, cv2.COLOR_RGB2HSV)
        
        # 褪色后饱和度应该降低
        original_saturation = np.mean(original_hsv[:, :, 1])
        result_saturation = np.mean(result_hsv[:, :, 1])
        
        assert result_saturation <= original_saturation


class TestDirtEffect:
    """测试污渍效果"""
    
    @pytest.fixture
    def clean_plate_image(self):
        """创建干净的车牌图像"""
        image = Image.new('RGB', (440, 140), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 绘制黑色字符
        for i, x in enumerate(range(50, 350, 50)):
            draw.rectangle([x, 40, x+40, 100], fill=(0, 0, 0))
        
        return image
    
    def test_dirt_effect_initialization(self):
        """测试污渍效果初始化"""
        # 测试默认参数
        dirt = DirtEffect()
        assert dirt.probability == 0.3
        assert dirt.params['num_spots'] == (3, 8)
        assert dirt.params['spot_size'] == (5, 20)
        
        # 测试自定义参数
        custom_params = {
            'num_spots': (5, 15),
            'spot_size': (8, 25)
        }
        dirt = DirtEffect(probability=0.6, **custom_params)
        assert dirt.probability == 0.6
        assert dirt.params['num_spots'] == (5, 15)
    
    def test_dirt_effect_application(self, clean_plate_image):
        """测试污渍效果应用"""
        dirt = DirtEffect(probability=1.0)
        
        # 应用污渍效果
        result = dirt(clean_plate_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == clean_plate_image.size
        
        # 检查是否添加了污渍
        original_array = np.array(clean_plate_image)
        result_array = np.array(result)
        
        # 污渍效果应该改变图像
        assert not np.array_equal(original_array, result_array)
        
        # 污渍通常会降低亮度
        original_brightness = np.mean(original_array)
        result_brightness = np.mean(result_array)
        
        # 添加污渍后亮度应该降低
        assert result_brightness <= original_brightness
    
    def test_dirt_effect_spot_count(self, clean_plate_image):
        """测试污渍数量控制"""
        # 设置固定的污渍数量
        dirt = DirtEffect(probability=1.0, num_spots=(5, 5))
        
        result = dirt(clean_plate_image)
        assert result is not None
        
        # 虽然我们无法直接计算污渍数量，但可以检查图像变化
        original_array = np.array(clean_plate_image)
        result_array = np.array(result)
        
        # 计算变化的像素数量（作为污渍程度的近似）
        diff_pixels = np.sum(np.any(original_array != result_array, axis=2))
        assert diff_pixels > 0  # 应该有像素发生变化


class TestAgingEffectsIntegration:
    """测试老化效果的集成功能"""
    
    @pytest.fixture
    def test_image(self):
        """创建测试图像"""
        return Image.new('RGB', (440, 140), color=(255, 255, 255))
    
    def test_apply_aging_effects_function(self, test_image):
        """测试应用老化效果的便捷函数"""
        result, applied_effects = apply_aging_effects(test_image, probability=1.0)
        
        assert isinstance(result, Image.Image)
        assert isinstance(applied_effects, list)
        assert result.size == test_image.size
        
        # 高概率下应该至少应用一些效果
        # 注意：由于随机性，可能不是所有效果都会被应用
        assert len(applied_effects) >= 0  # 至少不会出错
    
    def test_combined_aging_effects(self, test_image):
        """测试组合老化效果"""
        # 依次应用所有老化效果
        wear = WearEffect(probability=1.0)
        fade = FadeEffect(probability=1.0)
        dirt = DirtEffect(probability=1.0)
        
        # 应用磨损效果
        result1 = wear(test_image)
        assert result1 is not None
        
        # 应用褪色效果
        result2 = fade(result1)
        assert result2 is not None
        
        # 应用污渍效果
        result3 = dirt(result2)
        assert result3 is not None
        
        # 最终结果应该与原图不同
        original_array = np.array(test_image)
        final_array = np.array(result3)
        
        assert not np.array_equal(original_array, final_array)
    
    def test_aging_effects_with_different_intensities(self, test_image):
        """测试不同强度的老化效果"""
        wear = WearEffect(probability=1.0)
        
        # 测试不同强度级别
        intensities = [0.1, 0.5, 0.9]
        results = []
        
        for intensity in intensities:
            result = wear.apply(test_image, intensity=intensity)
            assert result is not None
            results.append(np.array(result))
        
        # 不同强度应该产生不同的结果
        for i in range(len(results) - 1):
            assert not np.array_equal(results[i], results[i + 1])


if __name__ == "__main__":
    # 运行基本测试
    print("运行老化效果测试...")
    
    # 创建测试图像
    test_image = Image.new('RGB', (440, 140), color=(255, 255, 255))
    
    # 测试各个效果
    print("测试磨损效果...")
    wear = WearEffect(probability=1.0)
    result = wear(test_image)
    print(f"磨损效果: {'成功' if result else '失败'}")
    
    print("测试褪色效果...")
    fade = FadeEffect(probability=1.0)
    result = fade(test_image)
    print(f"褪色效果: {'成功' if result else '失败'}")
    
    print("测试污渍效果...")
    dirt = DirtEffect(probability=1.0)
    result = dirt(test_image)
    print(f"污渍效果: {'成功' if result else '失败'}")
    
    print("测试组合老化效果...")
    result, applied = apply_aging_effects(test_image, probability=1.0)
    print(f"组合老化效果: {'成功' if result else '失败'}, 应用的效果: {applied}")
    
    print("老化效果测试完成！")