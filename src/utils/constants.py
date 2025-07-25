"""
常量定义模块
包含车牌生成和验证相关的所有常量
"""

from typing import Dict, List, Tuple
from enum import Enum


# 基础常量
class PlateConstants:
    """车牌基础常量"""
    
    # 禁用字母（符合GA 36-2018标准）
    FORBIDDEN_LETTERS: List[str] = ["I", "O"]
    
    # 所有可用字母（排除I、O）
    AVAILABLE_LETTERS: List[str] = [
        "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", 
        "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", 
        "W", "X", "Y", "Z"
    ]
    
    # 所有可用数字
    AVAILABLE_DIGITS: List[str] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    
    # 特殊字符
    SPECIAL_CHARS: Dict[str, str] = {
        "USE": "使",      # 使馆
        "LING": "领",     # 领馆
        "POLICE": "警",   # 警用
        "LEARN": "学",    # 教练
        "TRAILER": "挂",  # 挂车
        "HONG_KONG": "港", # 港澳入出境
        "MACAO": "澳",    # 港澳入出境
        "TEST": "试",     # 试验
        "SUPER": "超",    # 特型车
    }


# 序号生成规则常量
class SequenceConstants:
    """序号生成相关常量"""
    
    # 普通汽车5位序号的启用顺序（基于GA 36-2018）
    ORDINARY_SEQUENCE_PATTERNS: List[Dict[str, any]] = [
        {"order": 1, "pattern": "DDDDD", "description": "5位都是数字", "example": "12345"},
        {"order": 2, "pattern": "LDDDD", "description": "第1位是字母，其余是数字", "example": "A1234"},
        {"order": 3, "pattern": "LLDDD", "description": "第1、2位是字母，其余是数字", "example": "AB123"},
        {"order": 4, "pattern": "DLDDD", "description": "第2位是字母，其余是数字", "example": "1A234"},
        {"order": 5, "pattern": "DDLDD", "description": "第3位是字母，其余是数字", "example": "12A34"},
        {"order": 6, "pattern": "DDDLD", "description": "第4位是字母，其余是数字", "example": "123A4"},
        {"order": 7, "pattern": "DDDDL", "description": "第5位是字母，其余是数字", "example": "1234A"},
        {"order": 8, "pattern": "LDDDD", "description": "第1、5位是字母，其余是数字", "example": "A123B"},
        {"order": 9, "pattern": "DDDLL", "description": "第4、5位是字母，其余是数字", "example": "123AB"},
        {"order": 10, "pattern": "LDLDD", "description": "第1、3位是字母，其余是数字", "example": "A1B23"},
    ]
    
    # 新能源汽车纯电动字母（首位或末位）
    NEW_ENERGY_PURE_ELECTRIC_LETTERS: List[str] = ["D", "A", "B", "C", "E"]
    
    # 新能源汽车非纯电动字母（首位或末位）
    NEW_ENERGY_NON_PURE_ELECTRIC_LETTERS: List[str] = ["F", "G", "H", "J", "K"]
    
    # 序号资源使用率阈值（60%后可启用下一种组合方式）
    RESOURCE_USAGE_THRESHOLD: float = 0.6


# 车牌尺寸常量（单位：毫米）
class PlateDimensions:
    """车牌尺寸常量"""
    
    # 标准车牌尺寸
    SIZES: Dict[str, Tuple[int, int]] = {
        # 汽车号牌
        "large_car_front": (440, 140),      # 大型汽车号牌前牌
        "large_car_rear": (440, 220),       # 大型汽车号牌后牌
        "small_car": (440, 140),            # 小型汽车号牌
        "trailer": (440, 220),              # 挂车号牌
        "coach": (440, 140),                # 教练汽车号牌
        "police": (440, 140),               # 警用汽车号牌
        "embassy": (440, 140),              # 使馆汽车号牌
        "consulate": (440, 140),            # 领馆汽车号牌
        "hong_kong_macao": (440, 140),      # 港澳入出境车号牌
        
        # 新能源汽车号牌（宽度增加40mm）
        "new_energy_small": (480, 140),     # 小型新能源汽车号牌
        "new_energy_large": (480, 140),     # 大型新能源汽车号牌
        
        # 摩托车号牌
        "motorcycle": (220, 140),           # 普通摩托车号牌
        "light_motorcycle": (220, 140),     # 轻便摩托车号牌
        "embassy_motorcycle": (220, 140),   # 使馆摩托车号牌
        "consulate_motorcycle": (220, 140), # 领馆摩托车号牌
        "coach_motorcycle": (220, 140),     # 教练摩托车号牌
        "police_motorcycle": (220, 140),    # 警用摩托车号牌
        
        # 其他类型
        "low_speed_vehicle": (300, 165),    # 低速车号牌
        "temporary": (220, 140),            # 临时行驶车号牌
        "temporary_entry": (220, 140),      # 临时入境汽车号牌
        "temporary_entry_motorcycle": (88, 60),  # 临时入境摩托车号牌
    }


