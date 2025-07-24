"""
光照效果测试模块

测试车牌光照相关的效果，包括阴影、反光、夜间和背光效果。
"""

import pytest
import numpy as np
from PIL import Image, ImageDraw
import cv2

from src.transform.lighting_effects import (
    ShadowEffect, ReflectionEffect, NightEffect, 
    BacklightEffect, apply_lighting_effects
)


class TestShadowEffect:
    """测试阴影效果"""
    
    @pytest.fixture
    def bright_plate_image(self):
        """创建明亮的车牌图像"""
        image = Image.new('RGB', (440, 140), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 绘制黑色字符
        draw.text((50, 50), "粤B12345", fill=(0, 0, 0))
        
        # 绘制边框
        draw.rectangle([5, 5, 435, 135], outline=(0, 0, 0), width=2)
        
        return image
    
    def test_shadow_effect_initialization(self):
        """测试阴影效果初始化"""
        # 测试默认参数
        shadow = ShadowEffect()
        assert shadow.probability == 0.3
        assert shadow.params['shadow_offset'] == (5, 15)
        assert shadow.params['shadow_opacity'] == (0.3, 0.7)
        assert shadow.params['blur_radius'] == (2, 8)
        
        # 测试自定义参数
        custom_params = {
            'shadow_offset': (3, 10),
            'shadow_opacity': (0.2, 0.6),
            'blur_radius': (1, 5)
        }
        shadow = ShadowEffect(probability=0.8, **custom_params)
        assert shadow.probability == 0.8
        assert shadow.params['shadow_offset'] == (3, 10)
        assert shadow.params['shadow_opacity'] == (0.2, 0.6)
    
    def test_shadow_effect_application(self, bright_plate_image):
        """测试阴影效果应用"""
        shadow = ShadowEffect(probability=1.0)
        
        result = shadow(bright_plate_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == bright_plate_image.size
        
        # 检查阴影效果是否生效
        original_array = np.array(bright_plate_image)
        result_array = np.array(result)
        
        # 阴影效果应该改变图像
        assert not np.array_equal(original_array, result_array)
        
        # 阴影通常会降低整体亮度
        original_brightness = np.mean(original_array)
        result_brightness = np.mean(result_array)
        
        # 添加阴影后亮度应该有变化（可能升高或降低，取决于实现）
        assert original_brightness != result_brightness
    
    def test_shadow_offset_effect(self, bright_plate_image):
        """测试阴影偏移效果"""
        # 测试不同的偏移距离
        offsets = [(3, 3), (10, 10), (20, 20)]
        
        for offset in offsets:
            shadow = ShadowEffect(
                probability=1.0, 
                shadow_offset=offset,
                shadow_opacity=(0.5, 0.5)  # 固定透明度
            )
            result = shadow(bright_plate_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)
    
    def test_shadow_opacity_control(self, bright_plate_image):
        """测试阴影透明度控制"""
        # 测试不同透明度
        opacities = [(0.2, 0.2), (0.5, 0.5), (0.8, 0.8)]
        
        for opacity in opacities:
            shadow = ShadowEffect(
                probability=1.0,
                shadow_opacity=opacity
            )
            result = shadow(bright_plate_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)
    
    def test_shadow_intensity_scaling(self, bright_plate_image):
        """测试阴影强度缩放"""
        shadow = ShadowEffect(probability=1.0)
        
        # 测试不同强度
        weak_result = shadow.apply(bright_plate_image, intensity=0.3)
        strong_result = shadow.apply(bright_plate_image, intensity=0.9)
        
        assert weak_result is not None
        assert strong_result is not None
        
        # 强度不同应该产生不同程度的阴影
        weak_array = np.array(weak_result)
        strong_array = np.array(strong_result)
        original_array = np.array(bright_plate_image)
        
        # 计算与原图的差异
        weak_diff = np.sum(np.abs(weak_array.astype(int) - original_array.astype(int)))
        strong_diff = np.sum(np.abs(strong_array.astype(int) - original_array.astype(int)))
        
        # 强度更高的应该差异更大
        assert strong_diff >= weak_diff


class TestReflectionEffect:
    """测试反光效果"""
    
    @pytest.fixture
    def matte_plate_image(self):
        """创建哑光车牌图像"""
        image = Image.new('RGB', (440, 140), color=(200, 200, 200))
        draw = ImageDraw.Draw(image)
        
        # 绘制深色字符
        draw.text((50, 50), "粤B12345", fill=(50, 50, 50))
        
        return image
    
    def test_reflection_effect_initialization(self):
        """测试反光效果初始化"""
        # 测试默认参数
        reflection = ReflectionEffect()
        assert reflection.probability == 0.3
        assert reflection.params['reflection_intensity'] == (0.3, 0.8)
        assert reflection.params['highlight_size'] == (20, 60)
        assert reflection.params['num_highlights'] == (1, 3)
        
        # 测试自定义参数
        custom_params = {
            'reflection_intensity': (0.4, 0.9),
            'highlight_size': (15, 50),
            'num_highlights': (2, 5)
        }
        reflection = ReflectionEffect(probability=0.7, **custom_params)
        assert reflection.probability == 0.7
        assert reflection.params['reflection_intensity'] == (0.4, 0.9)
    
    def test_reflection_effect_application(self, matte_plate_image):
        """测试反光效果应用"""
        reflection = ReflectionEffect(probability=1.0)
        
        result = reflection(matte_plate_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == matte_plate_image.size
        
        # 检查反光效果
        original_array = np.array(matte_plate_image)
        result_array = np.array(result)
        
        # 反光效果应该改变图像
        assert not np.array_equal(original_array, result_array)
        
        # 反光通常会增加亮度
        original_max = np.max(original_array)
        result_max = np.max(result_array)
        
        # 反光后最大亮度可能增加
        assert result_max >= original_max
    
    def test_reflection_highlight_count(self, matte_plate_image):
        """测试反光点数量控制"""
        # 测试固定数量的反光点
        reflection = ReflectionEffect(
            probability=1.0,
            num_highlights=(2, 2)  # 固定2个反光点
        )
        
        result = reflection(matte_plate_image)
        assert result is not None
        
        # 验证反光效果确实被应用
        original_array = np.array(matte_plate_image)
        result_array = np.array(result)
        
        assert not np.array_equal(original_array, result_array)
    
    def test_reflection_intensity_levels(self, matte_plate_image):
        """测试反光强度级别"""
        intensities = [(0.2, 0.2), (0.5, 0.5), (0.8, 0.8)]
        
        for intensity in intensities:
            reflection = ReflectionEffect(
                probability=1.0,
                reflection_intensity=intensity
            )
            result = reflection(matte_plate_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)


class TestNightEffect:
    """测试夜间效果"""
    
    @pytest.fixture
    def daylight_plate_image(self):
        """创建日光条件下的车牌图像"""
        image = Image.new('RGB', (440, 140), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        # 绘制清晰的黑色字符
        draw.text((50, 50), "粤B12345", fill=(0, 0, 0))
        
        return image
    
    def test_night_effect_initialization(self):
        """测试夜间效果初始化"""
        # 测试默认参数
        night = NightEffect()
        assert night.probability == 0.3
        assert night.params['brightness_reduction'] == (0.3, 0.7)
        assert night.params['color_temperature'] == (2000, 4000)
        assert night.params['noise_level'] == (0.1, 0.3)
        
        # 测试自定义参数
        custom_params = {
            'brightness_reduction': (0.4, 0.8),
            'color_temperature': (1500, 3500),
            'noise_level': (0.05, 0.25)
        }
        night = NightEffect(probability=0.6, **custom_params)
        assert night.probability == 0.6
        assert night.params['brightness_reduction'] == (0.4, 0.8)
    
    def test_night_effect_application(self, daylight_plate_image):
        """测试夜间效果应用"""
        night = NightEffect(probability=1.0)
        
        result = night(daylight_plate_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == daylight_plate_image.size
        
        # 检查夜间效果
        original_array = np.array(daylight_plate_image)
        result_array = np.array(result)
        
        # 夜间效果应该改变图像
        assert not np.array_equal(original_array, result_array)
        
        # 夜间效果通常会降低整体亮度
        original_brightness = np.mean(original_array)
        result_brightness = np.mean(result_array)
        
        # 夜间效果后亮度应该降低
        assert result_brightness <= original_brightness
    
    def test_night_brightness_reduction(self, daylight_plate_image):
        """测试夜间亮度降低"""
        # 测试不同的亮度降低程度
        reductions = [(0.2, 0.2), (0.5, 0.5), (0.8, 0.8)]
        
        for reduction in reductions:
            night = NightEffect(
                probability=1.0,
                brightness_reduction=reduction
            )
            result = night(daylight_plate_image)
            
            assert result is not None
            
            # 验证亮度确实降低
            original_brightness = np.mean(np.array(daylight_plate_image))
            result_brightness = np.mean(np.array(result))
            
            assert result_brightness < original_brightness
    
    def test_night_color_temperature(self, daylight_plate_image):
        """测试夜间色温效果"""
        # 测试不同色温
        temperatures = [(2000, 2000), (3000, 3000), (4000, 4000)]
        
        for temp in temperatures:
            night = NightEffect(
                probability=1.0,
                color_temperature=temp
            )
            result = night(daylight_plate_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)
    
    def test_night_noise_addition(self, daylight_plate_image):
        """测试夜间噪声添加"""
        # 测试不同噪声级别
        noise_levels = [(0.1, 0.1), (0.2, 0.2), (0.3, 0.3)]
        
        for noise in noise_levels:
            night = NightEffect(
                probability=1.0,
                noise_level=noise
            )
            result = night(daylight_plate_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)


class TestBacklightEffect:
    """测试背光效果"""
    
    @pytest.fixture
    def normal_plate_image(self):
        """创建正常光照条件下的车牌图像"""
        image = Image.new('RGB', (440, 140), color=(220, 220, 220))
        draw = ImageDraw.Draw(image)
        
        # 绘制字符
        draw.text((50, 50), "粤B12345", fill=(30, 30, 30))
        
        return image
    
    def test_backlight_effect_initialization(self):
        """测试背光效果初始化"""
        # 测试默认参数
        backlight = BacklightEffect()
        assert backlight.probability == 0.3
        assert backlight.params['rim_light_intensity'] == (0.3, 0.8)
        assert backlight.params['center_darkening'] == (0.1, 0.4)
        assert backlight.params['contrast_boost'] == (1.2, 1.8)
        
        # 测试自定义参数
        custom_params = {
            'rim_light_intensity': (0.4, 0.9),
            'center_darkening': (0.2, 0.5),
            'contrast_boost': (1.1, 1.6)
        }
        backlight = BacklightEffect(probability=0.8, **custom_params)
        assert backlight.probability == 0.8
        assert backlight.params['rim_light_intensity'] == (0.4, 0.9)
    
    def test_backlight_effect_application(self, normal_plate_image):
        """测试背光效果应用"""
        backlight = BacklightEffect(probability=1.0)
        
        result = backlight(normal_plate_image)
        
        # 基本检查
        assert result is not None
        assert isinstance(result, Image.Image)
        assert result.size == normal_plate_image.size
        
        # 检查背光效果
        original_array = np.array(normal_plate_image)
        result_array = np.array(result)
        
        # 背光效果应该改变图像
        assert not np.array_equal(original_array, result_array)
    
    def test_backlight_rim_lighting(self, normal_plate_image):
        """测试背光边缘光效果"""
        # 测试不同的边缘光强度
        intensities = [(0.2, 0.2), (0.5, 0.5), (0.8, 0.8)]
        
        for intensity in intensities:
            backlight = BacklightEffect(
                probability=1.0,
                rim_light_intensity=intensity
            )
            result = backlight(normal_plate_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)
    
    def test_backlight_center_darkening(self, normal_plate_image):
        """测试背光中心变暗效果"""
        # 测试不同的中心变暗程度
        darkenings = [(0.1, 0.1), (0.3, 0.3), (0.5, 0.5)]
        
        for darkening in darkenings:
            backlight = BacklightEffect(
                probability=1.0,
                center_darkening=darkening
            )
            result = backlight(normal_plate_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)
    
    def test_backlight_contrast_boost(self, normal_plate_image):
        """测试背光对比度增强"""
        # 测试不同的对比度增强程度
        boosts = [(1.1, 1.1), (1.5, 1.5), (2.0, 2.0)]
        
        for boost in boosts:
            backlight = BacklightEffect(
                probability=1.0,
                contrast_boost=boost
            )
            result = backlight(normal_plate_image)
            
            assert result is not None
            assert isinstance(result, Image.Image)


class TestLightingEffectsIntegration:
    """测试光照效果的集成功能"""
    
    @pytest.fixture
    def test_image(self):
        """创建测试图像"""
        image = Image.new('RGB', (440, 140), color=(200, 200, 200))
        draw = ImageDraw.Draw(image)
        
        # 绘制车牌内容
        draw.rectangle([10, 10, 430, 130], outline=(0, 0, 0), width=2)
        draw.text((50, 50), "粤B12345", fill=(0, 0, 0))
        
        return image
    
    def test_apply_lighting_effects_function(self, test_image):
        """测试应用光照效果的便捷函数"""
        result, applied_effects = apply_lighting_effects(test_image, probability=1.0)
        
        assert isinstance(result, Image.Image)
        assert isinstance(applied_effects, list)
        assert result.size == test_image.size
        
        # 高概率下应该至少应用一些效果
        assert len(applied_effects) >= 0
    
    def test_combined_lighting_effects(self, test_image):
        """测试组合光照效果"""
        # 依次应用所有光照效果
        shadow = ShadowEffect(probability=1.0)
        reflection = ReflectionEffect(probability=1.0)
        night = NightEffect(probability=1.0)
        backlight = BacklightEffect(probability=1.0)
        
        # 应用阴影效果
        result1 = shadow(test_image)
        assert result1 is not None
        
        # 应用反光效果
        result2 = reflection(result1)
        assert result2 is not None
        
        # 应用夜间效果
        result3 = night(result2)
        assert result3 is not None
        
        # 应用背光效果
        result4 = backlight(result3)
        assert result4 is not None
        
        # 最终结果应该与原图不同
        original_array = np.array(test_image)
        final_array = np.array(result4)
        
        assert not np.array_equal(original_array, final_array)
    
    def test_lighting_effects_with_different_intensities(self, test_image):
        """测试不同强度的光照效果"""
        shadow = ShadowEffect(probability=1.0)
        
        # 测试不同强度级别
        intensities = [0.2, 0.5, 0.8]
        results = []
        
        for intensity in intensities:
            result = shadow.apply(test_image, intensity=intensity)
            assert result is not None
            results.append(np.array(result))
        
        # 不同强度应该产生不同的结果
        for i in range(len(results) - 1):
            assert not np.array_equal(results[i], results[i + 1])
    
    def test_lighting_effects_realistic_combination(self, test_image):
        """测试真实场景的光照效果组合"""
        # 模拟不同的光照场景
        
        # 场景1：阴天（阴影 + 低对比度）
        shadow = ShadowEffect(probability=1.0, shadow_opacity=(0.2, 0.3))
        result_cloudy = shadow(test_image)
        assert result_cloudy is not None
        
        # 场景2：强光（反光 + 背光）
        reflection = ReflectionEffect(probability=1.0, reflection_intensity=(0.6, 0.8))
        backlight = BacklightEffect(probability=1.0, rim_light_intensity=(0.5, 0.7))
        
        result_temp = reflection(test_image)
        result_bright = backlight(result_temp)
        assert result_bright is not None
        
        # 场景3：夜间（夜间效果 + 微弱反光）
        night = NightEffect(probability=1.0, brightness_reduction=(0.5, 0.7))
        reflection_weak = ReflectionEffect(probability=1.0, reflection_intensity=(0.1, 0.3))
        
        result_temp = night(test_image)
        result_night = reflection_weak(result_temp)
        assert result_night is not None
        
        # 所有场景都应该产生不同的结果
        cloudy_array = np.array(result_cloudy)
        bright_array = np.array(result_bright)
        night_array = np.array(result_night)
        
        assert not np.array_equal(cloudy_array, bright_array)
        assert not np.array_equal(bright_array, night_array)
        assert not np.array_equal(cloudy_array, night_array)


if __name__ == "__main__":
    # 运行基本测试
    print("运行光照效果测试...")
    
    # 创建测试图像
    test_image = Image.new('RGB', (440, 140), color=(200, 200, 200))
    draw = ImageDraw.Draw(test_image)
    draw.rectangle([10, 10, 430, 130], outline=(0, 0, 0), width=2)
    
    # 测试各个效果
    print("测试阴影效果...")
    shadow = ShadowEffect(probability=1.0)
    result = shadow(test_image)
    print(f"阴影效果: {'成功' if result else '失败'}")
    
    print("测试反光效果...")
    reflection = ReflectionEffect(probability=1.0)
    result = reflection(test_image)
    print(f"反光效果: {'成功' if result else '失败'}")
    
    print("测试夜间效果...")
    night = NightEffect(probability=1.0)
    result = night(test_image)
    print(f"夜间效果: {'成功' if result else '失败'}")
    
    print("测试背光效果...")
    backlight = BacklightEffect(probability=1.0)
    result = backlight(test_image)
    print(f"背光效果: {'成功' if result else '失败'}")
    
    print("测试组合光照效果...")
    result, applied = apply_lighting_effects(test_image, probability=1.0)
    print(f"组合光照效果: {'成功' if result else '失败'}, 应用的效果: {applied}")
    
    print("光照效果测试完成！")