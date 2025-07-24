#!/usr/bin/env python3
"""
车牌变换效果演示脚本

展示车牌增强变换系统的各种效果，生成示例图像以供观察和调试。
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse

# 添加项目路径
sys.path.append('.')

from src.generator.integrated_generator import IntegratedPlateGenerator
from src.transform import (
    WearEffect, FadeEffect, DirtEffect,
    TiltTransform, PerspectiveTransform, RotationTransform, GeometricDistortion,
    ShadowEffect, ReflectionEffect, NightEffect, BacklightEffect,
    CompositeTransform, TransformConfig, quick_enhance
)


def create_sample_plate_image():
    """创建示例车牌图像用于演示"""
    # 创建白色车牌背景
    plate_image = Image.new('RGB', (440, 140), color=(255, 255, 255))
    draw = ImageDraw.Draw(plate_image)
    
    # 绘制边框
    draw.rectangle([5, 5, 435, 135], outline=(0, 0, 0), width=3)
    
    # 绘制分隔符
    draw.rectangle([125, 25, 135, 115], fill=(0, 0, 0))
    
    # 模拟字符 - 使用矩形代替文字以避免字体依赖
    char_positions = [
        (30, 40, 70, 100),   # 粤
        (80, 40, 120, 100),  # B
        (150, 40, 190, 100), # 1
        (200, 40, 240, 100), # 2
        (250, 40, 290, 100), # 3
        (300, 40, 340, 100), # 4
        (350, 40, 390, 100)  # 5
    ]
    
    for pos in char_positions:
        draw.rectangle(pos, fill=(0, 0, 0))
    
    return plate_image


def get_base_image():
    """加载基础图像，如果找不到则创建默认图像"""
    input_image_path = "川A3790挂_yellow_double.jpg"
    try:
        base_image = Image.open(input_image_path).convert('RGB')
        print(f"  - 成功加载图像: {input_image_path}")
        return base_image
    except FileNotFoundError:
        print(f"  - 警告: 未找到图像 '{input_image_path}'。")
        print("  - 将使用默认生成的示例图像。")
        return create_sample_plate_image()


def demo_aging_effects(output_dir: str):
    """演示老化效果"""
    print("演示老化效果...")
    
    aging_dir = os.path.join(output_dir, "aging_effects")
    os.makedirs(aging_dir, exist_ok=True)
    
    base_image = get_base_image()
    base_image.save(os.path.join(aging_dir, "00_original.png"))
    
    # 磨损效果
    print("  - 磨损效果")
    wear_effect = WearEffect(probability=1.0)
    
    # 不同强度的磨损效果
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = wear_effect.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(aging_dir, f"01_wear_intensity_{intensity:.1f}.png"))
    
    # 褪色效果
    print("  - 褪色效果")
    fade_effect = FadeEffect(probability=1.0)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = fade_effect.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(aging_dir, f"02_fade_intensity_{intensity:.1f}.png"))
    
    # 污渍效果
    print("  - 污渍效果")
    dirt_effect = DirtEffect(probability=1.0)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = dirt_effect.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(aging_dir, f"03_dirt_intensity_{intensity:.1f}.png"))
    
    # 组合老化效果
    print("  - 组合老化效果")
    wear_result = wear_effect.apply(base_image, intensity=0.6)
    if wear_result:
        fade_result = fade_effect.apply(wear_result, intensity=0.5)
        if fade_result:
            dirt_result = dirt_effect.apply(fade_result, intensity=0.4)
            if dirt_result:
                dirt_result.save(os.path.join(aging_dir, "04_combined_aging.png"))


def demo_perspective_effects(output_dir: str):
    """演示透视变换效果"""
    print("演示透视变换效果...")
    
    perspective_dir = os.path.join(output_dir, "perspective_effects")
    os.makedirs(perspective_dir, exist_ok=True)
    
    base_image = get_base_image()
    base_image.save(os.path.join(perspective_dir, "00_original.png"))
    
    # 倾斜变换
    print("  - 倾斜变换")
    tilt_transform = TiltTransform(probability=1.0, max_angle=20)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = tilt_transform.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(perspective_dir, f"01_tilt_intensity_{intensity:.1f}.png"))
    
    # 透视变换
    print("  - 透视变换")
    perspective_transform = PerspectiveTransform(probability=1.0, max_distortion=0.3)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = perspective_transform.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(perspective_dir, f"02_perspective_intensity_{intensity:.1f}.png"))
    
    # 旋转变换
    print("  - 旋转变换")
    rotation_transform = RotationTransform(probability=1.0, max_angle=20)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = rotation_transform.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(perspective_dir, f"03_rotation_intensity_{intensity:.1f}.png"))
    
    # 几何扭曲
    print("  - 几何扭曲")
    geometric_distortion = GeometricDistortion(probability=1.0, max_displacement=0.2)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = geometric_distortion.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(perspective_dir, f"04_distortion_intensity_{intensity:.1f}.png"))


def demo_lighting_effects(output_dir: str):
    """演示光照效果"""
    print("演示光照效果...")
    
    lighting_dir = os.path.join(output_dir, "lighting_effects")
    os.makedirs(lighting_dir, exist_ok=True)
    
    base_image = get_base_image()
    base_image.save(os.path.join(lighting_dir, "00_original.png"))
    
    # 阴影效果
    print("  - 阴影效果")
    shadow_effect = ShadowEffect(probability=1.0)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = shadow_effect.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(lighting_dir, f"01_shadow_intensity_{intensity:.1f}.png"))
    
    # 反光效果
    print("  - 反光效果")
    reflection_effect = ReflectionEffect(probability=1.0)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = reflection_effect.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(lighting_dir, f"02_reflection_intensity_{intensity:.1f}.png"))
    
    # 夜间效果
    print("  - 夜间效果")
    night_effect = NightEffect(probability=1.0)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = night_effect.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(lighting_dir, f"03_night_intensity_{intensity:.1f}.png"))
    
    # 背光效果
    print("  - 背光效果")
    backlight_effect = BacklightEffect(probability=1.0)
    
    for i, intensity in enumerate([0.3, 0.6, 0.9]):
        result = backlight_effect.apply(base_image, intensity=intensity)
        if result:
            result.save(os.path.join(lighting_dir, f"04_backlight_intensity_{intensity:.1f}.png"))


def demo_composite_effects(output_dir: str):
    """演示复合变换效果"""
    print("演示复合变换效果...")
    
    composite_dir = os.path.join(output_dir, "composite_effects")
    os.makedirs(composite_dir, exist_ok=True)
    
    base_image = get_base_image()
    base_image.save(os.path.join(composite_dir, "00_original.png"))
    
    # 创建复合变换管理器
    transformer = CompositeTransform()
    
    # 不同数量的变换组合
    print("  - 不同数量的变换组合")
    for max_transforms in [1, 2, 3, 5]:
        result, applied_transforms = transformer.apply(
            base_image, 
            max_transforms=max_transforms,
            intensity_scale=0.8
        )
        if result:
            result.save(os.path.join(composite_dir, f"01_max_{max_transforms}_transforms.png"))
            # 保存应用的变换信息
            with open(os.path.join(composite_dir, f"01_max_{max_transforms}_transforms.txt"), 'w') as f:
                f.write(f"应用的变换: {', '.join(applied_transforms)}")
    
    # 单一类型的变换
    print("  - 单一类型的变换")
    from src.transform.transform_config import TransformType
    
    type_names = {
        TransformType.AGING: "aging",
        TransformType.PERSPECTIVE: "perspective", 
        TransformType.LIGHTING: "lighting"
    }
    
    for transform_type, type_name in type_names.items():
        result, applied_transforms = transformer.apply_single_type(
            base_image, 
            transform_type,
            intensity_scale=0.7
        )
        if result:
            result.save(os.path.join(composite_dir, f"02_{type_name}_only.png"))
    
    # 预设效果
    print("  - 预设效果")
    preset_names = ['light_aging', 'heavy_aging', 'perspective_only', 'lighting_only', 'balanced']
    
    for preset_name in preset_names:
        try:
            result, applied_transforms = transformer.apply_preset(base_image, preset_name)
            if result:
                result.save(os.path.join(composite_dir, f"03_preset_{preset_name}.png"))
        except ValueError:
            print(f"    预设 {preset_name} 不存在")


def demo_quick_enhance(output_dir: str):
    """演示快速增强功能"""
    print("演示快速增强功能...")
    
    quick_dir = os.path.join(output_dir, "quick_enhance")
    os.makedirs(quick_dir, exist_ok=True)
    
    base_image = get_base_image()
    base_image.save(os.path.join(quick_dir, "00_original.png"))
    
    # 不同强度级别
    print("  - 不同强度级别")
    intensities = ["light", "medium", "heavy"]
    
    for intensity in intensities:
        result, applied_transforms = quick_enhance(
            base_image, 
            intensity=intensity
        )
        if result:
            result.save(os.path.join(quick_dir, f"01_intensity_{intensity}.png"))
            # 保存应用的变换信息
            with open(os.path.join(quick_dir, f"01_intensity_{intensity}.txt"), 'w') as f:
                f.write(f"应用的变换: {', '.join(applied_transforms)}")
    
    # 不同风格
    print("  - 不同风格")
    styles = ["balanced", "aging", "perspective", "lighting"]
    
    for style in styles:
        result, applied_transforms = quick_enhance(
            base_image,
            style=style
        )
        if result:
            result.save(os.path.join(quick_dir, f"02_style_{style}.png"))


def demo_real_plate_generation(output_dir: str):
    """演示真实车牌生成和变换"""
    print("演示真实车牌生成和变换...")
    
    real_dir = os.path.join(output_dir, "real_plate_demo")
    os.makedirs(real_dir, exist_ok=True)
    
    try:
        # 创建集成生成器
        generator = IntegratedPlateGenerator()
        
        # 生成几个不同类型的车牌
        print("  - 生成不同类型的车牌")
        
        for i in range(5):
            # 生成原始车牌
            plate_info, plate_image = generator.generate_plate_with_image(enhance=False)
            original_filename = f"plate_{i+1:02d}_{plate_info.plate_number}_original.jpg"
            
            # 保存原始图像
            from PIL import Image as PILImage
            original_pil = PILImage.fromarray(plate_image)
            original_pil.save(os.path.join(real_dir, original_filename))
            
            # 生成增强版本
            plate_info, enhanced_image = generator.generate_plate_with_image(enhance=True)
            enhanced_filename = f"plate_{i+1:02d}_{plate_info.plate_number}_enhanced.jpg"
            
            # 保存增强图像
            enhanced_pil = PILImage.fromarray(enhanced_image)
            enhanced_pil.save(os.path.join(real_dir, enhanced_filename))
            
            print(f"    生成车牌: {plate_info.plate_number}")
            
    except Exception as e:
        print(f"    真实车牌生成失败: {e}")
        print("    跳过真实车牌演示")


def create_comparison_grid(output_dir: str):
    """创建效果对比网格图"""
    print("创建效果对比网格图...")
    
    try:
        base_image = get_base_image()
        
        # 创建不同效果的示例
        effects = []
        labels = []
        
        # 原始图像
        effects.append(base_image)
        labels.append("原始")
        
        # 各种单一效果
        single_effects = [
            (WearEffect(probability=1.0), "磨损"),
            (FadeEffect(probability=1.0), "褪色"),
            (DirtEffect(probability=1.0), "污渍"),
            (TiltTransform(probability=1.0), "倾斜"),
            (ShadowEffect(probability=1.0), "阴影"),
            (ReflectionEffect(probability=1.0), "反光"),
        ]
        
        for effect, label in single_effects:
            result = effect.apply(base_image, intensity=0.7)
            if result:
                effects.append(result)
                labels.append(label)
        
        # 创建网格图
        if len(effects) >= 4:
            grid_width = 3
            grid_height = (len(effects) + grid_width - 1) // grid_width
            
            # 单个图像尺寸
            img_width, img_height = effects[0].size
            
            # 网格图尺寸
            grid_img = Image.new('RGB', 
                               (img_width * grid_width + 20 * (grid_width - 1), 
                                img_height * grid_height + 40 * grid_height), 
                               color=(240, 240, 240))
            
            for i, (effect_img, label) in enumerate(zip(effects, labels)):
                row = i // grid_width
                col = i % grid_width
                
                x = col * (img_width + 20)
                y = row * (img_height + 40) + 30  # 留出标题空间
                
                grid_img.paste(effect_img, (x, y))
                
                # 添加标题
                draw = ImageDraw.Draw(grid_img)
                draw.text((x + img_width // 2, y - 25), label, 
                         fill=(0, 0, 0), anchor="mm")
            
            grid_img.save(os.path.join(output_dir, "effects_comparison_grid.png"))
            print("  效果对比网格图已保存")
        
    except Exception as e:
        print(f"  创建对比网格图失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="车牌变换效果演示")
    parser.add_argument("--output", "-o", default="transform_demo_output", 
                       help="输出目录，默认为 transform_demo_output")
    parser.add_argument("--effects", "-e", nargs="+", 
                       choices=["aging", "perspective", "lighting", "composite", "quick", "real", "grid"],
                       default=["aging", "perspective", "lighting", "composite", "quick"],
                       help="要演示的效果类型")
    
    args = parser.parse_args()
    
    # 创建输出目录
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"车牌变换效果演示")
    print(f"输出目录: {output_dir}")
    print("-" * 50)
    
    # 运行各种演示
    if "aging" in args.effects:
        demo_aging_effects(output_dir)
        print()
    
    if "perspective" in args.effects:
        demo_perspective_effects(output_dir)
        print()
    
    if "lighting" in args.effects:
        demo_lighting_effects(output_dir)
        print()
    
    if "composite" in args.effects:
        demo_composite_effects(output_dir)
        print()
    
    if "quick" in args.effects:
        demo_quick_enhance(output_dir)
        print()
    
    if "real" in args.effects:
        demo_real_plate_generation(output_dir)
        print()
    
    if "grid" in args.effects:
        create_comparison_grid(output_dir)
        print()
    
    print("-" * 50)
    print(f"演示完成！请查看 {output_dir} 目录中的结果图像。")
    
    # 创建README文件
    readme_content = f"""# 车牌变换效果演示结果

本目录包含车牌增强变换系统的各种效果演示。

## 目录结构

- `aging_effects/`: 老化效果演示（磨损、褪色、污渍）
- `perspective_effects/`: 透视变换效果演示（倾斜、透视、旋转、扭曲）
- `lighting_effects/`: 光照效果演示（阴影、反光、夜间、背光）
- `composite_effects/`: 复合变换效果演示（多种效果组合）
- `quick_enhance/`: 快速增强功能演示（不同强度和风格）
- `real_plate_demo/`: 真实车牌生成和变换演示
- `effects_comparison_grid.png`: 效果对比网格图

## 文件命名规则

- `00_original.png`: 原始未处理图像
- `01_effect_intensity_X.Y.png`: 特定效果在强度X.Y下的结果
- `XX_description.png`: 具体效果描述
- `XX_description.txt`: 相关的变换信息记录

## 使用说明

1. 原始图像展示车牌的基础外观
2. 不同强度展示同一效果在不同参数下的表现
3. 组合效果展示多种变换的叠加结果
4. 真实车牌演示展示在实际生成场景中的应用

生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open(os.path.join(output_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write(readme_content)


if __name__ == "__main__":
    main()
