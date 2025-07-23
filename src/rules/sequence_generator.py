"""
序号生成器模块
基于GA 36-2018标准实现车牌序号的生成逻辑
"""

import random
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from pydantic import BaseModel

from ..utils.constants import SequenceConstants, PlateConstants
from ..core.exceptions import SequenceGenerationError


class SequenceType(Enum):
    """序号类型枚举"""
    ORDINARY_5_DIGIT = "ordinary_5_digit"  # 普通汽车5位序号
    NEW_ENERGY_SMALL_6_DIGIT = "new_energy_small_6_digit"  # 小型新能源6位序号
    NEW_ENERGY_LARGE_6_DIGIT = "new_energy_large_6_digit"  # 大型新能源6位序号


class SequencePattern(BaseModel):
    """序号模式数据结构"""
    order: int  # 启用顺序
    pattern: str  # 模式字符串（D=数字，L=字母）
    description: str  # 模式描述
    example: str  # 示例
    is_active: bool = True  # 是否启用
    usage_rate: float = 0.0  # 使用率（0-1）


class SequenceGenerationConfig(BaseModel):
    """序号生成配置"""
    sequence_type: SequenceType  # 序号类型
    province: str  # 省份简称
    regional_code: str  # 发牌机关代号
    preferred_pattern_order: Optional[int] = None  # 首选模式顺序
    energy_type: Optional[str] = None  # 新能源类型：pure（纯电动）或 hybrid（非纯电动）
    force_pattern: Optional[str] = None  # 强制使用的模式


class SequenceResourceManager:
    """
    序号资源管理器
    管理各种模式的使用率和启用状态
    """
    
    def __init__(self):
        """初始化资源管理器"""
        self.usage_rates: Dict[str, float] = {}  # 每种模式的使用率
        self.threshold = SequenceConstants.RESOURCE_USAGE_THRESHOLD  # 60%阈值
    
    def get_usage_rate(self, pattern_key: str) -> float:
        """
        获取指定模式的使用率
        
        Args:
            pattern_key: 模式键值
            
        Returns:
            float: 使用率（0-1）
        """
        return self.usage_rates.get(pattern_key, 0.0)
    
    def update_usage_rate(self, pattern_key: str, usage_rate: float):
        """
        更新指定模式的使用率
        
        Args:
            pattern_key: 模式键值
            usage_rate: 使用率（0-1）
        """
        self.usage_rates[pattern_key] = min(1.0, max(0.0, usage_rate))
    
    def is_pattern_available(self, pattern_key: str) -> bool:
        """
        检查指定模式是否可用（未超过阈值）
        
        Args:
            pattern_key: 模式键值
            
        Returns:
            bool: True表示可用
        """
        return self.get_usage_rate(pattern_key) < self.threshold
    
    def get_available_patterns(self, patterns: List[SequencePattern]) -> List[SequencePattern]:
        """
        获取可用的模式列表
        
        Args:
            patterns: 所有模式列表
            
        Returns:
            List[SequencePattern]: 可用模式列表
        """
        available = []
        for pattern in patterns:
            pattern_key = f"{pattern.pattern}_{pattern.order}"
            if self.is_pattern_available(pattern_key) and pattern.is_active:
                pattern.usage_rate = self.get_usage_rate(pattern_key)
                available.append(pattern)
        return available


class BaseSequenceGenerator:
    """
    基础序号生成器
    提供序号生成的通用功能
    """
    
    def __init__(self):
        """初始化序号生成器"""
        self.resource_manager = SequenceResourceManager()
        self.available_letters = PlateConstants.AVAILABLE_LETTERS
        self.available_digits = PlateConstants.AVAILABLE_DIGITS
    
    def generate_random_letter(self, exclude: Optional[List[str]] = None) -> str:
        """
        生成随机字母
        
        Args:
            exclude: 要排除的字母列表
            
        Returns:
            str: 随机字母
        """
        available = self.available_letters.copy()
        if exclude:
            available = [letter for letter in available if letter not in exclude]
        
        if not available:
            raise SequenceGenerationError("没有可用的字母")
        
        return random.choice(available)
    
    def generate_random_digit(self, exclude: Optional[List[str]] = None) -> str:
        """
        生成随机数字
        
        Args:
            exclude: 要排除的数字列表
            
        Returns:
            str: 随机数字
        """
        available = self.available_digits.copy()
        if exclude:
            available = [digit for digit in available if digit not in exclude]
        
        if not available:
            raise SequenceGenerationError("没有可用的数字")
        
        return random.choice(available)
    
    def apply_pattern(self, pattern: str, **kwargs) -> str:
        """
        根据模式生成序号
        
        Args:
            pattern: 模式字符串（D=数字，L=字母）
            **kwargs: 其他参数
            
        Returns:
            str: 生成的序号
        """
        result = ""
        for char in pattern:
            if char == 'D':
                result += self.generate_random_digit()
            elif char == 'L':
                result += self.generate_random_letter()
            else:
                result += char  # 保持原字符（用于特殊模式）
        return result
    
    def validate_pattern(self, sequence: str, pattern: str) -> bool:
        """
        验证序号是否符合指定模式
        
        Args:
            sequence: 序号字符串
            pattern: 模式字符串
            
        Returns:
            bool: True表示符合模式
        """
        if len(sequence) != len(pattern):
            return False
        
        for i, (seq_char, pat_char) in enumerate(zip(sequence, pattern)):
            if pat_char == 'D' and not seq_char.isdigit():
                return False
            elif pat_char == 'L' and not seq_char.isalpha():
                return False
            elif pat_char == 'L' and seq_char in PlateConstants.FORBIDDEN_LETTERS:
                return False  # 检查禁用字母
            elif pat_char not in ['D', 'L'] and seq_char != pat_char:
                return False
        
        return True


