import argparse
import cv2
import os
from typing import Optional

from src.generator.integrated_generator import IntegratedPlateGenerator
from src.generator.plate_generator import PlateGenerationConfig
from src.rules.special_plate import SpecialPlateSubType, SpecialPlateRuleFactory
from src.utils.constants import PlateType


def parse_args():
    parser = argparse.ArgumentParser(description='特殊车牌生成器')
    
    # 特殊车牌类型选择
    parser.add_argument('--type', choices=['embassy', 'consulate', 'hong_kong_macao', 'military'], 
                       required=True, help='特殊车牌类型')
    
    # 可选参数
    parser.add_argument('--count', type=int, default=100, help='生成数量 (默认: 100)')
    parser.add_argument('--output-dir', default='./output_special_plates', help='输出目录 (默认: 当前目录)')
    parser.add_argument('--special-type', help='特殊子类型 (如军种类型、国家代码等)')
    parser.add_argument('--enhance', action='store_true', help='启用图像增强')
    
    # 指定车牌号码 (可选)
    parser.add_argument('--plate-number', help='指定车牌号码 (如果提供，将忽略其他生成参数)')
    
    args = parser.parse_args()
    return args


def get_plate_type_from_special_type(special_type: str) -> str:
    """根据特殊类型获取车牌类型"""
    type_mapping = {
        'embassy': PlateType.EMBASSY_BLACK,
        'consulate': PlateType.EMBASSY_BLACK,  # 领馆车牌使用相同的黑色类型
        'hong_kong_macao': PlateType.HONGKONG_BLACK,
        'military': PlateType.MILITARY_WHITE
    }
    return type_mapping.get(special_type, PlateType.EMBASSY_BLACK)


def generate_special_plate(generator: IntegratedPlateGenerator, 
                         special_type: str, 
                         special_sub_type: Optional[str] = None,
                         enhance: bool = False):
    """生成单个特殊车牌"""
    # 直接使用特殊车牌规则工厂创建规则
    rule = SpecialPlateRuleFactory.create_rule(special_type)
    
    # 生成车牌信息
    plate_info = rule.generate_plate(
        province="",
        regional_code="", 
        special_type=special_sub_type
    )
    
    # 生成车牌图像
    plate_image = generator.image_composer.compose_plate_image(plate_info, enhance)
    
    return plate_info, plate_image


def main():
    args = parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 使用集成的生成器
    generator = IntegratedPlateGenerator(
        plate_models_dir="plate_model", 
        font_models_dir="font_model"
    )
    
    print(f"开始生成 {args.type} 类型的特殊车牌...")
    
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
            print_plate_info(plate_info)
            
        else:
            # 批量生成随机特殊车牌
            successful_count = 0
            
            for i in range(args.count):
                try:
                    plate_info, plate_image = generate_special_plate(
                        generator, args.type, args.special_type, args.enhance
                    )
                    
                    # 保存图像
                    filename = os.path.join(args.output_dir, f"{plate_info.plate_number}.jpg")
                    cv2.imwrite(filename, plate_image)
                    
                    successful_count += 1
                    print(f"✅ [{successful_count}/{args.count}] 生成: {filename}")
                    
                    if args.count == 1:  # 只有生成一个时才显示详细信息
                        print_plate_info(plate_info)
                        
                except Exception as e:
                    print(f"❌ 第 {i+1} 个车牌生成失败: {e}")
            
            print(f"\n🎉 生成完成! 成功生成 {successful_count}/{args.count} 个特殊车牌")
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")


def print_plate_info(plate_info):
    """打印车牌信息"""
    print("\n--- 车牌信息 ---")
    print(f"  车牌号码: {plate_info.plate_number}")
    
    # 处理车牌类型（可能是枚举或字符串）
    plate_type_str = (plate_info.plate_type.value 
                     if hasattr(plate_info.plate_type, 'value') 
                     else plate_info.plate_type)
    print(f"  车牌类型: {plate_type_str}")
    
    print(f"  省份: {plate_info.province}")
    print(f"  地区代码: {plate_info.regional_code}")
    print(f"  序号: {plate_info.sequence}")
    
    # 处理背景颜色（可能是枚举或字符串）
    bg_color_str = (plate_info.background_color.value 
                   if hasattr(plate_info.background_color, 'value') 
                   else plate_info.background_color)
    print(f"  背景颜色: {bg_color_str}")
    
    # font_color字段可能不存在
    if hasattr(plate_info, 'font_color'):
        print(f"  字体颜色: {plate_info.font_color}")
    
    print(f"  是否双层: {'是' if plate_info.is_double_layer else '否'}")
    if plate_info.special_chars:
        print(f"  特殊字符: {', '.join(plate_info.special_chars)}")
    print("------------------")


if __name__ == '__main__':
    main()
