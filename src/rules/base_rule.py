"""
基础规则类模块
定义车牌规则的基类接口和通用验证方法
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel
from enum import Enum


class PlateType(Enum):
    """车牌类型枚举"""
    ORDINARY_LARGE = "ordinary_large"  # 大型汽车号牌（黄底黑字）
    ORDINARY_SMALL = "ordinary_small"  # 小型汽车号牌（蓝底白字）
    TRAILER = "trailer"  # 挂车号牌（黄底黑字）
    COACH = "coach"  # 教练汽车号牌（黄底黑字）
    POLICE = "police"  # 警用汽车号牌（白底黑字，红"警"字）
    NEW_ENERGY_SMALL = "new_energy_small"  # 小型新能源汽车号牌（渐变绿底黑字）
    NEW_ENERGY_LARGE = "new_energy_large"  # 大型新能源汽车号牌（黄绿双拼底黑字）
    EMBASSY = "embassy"  # 使馆汽车号牌（黑底白字）
    CONSULATE = "consulate"  # 领馆汽车号牌（黑底白字）
    HONG_KONG_MACAO = "hong_kong_macao"  # 港澳入出境车号牌（黑底白字）
    MILITARY = "military"  # 军队车牌（首位字母+红色）


class PlateColor(Enum):
    """车牌颜色枚举"""
    BLUE = "blue"  # 蓝底白字
    YELLOW = "yellow"  # 黄底黑字
    WHITE = "white"  # 白底黑字
    BLACK = "black"  # 黑底白字
    GREEN = "green"  # 渐变绿底黑字
    YELLOW_GREEN = "yellow_green"  # 黄绿双拼底黑字


class PlateInfo(BaseModel):
    """车牌信息数据结构"""
    plate_number: str  # 完整车牌号码
    plate_type: PlateType  # 车牌类型
    province: str  # 省份简称
    regional_code: str  # 发牌机关代号
    sequence: str  # 序号部分
    background_color: PlateColor  # 背景颜色
    is_double_layer: bool = False  # 是否双层车牌（如大型车）
    split_position: int = 2  # 分隔符位置（第几位字符后分隔，默认第2位后）
    special_chars: Optional[List[str]] = None  # 特殊字符（如"警"、"使"、"领"等）
    font_color: str = "black"  # 字体颜色（通常是黑或白）
    red_chars: Optional[List[str]] = None  # 红色字符列表（如"警"等）


class ValidationResult(BaseModel):
    """验证结果数据结构"""
    is_valid: bool  # 是否有效
    error_message: Optional[str] = None  # 错误信息
    warnings: Optional[List[str]] = None  # 警告信息


class BaseRule(ABC):
    """
    所有车牌规则的基类
    定义车牌生成和验证的通用接口
    """
    
    def __init__(self):
        """初始化基础规则"""
        self.plate_type: PlateType = PlateType.ORDINARY_SMALL
        self.sequence_length: int = 5  # 序号长度（默认5位）
        self.allow_letters: bool = True  # 是否允许字母
        self.forbidden_letters: List[str] = ["I", "O"]  # 禁用字母
    
    @abstractmethod
    def generate_sequence(self, 
                         province: str, 
                         regional_code: str,
                         **kwargs) -> str:
        """
        生成车牌序号
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            **kwargs: 其他参数
            
        Returns:
            str: 生成的序号
        """
        pass
    
    @abstractmethod
    def validate_sequence(self, sequence: str) -> ValidationResult:
        """
        验证序号是否符合规则
        
        Args:
            sequence: 序号字符串
            
        Returns:
            ValidationResult: 验证结果
        """
        pass
    
    @abstractmethod
    def get_plate_info(self, 
                      province: str, 
                      regional_code: str, 
                      sequence: str) -> PlateInfo:
        """
        生成完整的车牌信息
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            sequence: 序号
            
        Returns:
            PlateInfo: 车牌信息对象
        """
        pass
    
    def validate_province(self, province: str) -> ValidationResult:
        """
        验证省份简称
        
        Args:
            province: 省份简称
            
        Returns:
            ValidationResult: 验证结果
        """
        from .province_codes import ProvinceManager
        
        if not ProvinceManager.is_valid_province(province):
            return ValidationResult(
                is_valid=False,
                error_message=f"无效的省份简称: {province}"
            )
        return ValidationResult(is_valid=True)
    
    def validate_regional_code(self, province: str, regional_code: str) -> ValidationResult:
        """
        验证发牌机关代号
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            
        Returns:
            ValidationResult: 验证结果
        """
        from .regional_codes import RegionalCodeManager
        
        if not RegionalCodeManager.is_valid_regional_code(province, regional_code):
            return ValidationResult(
                is_valid=False,
                error_message=f"省份 {province} 不存在发牌机关代号 {regional_code}"
            )
        return ValidationResult(is_valid=True)
    
    def validate_plate_number(self, plate_number: str) -> ValidationResult:
        """
        验证完整车牌号码格式
        
        Args:
            plate_number: 完整车牌号码
            
        Returns:
            ValidationResult: 验证结果
        """
        if not plate_number:
            return ValidationResult(
                is_valid=False,
                error_message="车牌号码不能为空"
            )
        
        # 基本长度检查
        if len(plate_number) < 7:
            return ValidationResult(
                is_valid=False,
                error_message=f"车牌号码长度不足: {plate_number}"
            )
        
        # 提取省份和发牌机关代号
        province = plate_number[0]
        regional_code = plate_number[1]
        sequence = plate_number[2:]
        
        # 验证省份
        province_result = self.validate_province(province)
        if not province_result.is_valid:
            return province_result
        
        # 验证发牌机关代号
        regional_result = self.validate_regional_code(province, regional_code)
        if not regional_result.is_valid:
            return regional_result
        
        # 验证序号
        sequence_result = self.validate_sequence(sequence)
        if not sequence_result.is_valid:
            return sequence_result
        
        return ValidationResult(is_valid=True)
    
    def contains_forbidden_letters(self, text: str) -> bool:
        """
        检查文本是否包含禁用字母
        
        Args:
            text: 要检查的文本
            
        Returns:
            bool: True表示包含禁用字母
        """
        return any(letter in text.upper() for letter in self.forbidden_letters)
    
    def get_available_letters(self) -> List[str]:
        """
        获取可用的字母列表
        
        Returns:
            List[str]: 可用字母列表
        """
        all_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        return [letter for letter in all_letters if letter not in self.forbidden_letters]
    
    def get_available_digits(self) -> List[str]:
        """
        获取可用的数字列表
        
        Returns:
            List[str]: 可用数字列表
        """
        return [str(i) for i in range(10)]
    
    def format_plate_number(self, province: str, regional_code: str, sequence: str) -> str:
        """
        格式化车牌号码
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            sequence: 序号
            
        Returns:
            str: 格式化的车牌号码
        """
        return f"{province}{regional_code}{sequence}"
    
    def get_sequence_pattern_info(self) -> Dict[str, Any]:
        """
        获取序号模式信息
        
        Returns:
            Dict[str, Any]: 序号模式信息
        """
        return {
            "length": self.sequence_length,
            "allow_letters": self.allow_letters,
            "forbidden_letters": self.forbidden_letters,
            "available_letters": self.get_available_letters(),
            "available_digits": self.get_available_digits()
        }