"""
主车牌生成器模块

基于GA 36-2018标准的车牌生成器，整合新的规则系统。
提供统一的生成接口，支持自动车牌类型识别和生成。
"""

from typing import Optional, Dict, Any, Tuple, List
from pydantic import BaseModel
import random

from ..rules.ordinary_plate import OrdinaryPlateRuleFactory, OrdinaryPlateSubType
from ..rules.new_energy_plate import NewEnergyPlateRuleFactory
from ..rules.province_codes import ProvinceManager
from ..rules.regional_codes import RegionalCodeManager
from ..rules.special_plate import SpecialPlateRuleFactory
from ..utils.constants import PlateType
from ..core.exceptions import PlateGenerationError


class PlateInfo(BaseModel):
    """车牌信息数据结构"""
    plate_number: str
    plate_type: str
    province: str
    regional_code: str
    sequence: str
    background_color: str
    is_double_layer: bool
    split_position: int  # 分隔符位置（第几位字符后分隔）
    special_chars: Optional[List[str]] = None
    
    
class PlateGenerationConfig(BaseModel):
    """车牌生成配置"""
    plate_type: Optional[str] = None  # 指定车牌类型，None表示随机
    province: Optional[str] = None    # 指定省份，None表示随机
    regional_code: Optional[str] = None  # 指定地区代号，None表示随机
    new_energy_type: Optional[str] = None  # 新能源车类型：electric/hybrid，None表示随机
    special_type: Optional[str] = None  # 特殊车牌类型
    

