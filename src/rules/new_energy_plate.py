"""
新能源汽车号牌规则模块
基于GA 36-2018标准实现新能源汽车号牌的生成和验证规则
包括：小型新能源汽车号牌和大型新能源汽车号牌
区分纯电动车和非纯电动车（包括插电式混合动力车、燃料电池车等）
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import random

from .base_rule import BaseRule, PlateType, PlateColor, PlateInfo, ValidationResult
from .sequence_generator import NewEnergySequenceGenerator, SequenceGeneratorFactory, SequenceType
from ..core.exceptions import PlateGenerationError


class NewEnergyPlateSubType(Enum):
    """新能源汽车号牌子类型"""
    SMALL_CAR = "small_car"  # 小型新能源汽车号牌
    LARGE_CAR = "large_car"  # 大型新能源汽车号牌


class EnergyType(Enum):
    """能源类型"""
    PURE_ELECTRIC = "pure"  # 纯电动
    NON_PURE_ELECTRIC = "hybrid"  # 非纯电动（包括插电式混合动力、燃料电池等）


class NewEnergyPlateRule(BaseRule):
    """
    新能源汽车号牌规则类
    实现GA 36-2018标准中关于新能源汽车号牌的各项规则
    """
    
    def __init__(self, sub_type: NewEnergyPlateSubType = NewEnergyPlateSubType.SMALL_CAR):
        """
        初始化新能源汽车号牌规则
        
        Args:
            sub_type: 新能源汽车号牌子类型
        """
        super().__init__()
        self.sub_type = sub_type
        self.sequence_length = 6  # 新能源汽车号牌序号长度为6位
        self.allow_letters = True
        self.forbidden_letters = ["I", "O"]
        
        # 根据子类型设置车牌属性
        self._setup_plate_properties()
        
        # 初始化序号生成器
        self.sequence_generator = NewEnergySequenceGenerator()
        
        # 能源类型标识字母
        self.pure_electric_letters = ["D", "A", "B", "C", "E"]  # 纯电动车标识
        self.non_pure_electric_letters = ["F", "G", "H", "J", "K"]  # 非纯电动车标识
    
    def _setup_plate_properties(self):
        """根据子类型设置车牌属性"""
        if self.sub_type == NewEnergyPlateSubType.SMALL_CAR:
            self.plate_type = PlateType.NEW_ENERGY_SMALL
            self.background_color = PlateColor.GREEN  # 小型新能源车：渐变绿底
            self.font_color = "black"
            self.is_double_layer = False
            
        elif self.sub_type == NewEnergyPlateSubType.LARGE_CAR:
            self.plate_type = PlateType.NEW_ENERGY_LARGE
            self.background_color = PlateColor.YELLOW_GREEN  # 大型新能源车：黄绿双拼底
            self.font_color = "black"
            self.is_double_layer = True  # 大型新能源汽车号牌为双层
    
    def generate_sequence(self, 
                         province: str, 
                         regional_code: str,
                         energy_type: EnergyType = EnergyType.PURE_ELECTRIC,
                         preferred_letter: Optional[str] = None,
                         double_letter: bool = False,
                         **kwargs) -> str:
        """
        生成新能源汽车号牌序号
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            energy_type: 能源类型（纯电动或非纯电动）
            preferred_letter: 首选能源标识字母
            double_letter: 是否使用双字母（仅小型车有效）
            **kwargs: 其他参数
            
        Returns:
            str: 生成的6位序号
        
        Raises:
            PlateGenerationError: 序号生成失败时抛出
        """
        try:
            if self.sub_type == NewEnergyPlateSubType.SMALL_CAR:
                # 小型新能源汽车：第1位或前两位为字母，其余为数字
                sequence, used_letter = self.sequence_generator.generate_small_car_sequence(
                    energy_type=energy_type.value,
                    preferred_letter=preferred_letter,
                    double_letter=double_letter
                )
            else:
                # 大型新能源汽车：前5位为数字，第6位为能源标识字母
                sequence, used_letter = self.sequence_generator.generate_large_car_sequence(
                    energy_type=energy_type.value
                )
            
            return sequence
        except Exception as e:
            raise PlateGenerationError(f"新能源汽车号牌序号生成失败: {str(e)}")
    
    def validate_sequence(self, sequence: str) -> ValidationResult:
        """
        验证新能源汽车号牌序号
        
        Args:
            sequence: 6位序号字符串
            
        Returns:
            ValidationResult: 验证结果
        """
        # 基本长度检查
        if len(sequence) != 6:
            return ValidationResult(
                is_valid=False,
                error_message=f"新能源汽车号牌序号长度必须为6位，当前为{len(sequence)}位"
            )
        
        # 检查是否包含禁用字母
        if self.contains_forbidden_letters(sequence):
            return ValidationResult(
                is_valid=False,
                error_message=f"序号包含禁用字母(I, O): {sequence}"
            )
        
        # 使用序号生成器验证格式
        car_type = "small" if self.sub_type == NewEnergyPlateSubType.SMALL_CAR else "large"
        
        if not self.sequence_generator.validate_new_energy_sequence(sequence, car_type):
            return ValidationResult(
                is_valid=False,
                error_message=f"序号不符合新能源汽车号牌格式: {sequence}"
            )
        
        # 验证能源标识字母
        energy_type = self.get_energy_type_from_sequence(sequence)
        if energy_type == "unknown":
            return ValidationResult(
                is_valid=False,
                error_message=f"序号包含无效的能源标识字母: {sequence}"
            )
        
        return ValidationResult(is_valid=True)
    
    def get_energy_type_from_sequence(self, sequence: str) -> str:
        """
        从序号中识别能源类型
        
        Args:
            sequence: 6位序号
            
        Returns:
            str: "pure"（纯电动）、"hybrid"（非纯电动）或"unknown"（未知）
        """
        car_type = "small" if self.sub_type == NewEnergyPlateSubType.SMALL_CAR else "large"
        return self.sequence_generator.get_energy_type_from_sequence(sequence, car_type)
    
    def get_energy_identifier_letter(self, sequence: str) -> Optional[str]:
        """
        从序号中提取能源标识字母
        
        Args:
            sequence: 6位序号
            
        Returns:
            Optional[str]: 能源标识字母，无法识别时返回None
        """
        if len(sequence) != 6:
            return None
        
        if self.sub_type == NewEnergyPlateSubType.SMALL_CAR:
            # 小型车：第1位是能源标识字母
            first_char = sequence[0]
            if first_char in (self.pure_electric_letters + self.non_pure_electric_letters):
                return first_char
        else:
            # 大型车：第6位是能源标识字母
            last_char = sequence[5]
            if last_char in (self.pure_electric_letters + self.non_pure_electric_letters):
                return last_char
        
        return None
    
    def get_plate_info(self, 
                      province: str, 
                      regional_code: str, 
                      sequence: str) -> PlateInfo:
        """
        生成完整的新能源汽车号牌信息
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            sequence: 6位序号
            
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
            special_chars=None,  # 新能源车牌无特殊字符
            font_color=self.font_color,
            red_chars=None  # 新能源车牌无红色字符
        )
        
        return plate_info
    
    def generate_plate(self, 
                      province: str, 
                      regional_code: str,
                      energy_type: EnergyType = EnergyType.PURE_ELECTRIC,
                      preferred_letter: Optional[str] = None,
                      double_letter: bool = False,
                      **kwargs) -> PlateInfo:
        """
        生成完整的新能源汽车号牌
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            energy_type: 能源类型
            preferred_letter: 首选能源标识字母
            double_letter: 是否使用双字母（仅小型车有效）
            **kwargs: 其他参数
            
        Returns:
            PlateInfo: 生成的车牌信息
        """
        # 生成序号
        sequence = self.generate_sequence(
            province=province,
            regional_code=regional_code,
            energy_type=energy_type,
            preferred_letter=preferred_letter,
            double_letter=double_letter,
            **kwargs
        )
        
        # 生成完整车牌信息
        return self.get_plate_info(province, regional_code, sequence)
    
    def get_available_energy_letters(self, energy_type: EnergyType) -> List[str]:
        """
        获取指定能源类型的可用标识字母
        
        Args:
            energy_type: 能源类型
            
        Returns:
            List[str]: 可用的能源标识字母列表
        """
        if energy_type == EnergyType.PURE_ELECTRIC:
            return self.pure_electric_letters.copy()
        else:
            return self.non_pure_electric_letters.copy()
    
    def get_energy_type_description(self, energy_type: EnergyType) -> str:
        """
        获取能源类型的中文描述
        
        Args:
            energy_type: 能源类型
            
        Returns:
            str: 中文描述
        """
        descriptions = {
            EnergyType.PURE_ELECTRIC: "纯电动车",
            EnergyType.NON_PURE_ELECTRIC: "非纯电动车（包括插电式混合动力、燃料电池等）"
        }
        return descriptions.get(energy_type, "未知类型")
    
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
            "sequence_length": self.sequence_length,
            "pure_electric_letters": self.pure_electric_letters,
            "non_pure_electric_letters": self.non_pure_electric_letters,
            "energy_types": [
                {
                    "type": EnergyType.PURE_ELECTRIC.value,
                    "description": self.get_energy_type_description(EnergyType.PURE_ELECTRIC),
                    "letters": self.pure_electric_letters
                },
                {
                    "type": EnergyType.NON_PURE_ELECTRIC.value,
                    "description": self.get_energy_type_description(EnergyType.NON_PURE_ELECTRIC),
                    "letters": self.non_pure_electric_letters
                }
            ]
        }
    
    def analyze_plate_number(self, plate_number: str) -> Dict[str, Any]:
        """
        分析新能源车牌号码，提取详细信息
        
        Args:
            plate_number: 完整车牌号码
            
        Returns:
            Dict[str, Any]: 车牌分析结果
        """
        if len(plate_number) < 8:  # 新能源车牌至少8位（省份+地区+6位序号）
            return {"error": "车牌号码长度不足"}
        
        province = plate_number[0]
        regional_code = plate_number[1]
        sequence = plate_number[2:]
        
        # 验证车牌
        validation = self.validate_plate_number(plate_number)
        if not validation.is_valid:
            return {"error": validation.error_message}
        
        # 分析能源类型
        energy_type = self.get_energy_type_from_sequence(sequence)
        energy_letter = self.get_energy_identifier_letter(sequence)
        
        # 分析序号模式
        sequence_pattern = self._analyze_sequence_pattern(sequence)
        
        return {
            "plate_number": plate_number,
            "province": province,
            "regional_code": regional_code,
            "sequence": sequence,
            "energy_type": energy_type,
            "energy_type_description": self.get_energy_type_description(
                EnergyType.PURE_ELECTRIC if energy_type == "pure" else EnergyType.NON_PURE_ELECTRIC
            ),
            "energy_identifier_letter": energy_letter,
            "sequence_pattern": sequence_pattern,
            "sub_type": self.sub_type.value,
            "plate_type": self.plate_type.value,
            "background_color": self.background_color.value,
            "is_double_layer": self.is_double_layer
        }
    
    def _analyze_sequence_pattern(self, sequence: str) -> Dict[str, Any]:
        """
        分析序号模式
        
        Args:
            sequence: 6位序号
            
        Returns:
            Dict[str, Any]: 序号模式分析结果
        """
        if len(sequence) != 6:
            return {"error": "序号长度不正确"}
        
        pattern_info = {
            "length": len(sequence),
            "positions": []
        }
        
        for i, char in enumerate(sequence):
            position_info = {
                "position": i + 1,
                "character": char,
                "type": "letter" if char.isalpha() else "digit"
            }
            
            if char.isalpha():
                if char in self.pure_electric_letters:
                    position_info["energy_indicator"] = "pure_electric"
                elif char in self.non_pure_electric_letters:
                    position_info["energy_indicator"] = "non_pure_electric"
                else:
                    position_info["energy_indicator"] = "none"
            
            pattern_info["positions"].append(position_info)
        
        # 判断整体模式
        if self.sub_type == NewEnergyPlateSubType.SMALL_CAR:
            if sequence[0].isalpha() and sequence[1].isalpha():
                pattern_info["pattern_type"] = "double_letter_start"
                pattern_info["description"] = "前两位字母，后四位数字"
            elif sequence[0].isalpha():
                pattern_info["pattern_type"] = "single_letter_start"
                pattern_info["description"] = "第一位字母，后五位数字"
            else:
                pattern_info["pattern_type"] = "unknown"
        else:
            if sequence[5].isalpha() and sequence[:5].isdigit():
                pattern_info["pattern_type"] = "digit_letter_end"
                pattern_info["description"] = "前五位数字，最后一位字母"
            else:
                pattern_info["pattern_type"] = "unknown"
        
        return pattern_info


