#!/usr/bin/env python3
"""
增强配置示例

展示如何使用不同类型的enhance参数来生成车牌图像。
"""

import os
import cv2
from src.generator.integrated_generator import IntegratedPlateGenerator
from src.generator.plate_generator import PlateGenerationConfig
from src.transform.transform_config import TransformConfig, TransformParams, TransformType
from src.core.enhance_config import EnhanceConfig
from src.utils.constants import PlateType

def main():
    """主函数：演示不同的enhance配置用法"""
    
    # 初始化生成器
    generator = IntegratedPlateGenerator("plate_model", "font_model")
    
    # 创建输出目录
    output_dir = "enhance_examples"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== 增强配置示例 ===")
    
    # 配置生成参数
    config = PlateGenerationConfig(
        province="京",
        plate_type=PlateType.ORDINARY_BLUE
    )
    
    # 示例1: 禁用增强 (enhance=False)
    print("\n1. 生成无增强车牌...")
    plate_info, plate_image = generator.generate_plate_with_image(config, enhance=False)
    filename = f"{plate_info.plate_number}_no_enhance.jpg"
    cv2.imwrite(os.path.join(output_dir, filename), plate_image)
    print(f"   保存到: {filename}")
    
    # 示例2: 启用默认增强 (enhance=True)  
    print("\n2. 生成默认增强车牌...")
    plate_info, plate_image = generator.generate_plate_with_image(config, enhance=True)
    filename = f"{plate_info.plate_number}_default_enhance.jpg"
    cv2.imwrite(os.path.join(output_dir, filename), plate_image)
    print(f"   保存到: {filename}")
    
    # 示例3: 使用EnhanceConfig包装自定义配置 - 仅老化效果
    print("\n3. 生成仅老化效果的车牌（使用EnhanceConfig）...")
    aging_transform_config = TransformConfig()
    # 清除所有变换
    aging_transform_config._transforms.clear()
    # 只添加老化效果
    aging_transform_config.add_transform(TransformParams(
        name="heavy_aging",
        transform_type=TransformType.AGING,
        probability=1.0,  # 100%概率应用
        intensity_range=(0.5, 0.8),  # 较强的老化效果
        custom_params={
            "wear_strength": 0.6,
            "fade_factor": 0.5,
            "dirt_density": 0.1
        }
    ))
    
    # 使用EnhanceConfig包装TransformConfig
    aging_enhance_config = EnhanceConfig(aging_transform_config)
    print(f"   增强配置状态: {aging_enhance_config}")
    
    plate_info, plate_image = generator.generate_plate_with_image(config, enhance=aging_enhance_config)
    filename = f"{plate_info.plate_number}_aging_only.jpg"
    cv2.imwrite(os.path.join(output_dir, filename), plate_image)
    print(f"   保存到: {filename}")
    
    # 示例4: 直接传递TransformConfig（向后兼容）
    print("\n4. 生成强透视变换车牌（直接传递TransformConfig）...")
    perspective_config = TransformConfig()
    perspective_config._transforms.clear()
    perspective_config.add_transform(TransformParams(
        name="strong_perspective",
        transform_type=TransformType.PERSPECTIVE,
        probability=1.0,
        intensity_range=(0.6, 0.9),
        custom_params={
            "max_angle": 25,  # 更大的倾斜角度
            "perspective_strength": 0.4,
            "max_rotation": 15
        }
    ))
    
    # 直接传递TransformConfig（内部会自动转换为EnhanceConfig）
    plate_info, plate_image = generator.generate_plate_with_image(config, enhance=perspective_config)
    filename = f"{plate_info.plate_number}_strong_perspective.jpg"
    cv2.imwrite(os.path.join(output_dir, filename), plate_image)
    print(f"   保存到: {filename}")
    
    # 示例5: 使用EnhanceConfig的便利函数创建组合配置
    print("\n5. 生成组合效果车牌（使用便利函数）...")
    
    # 创建基础变换配置
    combo_transform_config = TransformConfig()
    combo_transform_config._transforms.clear()
    
    # 添加轻度老化
    combo_transform_config.add_transform(TransformParams(
        name="light_aging",
        transform_type=TransformType.AGING,
        probability=0.8,
        intensity_range=(0.2, 0.4),
        custom_params={"wear_strength": 0.2, "fade_factor": 0.8}
    ))
    
    # 添加轻度透视
    combo_transform_config.add_transform(TransformParams(
        name="light_perspective", 
        transform_type=TransformType.PERSPECTIVE,
        probability=0.6,
        intensity_range=(0.1, 0.3),
        custom_params={"max_angle": 8, "max_rotation": 5}
    ))
    
    # 添加光照效果
    combo_transform_config.add_transform(TransformParams(
        name="lighting",
        transform_type=TransformType.LIGHTING,
        probability=0.5,
        intensity_range=(0.2, 0.5),
        custom_params={"shadow_strength": 0.3}
    ))
    
    # 设置全局概率
    combo_transform_config.set_global_probability(0.7)  # 降低整体应用概率
    combo_transform_config.set_max_concurrent_transforms(2)  # 最多同时应用2个变换
    
    # 使用便利函数创建EnhanceConfig
    from src.core.enhance_config import create_enhance_config
    combo_enhance_config = create_enhance_config(combo_transform_config)
    print(f"   增强配置状态: {combo_enhance_config}")
    
    plate_info, plate_image = generator.generate_plate_with_image(config, enhance=combo_enhance_config)
    filename = f"{plate_info.plate_number}_custom_combo.jpg"
    cv2.imwrite(os.path.join(output_dir, filename), plate_image)
    print(f"   保存到: {filename}")
    
    # 示例6: 从配置文件加载
    print("\n6. 创建并使用配置文件...")
    
    # 保存配置到文件
    config_file = os.path.join(output_dir, "my_transform_config.json")
    combo_transform_config.save_to_file(config_file)
    print(f"   配置已保存到: my_transform_config.json")
    
    # 从文件加载配置并使用EnhanceConfig
    loaded_transform_config = TransformConfig(config_file)
    loaded_enhance_config = EnhanceConfig(loaded_transform_config)
    print(f"   从文件加载的配置: {loaded_enhance_config}")
    
    plate_info, plate_image = generator.generate_plate_with_image(config, enhance=loaded_enhance_config)
    filename = f"{plate_info.plate_number}_from_config_file.jpg"
    cv2.imwrite(os.path.join(output_dir, filename), plate_image)
    print(f"   保存到: {filename}")
    
    print(f"\n所有示例车牌已生成到 '{output_dir}' 目录")
    print("\n=== 配置类型总结 ===")
    print("• enhance=False                    -> 无增强")  
    print("• enhance=True                     -> 默认增强配置")
    print("• enhance=TransformConfig          -> 自定义变换配置（自动转换）")
    print("• enhance=EnhanceConfig(...)       -> 显式使用EnhanceConfig")
    print("• create_enhance_config(...)       -> 便利函数创建")
    print("• 支持从JSON文件加载配置")
    print("• 支持精确控制每种变换的概率和参数")
    print("\n=== EnhanceConfig的优势 ===")
    print("• 统一的配置管理接口")
    print("• 严格的类型验证")
    print("• 清晰的状态显示")
    print("• 完全的向后兼容性")
    

if __name__ == "__main__":
    main()