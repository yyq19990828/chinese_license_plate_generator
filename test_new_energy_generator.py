#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新能源车牌生成器使用示例
演示各种生成场景和功能
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"🔧 命令: {cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("📤 输出:")
        print(result.stdout)
    
    if result.stderr:
        print("⚠️ 错误:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ 命令执行失败，退出码: {result.returncode}")
    else:
        print("✅ 命令执行成功")
    
    return result.returncode == 0

def main():
    """主函数 - 运行各种示例"""
    print("🚗 新能源车牌生成器功能演示")
    print("="*60)
    
    # 确保在正确的目录下
    script_dir = "/home/tyjt/桌面/车牌生成开源项目/chinese_license_plate_generator"
    os.chdir(script_dir)
    
    # 清理输出目录
    output_dir = "./output_new_energy_plates"
    if os.path.exists(output_dir):
        subprocess.run(f"rm -rf {output_dir}/*", shell=True)
    
    examples = [
        {
            "cmd": "python3 generate_new_energy_plate.py --size small --energy-type pure --count 3 --province 京 --regional-code A",
            "desc": "生成3个北京小型纯电动车牌"
        },
        {
            "cmd": "python3 generate_new_energy_plate.py --size large --energy-type hybrid --count 2 --province 沪 --regional-code A",
            "desc": "生成2个上海大型非纯电动车牌"
        },
        {
            "cmd": "python3 generate_new_energy_plate.py --size small --energy-type pure --count 2 --double-letter --province 粤 --regional-code B",
            "desc": "生成2个广东双字母格式小型纯电动车牌"
        },
        {
            "cmd": "python3 generate_new_energy_plate.py --size small --plate-number '川AD12345' --verbose",
            "desc": "生成指定号码的四川新能源车牌并显示详细信息"
        },
        {
            "cmd": "python3 generate_new_energy_plate.py --size large --energy-type hybrid --count 2 --preferred-letter F --province 浙 --regional-code A",
            "desc": "生成2个浙江大型非纯电动车牌，首选字母F"
        },
        {
            "cmd": "python3 generate_new_energy_plate.py --size small --energy-type pure --count 1 --enhance --verbose",
            "desc": "生成1个带图像增强的小型纯电动车牌"
        }
    ]
    
    success_count = 0
    total_count = len(examples)
    
    for i, example in enumerate(examples, 1):
        print(f"\n🔸 示例 {i}/{total_count}")
        success = run_command(example["cmd"], example["desc"])
        if success:
            success_count += 1
        
        # 添加分隔符
        print("\n" + "-" * 60)
    
    # 最后显示统计信息
    print(f"\n🎯 最终演示结果")
    print(f"✅ 成功: {success_count}/{total_count} 个示例")
    
    if success_count == total_count:
        print("🎉 所有示例都执行成功！")
    else:
        print(f"⚠️ 有 {total_count - success_count} 个示例执行失败")
    
    # 显示生成的文件统计
    try:
        files = [f for f in os.listdir(output_dir) if f.endswith('.jpg')]
        print(f"\n📁 输出目录: {output_dir}")
        print(f"📄 生成的车牌图片数量: {len(files)}")
        
        if files:
            print("\n📋 生成的车牌号码列表:")
            for filename in sorted(files):
                plate_number = filename.replace('.jpg', '')
                print(f"   🚗 {plate_number}")
    except Exception as e:
        print(f"❌ 统计文件时出错: {e}")

if __name__ == '__main__':
    main()
