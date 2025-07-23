import argparse
import cv2
import os

from src.generator.integrated_generator import IntegratedPlateGenerator


def parse_args():
    parser = argparse.ArgumentParser(description='指定车牌生成器 (重构版)')
    parser.add_argument('--plate-number', required=True, help='要生成的车牌号码')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print(args)

    # 使用集成的生成器
    generator = IntegratedPlateGenerator(plate_models_dir="plate_model", font_models_dir="font_model")
    
    try:
        # 生成指定车牌的信息和图像
        plate_info, plate_image = generator.generate_specific_plate_with_image(args.plate_number)
        
        # 保存图像
        filename = f"{plate_info.plate_number}.jpg"
        cv2.imwrite(filename, plate_image)
        
        print(f"\n成功生成车牌图像，并保存为: {filename}")
        print("\n--- 车牌分析结果 ---")
        print(f"  车牌号码: {plate_info.plate_number}")
        print(f"  车牌类型: {plate_info.plate_type}")
        print(f"  背景颜色: {plate_info.background_color}")
        print(f"  是否双层: {'是' if plate_info.is_double_layer else '否'}")
        print("--------------------")

    except Exception as e:
        print(f"\n生成失败: {e}")
