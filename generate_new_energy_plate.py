#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新能源车牌生成器
基于GA 36-2018标准生成小型和大型新能源汽车号牌
支持纯电动车和非纯电动车（插电式混合动力、燃料电池等）
"""

import argparse
import cv2
import os
import sys
from typing import Optional

from src.generator.integrated_generator import IntegratedPlateGenerator
from src.generator.plate_generator import PlateGenerationConfig
from src.rules.new_energy_plate import NewEnergyPlateSubType, EnergyType, NewEnergyPlateRuleFactory
from src.utils.constants import PlateType


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='新能源车牌生成器 - 支持小型车和大型车')
    
    # 车牌尺寸类型选择 (必选)
    parser.add_argument('--size', choices=['small', 'large'], 
                       required=True, help='新能源车牌尺寸类型')
    
    # 能源类型选择 (可选，默认纯电动)
    parser.add_argument('--energy-type', choices=['pure', 'hybrid'], 
                       default='pure', help='能源类型 (默认: pure纯电动)')
    
    # 基本参数
    parser.add_argument('--count', type=int, default=100, help='生成数量 (默认: 100)')
    parser.add_argument('--output-dir', default='./output_new_energy_plates', help='输出目录 (默认: ./output_new_energy_plates)')
    parser.add_argument('--enhance', action='store_true', help='启用图像增强')
    
    # 指定车牌号码 (可选)
    parser.add_argument('--plate-number', help='指定车牌号码 (如果提供，将忽略其他生成参数)')
    
    # 省份和地区代码
    parser.add_argument('--province', help='指定省份简称 (如: 京, 沪, 粤等)')
    parser.add_argument('--regional-code', help='指定地区代码 (如: A, B, C等)')
    
    # 新能源特有参数
    parser.add_argument('--preferred-letter', help='首选能源标识字母 (如: D, F等)')
    parser.add_argument('--double-letter', action='store_true', 
                       help='使用双字母格式 (仅小型车有效, 如: DF1234)')
    
    # 显示选项
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    parser.add_argument('--show-stats', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    return args


def get_plate_type_from_size(size: str) -> str:
    """根据尺寸类型获取车牌类型"""
    type_mapping = {
        'small': PlateType.NEW_ENERGY_SMALL,
        'large': PlateType.NEW_ENERGY_LARGE
    }
    return type_mapping.get(size, PlateType.NEW_ENERGY_SMALL)


def generate_new_energy_plate(generator: IntegratedPlateGenerator, 
                            size: str,
                            energy_type: str = 'pure',
                            province: Optional[str] = None,
                            regional_code: Optional[str] = None,
                            preferred_letter: Optional[str] = None,
                            double_letter: bool = False,
                            enhance: bool = False):
    """生成单个新能源车牌"""
    # 创建新能源车牌规则
    rule = NewEnergyPlateRuleFactory.create_rule(size + "_car")
    
    # 确定省份和地区代码
    if not province:
        # 如果未指定省份，随机选择
        import random
        province_codes = ["京", "津", "沪", "渝", "冀", "豫", "云", "辽", "黑", "湘", 
                         "皖", "鲁", "新", "苏", "浙", "赣", "鄂", "桂", "甘", "晋", 
                         "蒙", "陕", "吉", "闽", "贵", "粤", "青", "藏", "川", "宁", "琼"]
        province = random.choice(province_codes)
    
    if not regional_code:
        # 如果未指定地区代码，随机选择
        import random
        regional_codes = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        regional_code = random.choice(regional_codes)
    
    # 转换能源类型
    energy_enum = EnergyType.PURE_ELECTRIC if energy_type == 'pure' else EnergyType.NON_PURE_ELECTRIC
    
    # 生成车牌信息
    plate_info = rule.generate_plate(
        province=province,
        regional_code=regional_code,
        energy_type=energy_enum,
        preferred_letter=preferred_letter,
        double_letter=double_letter
    )
    
    # 生成车牌图像
    plate_image = generator.image_composer.compose_plate_image(plate_info, enhance)
    
    return plate_info, plate_image


def validate_args(args):
    """验证命令行参数"""
    errors = []
    
    # 验证双字母选项仅适用于小型车
    if args.double_letter and args.size != 'small':
        errors.append("--double-letter 选项仅适用于小型新能源车 (--size small)")
    
    # 验证首选字母
    if args.preferred_letter:
        if len(args.preferred_letter) != 1 or not args.preferred_letter.isalpha():
            errors.append("--preferred-letter 必须是单个字母")
        
        # 验证字母是否在有效范围内
        valid_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"]  # 排除I和O
        if args.preferred_letter.upper() not in valid_letters:
            errors.append(f"--preferred-letter 必须是有效字母 (可选: {', '.join(valid_letters)})")
    
    # 验证省份
    if args.province:
        valid_provinces = ["京", "津", "沪", "渝", "冀", "豫", "云", "辽", "黑", "湘", 
                          "皖", "鲁", "新", "苏", "浙", "赣", "鄂", "桂", "甘", "晋", 
                          "蒙", "陕", "吉", "闽", "贵", "粤", "青", "藏", "川", "宁", "琼"]
        if args.province not in valid_provinces:
            errors.append(f"无效的省份简称: {args.province}")
    
    # 验证地区代码
    if args.regional_code:
        if len(args.regional_code) != 1 or not args.regional_code.isalpha():
            errors.append("--regional-code 必须是单个字母")
        if args.regional_code.upper() in ["I", "O"]:
            errors.append("--regional-code 不能是字母 I 或 O")
    
    if errors:
        print("❌ 参数验证失败:")
        for error in errors:
            print(f"   {error}")
        sys.exit(1)


def main():
    """主函数"""
    args = parse_args()
    
    # 验证参数
    validate_args(args)
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 使用集成的生成器
    generator = IntegratedPlateGenerator(
        plate_models_dir="plate_model", 
        font_models_dir="font_model"
    )
    
    # 打印配置信息
    size_name = "小型" if args.size == 'small' else "大型"
    energy_name = "纯电动" if args.energy_type == 'pure' else "非纯电动"
    
    print(f"🚗 新能源车牌生成器")
    print(f"   车牌类型: {size_name}新能源汽车号牌")
    print(f"   能源类型: {energy_name}")
    if args.province:
        print(f"   指定省份: {args.province}")
    if args.regional_code:
        print(f"   指定地区: {args.regional_code}")
    if args.preferred_letter:
        print(f"   首选字母: {args.preferred_letter}")
    if args.double_letter:
        print(f"   使用双字母格式")
    print(f"   输出目录: {args.output_dir}")
    print(f"   图像增强: {'启用' if args.enhance else '禁用'}")
    print()
    
    try:
        if args.plate_number:
            # 生成指定车牌
            print(f"生成指定车牌: {args.plate_number}")
            plate_info, plate_image = generator.generate_specific_plate_with_image(
                args.plate_number, args.enhance
            )
            
            # 保存图像
            filename = os.path.join(args.output_dir, f"{plate_info.plate_number}.jpg")
            cv2.imwrite(filename, plate_image)
            
            print(f"✅ 成功生成: {filename}")
            
            if args.verbose:
                print_plate_info(plate_info, args.energy_type)
            
        else:
            # 批量生成新能源车牌
            successful_count = 0
            failed_count = 0
            
            print(f"开始生成 {args.count} 个{size_name}{energy_name}车牌...")
            
            for i in range(args.count):
                try:
                    plate_info, plate_image = generate_new_energy_plate(
                        generator=generator,
                        size=args.size,
                        energy_type=args.energy_type,
                        province=args.province,
                        regional_code=args.regional_code,
                        preferred_letter=args.preferred_letter,
                        double_letter=args.double_letter,
                        enhance=args.enhance
                    )
                    
                    # 保存图像
                    filename = os.path.join(args.output_dir, f"{plate_info.plate_number}.jpg")
                    cv2.imwrite(filename, plate_image)
                    
                    successful_count += 1
                    
                    if args.verbose:
                        print(f"✅ [{successful_count}/{args.count}] 生成: {filename}")
                        if args.count == 1:  # 只有生成一个时才显示详细信息
                            print_plate_info(plate_info, args.energy_type)
                    elif successful_count % 10 == 0:
                        print(f"✅ 已生成 {successful_count}/{args.count} 个车牌...")
                        
                except Exception as e:
                    failed_count += 1
                    if args.verbose:
                        print(f"❌ 第 {i+1} 个车牌生成失败: {e}")
            
            print(f"\n🎉 生成完成!")
            print(f"   成功: {successful_count}/{args.count} 个车牌")
            if failed_count > 0:
                print(f"   失败: {failed_count} 个车牌")
            
            # 显示统计信息
            if args.show_stats:
                print_statistics(args.output_dir)
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        sys.exit(1)


def print_plate_info(plate_info, energy_type: str):
    """打印车牌详细信息"""
    print("\n--- 车牌详细信息 ---")
    print(f"  车牌号码: {plate_info.plate_number}")
    
    # 处理车牌类型（可能是枚举或字符串）
    plate_type_str = (plate_info.plate_type.value 
                     if hasattr(plate_info.plate_type, 'value') 
                     else plate_info.plate_type)
    print(f"  车牌类型: {plate_type_str}")
    
    print(f"  省份简称: {plate_info.province}")
    print(f"  地区代码: {plate_info.regional_code}")
    print(f"  序号: {plate_info.sequence}")
    
    # 处理背景颜色（可能是枚举或字符串）
    bg_color_str = (plate_info.background_color.value 
                   if hasattr(plate_info.background_color, 'value') 
                   else plate_info.background_color)
    print(f"  背景颜色: {bg_color_str}")
    
    # 分析序号模式
    analyze_sequence(plate_info.sequence, energy_type)
    
    print(f"  是否双层: {'是' if plate_info.is_double_layer else '否'}")
    print("----------------------\n")


def analyze_sequence(sequence: str, energy_type: str):
    """分析序号模式和能源类型"""
    print(f"  序号长度: {len(sequence)} 位")
    print(f"  能源类型: {'纯电动' if energy_type == 'pure' else '非纯电动'}")
    
    # 分析序号组成
    letters = [c for c in sequence if c.isalpha()]
    digits = [c for c in sequence if c.isdigit()]
    
    print(f"  字母数量: {len(letters)} 个 {letters if letters else ''}")
    print(f"  数字数量: {len(digits)} 个")
    
    # 分析能源标识字母
    pure_electric_letters = ["D", "A", "B", "C", "E"]
    non_pure_electric_letters = ["F", "G", "H", "J", "K"]
    
    energy_letters = []
    for letter in letters:
        if letter in pure_electric_letters:
            energy_letters.append(f"{letter}(纯电动)")
        elif letter in non_pure_electric_letters:
            energy_letters.append(f"{letter}(非纯电动)")
    
    if energy_letters:
        print(f"  能源标识: {', '.join(energy_letters)}")


def print_statistics(output_dir: str):
    """打印生成统计信息"""
    try:
        files = [f for f in os.listdir(output_dir) if f.endswith('.jpg')]
        print(f"\n📊 生成统计:")
        print(f"   总文件数: {len(files)}")
        
        # 统计不同车牌类型
        small_count = 0
        large_count = 0
        
        for filename in files:
            plate_number = filename.replace('.jpg', '')
            # 简单判断：小型车通常第1位是字母，大型车通常最后1位是字母
            if len(plate_number) >= 8:  # 省份+地区+6位序号
                sequence = plate_number[2:]  # 去掉省份和地区代码
                if len(sequence) == 6:
                    if sequence[0].isalpha():
                        small_count += 1
                    elif sequence[5].isalpha():
                        large_count += 1
        
        print(f"   小型车牌: {small_count} 个")
        print(f"   大型车牌: {large_count} 个")
        
    except Exception as e:
        print(f"❌ 统计信息获取失败: {e}")


if __name__ == '__main__':
    main()