class OrdinarySequenceGenerator(BaseSequenceGenerator):
    """
    普通汽车序号生成器
    按照GA 36-2018标准的10种启用顺序生成5位序号
    """
    
    def __init__(self):
        """初始化普通汽车序号生成器"""
        super().__init__()
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> List[SequencePattern]:
        """
        初始化序号模式列表
        
        Returns:
            List[SequencePattern]: 模式列表
        """
        patterns = []
        for pattern_data in SequenceConstants.ORDINARY_SEQUENCE_PATTERNS:
            patterns.append(SequencePattern(**pattern_data))
        return patterns
    
    def generate_sequence(self, 
                         province: str, 
                         regional_code: str,
                         preferred_order: Optional[int] = None,
                         force_pattern: Optional[str] = None) -> Tuple[str, SequencePattern]:
        """
        生成普通汽车5位序号
        
        Args:
            province: 省份简称
            regional_code: 发牌机关代号
            preferred_order: 首选启用顺序
            force_pattern: 强制使用的模式
            
        Returns:
            Tuple[str, SequencePattern]: (生成的序号, 使用的模式)
        """
        # 如果指定了强制模式
        if force_pattern:
            for pattern in self.patterns:
                if pattern.pattern == force_pattern:
                    sequence = self.apply_pattern(pattern.pattern)
                    return sequence, pattern
            raise SequenceGenerationError(f"未找到指定的模式: {force_pattern}")
        
        # 获取可用的模式
        available_patterns = self.resource_manager.get_available_patterns(self.patterns)
        
        if not available_patterns:
            raise SequenceGenerationError("没有可用的序号模式")
        
        # 如果指定了首选顺序
        if preferred_order:
            for pattern in available_patterns:
                if pattern.order == preferred_order:
                    sequence = self.apply_pattern(pattern.pattern)
                    return sequence, pattern
        
        # 按启用顺序选择第一个可用模式
        available_patterns.sort(key=lambda x: x.order)
        selected_pattern = available_patterns[0]
        
        sequence = self.apply_pattern(selected_pattern.pattern)
        return sequence, selected_pattern
    
    def get_pattern_by_order(self, order: int) -> Optional[SequencePattern]:
        """
        根据启用顺序获取模式
        
        Args:
            order: 启用顺序
            
        Returns:
            Optional[SequencePattern]: 模式对象
        """
        for pattern in self.patterns:
            if pattern.order == order:
                return pattern
        return None
    
    def get_available_orders(self) -> List[int]:
        """
        获取当前可用的启用顺序列表
        
        Returns:
            List[int]: 可用的启用顺序
        """
        available_patterns = self.resource_manager.get_available_patterns(self.patterns)
        return sorted([pattern.order for pattern in available_patterns])


