"""
特殊车牌规则模块
基于GA 36-2018标准实现特殊车牌的生成和验证规则
包括：使馆汽车号牌、领馆汽车号牌、港澳入出境车号牌、军队车牌
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
import random

from .base_rule import BaseRule, PlateType, PlateColor, PlateInfo, ValidationResult
from .sequence_generator import OrdinarySequenceGenerator
from ..core.exceptions import PlateGenerationError


class SpecialPlateSubType(Enum):
    """特殊车牌子类型"""
    EMBASSY = "embassy"  # 使馆汽车号牌
    CONSULATE = "consulate"  # 领馆汽车号牌
    HONG_KONG_MACAO = "hong_kong_macao"  # 港澳入出境车号牌
    MILITARY = "military"  # 军队车牌


class EmbassyPlateType(Enum):
    """使馆车牌类型"""
    EMBASSY_CHIEF = "embassy_chief"  # 使馆馆长车
    EMBASSY_STAFF = "embassy_staff"  # 使馆工作人员车
    EMBASSY_TEMPORARY = "embassy_temporary"  # 使馆临时车牌


class ConsulatePlateType(Enum):
    """领馆车牌类型"""
    CONSULATE_CHIEF = "consulate_chief"  # 领馆总领事车
    CONSULATE_STAFF = "consulate_staff"  # 领馆工作人员车
    CONSULATE_TEMPORARY = "consulate_temporary"  # 领馆临时车牌


class HongKongMacaoPlateType(Enum):
    """港澳车牌类型"""
    HONG_KONG = "hong_kong"  # 港车北上
    MACAO = "macao"  # 澳车北上


class MilitaryPlateType(Enum):
    """军队车牌类型"""
    ARMY = "army"  # 陆军
    NAVY = "navy"  # 海军
    AIR_FORCE = "air_force"  # 空军
    ROCKET_FORCE = "rocket_force"  # 火箭军
    STRATEGIC_SUPPORT = "strategic_support"  # 战略支援部队
    JOINT_LOGISTICS = "joint_logistics"  # 联勤保障部队
    ARMED_POLICE = "armed_police"  # 武警部队


class SpecialPlateRule(BaseRule):
    """
    特殊车牌规则类
    实现GA 36-2018标准中关于特殊车牌的各项规则
    """
    
    def __init__(self, sub_type: SpecialPlateSubType):
        """
        初始化特殊车牌规则
        
        Args:
            sub_type: 特殊车牌子类型
        """
        super().__init__()
        self.sub_type = sub_type
        self.sequence_length = 5  # 大部分特殊车牌序号长度为5位
        self.allow_letters = True
        self.forbidden_letters = ["I", "O"]
        
        # 根据子类型设置车牌属性
        self._setup_plate_properties()
        
        # 初始化序号生成器（使用普通汽车的序号生成逻辑）
        self.sequence_generator = OrdinarySequenceGenerator()
    
    def _setup_plate_properties(self):
        """根据子类型设置车牌属性"""
        if self.sub_type == SpecialPlateSubType.EMBASSY:
            self.plate_type = PlateType.EMBASSY
            self.background_color = PlateColor.BLACK
            self.font_color = "white"
            self.special_chars = ["使"]
            self.red_chars = []  # 使字符为白色，不是红色
            self.is_double_layer = False
            self.sequence_length = 6
            
        elif self.sub_type == SpecialPlateSubType.CONSULATE:
            self.plate_type = PlateType.CONSULATE
            self.background_color = PlateColor.BLACK
            self.font_color = "white"
            self.special_chars = ["领"]
            self.red_chars = []  # 领字符为白色，不是红色
            self.is_double_layer = False
            self.sequence_length = 5  # 5位数字序号
            
        elif self.sub_type == SpecialPlateSubType.HONG_KONG_MACAO:
            self.plate_type = PlateType.HONG_KONG_MACAO
            self.background_color = PlateColor.BLACK
            self.font_color = "white"
            self.special_chars = []  # 会根据具体类型设置港或澳
            self.red_chars = []  # 港澳字符为白色
            self.is_double_layer = False
            self.sequence_length = 5
            
        elif self.sub_type == SpecialPlateSubType.MILITARY:
            self.plate_type = PlateType.MILITARY
            self.background_color = PlateColor.WHITE
            self.font_color = "red"  # 军队车牌为红字
            self.special_chars = []  # 首位为军种字母
            self.red_chars = []  # 所有字符都是红色
            self.is_double_layer = False
            self.sequence_length = 5  # 军队车牌序号5位
    
    def generate_sequence(self, 
                         province: str, 
                         regional_code: str,
                         special_type: Optional[str] = None,
                         **kwargs) -> str:
        """
        生成特殊车牌序号
        
        Args:
            province: 省份简称（对于使馆、领馆车牌通常为"使"或"领"）
            regional_code: 发牌机关代号或特殊标识
            special_type: 特殊类型（如军种、国家代码等）
            **kwargs: 其他参数
            
        Returns:
            str: 生成的序号
        
        Raises:
            PlateGenerationError: 序号生成失败时抛出
        """
        try:
            if self.sub_type == SpecialPlateSubType.EMBASSY:
                return self._generate_embassy_sequence(special_type)
            elif self.sub_type == SpecialPlateSubType.CONSULATE:
                return self._generate_consulate_sequence(special_type)
            elif self.sub_type == SpecialPlateSubType.HONG_KONG_MACAO:
                return self._generate_hong_kong_macao_sequence(special_type)
            elif self.sub_type == SpecialPlateSubType.MILITARY:
                return self._generate_military_sequence(special_type)
            else:
                raise PlateGenerationError(f"不支持的特殊车牌类型: {self.sub_type}")
                
        except Exception as e:
            raise PlateGenerationError(f"特殊车牌序号生成失败: {str(e)}")
    
    def _generate_embassy_sequence(self, embassy_type: Optional[str] = None) -> str:
        """
        生成使馆汽车号牌序号
        格式：三位驻华外交机构编号 + 三位序号 (最终车牌号为：三位机构编号·三位序号+使)
        
        Args:
            embassy_type: 使馆类型
            
        Returns:
            str: 生成的序号 (6位数字：前3位为机构编号，后3位为序号)
        """
        # 三位驻华外交机构编号 (示例范围: 001-223)
        institution_code = "".join([str(random.randint(0, 9)) for _ in range(3)])
        # 确保机构编号不以00开头（除了001这种情况）
        if institution_code == "000":
            institution_code = "001"
        
        # 三位序号
        sequence_digits = "".join([str(random.randint(0, 9)) for _ in range(3)])
        
        return f"{institution_code}{sequence_digits}"
    
    def _generate_consulate_sequence(self, consulate_type: Optional[str] = None) -> str:
        """
        生成领馆汽车号牌序号
        格式：三位驻华外交机构编号 + 两位序号 (最终车牌号为：省份+三位机构编号·两位序号+领)
        
        Args:
            consulate_type: 领馆类型
            
        Returns:
            str: 生成的序号 (5位数字：前3位为机构编号，后2位为序号)
        """
        # 三位驻华外交机构编号 (示例范围: 224-999)
        institution_code = "".join([str(random.randint(0, 9)) for _ in range(3)])
        # 确保机构编号不以00开头
        if institution_code.startswith("00"):
            institution_code = f"2{institution_code[2:]}"
        
        # 两位序号
        sequence_digits = "".join([str(random.randint(0, 9)) for _ in range(2)])
        
        return f"{institution_code}{sequence_digits}"
    
    def _generate_hong_kong_macao_sequence(self, region_type: Optional[str] = None) -> str:
        """
        生成港澳入出境车号牌序号
        格式：港/澳 + 字母 + 数字
        
        Args:
            region_type: 地区类型（hong_kong或macao）
            
        Returns:
            str: 生成的序号
        """
        # 生成1个字母和4位数字
        letter = random.choice(self.get_available_letters())
        digits = "".join([str(random.randint(0, 9)) for _ in range(4)])
        
        return f"{letter}{digits}"
    
    def _generate_military_sequence(self, military_type: Optional[str] = None) -> str:
        """
        生成军队车牌序号
        格式：军种字母 + 4位数字或字母数字组合
        
        Args:
            military_type: 军种类型
            
        Returns:
            str: 生成的序号
        """
        # 军种字母代码 # TODO: 替换为真实的军种字母
        military_letters = {
            "army": "A",  # 陆军
            "navy": "N",  # 海军
            "air_force": "R",  # 空军
            "rocket_force": "S",  # 火箭军
            "strategic_support": "T",  # 战略支援部队
            "joint_logistics": "L",  # 联勤保障部队
            "armed_police": "W"  # 武警部队
        }
        
        # 选择军种字母
        if military_type and military_type in military_letters:
            military_letter = military_letters[military_type]
        else:
            military_letter = random.choice(list(military_letters.values()))
        
        # 生成4位序号（可以是数字或字母数字组合）
        sequence = ""
        for _ in range(4):
            if random.choice([True, False]):  # 50%概率选择数字或字母
                sequence += str(random.randint(0, 9))
            else:
                sequence += random.choice(self.get_available_letters())
        
        return f"{military_letter}{sequence}"
    
    def validate_sequence(self, sequence: str) -> ValidationResult:
        """
        验证特殊车牌序号
        
        Args:
            sequence: 序号字符串
            
        Returns:
            ValidationResult: 验证结果
        """
        # 基本长度检查
        expected_length = self.sequence_length
        if len(sequence) != expected_length:
            return ValidationResult(
                is_valid=False,
                error_message=f"特殊车牌序号长度必须为{expected_length}位，当前为{len(sequence)}位"
            )
        
        # 检查是否包含禁用字母
        if self.contains_forbidden_letters(sequence):
            return ValidationResult(
                is_valid=False,
                error_message=f"序号包含禁用字母(I, O): {sequence}"
            )
        
        # 根据子类型进行具体验证
        if self.sub_type == SpecialPlateSubType.EMBASSY:
            return self._validate_embassy_sequence(sequence)
        elif self.sub_type == SpecialPlateSubType.CONSULATE:
            return self._validate_consulate_sequence(sequence)
        elif self.sub_type == SpecialPlateSubType.HONG_KONG_MACAO:
            return self._validate_hong_kong_macao_sequence(sequence)
        elif self.sub_type == SpecialPlateSubType.MILITARY:
            return self._validate_military_sequence(sequence)
        
        return ValidationResult(is_valid=True)
    
    def _validate_embassy_sequence(self, sequence: str) -> ValidationResult:
        """验证使馆车牌序号"""
        # 使馆车牌：机构编号（3位数字）+ 序号（3位数字）
        if len(sequence) != 6:
            return ValidationResult(
                is_valid=False,
                error_message="使馆车牌序号必须为6位（3位机构编号+3位序号）"
            )
        
        if not sequence.isdigit():
            return ValidationResult(
                is_valid=False,
                error_message="使馆车牌序号必须全为数字"
            )
        
        # 检查机构编号不应该为000
        institution_code = sequence[:3]
        if institution_code == "000":
            return ValidationResult(
                is_valid=False,
                error_message="使馆车牌机构编号不能为000"
            )
        
        return ValidationResult(is_valid=True)
    
    def _validate_consulate_sequence(self, sequence: str) -> ValidationResult:
        """验证领馆车牌序号"""
        # 领馆车牌：5位数字序号（前3位机构编号+后2位序号）
        if len(sequence) != 5:
            return ValidationResult(
                is_valid=False,
                error_message="领馆车牌序号必须为5位（3位机构编号+2位序号）"
            )
        
        if not sequence.isdigit():
            return ValidationResult(
                is_valid=False,
                error_message="领馆车牌序号必须全为数字"
            )
        
        # 检查机构编号不应该为000
        institution_code = sequence[:3]
        if institution_code == "000":
            return ValidationResult(
                is_valid=False,
                error_message="领馆车牌机构编号不能为000"
            )
        
        return ValidationResult(is_valid=True)
    
    def _validate_hong_kong_macao_sequence(self, sequence: str) -> ValidationResult:
        """验证港澳车牌序号"""
        # 港澳车牌：字母（1位）+ 数字（4位）
        if len(sequence) != 5:
            return ValidationResult(
                is_valid=False,
                error_message="港澳车牌序号必须为5位"
            )
        
        if not sequence[0].isalpha():
            return ValidationResult(
                is_valid=False,
                error_message="港澳车牌序号第1位必须为字母"
            )
        
        if not sequence[1:].isdigit():
            return ValidationResult(
                is_valid=False,
                error_message="港澳车牌序号第2-5位必须为数字"
            )
        
        return ValidationResult(is_valid=True)
    
    def _validate_military_sequence(self, sequence: str) -> ValidationResult:
        """验证军队车牌序号"""
        # 军队车牌：军种字母（1位）+ 序号（4位数字或字母数字组合）
        if len(sequence) != 5:
            return ValidationResult(
                is_valid=False,
                error_message="军队车牌序号必须为5位"
            )
        
        if not sequence[0].isalpha():
            return ValidationResult(
                is_valid=False,
                error_message="军队车牌序号第1位必须为军种字母"
            )
        
        # 检查军种字母是否有效
        valid_military_letters = ["A", "N", "R", "S", "T", "L", "W"]
        if sequence[0] not in valid_military_letters:
            return ValidationResult(
                is_valid=False,
                error_message=f"无效的军种字母: {sequence[0]}"
            )
        
        # 检查后4位是否为有效字符
        for i, char in enumerate(sequence[1:], 1):
            if not (char.isdigit() or char.isalpha()):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"军队车牌序号第{i+1}位字符无效: {char}"
                )
        
        return ValidationResult(is_valid=True)
    
    def get_plate_info(self, 
                      province: str, 
                      regional_code: str, 
                      sequence: str,
                      special_type: Optional[str] = None) -> PlateInfo:
        """
        生成完整的特殊车牌信息
        
        Args:
            province: 省份简称或特殊标识（如"使"、"领"、"港"、"澳"）
            regional_code: 发牌机关代号或特殊标识
            sequence: 序号
            special_type: 特殊类型
            
        Returns:
            PlateInfo: 车牌信息对象
        """
        # 验证序号
        sequence_result = self.validate_sequence(sequence)
        if not sequence_result.is_valid:
            raise PlateGenerationError(sequence_result.error_message)
        
        special_chars = list(self.special_chars)  # 创建副本以避免副作用
        plate_number = ""

        # 根据特殊车牌类型处理省份、地区代号和车牌号
        if self.sub_type == SpecialPlateSubType.EMBASSY:
            # 使馆车牌：不包含分隔符，纯字符序列
            province = ""
            regional_code = ""
            plate_number = f"{sequence}使"
        elif self.sub_type == SpecialPlateSubType.CONSULATE:
            # 领馆车牌：不包含分隔符，纯字符序列
            # 随机选择一个省份简称
            province_codes = ["京", "津", "沪", "渝", "冀", "豫", "云", "辽", "黑", "湘", "皖", "鲁", "新", "苏", "浙", "赣", "鄂", "桂", "甘", "晋", "蒙", "陕", "吉", "闽", "贵", "粤", "青", "藏", "川", "宁", "琼"]
            import random
            province = random.choice(province_codes)
            regional_code = ""
            plate_number = f"{province}{sequence}领"
                
        elif self.sub_type == SpecialPlateSubType.HONG_KONG_MACAO:
            province = "粤"
            regional_code = "Z"
            if special_type == "macao":
                special_chars = ["澳"]
            else: # 默认为港牌
                special_chars = ["港"]
            plate_number = f"{province}{regional_code}{sequence}{special_chars[0]}"
        
        elif self.sub_type == SpecialPlateSubType.MILITARY:
            # 对于军队车牌, plate_number 就是完整的序号
            plate_number = sequence
            # Reason: 军队车牌的省份和地区代码是其序号的一部分, 此处进行修正
            province = sequence[0]
            regional_code = ""
        
        # 如果有未处理的类型, 使用基类格式
        if not plate_number:
            plate_number = super().format_plate_number(province, regional_code, sequence)

        # 创建车牌信息对象
        plate_info = PlateInfo(
            plate_number=plate_number,
            plate_type=self.plate_type,
            province=province,
            regional_code=regional_code,
            sequence=sequence,
            background_color=self.background_color,
            is_double_layer=self.is_double_layer,
            special_chars=special_chars,
            font_color=self.font_color,
            red_chars=self.red_chars
        )
        
        return plate_info

    def format_plate_number(self, province: str, regional_code: str, sequence: str) -> str:
        """
        重写格式化方法以处理特殊车牌
        """
        if self.sub_type in [SpecialPlateSubType.EMBASSY, SpecialPlateSubType.CONSULATE]:
            # 使领馆车牌格式: 使/领 + 序号
            return f"{province}{sequence}"
        
        if self.sub_type == SpecialPlateSubType.HONG_KONG_MACAO:
            # 港澳车牌格式: 粤Z + 序号 + 港/澳
            return f"{province}{regional_code}{sequence}{self.special_chars[0]}"

        return super().format_plate_number(province, regional_code, sequence)
    
    def generate_plate(self, 
                      province: str = "",
                      regional_code: str = "",
                      special_type: Optional[str] = None,
                      **kwargs) -> PlateInfo:
        """
        生成完整的特殊车牌
        
        Args:
            province: 省份简称（特殊车牌可以为空）
            regional_code: 发牌机关代号（特殊车牌可以为空）
            special_type: 特殊类型
            **kwargs: 其他参数
            
        Returns:
            PlateInfo: 生成的车牌信息
        """
        # 军牌需要特殊处理，因为它不使用传统的省份和地区代码
        if self.sub_type == SpecialPlateSubType.MILITARY:
            # 1. 生成完整的5位军牌序号（例如 "A1234"）
            sequence = self.generate_sequence(province, regional_code, special_type, **kwargs)
            
            # 2. 解析军牌结构
            prov = sequence[0]  # 省份/军种
            reg_code = ""  # 军队车牌没有传统意义上的地区代码
            
            # 3. 直接使用完整的5位序号创建 PlateInfo
            return self.get_plate_info(prov, reg_code, sequence, special_type)

        # 其他特殊车牌（使、领、港澳）的逻辑
        sequence = self.generate_sequence(
            province=province,
            regional_code=regional_code,
            special_type=special_type,
            **kwargs
        )
        
        # 生成完整车牌信息
        return self.get_plate_info(province, regional_code, sequence, special_type)
    
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
    
    def get_available_special_types(self) -> List[str]:
        """
        获取可用的特殊类型列表
        
        Returns:
            List[str]: 特殊类型列表
        """
        if self.sub_type == SpecialPlateSubType.EMBASSY:
            return [e.value for e in EmbassyPlateType]
        elif self.sub_type == SpecialPlateSubType.CONSULATE:
            return [c.value for c in ConsulatePlateType]
        elif self.sub_type == SpecialPlateSubType.HONG_KONG_MACAO:
            return [h.value for h in HongKongMacaoPlateType]
        elif self.sub_type == SpecialPlateSubType.MILITARY:
            return [m.value for m in MilitaryPlateType]
        else:
            return []


class SpecialPlateRuleFactory:
    """
    特殊车牌规则工厂类
    根据车牌子类型创建相应的规则对象
    """
    
    @staticmethod
    def create_rule(sub_type: Union[str, SpecialPlateSubType]) -> "SpecialPlateRule":
        """
        创建特殊车牌规则
        
        Args:
            sub_type: 特殊车牌子类型
            
        Returns:
            SpecialPlateRule: 规则对象
        """
        if isinstance(sub_type, str):
            st = SpecialPlateSubType(sub_type)
        else:
            st = sub_type
        return SpecialPlateRule(st)
    
    @staticmethod
    def create_embassy_rule() -> SpecialPlateRule:
        """
        创建使馆汽车号牌规则
        
        Returns:
            SpecialPlateRule: 使馆汽车号牌规则对象
        """
        return SpecialPlateRuleFactory.create_rule(SpecialPlateSubType.EMBASSY)
    
    @staticmethod
    def create_consulate_rule() -> SpecialPlateRule:
        """
        创建领馆汽车号牌规则
        
        Returns:
            SpecialPlateRule: 领馆汽车号牌规则对象
        """
        return SpecialPlateRuleFactory.create_rule(SpecialPlateSubType.CONSULATE)
    
    @staticmethod
    def create_hong_kong_macao_rule() -> SpecialPlateRule:
        """
        创建港澳入出境车号牌规则
        
        Returns:
            SpecialPlateRule: 港澳入出境车号牌规则对象
        """
        return SpecialPlateRuleFactory.create_rule(SpecialPlateSubType.HONG_KONG_MACAO)
    
    @staticmethod
    def create_military_rule() -> SpecialPlateRule:
        """
        创建军队车牌规则
        
        Returns:
            SpecialPlateRule: 军队车牌规则对象
        """
        return SpecialPlateRuleFactory.create_rule(SpecialPlateSubType.MILITARY)
    
    @staticmethod
    def get_all_sub_types() -> List[SpecialPlateSubType]:
        """
        获取所有特殊车牌子类型
        
        Returns:
            List[SpecialPlateSubType]: 子类型列表
        """
        return list(SpecialPlateSubType)
    
    @staticmethod
    def get_sub_type_by_name(name: str) -> Optional[SpecialPlateSubType]:
        """
        根据名称获取子类型
        
        Args:
            name: 子类型名称
            
        Returns:
            Optional[SpecialPlateSubType]: 子类型对象，未找到时返回None
        """
        for sub_type in SpecialPlateSubType:
            if sub_type.value == name:
                return sub_type
        return None