class NewEnergyPlateRuleFactory:
    """
    新能源汽车号牌规则工厂类
    根据车牌子类型创建相应的规则对象
    """
    
    @staticmethod
    def create_rule(sub_type: NewEnergyPlateSubType) -> NewEnergyPlateRule:
        """
        创建新能源汽车号牌规则
        
        Args:
            sub_type: 新能源汽车号牌子类型
            
        Returns:
            NewEnergyPlateRule: 规则对象
        """
        return NewEnergyPlateRule(sub_type)
    
    @staticmethod
    def create_small_car_rule() -> NewEnergyPlateRule:
        """
        创建小型新能源汽车号牌规则
        
        Returns:
            NewEnergyPlateRule: 小型新能源汽车号牌规则对象
        """
        return NewEnergyPlateRuleFactory.create_rule(NewEnergyPlateSubType.SMALL_CAR)
    
    @staticmethod
    def create_large_car_rule() -> NewEnergyPlateRule:
        """
        创建大型新能源汽车号牌规则
        
        Returns:
            NewEnergyPlateRule: 大型新能源汽车号牌规则对象
        """
        return NewEnergyPlateRuleFactory.create_rule(NewEnergyPlateSubType.LARGE_CAR)
    
    @staticmethod
    def get_all_sub_types() -> List[NewEnergyPlateSubType]:
        """
        获取所有新能源汽车号牌子类型
        
        Returns:
            List[NewEnergyPlateSubType]: 子类型列表
        """
        return list(NewEnergyPlateSubType)
    
    @staticmethod
    def get_all_energy_types() -> List[EnergyType]:
        """
        获取所有能源类型
        
        Returns:
            List[EnergyType]: 能源类型列表
        """
        return list(EnergyType)
    
    @staticmethod
    def get_sub_type_by_name(name: str) -> Optional[NewEnergyPlateSubType]:
        """
        根据名称获取子类型
        
        Args:
            name: 子类型名称
            
        Returns:
            Optional[NewEnergyPlateSubType]: 子类型对象，未找到时返回None
        """
        for sub_type in NewEnergyPlateSubType:
            if sub_type.value == name:
                return sub_type
        return None
    
    @staticmethod
    def get_energy_type_by_name(name: str) -> Optional[EnergyType]:
        """
        根据名称获取能源类型
        
        Args:
            name: 能源类型名称
            
        Returns:
            Optional[EnergyType]: 能源类型对象，未找到时返回None
        """
        for energy_type in EnergyType:
            if energy_type.value == name:
                return energy_type
        return None