class NewEnergySequenceGenerator(BaseSequenceGenerator):
    """
    新能源汽车序号生成器
    按照GA 36-2018标准生成6位新能源车牌序号
    """
    
    def __init__(self):
        """初始化新能源汽车序号生成器"""
        super().__init__()
        self.pure_electric_letters = SequenceConstants.NEW_ENERGY_PURE_ELECTRIC_LETTERS
        self.non_pure_electric_letters = SequenceConstants.NEW_ENERGY_NON_PURE_ELECTRIC_LETTERS
    
    def generate_small_car_sequence(self, 
                                   energy_type: str = "pure",
                                   preferred_letter: Optional[str] = None,
                                   double_letter: bool = False) -> Tuple[str, str]:
        """
        生成小型新能源汽车6位序号
        格式：第1位或前两位为字母，其余为数字
        
        Args:
            energy_type: 能源类型，"pure"（纯电动）或"hybrid"（非纯电动）
            preferred_letter: 首选字母
            double_letter: 是否使用双字母（前两位都是字母）
            
        Returns:
            Tuple[str, str]: (生成的序号, 使用的能源标识字母)
        """
        # 选择能源标识字母
        if energy_type == "pure":
            available_letters = self.pure_electric_letters
        else:
            available_letters = self.non_pure_electric_letters
        
        # 选择首位字母
        if preferred_letter and preferred_letter in available_letters:
            first_letter = preferred_letter
        else:
            first_letter = random.choice(available_letters)
        
        # 生成序号
        if double_letter:
            # 前两位都是字母的情况
            second_letter = self.generate_random_letter()
            remaining_digits = "".join([self.generate_random_digit() for _ in range(4)])
            sequence = f"{first_letter}{second_letter}{remaining_digits}"
        else:
            # 只有第一位是字母的情况
            remaining_digits = "".join([self.generate_random_digit() for _ in range(5)])
            sequence = f"{first_letter}{remaining_digits}"
        
        return sequence, first_letter
    
    def generate_large_car_sequence(self, 
                                   energy_type: str = "pure") -> Tuple[str, str]:
        """
        生成大型新能源汽车6位序号
        格式：前5位为数字，第6位为能源标识字母
        
        Args:
            energy_type: 能源类型，"pure"（纯电动）或"hybrid"（非纯电动）
            
        Returns:
            Tuple[str, str]: (生成的序号, 使用的能源标识字母)
        """
        # 选择能源标识字母
        if energy_type == "pure":
            available_letters = self.pure_electric_letters
        else:
            available_letters = self.non_pure_electric_letters
        
        last_letter = random.choice(available_letters)
        
        # 生成前5位数字
        digits = "".join([self.generate_random_digit() for _ in range(5)])
        sequence = f"{digits}{last_letter}"
        
        return sequence, last_letter
    
    def get_energy_type_from_sequence(self, sequence: str, car_type: str) -> str:
        """
        从序号判断能源类型
        
        Args:
            sequence: 6位序号
            car_type: 车型，"small"或"large"
            
        Returns:
            str: "pure"（纯电动）或"hybrid"（非纯电动）
        """
        if car_type == "small":
            # 小型车：看第一位字母
            first_char = sequence[0]
            if first_char in self.pure_electric_letters:
                return "pure"
            elif first_char in self.non_pure_electric_letters:
                return "hybrid"
        elif car_type == "large":
            # 大型车：看最后一位字母
            last_char = sequence[-1]
            if last_char in self.pure_electric_letters:
                return "pure"
            elif last_char in self.non_pure_electric_letters:
                return "hybrid"
        
        return "unknown"
    
    def validate_new_energy_sequence(self, sequence: str, car_type: str) -> bool:
        """
        验证新能源车牌序号格式
        
        Args:
            sequence: 6位序号
            car_type: 车型，"small"或"large"
            
        Returns:
            bool: True表示格式正确
        """
        if len(sequence) != 6:
            return False
        
        if car_type == "small":
            # 小型车：第1位必须是字母，其余可以是字母或数字
            if not sequence[0].isalpha():
                return False
            # 检查第1位字母是否为合法的新能源标识
            if sequence[0] not in (self.pure_electric_letters + self.non_pure_electric_letters):
                return False
        elif car_type == "large":
            # 大型车：前5位必须是数字，第6位必须是字母
            if not sequence[:5].isdigit():
                return False
            if not sequence[5].isalpha():
                return False
            # 检查第6位字母是否为合法的新能源标识
            if sequence[5] not in (self.pure_electric_letters + self.non_pure_electric_letters):
                return False
        
        # 检查是否包含禁用字母
        if any(letter in sequence.upper() for letter in PlateConstants.FORBIDDEN_LETTERS):
            return False
        
        return True


class SequenceGeneratorFactory:
    """
    序号生成器工厂类
    根据车牌类型创建相应的序号生成器
    """
    
    @staticmethod
    def create_generator(sequence_type: SequenceType) -> BaseSequenceGenerator:
        """
        创建序号生成器
        
        Args:
            sequence_type: 序号类型
            
        Returns:
            BaseSequenceGenerator: 序号生成器实例
        """
        if sequence_type == SequenceType.ORDINARY_5_DIGIT:
            return OrdinarySequenceGenerator()
        elif sequence_type in [SequenceType.NEW_ENERGY_SMALL_6_DIGIT, 
                               SequenceType.NEW_ENERGY_LARGE_6_DIGIT]:
            return NewEnergySequenceGenerator()
        else:
            raise SequenceGenerationError(f"不支持的序号类型: {sequence_type}")
    
    @staticmethod
    def get_generator_for_plate_type(plate_type: str) -> BaseSequenceGenerator:
        """
        根据车牌类型获取序号生成器
        
        Args:
            plate_type: 车牌类型
            
        Returns:
            BaseSequenceGenerator: 序号生成器实例
        """
        type_mapping = {
            "ordinary_large": SequenceType.ORDINARY_5_DIGIT,
            "ordinary_small": SequenceType.ORDINARY_5_DIGIT,
            "trailer": SequenceType.ORDINARY_5_DIGIT,
            "coach": SequenceType.ORDINARY_5_DIGIT,
            "police": SequenceType.ORDINARY_5_DIGIT,
            "new_energy_small": SequenceType.NEW_ENERGY_SMALL_6_DIGIT,
            "new_energy_large": SequenceType.NEW_ENERGY_LARGE_6_DIGIT,
        }
        
        sequence_type = type_mapping.get(plate_type)
        if not sequence_type:
            raise SequenceGenerationError(f"不支持的车牌类型: {plate_type}")
        
        return SequenceGeneratorFactory.create_generator(sequence_type)