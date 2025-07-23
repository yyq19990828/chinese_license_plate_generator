import argparse
import os
from tqdm import tqdm
import cv2
import logging

from src.generator.integrated_generator import IntegratedPlateGenerator

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_args():
    parser = argparse.ArgumentParser(description='中国车牌生成器 (重构版)')
    parser.add_argument('--number', default=100, type=int, help='生成车牌数量')
    parser.add_argument('--save-adr', default='multi_val', help='车牌图像保存路径')
    args = parser.parse_args()
    return args


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError:
        pass


if __name__ == '__main__':
    args = parse_args()
    logging.info(f"命令行参数: {args}")

    logging.info(f'将在 {args.save_adr} 目录下保存生成的车牌图像...')
    mkdir(args.save_adr)
    
    # 使用集成的生成器
    generator = IntegratedPlateGenerator(plate_models_dir="plate_model", font_models_dir="font_model")

    for i in tqdm(range(args.number), desc="正在生成车牌"):
        try:
            # 生成车牌信息和图像
            plate_info, plate_image = generator.generate_plate_with_image()
            
            # 保存图像
            filename = f"{plate_info.plate_number}_{plate_info.background_color}_{plate_info.is_double_layer}.jpg"
            filepath = os.path.join(args.save_adr, filename)
            cv2.imwrite(filepath, plate_image)

        except Exception as e:
            logging.error(f"生成第 {i+1} 个车牌时失败，跳过。", exc_info=True)
            continue
    
    logging.info(f"成功生成 {args.number} 个车牌图像到 {args.save_adr}")
