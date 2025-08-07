import argparse
import os
from tqdm import tqdm
import cv2
import logging
import random

from src.generator.integrated_generator import IntegratedPlateGenerator
from src.generator.plate_generator import PlateGenerationConfig
from src.rules.province_codes import ProvinceManager
from src.utils.constants import PlateType

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='根据省份生成车牌')
    
    # 获取所有有效的省份简称用于 choices
    valid_provinces = ProvinceManager.get_all_abbreviations()
    
    parser.add_argument('--province', 
                        required=True, 
                        type=str,
                        choices=valid_provinces,
                        help=f'指定的省份简称. 可选值: {", ".join(valid_provinces)}')
    
    parser.add_argument('--number', 
                        default=10, 
                        type=int, 
                        help='为该省份生成的车牌数量')
    
    parser.add_argument('--save-dir', 
                        default='output_province', 
                        help='车牌图像保存的根目录')
                        
    parser.add_argument('--double-ratio',
                        default=0.2,
                        type=float,
                        help='生成双层车牌的比例 (0.0 到 1.0 之间)')
    
    parser.add_argument('--convert-double-to-single',
                        action='store_true',
                        help='将双层车牌转换为单层显示（上下行拼接）')
                        
    args = parser.parse_args()
    
    if not 0.0 <= args.double_ratio <= 1.0:
        raise ValueError("double-ratio 参数必须在 0.0 和 1.0 之间")
        
    return args


def mkdir(path):
    """创建目录"""
    try:
        os.makedirs(path)
    except OSError:
        pass


if __name__ == '__main__':
    args = parse_args()
    logging.info(f"命令行参数: {args}")

    # 创建特定省份的保存目录
    province_save_path = os.path.join(args.save_dir, args.province)
    mkdir(province_save_path)
    logging.info(f'将在 {province_save_path} 目录下保存生成的车牌图像...')
    
    # 初始化集成生成器
    generator = IntegratedPlateGenerator(plate_models_dir="plate_model", font_models_dir="font_model")
    
    # 定义可能生成双层车牌的类型
    double_layer_types = [PlateType.ORDINARY_YELLOW, PlateType.ORDINARY_TRAILER]

    for i in tqdm(range(args.number), desc=f"正在为省份 '{args.province}' 生成车牌"):
        try:
            # 按指定比例决定是否强制生成双层车牌
            if random.random() < args.double_ratio:
                plate_type = random.choice(double_layer_types)
            else:
                plate_type = None # 随机选择，大概率为单层

            # 配置生成器
            config = PlateGenerationConfig(
                province=args.province,
                plate_type=plate_type,
                convert_double_to_single=args.convert_double_to_single
            )

            # 生成车牌信息和图像
            plate_info, plate_image = generator.generate_plate_with_image(config, enhance=True)
            
            # 格式化文件名
            layer_str = "double" if plate_info.is_double_layer else "single"
            filename = f"{plate_info.plate_number}_{plate_info.background_color}_{layer_str}.jpg"
            filepath = os.path.join(province_save_path, filename)
            cv2.imwrite(filepath, plate_image)

        except Exception as e:
            logging.error(f"为省份 '{args.province}' 生成第 {i+1} 个车牌时失败，跳过。", exc_info=True)
            continue
    
    logging.info(f"成功为省份 '{args.province}' 生成 {args.number} 个车牌图像到 {province_save_path}")
