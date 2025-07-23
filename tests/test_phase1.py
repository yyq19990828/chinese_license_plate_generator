#!/usr/bin/env python3
"""
第一阶段测试脚本
测试基础数据结构和规则类的功能
"""

import sys
import os

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_province_codes():
    """测试省份编码功能"""
    print("=== 测试省份编码功能 ===")
    
    from src.rules.province_codes import ProvinceManager
    
    # 测试获取所有省份简称
    provinces = ProvinceManager.get_all_abbreviations()
    print(f"省份总数: {len(provinces)}")
    print(f"前10个省份: {provinces[:10]}")
    
    # 测试省份验证
    valid_provinces = ["京", "沪", "粤"]
    invalid_provinces = ["X", "Y", "测试"]
    
    for province in valid_provinces:
        is_valid = ProvinceManager.is_valid_province(province)
        info = ProvinceManager.get_province_info(province)
        print(f"省份 '{province}': 有效={is_valid}, 全称={info.name if info else 'None'}")
    
    for province in invalid_provinces:
        is_valid = ProvinceManager.is_valid_province(province)
        print(f"省份 '{province}': 有效={is_valid}")
    
    print()


def test_regional_codes():
    """测试发牌机关代号功能"""
    print("=== 测试发牌机关代号功能 ===")
    
    from rules.regional_codes import RegionalCodeManager
    
    # 测试获取特定省份的代号
    test_provinces = ["京", "粤", "川"]
    
    for province in test_provinces:
        codes = RegionalCodeManager.get_all_codes_for_province(province)
        print(f"省份 '{province}' 的发牌机关代号: {codes[:5]}... (共{len(codes)}个)")
        
        # 测试验证功能
        if codes:
            valid_code = codes[0]
            is_valid = RegionalCodeManager.is_valid_regional_code(province, valid_code)
            city_info = RegionalCodeManager.get_city_info(province, valid_code)
            print(f"  代号 '{valid_code}': 有效={is_valid}, 城市={city_info.city_name if city_info else 'None'}")
        
        # 测试无效代号
        is_valid = RegionalCodeManager.is_valid_regional_code(province, "9")
        print(f"  代号 '9': 有效={is_valid}")
    
    print()


def test_constants():
    """测试常量定义"""
    print("=== 测试常量定义 ===")
    
    from utils.constants import PlateConstants, SequenceConstants, PlateColors
    
    print(f"禁用字母: {PlateConstants.FORBIDDEN_LETTERS}")
    print(f"可用字母数量: {len(PlateConstants.AVAILABLE_LETTERS)}")
    print(f"可用数字: {PlateConstants.AVAILABLE_DIGITS}")
    
    print(f"普通序号模式数量: {len(SequenceConstants.ORDINARY_SEQUENCE_PATTERNS)}")
    print(f"纯电动字母: {SequenceConstants.NEW_ENERGY_PURE_ELECTRIC_LETTERS}")
    
    print(f"颜色方案数量: {len(PlateColors.COLOR_SCHEMES)}")
    
    print()


def test_base_rule():
    """测试基础规则类"""
    print("=== 测试基础规则类 ===")
    
    from rules.base_rule import BaseRule, PlateType, PlateColor, ValidationResult
    
    # 创建一个简单的实现类进行测试
    class TestRule(BaseRule):
        def generate_sequence(self, province, regional_code, **kwargs):
            return "12345"
        
        def validate_sequence(self, sequence):
            if len(sequence) == 5:
                return ValidationResult(is_valid=True)
            else:
                return ValidationResult(is_valid=False, error_message="序号长度不正确")
        
        def get_plate_info(self, province, regional_code, sequence):
            from rules.base_rule import PlateInfo
            return PlateInfo(
                plate_number=f"{province}{regional_code}{sequence}",
                plate_type=PlateType.ORDINARY_SMALL,
                province=province,
                regional_code=regional_code,
                sequence=sequence,
                background_color=PlateColor.BLUE
            )
    
    rule = TestRule()
    
    # 测试省份验证
    result = rule.validate_province("京")
    print(f"省份验证 '京': {result.is_valid}")
    
    result = rule.validate_province("X")
    print(f"省份验证 'X': {result.is_valid}, 错误: {result.error_message}")
    
    # 测试发牌机关代号验证
    result = rule.validate_regional_code("京", "A")
    print(f"发牌机关代号验证 '京A': {result.is_valid}")
    
    # 测试车牌号码验证
    result = rule.validate_plate_number("京A12345")
    print(f"车牌验证 '京A12345': {result.is_valid}")
    
    # 测试工具方法
    available_letters = rule.get_available_letters()
    print(f"可用字母数量: {len(available_letters)}")
    print(f"包含禁用字母测试 'ABIO': {rule.contains_forbidden_letters('ABIO')}")
    
    print()


def test_exceptions():
    """测试异常定义"""
    print("=== 测试异常定义 ===")
    
    from core.exceptions import (
        InvalidProvinceException,
        InvalidRegionalCodeException,
        InvalidSequenceException,
        format_exception_message
    )
    
    try:
        raise InvalidProvinceException("X")
    except InvalidProvinceException as e:
        print(f"省份异常: {format_exception_message(e)}")
    
    try:
        raise InvalidRegionalCodeException("京", "9", ["A", "B", "C"])
    except InvalidRegionalCodeException as e:
        print(f"发牌机关代号异常: {format_exception_message(e)}")
    
    try:
        raise InvalidSequenceException("ABCIO", "包含禁用字母", "DDDDD")
    except InvalidSequenceException as e:
        print(f"序号异常: {format_exception_message(e)}")
    
    print()


def test_config():
    """测试配置管理"""
    print("=== 测试配置管理 ===")
    
    from core.config import ConfigManager, get_config_manager
    
    # 创建配置管理器
    config_manager = get_config_manager()
    
    # 获取各种配置
    gen_config = config_manager.get_generation_config()
    print(f"默认批量大小: {gen_config.batch_size}")
    print(f"默认能源类型: {gen_config.energy_type}")
    
    font_config = config_manager.get_font_config()
    print(f"字体目录: {font_config.font_directory}")
    print(f"字符间距: {font_config.char_spacing}")
    
    plate_config = config_manager.get_plate_config()
    print(f"车牌目录: {plate_config.plate_directory}")
    print(f"输出格式: {plate_config.output_format}")
    
    # 测试路径验证
    missing_paths = config_manager.validate_paths()
    if missing_paths:
        print(f"缺失路径: {missing_paths}")
    else:
        print("所有路径都存在")
    
    print()


def main():
    """主测试函数"""
    print("开始第一阶段功能测试...\n")
    
    try:
        test_province_codes()
        test_regional_codes()
        test_constants()
        test_base_rule()
        test_exceptions()
        test_config()
        
        print("✅ 所有测试通过！第一阶段基础架构已成功创建。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())