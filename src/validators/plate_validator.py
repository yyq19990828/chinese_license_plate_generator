# -*- coding: utf-8 -*-
from typing import Dict, Any

from src.core.exceptions import PlateNumberError
from src.rules.province_codes import ProvinceManager
from src.rules.regional_codes import RegionalCodeManager


class PlateValidator:
    """
    车牌号码验证器
    
    用于验证车牌号码的格式、规则一致性以及省份和地区代号的有效性。
    """

    def __init__(self, plate_number: str):
        """
        初始化验证器。

        Args:
            plate_number (str): 待验证的车牌号码。
        """
        self.plate_number = plate_number.upper()

    def validate(self) -> bool:
        """
        执行所有验证。

        Returns:
            bool: 如果车牌号码有效，则返回 True。
        
        Raises:
            PlateNumberError: 如果验证失败。
        """
        self.validate_format()
        self.validate_province_and_regional_code()
        self.validate_consistency()
        return True

    def validate_format(self) -> bool:
        """
        验证车牌号码的基本格式。
        
        - 长度是否在7到8位之间。
        - 是否包含非法字符。
        - 检查首位是否为省份简称，第二位是否为地区代号。
        - 检查序号部分是否合规（无I, O）。

        Returns:
            bool: 如果格式有效，则返回 True。
        
        Raises:
            PlateNumberError: 如果格式无效。
        """
        # 1. 长度检查
        if not 7 <= len(self.plate_number) <= 8:
            raise PlateNumberError(f"无效的车牌长度: {len(self.plate_number)}")

        # 2. 首字符省份简称检查
        province_char = self.plate_number[0]
        if not ProvinceManager.is_valid_province(province_char):
            raise PlateNumberError(f"无效的省份简称: {province_char}")

        # 3. 第二字符地区代码检查
        regional_char = self.plate_number[1]
        if not 'A' <= regional_char <= 'Z':
            raise PlateNumberError(f"无效的地区代号格式: {regional_char}")

        # 4. 序号部分检查
        sequence = self.plate_number[2:]
        for char in sequence:
            if not ('A' <= char <= 'Z' or '0' <= char <= '9'):
                # 特殊字符如 '警', '挂' 等在一致性检查中处理
                if char not in ['警', '挂', '学', '港', '澳', '使', '领']:
                    raise PlateNumberError(f"序号中包含无效字符: {char}")
            
            if char in ['I', 'O']:
                raise PlateNumberError(f"序号中包含禁用字母: {char}")

        return True

    def validate_province_and_regional_code(self) -> bool:
        """
        验证省份和地区代号的有效性。

        - 检查省份简称是否在 `province_codes` 中。
        - 检查地区代号是否在对应省份的 `regional_codes` 中。

        Returns:
            bool: 如果省份和地区代号有效，则返回 True。
        
        Raises:
            PlateNumberError: 如果省份或地区代号无效。
        """
        province_char = self.plate_number[0]
        regional_char = self.plate_number[1]

        if not ProvinceManager.is_valid_province(province_char):
            raise PlateNumberError(f"无效的省份简称: {province_char}")

        if not RegionalCodeManager.is_valid_regional_code(province_char, regional_char):
            raise PlateNumberError(f"无效的地区代号: {regional_char} (省份: {province_char})")
            
        return True

    def validate_consistency(self) -> bool:
        """
        验证车牌号码的规则一致性。

        - 新能源车牌规则 (8位)
        - 普通车牌规则 (7位)
        - 特殊车牌规则 (如警、挂等)

        Returns:
            bool: 如果规则一致，则返回 True。
        
        Raises:
            PlateNumberError: 如果规则不一致。
        """
        if len(self.plate_number) == 8:
            self._validate_new_energy_plate()
        elif len(self.plate_number) == 7:
            self._validate_ordinary_plate()
        
        # 可在此处添加其他特殊车牌的验证逻辑
        
        return True

    def _validate_new_energy_plate(self):
        """验证新能源车牌 (8位)"""
        sequence = self.plate_number[2:]
        
        # 小型新能源车
        if sequence[0].isalpha():
            first_char = sequence[0]
            if first_char not in "DFABCDEGHK":
                 raise PlateNumberError(f"小型新能源车牌序号首位字母无效: {first_char}")
        # 大型新能源车
        elif sequence[-1].isalpha():
            last_char = sequence[-1]
            if last_char not in "DFABCDEGHK":
                raise PlateNumberError(f"大型新能源车牌序号末位字母无效: {last_char}")
            
            for char in sequence[:-1]:
                if not char.isdigit():
                    raise PlateNumberError(f"大型新能源车牌序号前五位必须是数字，但找到: {char}")
        else:
            raise PlateNumberError("无效的新能源车牌格式")

    def _validate_ordinary_plate(self):
        """验证普通车牌 (7位)"""
        sequence = self.plate_number[2:]
        
        # 检查特殊车牌标记，如 '警', '挂'
        if sequence.endswith('警'):
            # 警车规则：最后一位为'警'，其余部分可以是数字或字母
            pass # 更多细化规则可在此添加
        elif sequence.endswith('挂'):
            # 挂车规则：最后一位为'挂'
            pass
        elif '学' in sequence:
            # 教练车规则
            pass
        # 其他普通车牌的序号规则可以在此细化
        # 例如，检查字母和数字的组合是否符合启用顺序
        # 目前只做基本字符验证，已在 validate_format 中完成
        
        return True

def validate_plate_number(plate_number: str) -> bool:
    """
    便捷函数，用于快速验证车牌号码。

    Args:
        plate_number (str): 待验证的车牌号码。

    Returns:
        bool: 如果车牌号码有效，则返回 True。
    """
    try:
        validator = PlateValidator(plate_number)
        return validator.validate()
    except PlateNumberError:
        return False