class PlateGenerator:
    """
    主车牌生成器
    
    整合所有车牌规则，提供统一的生成接口。
    这是与外部交互的主要类。
    """
    
    def __init__(self):
        """
        初始化生成器。
        
        在初始化过程中，会加载所有车牌类型的规则工厂，
        并设置一个符合真实世界情况的车牌类型生成权重。
        """
        # 初始化规则工厂
        self.ordinary_factory = OrdinaryPlateRuleFactory()
        self.new_energy_factory = NewEnergyPlateRuleFactory()
        self.special_factory = SpecialPlateRuleFactory()
        
        # 车牌类型权重分布(基于现实情况)
        self.type_weights = {
            PlateType.ORDINARY_BLUE: 0.6,      # 普通蓝牌 60%
            PlateType.NEW_ENERGY_GREEN: 0.25,  # 新能源绿牌 25%
            PlateType.ORDINARY_YELLOW: 0.08,   # 黄牌 8%
            PlateType.POLICE_WHITE: 0.03,      # 警车白牌 3%
            PlateType.EMBASSY_BLACK: 0.02,     # 使领馆黑牌 2%
            PlateType.MILITARY_WHITE: 0.02,    # 军车白牌 2%
        }
        
    def generate_random_plate(self, config: Optional[PlateGenerationConfig] = None) -> PlateInfo:
        """
        随机生成一个符合GA 36-2018标准的车牌。
        
        可以不提供任何配置，生成器会根据内置的权重随机选择车牌类型。
        也可以通过 `PlateGenerationConfig` 提供详细的生成参数，如省份、
        地区、车牌类型等。

        Args:
            config (Optional[PlateGenerationConfig]): 
                生成配置。如果为None，则完全随机生成。
                可以指定 `plate_type`, `province`, `regional_code` 等参数。
            
        Returns:
            PlateInfo: 包含车牌号码、类型、颜色等信息的详细数据结构。
            
        Raises:
            PlateGenerationError: 如果根据提供的配置无法生成车牌，则抛出此异常。
        """
        if config is None:
            config = PlateGenerationConfig()
            
        try:
            # 确定车牌类型
            plate_type = self._determine_plate_type(config.plate_type)
            
            # 根据车牌类型生成
            if plate_type in [PlateType.ORDINARY_BLUE, PlateType.ORDINARY_YELLOW, 
                             PlateType.POLICE_WHITE, PlateType.ORDINARY_COACH, PlateType.ORDINARY_TRAILER]:
                return self._generate_ordinary_plate(plate_type, config)
            elif plate_type in [PlateType.NEW_ENERGY_GREEN, PlateType.NEW_ENERGY_SMALL, PlateType.NEW_ENERGY_LARGE]:
                return self._generate_new_energy_plate(config)
            elif plate_type in [PlateType.EMBASSY_BLACK, PlateType.MILITARY_WHITE, 
                               PlateType.HONGKONG_BLACK, PlateType.MACAO_BLACK]:
                return self._generate_special_plate(plate_type, config)
            else:
                raise PlateGenerationError(f"不支持的车牌类型: {plate_type}")
                
        except Exception as e:
            raise PlateGenerationError(f"车牌生成失败: {str(e)}")
    
    def generate_specific_plate(self, plate_number: str) -> PlateInfo:
        """
        根据给定的车牌号码字符串，分析其结构并生成对应的车牌信息。
        
        此方法会尝试自动识别车牌类型（如新能源、警车等），并解析出
        省份、地区代码和序号。
        
        Args:
            plate_number (str): 要生成的车牌号码字符串。
            
        Returns:
            PlateInfo: 包含分析出的车牌信息的详细数据结构。
            
        Raises:
            PlateGenerationError: 如果车牌号码格式无效或无法解析，则抛出此异常。
        """
        try:
            # 分析号码确定车牌类型
            plate_type = self._analyze_plate_type(plate_number)
            
            # 解析号码组成
            province, regional_code, sequence = self._parse_plate_number(plate_number)
            
            # 获取背景颜色和是否双层
            bg_color, is_double = self._get_plate_style(plate_type, plate_number)
            
            # 检测特殊字符
            special_chars = self._detect_special_chars(plate_number)
            
            # 确定分隔位置
            split_pos = self._determine_split_position(plate_type, plate_number)
            
            return PlateInfo(
                plate_number=plate_number,
                plate_type=plate_type,
                province=province,
                regional_code=regional_code,
                sequence=sequence,
                background_color=bg_color,
                is_double_layer=is_double,
                split_position=split_pos,
                special_chars=special_chars
            )
            
        except Exception as e:
            raise PlateGenerationError(f"指定车牌生成失败: {str(e)}")
    
    def generate_batch_plates(self, count: int, config: Optional[PlateGenerationConfig] = None) -> List[PlateInfo]:
        """
        批量生成车牌。
        
        可以像 `generate_random_plate` 一样提供配置。如果生成过程中
        遇到错误，会跳过当前失败的生成并继续尝试，直到达到指定数量。
        
        Args:
            count (int): 要生成的车牌数量。
            config (Optional[PlateGenerationConfig]): 应用于所有生成车牌的配置。
            
        Returns:
            List[PlateInfo]: 生成的车牌信息列表。
        """
        plates = []
        for _ in range(count):
            try:
                plate = self.generate_random_plate(config)
                plates.append(plate)
            except PlateGenerationError:
                # 跳过失败的生成，继续尝试
                continue
        return plates
    
    def _determine_plate_type(self, specified_type: Optional[str]) -> str:
        """确定车牌类型"""
        if specified_type:
            return specified_type
        
        # 按权重随机选择
        types = list(self.type_weights.keys())
        weights = list(self.type_weights.values())
        return random.choices(types, weights=weights)[0]
    
    def _generate_ordinary_plate(self, plate_type: str, config: PlateGenerationConfig) -> PlateInfo:
        """生成普通车牌"""
        # 根据类型获取规则
        if plate_type == PlateType.ORDINARY_BLUE:
            rule = self.ordinary_factory.create_rule(OrdinaryPlateSubType.SMALL_CAR)
        elif plate_type == PlateType.ORDINARY_YELLOW:
            rule = self.ordinary_factory.create_rule(OrdinaryPlateSubType.LARGE_CAR)
        elif plate_type == PlateType.POLICE_WHITE:
            rule = self.ordinary_factory.create_rule(OrdinaryPlateSubType.POLICE)
        elif plate_type == PlateType.ORDINARY_COACH:
            rule = self.ordinary_factory.create_rule(OrdinaryPlateSubType.COACH)
        elif plate_type == PlateType.ORDINARY_TRAILER:
            rule = self.ordinary_factory.create_rule(OrdinaryPlateSubType.TRAILER)
        else:
            rule = self.ordinary_factory.create_rule(OrdinaryPlateSubType.SMALL_CAR)
        
        # 生成车牌信息
        if config.province and config.regional_code:
            plate_info = rule.generate_plate(
                province=config.province,
                regional_code=config.regional_code
            )
        else:
            # 随机选择省份和地区代号
            if config.province:
                province = config.province
            else:
                province = random.choice(ProvinceManager.get_all_abbreviations())
            
            if config.regional_code:
                regional_code = config.regional_code
            else:
                available_codes = RegionalCodeManager.get_all_codes_for_province(province)
                if not available_codes:
                    raise PlateGenerationError(f"省份 {province} 没有可用的地区代号")
                regional_code = random.choice(available_codes)
            
            plate_info = rule.generate_plate(province, regional_code)
        
        # 从生成的PlateInfo中提取号码
        plate_number = plate_info.plate_number
        
        # 解析号码组成
        province, regional_code, sequence = self._parse_plate_number(plate_number)
        
        # 获取样式信息
        bg_color, is_double = self._get_plate_style(plate_type, plate_number)
        special_chars = self._detect_special_chars(plate_number)
        split_pos = self._determine_split_position(plate_type, plate_number)
        
        return PlateInfo(
            plate_number=plate_number,
            plate_type=plate_type,
            province=province,
            regional_code=regional_code,
            sequence=sequence,
            background_color=bg_color,
            is_double_layer=is_double,
            split_position=split_pos,
            special_chars=special_chars
        )
    
    def _generate_new_energy_plate(self, config: PlateGenerationConfig) -> PlateInfo:
        """生成新能源车牌"""
        # 确定新能源车类型
        if config.new_energy_type == "electric":
            rule = self.new_energy_factory.create_rule("small_electric")
        elif config.new_energy_type == "hybrid":
            rule = self.new_energy_factory.create_rule("small_hybrid")
        else:
            # 随机选择
            ne_type = random.choice(["small_electric", "small_hybrid", "large_electric", "large_hybrid"])
            rule = self.new_energy_factory.create_rule(ne_type)
        
        # 生成车牌信息
        if config.province and config.regional_code:
            plate_info = rule.generate_plate(
                province=config.province,
                regional_code=config.regional_code
            )
        else:
            # 随机选择省份和地区代号
            if config.province:
                province = config.province
            else:
                province = random.choice(ProvinceManager.get_all_abbreviations())
            
            if config.regional_code:
                regional_code = config.regional_code
            else:
                available_codes = RegionalCodeManager.get_all_codes_for_province(province)
                if not available_codes:
                    raise PlateGenerationError(f"省份 {province} 没有可用的地区代号")
                regional_code = random.choice(available_codes)
            
            plate_info = rule.generate_plate(province, regional_code)
        
        # 直接返回rule生成的PlateInfo，它已经包含了正确的类型和背景颜色
        return plate_info
    
    def _generate_special_plate(self, plate_type: str, config: PlateGenerationConfig) -> PlateInfo:
        """生成特殊车牌"""
        # 根据类型获取规则
        if plate_type == PlateType.EMBASSY_BLACK:
            rule = self.special_factory.create_rule("embassy")
        elif plate_type == PlateType.MILITARY_WHITE:
            rule = self.special_factory.create_rule("military")
        elif plate_type == PlateType.HONGKONG_BLACK:
            rule = self.special_factory.create_rule("hong_kong_macao")
        elif plate_type == PlateType.MACAO_BLACK:
            rule = self.special_factory.create_rule("hong_kong_macao")
        else:
            rule = self.special_factory.create_rule("embassy")
        
        # 生成车牌信息
        if config.province and config.regional_code:
            plate_info = rule.generate_plate(
                province=config.province,
                regional_code=config.regional_code
            )
        else:
            # 随机选择省份和地区代号
            if config.province:
                province = config.province
            else:
                province = random.choice(ProvinceManager.get_all_abbreviations())
            
            if config.regional_code:
                regional_code = config.regional_code
            else:
                available_codes = RegionalCodeManager.get_all_codes_for_province(province)
                if not available_codes:
                    raise PlateGenerationError(f"省份 {province} 没有可用的地区代号")
                regional_code = random.choice(available_codes)
            
            plate_info = rule.generate_plate(province, regional_code)
        
        # 从生成的PlateInfo中提取号码
        plate_number = plate_info.plate_number
        
        # 解析号码组成
        province, regional_code, sequence = self._parse_plate_number(plate_number)
        
        # 获取样式信息
        bg_color, is_double = self._get_plate_style(plate_type, plate_number)
        special_chars = self._detect_special_chars(plate_number)
        split_pos = self._determine_split_position(plate_type, plate_number)
        
        return PlateInfo(
            plate_number=plate_number,
            plate_type=plate_type,
            province=province,
            regional_code=regional_code,
            sequence=sequence,
            background_color=bg_color,
            is_double_layer=is_double,
            split_position=split_pos,
            special_chars=special_chars
        )
    
    def _analyze_plate_type(self, plate_number: str) -> str:
        """分析车牌号码确定类型"""
        # 8位数字表示新能源
        if len(plate_number) == 8:
            return PlateType.NEW_ENERGY_GREEN
        
        # 检查特殊字符
        if '使' in plate_number:
            return PlateType.EMBASSY_BLACK
        elif '领' in plate_number:
            return PlateType.EMBASSY_BLACK
        elif '港' in plate_number:
            return PlateType.HONGKONG_BLACK
        elif '澳' in plate_number:
            return PlateType.MACAO_BLACK
        elif '警' in plate_number:
            return PlateType.POLICE_WHITE
        elif '学' in plate_number:
            return PlateType.ORDINARY_COACH
        elif '挂' in plate_number:
            return PlateType.ORDINARY_TRAILER
        elif plate_number[0].isalpha() and plate_number[0] not in ProvinceManager.get_all_abbreviations():
            return PlateType.MILITARY_WHITE
        
        # 默认为普通蓝牌
        return PlateType.ORDINARY_BLUE
    
    def _parse_plate_number(self, plate_number: str) -> Tuple[str, str, str]:
        """解析车牌号码组成"""
        if len(plate_number) >= 2:
            province = plate_number[0]
            regional_code = plate_number[1]
            sequence = plate_number[2:]
        else:
            raise PlateGenerationError(f"无效的车牌号码格式: {plate_number}")
        
        return province, regional_code, sequence
    
    def _get_plate_style(self, plate_type: str, plate_number: str) -> Tuple[str, bool]:
        """获取车牌样式信息"""
        # 背景颜色映射
        color_map = {
            PlateType.ORDINARY_BLUE: "blue",
            PlateType.ORDINARY_YELLOW: "yellow", 
            PlateType.NEW_ENERGY_GREEN: "green_car",
            PlateType.POLICE_WHITE: "white",
            PlateType.MILITARY_WHITE: "white_army",
            PlateType.EMBASSY_BLACK: "black_shi" if '使' in plate_number else "black",
            PlateType.HONGKONG_BLACK: "black",
            PlateType.MACAO_BLACK: "black",
            PlateType.ORDINARY_COACH: "yellow",
            PlateType.ORDINARY_TRAILER: "yellow",
        }
        
        # 是否双层判断
        is_double = False
        if '挂' in plate_number:  # 挂车通常是双层
            is_double = True
        elif plate_type in [PlateType.ORDINARY_YELLOW]:  # 部分黄牌可能是双层
            is_double = random.choice([True, False])
        
        bg_color = color_map.get(plate_type, "blue")
        return bg_color, is_double
    
    def _detect_special_chars(self, plate_number: str) -> Optional[List[str]]:
        """检测特殊字符"""
        special_chars = []
        special_set = {'使', '领', '港', '澳', '警', '学', '挂'}
        
        for char in plate_number:
            if char in special_set:
                special_chars.append(char)
        
        return special_chars if special_chars else None
    
    def _determine_split_position(self, plate_type: str, plate_number: str) -> int:
        """
        确定车牌分隔符位置
        
        Args:
            plate_type: 车牌类型
            plate_number: 车牌号码
            
        Returns:
            int: 分隔符位置（第几位后分隔）
        """
        # 特殊字符分隔位置映射
        SPECIAL_CHAR_SPLIT_MAP = {
            '使': 3,  # 使馆车牌: 省12·3456使
            '领': 4,  # 领馆车牌: 省123·45领  
            '港': 2,  # 港澳车牌: 粤Z·1234港
            '澳': 2,  # 港澳车牌: 粤Z·1234澳
        }
        
        # 检查特殊字符
        for char, position in SPECIAL_CHAR_SPLIT_MAP.items():
            if char in plate_number:
                return position
                
        # 特殊车牌类型
        if plate_type == PlateType.MILITARY_WHITE:
            return 2  # 军队车牌: AB·1234
            
        # 默认分隔位置
        return 2