# 车牌颜色配置常量
class PlateColors:
    """车牌颜色配置常量"""
    
    COLOR_SCHEMES: Dict[str, Dict[str, str]] = {
        "blue": {
            "background": "#1E90FF",    # 蓝色背景
            "text": "#FFFFFF",          # 白色文字
            "border": "#000000",        # 黑色边框
        },
        "yellow": {
            "background": "#FFD700",    # 黄色背景
            "text": "#000000",          # 黑色文字
            "border": "#000000",        # 黑色边框
        },
        "white": {
            "background": "#FFFFFF",    # 白色背景
            "text": "#000000",          # 黑色文字
            "border": "#000000",        # 黑色边框
            "special_red": "#FF0000",   # 红色特殊字符（如"警"）
        },
        "black": {
            "background": "#000000",    # 黑色背景
            "text": "#FFFFFF",          # 白色文字
            "border": "#FFFFFF",        # 白色边框
            "special_red": "#FF0000",   # 红色特殊字符（如"使"、"领"）
        },
        "green": {
            "background": "#32CD32",    # 渐变绿色背景
            "text": "#000000",          # 黑色文字
            "border": "#000000",        # 黑色边框
        },
        "yellow_green": {
            "background_top": "#FFD700",    # 上半部分黄色
            "background_bottom": "#32CD32", # 下半部分绿色
            "text": "#000000",              # 黑色文字
            "border": "#000000",            # 黑色边框
        },
    }


# 车牌类型与颜色映射
class PlateTypeColorMapping:
    """车牌类型与颜色的映射关系"""
    
    TYPE_COLOR_MAP: Dict[str, str] = {
        "ordinary_large": "yellow",         # 大型汽车 - 黄底黑字
        "ordinary_small": "blue",           # 小型汽车 - 蓝底白字
        "trailer": "yellow",                # 挂车 - 黄底黑字
        "coach": "yellow",                  # 教练汽车 - 黄底黑字
        "police": "white",                  # 警用汽车 - 白底黑字（红"警"）
        "new_energy_small": "green",        # 小型新能源 - 渐变绿底黑字
        "new_energy_large": "yellow_green", # 大型新能源 - 黄绿双拼底黑字
        "embassy": "black",                 # 使馆汽车 - 黑底白字（红"使"）
        "consulate": "black",               # 领馆汽车 - 黑底白字（红"领"）
        "hong_kong_macao": "black",         # 港澳入出境 - 黑底白字
        "military": "white",                # 军队车牌 - 特殊格式
        "motorcycle": "yellow",             # 普通摩托车 - 黄底黑字
        "light_motorcycle": "blue",         # 轻便摩托车 - 蓝底白字
        "low_speed_vehicle": "yellow",      # 低速车 - 黄底黑字
        "temporary": "blue",                # 临时号牌 - 天蓝底纹黑字
    }


