#!/usr/bin/env python3
"""
第四阶段测试脚本

测试重构后的生成器系统功能。
"""

import os
import sys
import traceback

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import PlateGenerator, PlateGenerationConfig, IntegratedPlateGenerator, create_generator
from src.utils.constants import PlateType


def test_plate_generator():
    """测试车牌生成器"""
    print("=== 测试车牌生成器 ===")
    
    try:
        generator = PlateGenerator()
        
        # 测试随机生成
        print("1. 测试随机生成")
        for i in range(5):
            plate_info = generator.generate_random_plate()
            print(f"  {plate_info.plate_number} | {plate_info.plate_type} | {plate_info.background_color}")
        
        # 测试指定省份生成
        print("\n2. 测试指定省份生成")
        config = PlateGenerationConfig(province="京")
        for i in range(3):
            plate_info = generator.generate_random_plate(config)
            print(f"  {plate_info.plate_number} | {plate_info.plate_type}")
        
        # 测试指定车牌类型生成
        print("\n3. 测试指定车牌类型生成")
        config = PlateGenerationConfig(plate_type=PlateType.NEW_ENERGY_GREEN)
        for i in range(3):
            plate_info = generator.generate_random_plate(config)
            print(f"  {plate_info.plate_number} | {plate_info.plate_type}")
        
        # 测试指定号码解析
        print("\n4. 测试指定号码解析")
        test_plates = ["京A12345", "沪AD1234E", "粤B港123", "使123456"]
        for plate_number in test_plates:
            try:
                plate_info = generator.generate_specific_plate(plate_number)
                print(f"  {plate_info.plate_number} | {plate_info.plate_type} | {plate_info.background_color}")
            except Exception as e:
                print(f"  {plate_number} - 解析失败: {str(e)}")
        
        # 测试批量生成
        print("\n5. 测试批量生成")
        plates = generator.generate_batch_plates(10)
        print(f"  批量生成了 {len(plates)} 个车牌")
        
        print("✅ 车牌生成器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 车牌生成器测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_integrated_generator():
    """测试集成生成器"""
    print("\n=== 测试集成生成器 ===")
    
    try:
        # 检查资源目录是否存在
        if not os.path.exists("plate_model") or not os.path.exists("font_model"):
            print("⚠️  资源目录不存在，跳过图像生成测试")
            return True
        
        generator = create_generator()
        
        # 测试生成带图像的车牌
        print("1. 测试生成单个车牌图像")
        try:
            plate_info, plate_image = generator.generate_plate_with_image()
            print(f"  生成成功: {plate_info.plate_number} | 图像尺寸: {plate_image.shape}")
        except Exception as e:
            print(f"  生成失败: {str(e)}")
        
        # 测试指定号码生成
        print("\n2. 测试指定号码生成图像")
        try:
            plate_info, plate_image = generator.generate_specific_plate_with_image("京A12345")
            print(f"  生成成功: {plate_info.plate_number} | 图像尺寸: {plate_image.shape}")
        except Exception as e:
            print(f"  生成失败: {str(e)}")
        
        # 测试系统统计
        print("\n3. 测试系统统计")
        stats = generator.get_system_stats()
        print(f"  系统统计: {stats}")
        
        # 测试车牌类型信息
        print("\n4. 测试车牌类型信息")
        types_info = generator.get_plate_types_info()
        print(f"  支持的车牌类型数量: {sum(len(v) for v in types_info.values())}")
        
        print("✅ 集成生成器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 集成生成器测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_generation_config():
    """测试生成配置"""
    print("\n=== 测试生成配置 ===")
    
    try:
        generator = PlateGenerator()
        
        # 测试各种配置组合
        configs = [
            PlateGenerationConfig(),  # 默认配置
            PlateGenerationConfig(province="沪"),  # 指定省份
            PlateGenerationConfig(plate_type=PlateType.POLICE_WHITE),  # 指定类型
            PlateGenerationConfig(province="粤", plate_type=PlateType.ORDINARY_BLUE),  # 组合配置
        ]
        
        for i, config in enumerate(configs):
            print(f"  配置 {i+1}:")
            try:
                plate_info = generator.generate_random_plate(config)
                print(f"    结果: {plate_info.plate_number} | {plate_info.plate_type}")
            except Exception as e:
                print(f"    失败: {str(e)}")
        
        print("✅ 生成配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 生成配置测试失败: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚗 开始第四阶段生成器重构测试")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(test_plate_generator())
    test_results.append(test_integrated_generator())
    test_results.append(test_generation_config())
    
    # 输出总结
    print("\n" + "=" * 50)
    print("📊 测试总结:")
    print(f"  通过: {sum(test_results)}/{len(test_results)}")
    
    if all(test_results):
        print("🎉 第四阶段重构测试全部通过！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关代码")
        return 1


if __name__ == "__main__":
    exit(main())