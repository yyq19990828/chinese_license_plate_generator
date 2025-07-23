#!/usr/bin/env python3
"""
序号生成器测试脚本
用于验证第二阶段序号生成器的功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rules.sequence_generator import (
    OrdinarySequenceGenerator,
    NewEnergySequenceGenerator,
    SequenceGeneratorFactory,
    SequenceType
)
from src.core.exceptions import SequenceGenerationError


def test_ordinary_sequence_generator():
    """测试普通汽车序号生成器"""
    print("=== 测试普通汽车序号生成器 ===")
    
    generator = OrdinarySequenceGenerator()
    
    # 测试基本生成功能
    print("\n1. 测试基本序号生成:")
    for i in range(5):
        try:
            sequence, pattern = generator.generate_sequence("湘", "A")
            print(f"  生成序号: {sequence}, 模式: {pattern.pattern} (顺序: {pattern.order})")
            print(f"    描述: {pattern.description}")
            print(f"    示例: {pattern.example}")
        except Exception as e:
            print(f"  生成失败: {e}")
    
    # 测试指定启用顺序
    print("\n2. 测试指定启用顺序:")
    for order in [1, 2, 3, 4, 5]:
        try:
            sequence, pattern = generator.generate_sequence("京", "A", preferred_order=order)
            print(f"  顺序 {order}: {sequence} - {pattern.description}")
        except Exception as e:
            print(f"  顺序 {order} 生成失败: {e}")
    
    # 测试强制模式
    print("\n3. 测试强制模式:")
    force_patterns = ["DDDDD", "LDDDD", "LLDDD", "DLDDD"]
    for pattern_str in force_patterns:
        try:
            sequence, pattern = generator.generate_sequence("粤", "B", force_pattern=pattern_str)
            print(f"  模式 {pattern_str}: {sequence}")
        except Exception as e:
            print(f"  模式 {pattern_str} 生成失败: {e}")
    
    # 测试模式验证
    print("\n4. 测试模式验证:")
    test_cases = [
        ("12345", "DDDDD", True),
        ("A1234", "LDDDD", True),
        ("AB123", "LLDDD", True),
        ("1A234", "DLDDD", True),
        ("12A34", "DDLDD", True),
        ("A123B", "LDDDL", True),
        ("123AB", "DDDLL", True),
        ("12I34", "DDLDD", False),  # 包含禁用字母I
        ("A12", "LDDDD", False),    # 长度不匹配
    ]
    
    for sequence, pattern, expected in test_cases:
        result = generator.validate_pattern(sequence, pattern)
        status = "✓" if result == expected else "✗"
        print(f"  {status} 序号 '{sequence}' 匹配模式 '{pattern}': {result} (期望: {expected})")
    
    # 测试获取可用顺序
    print(f"\n5. 当前可用的启用顺序: {generator.get_available_orders()}")


def test_new_energy_sequence_generator():
    """测试新能源汽车序号生成器"""
    print("\n=== 测试新能源汽车序号生成器 ===")
    
    generator = NewEnergySequenceGenerator()
    
    # 测试小型新能源车序号生成
    print("\n1. 测试小型新能源车序号生成:")
    print("  纯电动车型:")
    for i in range(3):
        sequence, energy_letter = generator.generate_small_car_sequence(energy_type="pure")
        print(f"    {sequence} (能源标识: {energy_letter})")
    
    print("  非纯电动车型:")
    for i in range(3):
        sequence, energy_letter = generator.generate_small_car_sequence(energy_type="hybrid")
        print(f"    {sequence} (能源标识: {energy_letter})")
    
    print("  双字母模式:")
    for i in range(3):
        sequence, energy_letter = generator.generate_small_car_sequence(energy_type="pure", double_letter=True)
        print(f"    {sequence} (能源标识: {energy_letter})")
    
    # 测试大型新能源车序号生成
    print("\n2. 测试大型新能源车序号生成:")
    print("  纯电动车型:")
    for i in range(3):
        sequence, energy_letter = generator.generate_large_car_sequence(energy_type="pure")
        print(f"    {sequence} (能源标识: {energy_letter})")
    
    print("  非纯电动车型:")
    for i in range(3):
        sequence, energy_letter = generator.generate_large_car_sequence(energy_type="hybrid")
        print(f"    {sequence} (能源标识: {energy_letter})")
    
    # 测试能源类型识别
    print("\n3. 测试能源类型识别:")
    test_sequences = [
        ("D12345", "small", "pure"),
        ("F12345", "small", "hybrid"),
        ("A12345", "small", "pure"),
        ("G12345", "small", "hybrid"),
        ("12345D", "large", "pure"),
        ("12345F", "large", "hybrid"),
    ]
    
    for sequence, car_type, expected_type in test_sequences:
        detected_type = generator.get_energy_type_from_sequence(sequence, car_type)
        status = "✓" if detected_type == expected_type else "✗"
        print(f"  {status} {sequence} ({car_type}): {detected_type} (期望: {expected_type})")
    
    # 测试序号验证
    print("\n4. 测试序号验证:")
    validation_cases = [
        ("D12345", "small", True),   # 小型纯电动
        ("F12345", "small", True),   # 小型非纯电动
        ("AB1234", "small", True),   # 小型双字母
        ("12345D", "large", True),   # 大型纯电动
        ("12345F", "large", True),   # 大型非纯电动
        ("I12345", "small", False),  # 包含禁用字母I
        ("D1234", "small", False),   # 长度不正确
        ("1234AD", "large", False),  # 大型车格式错误
        ("X12345", "small", False),  # 无效能源标识字母
    ]
    
    for sequence, car_type, expected in validation_cases:
        result = generator.validate_new_energy_sequence(sequence, car_type)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {sequence} ({car_type}): {result} (期望: {expected})")


def test_sequence_generator_factory():
    """测试序号生成器工厂"""
    print("\n=== 测试序号生成器工厂 ===")
    
    # 测试按序号类型创建
    print("\n1. 测试按序号类型创建生成器:")
    sequence_types = [
        SequenceType.ORDINARY_5_DIGIT,
        SequenceType.NEW_ENERGY_SMALL_6_DIGIT,
        SequenceType.NEW_ENERGY_LARGE_6_DIGIT,
    ]
    
    for seq_type in sequence_types:
        try:
            generator = SequenceGeneratorFactory.create_generator(seq_type)
            print(f"  ✓ {seq_type.value}: {type(generator).__name__}")
        except Exception as e:
            print(f"  ✗ {seq_type.value}: {e}")
    
    # 测试按车牌类型创建
    print("\n2. 测试按车牌类型创建生成器:")
    plate_types = [
        "ordinary_large",
        "ordinary_small", 
        "trailer",
        "coach",
        "police",
        "new_energy_small",
        "new_energy_large",
    ]
    
    for plate_type in plate_types:
        try:
            generator = SequenceGeneratorFactory.get_generator_for_plate_type(plate_type)
            print(f"  ✓ {plate_type}: {type(generator).__name__}")
        except Exception as e:
            print(f"  ✗ {plate_type}: {e}")


def test_resource_management():
    """测试资源管理功能"""
    print("\n=== 测试资源管理功能 ===")
    
    generator = OrdinarySequenceGenerator()
    resource_manager = generator.resource_manager
    
    # 测试使用率管理
    print("\n1. 测试使用率管理:")
    pattern_key = "DDDDD_1"
    
    print(f"  初始使用率: {resource_manager.get_usage_rate(pattern_key)}")
    print(f"  是否可用: {resource_manager.is_pattern_available(pattern_key)}")
    
    # 模拟使用率增加
    resource_manager.update_usage_rate(pattern_key, 0.3)
    print(f"  更新使用率到30%: {resource_manager.get_usage_rate(pattern_key)}")
    print(f"  是否可用: {resource_manager.is_pattern_available(pattern_key)}")
    
    resource_manager.update_usage_rate(pattern_key, 0.7)
    print(f"  更新使用率到70%: {resource_manager.get_usage_rate(pattern_key)}")
    print(f"  是否可用: {resource_manager.is_pattern_available(pattern_key)}")
    
    # 测试可用模式获取
    print(f"\n2. 当前可用模式数量: {len(resource_manager.get_available_patterns(generator.patterns))}")


def main():
    """主测试函数"""
    print("开始测试序号生成器模块...")
    
    try:
        test_ordinary_sequence_generator()
        test_new_energy_sequence_generator()
        test_sequence_generator_factory()
        test_resource_management()
        
        print("\n" + "="*50)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())