# 字体相关常量
class FontConstants:
    """字体相关常量"""
    
    # 字符间距（像素）
    CHAR_SPACING: Dict[str, int] = {
        "standard": 8,      # 标准间距
        "new_energy": 6,    # 新能源车牌（字符更多）
        "motorcycle": 10,   # 摩托车号牌
    }
    
    # 字体大小（像素）
    FONT_SIZES: Dict[str, int] = {
        "province": 45,     # 省份简称字体大小
        "code": 45,         # 发牌机关代号字体大小
        "sequence": 45,     # 序号字体大小
        "special": 40,      # 特殊字符字体大小（警、使、领等）
    }
    
    # 字符位置偏移
    CHAR_OFFSETS: Dict[str, Tuple[int, int]] = {
        "province": (20, 50),       # 省份简称位置
        "regional_code": (75, 50),  # 发牌机关代号位置
        "sequence_start": (130, 50), # 序号起始位置
    }


# 验证规则常量
class ValidationConstants:
    """验证规则常量"""
    
    # 车牌号码长度限制
    PLATE_LENGTH_LIMITS: Dict[str, Tuple[int, int]] = {
        "ordinary": (7, 7),         # 普通车牌：7位（省份+代号+5位序号）
        "new_energy": (8, 8),       # 新能源车牌：8位（省份+代号+6位序号）
        "special": (7, 8),          # 特殊车牌：7-8位（可能有特殊字符）
    }
    
    # 错误信息模板
    ERROR_MESSAGES: Dict[str, str] = {
        "invalid_province": "无效的省份简称: {province}",
        "invalid_regional_code": "省份 {province} 不存在发牌机关代号 {code}",
        "invalid_sequence_length": "序号长度不正确，期望 {expected}，实际 {actual}",
        "forbidden_letter": "序号包含禁用字母: {letters}",
        "invalid_pattern": "序号不符合指定模式: {pattern}",
        "empty_plate": "车牌号码不能为空",
        "invalid_special_char": "无效的特殊字符: {char}",
    }


# 生成器配置常量
class GeneratorConstants:
    """生成器配置常量"""
    
    # 默认生成参数
    DEFAULT_PARAMS: Dict[str, any] = {
        "batch_size": 1,            # 批量生成数量
        "allow_duplicates": False,  # 是否允许重复
        "preferred_pattern": None,  # 首选序号模式
        "region_preference": None,  # 地区偏好
        "energy_type": "pure",      # 新能源类型：pure（纯电动）或 hybrid（非纯电动）
    }
    
    # 性能限制
    PERFORMANCE_LIMITS: Dict[str, int] = {
        "max_batch_size": 10000,    # 最大批量生成数量
        "max_retry_count": 1000,    # 最大重试次数
        "generation_timeout": 30,   # 生成超时时间（秒）
    }


# 车牌类型枚举
class PlateType:
    """车牌类型常量"""
    
    # 普通汽车号牌
    ORDINARY_BLUE = "ordinary_blue"           # 蓝牌小型汽车
    ORDINARY_YELLOW = "ordinary_yellow"       # 黄牌大型汽车
    ORDINARY_COACH = "ordinary_coach"         # 教练汽车
    ORDINARY_TRAILER = "ordinary_trailer"     # 挂车
    
    # 特种车号牌
    POLICE_WHITE = "police_white"             # 警用汽车白牌
    MILITARY_WHITE = "military_white"         # 军队车牌
    
    # 新能源汽车号牌
    NEW_ENERGY_GREEN = "new_energy_green"     # 新能源汽车绿牌（兼容性）
    NEW_ENERGY_SMALL = "new_energy_small"     # 小型新能源汽车绿牌
    NEW_ENERGY_LARGE = "new_energy_large"     # 大型新能源汽车绿牌
    
    # 特殊用途号牌
    EMBASSY_BLACK = "embassy_black"           # 使领馆黑牌
    HONGKONG_BLACK = "hongkong_black"         # 港澳入出境黑牌
    MACAO_BLACK = "macao_black"               # 港澳入出境黑牌


# 省份代码列表
PROVINCE_CODES = [
    "京", "津", "冀", "晋", "蒙", "辽", "吉", "黑", "沪",
    "苏", "浙", "皖", "闽", "赣", "鲁", "豫", "鄂", "湘",
    "粤", "桂", "琼", "渝", "川", "贵", "云", "藏", "陕",
    "甘", "青", "宁", "新"
]

# 可用字母（排除I、O）
LETTERS = PlateConstants.AVAILABLE_LETTERS

# 可用数字
DIGITS = PlateConstants.AVAILABLE_DIGITS