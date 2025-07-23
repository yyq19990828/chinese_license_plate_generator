#!/usr/bin/env python3
"""
第四阶段重构演示脚本

展示重构后的车牌生成器系统的主要功能和改进。
"""

import os
import sys

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_basic_generation():
    """演示基础车牌生成功能"""
    print("🚗 基础车牌生成演示")
    print("=" * 40)
    
    from src.generator import PlateGenerator, PlateGenerationConfig
    from src.utils.constants import PlateType
    
    generator = PlateGenerator()
    
    # 1. 随机生成
    print("1. 随机生成普通车牌:")
    for i in range(3):
        try:
            plate_info = generator.generate_random_plate()
            print(f"   {plate_info.plate_number} | {plate_info.plate_type} | {plate_info.background_color}")
        except Exception as e:
            print(f"   生成失败: {e}")
    
    # 2. 指定类型生成
    print("\n2. 指定类型生成:")
    configs = [
        (PlateType.POLICE_WHITE, "警用车牌"),
        (PlateType.NEW_ENERGY_GREEN, "新能源车牌"),
    ]
    
    for plate_type, desc in configs:
        try:
            config = PlateGenerationConfig(plate_type=plate_type)
            plate_info = generator.generate_random_plate(config)
            print(f"   {desc}: {plate_info.plate_number}")
        except Exception as e:
            print(f"   {desc}: 生成失败 - {e}")
    
    # 3. 指定省份生成
    print("\n3. 指定省份生成:")
    config = PlateGenerationConfig(province="京")
    for i in range(3):
        try:
            plate_info = generator.generate_random_plate(config)
            print(f"   {plate_info.plate_number}")
        except Exception as e:
            print(f"   生成失败: {e}")

def demo_integrated_generation():
    """演示集成生成器功能"""
    print("\n📸 集成车牌生成演示")
    print("=" * 40)
    
    # 检查资源目录
    if not os.path.exists("plate_model") or not os.path.exists("font_model"):
        print("⚠️  资源目录不存在，跳过图像生成演示")
        return
    
    from src.generator import create_generator
    
    generator = create_generator()
    
    # 1. 生成带图像的车牌
    print("1. 生成车牌图像:")
    try:
        plate_info, plate_image = generator.generate_plate_with_image()
        print(f"   成功: {plate_info.plate_number} | 图像尺寸: {plate_image.shape}")
        
        # 保存图像示例
        save_path = generator.save_plate_image(plate_image, plate_info, "demo_output")
        print(f"   已保存到: {save_path}")
        
    except Exception as e:
        print(f"   生成失败: {e}")
    
    # 2. 指定号码生成图像
    print("\n2. 指定号码生成图像:")
    test_plates = ["京A12345", "沪B67890"]
    
    for plate_number in test_plates:
        try:
            plate_info, plate_image = generator.generate_specific_plate_with_image(plate_number)
            print(f"   {plate_number}: 成功 | 图像尺寸: {plate_image.shape}")
        except Exception as e:
            print(f"   {plate_number}: 失败 - {str(e)[:50]}...")

def demo_system_features():
    """演示系统特性"""
    print("\n⚙️  系统特性演示")
    print("=" * 40)
    
    from src.generator import create_generator
    
    generator = create_generator()
    
    # 1. 系统统计
    print("1. 系统统计信息:")
    stats = generator.get_system_stats()
    if stats['font_cache_stats']:
        cache_stats = stats['font_cache_stats']
        print(f"   字体缓存: {cache_stats['cache_size']}/{cache_stats['max_size']}")
        print(f"   缓存命中次数: {cache_stats['total_access']}")
    print(f"   支持字符数: {stats['supported_characters']}")
    
    # 2. 支持的车牌类型
    print("\n2. 支持的车牌类型:")
    types_info = generator.get_plate_types_info()
    for category, types in types_info.items():
        print(f"   {category}: {len(types)} 种")
        for plate_type in types:
            print(f"     - {plate_type}")

def demo_architecture_improvements():
    """演示架构改进"""
    print("\n🏗️  架构改进演示")
    print("=" * 40)
    
    print("1. 模块化设计:")
    print("   ✅ 车牌生成器 (PlateGenerator) - 统一生成接口")
    print("   ✅ 图像合成器 (ImageComposer) - 智能布局和颜色")
    print("   ✅ 字体管理器 (FontManager) - 缓存和优化")
    print("   ✅ 集成生成器 (IntegratedPlateGenerator) - 完整解决方案")
    
    print("\n2. 新功能特性:")
    print("   ✅ 车牌类型自动识别")
    print("   ✅ 基于车牌类型的自动布局计算")
    print("   ✅ 字符颜色自动判断 (红色特殊字符)")
    print("   ✅ 双层车牌支持")
    print("   ✅ 字体资源预加载和缓存")
    print("   ✅ 不同车牌尺寸适配")
    
    print("\n3. 向后兼容性:")
    print("   ✅ 保持现有接口可用")
    print("   ✅ 支持原有资源文件格式")
    print("   ✅ 渐进式迁移支持")

def main():
    """主演示函数"""
    print("🎉 第四阶段重构成果演示")
    print("🚀 基于GA 36-2018标准的车牌生成器系统")
    print("=" * 60)
    
    # 运行各个演示
    demo_basic_generation()
    demo_integrated_generation()
    demo_system_features()
    demo_architecture_improvements()
    
    print("\n" + "=" * 60)
    print("✨ 第四阶段重构已完成！")
    print("📋 主要成就:")
    print("   • 重构了主生成器，使用新规则系统")
    print("   • 优化了图像合成器，支持智能布局")
    print("   • 改进了字体管理器，实现缓存优化")
    print("   • 创建了集成生成器，提供完整解决方案")
    print("   • 修复了规则系统兼容性问题")
    print("\n🎯 系统现已支持:")
    print("   • 统一的车牌生成接口")
    print("   • 车牌类型自动识别")
    print("   • 智能图像合成")
    print("   • 字体资源优化管理")
    print("   • 高性能批量生成")

if __name__ == "__main__":
    main()