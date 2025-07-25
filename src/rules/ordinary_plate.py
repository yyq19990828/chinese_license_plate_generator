"""
普通汽车号牌规则模块
基于GA 36-2018标准实现普通汽车号牌的生成和验证规则
包括：大型汽车、小型汽车、挂车、教练汽车、警用汽车号牌
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import random

from .base_rule import BaseRule, PlateType, PlateColor, PlateInfo, ValidationResult
from .sequence_generator import OrdinarySequenceGenerator, SequenceGeneratorFactory, SequenceType
from ..core.exceptions import PlateGenerationError


class OrdinaryPlateSubType(Enum):
    """普通汽车号牌子类型"""
    LARGE_CAR = "large_car"  # 大型汽车号牌
    SMALL_CAR = "small_car"  # 小型汽车号牌
    TRAILER = "trailer"  # 挂车号牌
    COACH = "coach"  # 教练汽车号牌
    POLICE = "police"  # 警用汽车号牌


class OrdinaryPlateRule(BaseRule):
    """
    普通汽车号牌规则类
    实现GA 36-2018标准中关于普通汽车号牌的各项规则
    """
    
    def __init__(self, sub_type: OrdinaryPlateSubType = OrdinaryPlateSubType.SMALL_CAR):
        """
        初始化普通汽车号牌规则
        
        Args:
            sub_type: 普通汽车号牌子类型
        """
        super().__init__()
        self.sub_type = sub_type
        self.sequence_length = 5  # NOTE 普通汽车号牌序号长度为5位
        self.allow_letters = True
        self.forbidden_letters = ["I", "O"]
        
        # 根据子类型设置车牌属性
        self._setup_plate_properties()
        
        # 初始化序号生成器
        self.sequence_generator = OrdinarySequenceGenerator()
    
    def _setup_plate_properties(self):
        """根据子类型设置车牌属性"""
        # 设置默认属性
        self.special_chars = []
        self.red_chars = []
        
        if self.sub_type == OrdinaryPlateSubType.SMALL_CAR:
            self.plate_type = PlateType.ORDINARY_SMALL
            self.background_color = PlateColor.BLUE
            self.font_color = "white"
            self.is_double_layer = False
            
        elif self.sub_type == OrdinaryPlateSubType.LARGE_CAR:
            self.plate_type = PlateType.ORDINARY_LARGE
            self.background_color = PlateColor.YELLOW
            self.font_color = "black"
            self.is_double_layer = True  # 大型汽车号牌为双层
            
        elif self.sub_type == OrdinaryPlateSubType.TRAILER:
            self.plate_type = PlateType.TRAILER
            self.background_color = PlateColor.YELLOW
            self.font_color = "black"
            self.is_double_layer = False
            self.special_chars = ["挂"]
            
        elif self.sub_type == OrdinaryPlateSubType.COACH:
            self.plate_type = PlateType.COACH
            self.background_color = PlateColor.YELLOW
            self.font_color = "black"
            self.is_double_layer = False
            self.special_chars = ["学"]
            
        elif self.sub_type == OrdinaryPlateSubType.POLICE:
            self.plate_type = PlateType.POLICE
            self.background_color = PlateColor.WHITE
            self.font_color = "black"
            self.special_chars = ["警"]
            self.red_chars = ["警"]
            self.is_double_layer = False
    
    def generate_sequence(self, 
                         province: str, 
                         regional_code: str,
                         preferred_order: Optional[int] = None,
                         force_pattern: Optional[str] = None,
                         **kwargs) -> str:
        """
        生成普通汽车号牌序号
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            preferred_order: 首选启用顺序
            force_pattern: 强制使用的模式
            **kwargs: 其他参数
            
        Returns:
            str: 生成的5位序号
        
        Raises:
            PlateGenerationError: 序号生成失败时抛出
        """
        try:
            sequence, pattern = self.sequence_generator.generate_sequence(
                province=province,
                regional_code=regional_code,
                preferred_order=preferred_order,
                force_pattern=force_pattern
            )
            return sequence
        except Exception as e:
            raise PlateGenerationError(f"普通汽车号牌序号生成失败: {str(e)}")
    
    def validate_sequence(self, sequence: str) -> ValidationResult:
        """
        验证普通汽车号牌序号
        
        Args:
            sequence: 5位序号字符串
            
        Returns:
            ValidationResult: 验证结果
        """
        # 基本长度检查
        if len(sequence) != 5:
            return ValidationResult(
                is_valid=False,
                error_message=f"普通汽车号牌序号长度必须为5位，当前为{len(sequence)}位"
            )
        
        # 检查是否包含禁用字母
        if self.contains_forbidden_letters(sequence):
            return ValidationResult(
                is_valid=False,
                error_message=f"序号包含禁用字母(I, O): {sequence}"
            )
        
        # 检查字符类型（必须是数字或字母）
        for i, char in enumerate(sequence):
            if not (char.isdigit() or char.isalpha()):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"序号第{i+1}位字符无效: {char}"
                )
        
        # 验证是否符合已知的序号模式
        patterns = self.sequence_generator.patterns
        is_valid_pattern = False
        
        for pattern in patterns:
            if self.sequence_generator.validate_pattern(sequence, pattern.pattern):
                is_valid_pattern = True
                break
        
        if not is_valid_pattern:
            return ValidationResult(
                is_valid=False,
                error_message=f"序号不符合任何有效的普通汽车号牌模式: {sequence}"
            )
        
        return ValidationResult(is_valid=True)
    
    def get_plate_info(self, 
                      province: str, 
                      regional_code: str, 
                      sequence: str) -> PlateInfo:
        """
        生成完整的普通汽车号牌信息
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            sequence: 5位序号
            
        Returns:
            PlateInfo: 车牌信息对象
        """
        # 验证省份和发牌机关代号
        province_result = self.validate_province(province)
        if not province_result.is_valid:
            raise PlateGenerationError(province_result.error_message)
        
        regional_result = self.validate_regional_code(province, regional_code)
        if not regional_result.is_valid:
            raise PlateGenerationError(regional_result.error_message)
        
        # 验证序号
        sequence_result = self.validate_sequence(sequence)
        if not sequence_result.is_valid:
            raise PlateGenerationError(sequence_result.error_message)
        
        # 构造完整车牌号码
        plate_number = self.format_plate_number(province, regional_code, sequence)
        
        # 创建车牌信息对象
        plate_info = PlateInfo(
            plate_number=plate_number,
            plate_type=self.plate_type,
            province=province,
            regional_code=regional_code,
            sequence=sequence,
            background_color=self.background_color,
            is_double_layer=self.is_double_layer,
            special_chars=self.special_chars,
            font_color=self.font_color,
            red_chars=self.red_chars
        )
        
        return plate_info
    
    def generate_plate(self, 
                      province: str, 
                      regional_code: str,
                      preferred_order: Optional[int] = None,
                      force_pattern: Optional[str] = None,
                      **kwargs) -> PlateInfo:
        """
        生成完整的普通汽车号牌
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            preferred_order: 首选启用顺序
            force_pattern: 强制使用的模式
            **kwargs: 其他参数
            
        Returns:
            PlateInfo: 生成的车牌信息
        """
        # 生成序号
        sequence = self.generate_sequence(
            province=province,
            regional_code=regional_code,
            preferred_order=preferred_order,
            force_pattern=force_pattern,
            **kwargs
        )

        if self.sub_type == OrdinaryPlateSubType.POLICE:
            sequence = sequence[:-1] + '警'
        elif self.sub_type == OrdinaryPlateSubType.TRAILER:
            sequence = sequence[:-1] + '挂'
        elif self.sub_type == OrdinaryPlateSubType.COACH:
            sequence = '学' + sequence[1:]
        
        # 生成完整车牌信息
        return self.get_plate_info(province, regional_code, sequence)
    
    def get_available_sequence_patterns(self) -> List[Dict[str, Any]]:
        """
        获取可用的序号模式列表
        
        Returns:
            List[Dict[str, Any]]: 可用模式信息列表
        """
        available_patterns = self.sequence_generator.resource_manager.get_available_patterns(
            self.sequence_generator.patterns
        )
        
        return [
            {
                "order": pattern.order,
                "pattern": pattern.pattern,
                "description": pattern.description,
                "example": pattern.example,
                "usage_rate": pattern.usage_rate,
                "is_active": pattern.is_active
            }
            for pattern in available_patterns
        ]
    
    def get_plate_type_info(self) -> Dict[str, Any]:
        """
        获取车牌类型信息
        
        Returns:
            Dict[str, Any]: 车牌类型信息
        """
        return {
            "sub_type": self.sub_type.value,
            "plate_type": self.plate_type.value,
            "background_color": self.background_color.value,
            "font_color": self.font_color,
            "is_double_layer": self.is_double_layer,
            "special_chars": self.special_chars,
            "red_chars": self.red_chars,
            "sequence_length": self.sequence_length,
            "allow_letters": self.allow_letters,
            "forbidden_letters": self.forbidden_letters
        }
    
    def set_sequence_usage_rate(self, pattern_order: int, usage_rate: float):
        """
        设置指定模式的使用率
        
        Args:
            pattern_order: 模式启用顺序
            usage_rate: 使用率（0-1）
        """
        pattern = self.sequence_generator.get_pattern_by_order(pattern_order)
        if pattern:
            pattern_key = f"{pattern.pattern}_{pattern.order}"
            self.sequence_generator.resource_manager.update_usage_rate(pattern_key, usage_rate)
    
    def get_sequence_usage_rate(self, pattern_order: int) -> float:
        """
        获取指定模式的使用率
        
        Args:
            pattern_order: 模式启用顺序
            
        Returns:
            float: 使用率（0-1）
        """
        pattern = self.sequence_generator.get_pattern_by_order(pattern_order)
        if pattern:
            pattern_key = f"{pattern.pattern}_{pattern.order}"
            return self.sequence_generator.resource_manager.get_usage_rate(pattern_key)
        return 0.0


class OrdinaryPlateRuleFactory:
    """
    普通汽车号牌规则工厂类
    根据车牌子类型创建相应的规则对象
    """
    
    @staticmethod
    def create_rule(sub_type: OrdinaryPlateSubType) -> OrdinaryPlateRule:
        """
        创建普通汽车号牌规则
        
        Args:
            sub_type: 普通汽车号牌子类型
            
        Returns:
            OrdinaryPlateRule: 规则对象
        """
        return OrdinaryPlateRule(sub_type)
    
    @staticmethod
    def create_small_car_rule() -> OrdinaryPlateRule:
        """
        创建小型汽车号牌规则
        
        Returns:
            OrdinaryPlateRule: 小型汽车号牌规则对象
        """
        return OrdinaryPlateRuleFactory.create_rule(OrdinaryPlateSubType.SMALL_CAR)
    
    @staticmethod
    def create_large_car_rule() -> OrdinaryPlateRule:
        """
        创建大型汽车号牌规则
        
        Returns:
            OrdinaryPlateRule: 大型汽车号牌规则对象
        """
        return OrdinaryPlateRuleFactory.create_rule(OrdinaryPlateSubType.LARGE_CAR)
    
    @staticmethod
    def create_trailer_rule() -> OrdinaryPlateRule:
        """
        创建挂车号牌规则
        
        Returns:
            OrdinaryPlateRule: 挂车号牌规则对象
        """
        return OrdinaryPlateRuleFactory.create_rule(OrdinaryPlateSubType.TRAILER)
    
    @staticmethod
    def create_coach_rule() -> OrdinaryPlateRule:
        """
        创建教练汽车号牌规则
        
        Returns:
            OrdinaryPlateRule: 教练汽车号牌规则对象
        """
        return OrdinaryPlateRuleFactory.create_rule(OrdinaryPlateSubType.COACH)
    
    @staticmethod
    def create_police_rule() -> OrdinaryPlateRule:
        """
        创建警用汽车号牌规则
        
        Returns:
            OrdinaryPlateRule: 警用汽车号牌规则对象
        """
        return OrdinaryPlateRuleFactory.create_rule(OrdinaryPlateSubType.POLICE)
    
    @staticmethod
    def get_all_sub_types() -> List[OrdinaryPlateSubType]:
        """
        获取所有普通汽车号牌子类型
        
        Returns:
            List[OrdinaryPlateSubType]: 子类型列表
        """
        return list(OrdinaryPlateSubType)
    
    @staticmethod
    def get_sub_type_by_name(name: str) -> Optional[OrdinaryPlateSubType]:
        """
        根据名称获取子类型
        
        Args:
            name: 子类型名称
            
        Returns:
            Optional[OrdinaryPlateSubType]: 子类型对象，未找到时返回None
        """
        for sub_type in OrdinaryPlateSubType:
            if sub_type.value == name:
                return sub_type
        return None