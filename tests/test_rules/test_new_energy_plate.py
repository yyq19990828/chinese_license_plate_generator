"""
新能源汽车号牌规则测试模块
测试新能源汽车号牌规则类的所有功能
"""

import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.rules.new_energy_plate import (
    NewEnergyPlateRule, 
    NewEnergyPlateSubType, 
    EnergyType,
    NewEnergyPlateRuleFactory
)
from src.rules.base_rule import PlateType, PlateColor, ValidationResult
from src.core.exceptions import PlateGenerationError


class TestNewEnergyPlateRule:
    """新能源汽车号牌规则测试类"""
    
    def setup_method(self):
        """测试前的准备工作"""
        self.small_car_rule = NewEnergyPlateRule(NewEnergyPlateSubType.SMALL_CAR)
        self.large_car_rule = NewEnergyPlateRule(NewEnergyPlateSubType.LARGE_CAR)
    
    def test_init_small_car(self):
        """测试小型新能源汽车号牌规则初始化"""
        rule = NewEnergyPlateRule(NewEnergyPlateSubType.SMALL_CAR)
        
        assert rule.sub_type == NewEnergyPlateSubType.SMALL_CAR
        assert rule.plate_type == PlateType.NEW_ENERGY_SMALL
        assert rule.background_color == PlateColor.GREEN
        assert rule.font_color == "black"
        assert rule.is_double_layer == False
        assert rule.sequence_length == 6
        assert rule.allow_letters == True
        assert rule.forbidden_letters == ["I", "O"]
        assert rule.pure_electric_letters == ["D", "A", "B", "C", "E"]
        assert rule.non_pure_electric_letters == ["F", "G", "H", "J", "K"]
    
    def test_init_large_car(self):
        """测试大型新能源汽车号牌规则初始化"""
        rule = NewEnergyPlateRule(NewEnergyPlateSubType.LARGE_CAR)
        
        assert rule.sub_type == NewEnergyPlateSubType.LARGE_CAR
        assert rule.plate_type == PlateType.NEW_ENERGY_LARGE
        assert rule.background_color == PlateColor.GREEN_YELLOW
        assert rule.font_color == "black"
        assert rule.is_double_layer == False  # 新能源车牌目前只有单层设计
        assert rule.sequence_length == 6
    
    @patch('src.rules.new_energy_plate.NewEnergySequenceGenerator')
    def test_generate_sequence_small_car_success(self, mock_generator_class):
        """测试小型新能源汽车序号生成成功"""
        mock_generator = MagicMock()
        mock_generator.generate_small_car_sequence.return_value = ("D12345", "D")
        mock_generator_class.return_value = mock_generator
        
        rule = NewEnergyPlateRule(NewEnergyPlateSubType.SMALL_CAR)
        sequence = rule.generate_sequence("京", "A", EnergyType.PURE_ELECTRIC)
        
        assert sequence == "D12345"
        mock_generator.generate_small_car_sequence.assert_called_once_with(
            energy_type="pure",
            preferred_letter=None,
            double_letter=False
        )
    
    @patch('src.rules.new_energy_plate.NewEnergySequenceGenerator')
    def test_generate_sequence_large_car_success(self, mock_generator_class):
        """测试大型新能源汽车序号生成成功"""
        mock_generator = MagicMock()
        mock_generator.generate_large_car_sequence.return_value = ("12345D", "D")
        mock_generator_class.return_value = mock_generator
        
        rule = NewEnergyPlateRule(NewEnergyPlateSubType.LARGE_CAR)
        sequence = rule.generate_sequence("京", "A", EnergyType.PURE_ELECTRIC)
        
        assert sequence == "12345D"
        mock_generator.generate_large_car_sequence.assert_called_once_with(
            energy_type="pure"
        )
    
    @patch('src.rules.new_energy_plate.NewEnergySequenceGenerator')
    def test_generate_sequence_with_params(self, mock_generator_class):
        """测试带参数的序号生成"""
        mock_generator = MagicMock()
        mock_generator.generate_small_car_sequence.return_value = ("A12345", "A")
        mock_generator_class.return_value = mock_generator
        
        rule = NewEnergyPlateRule(NewEnergyPlateSubType.SMALL_CAR)
        sequence = rule.generate_sequence(
            "京", "A", 
            energy_type=EnergyType.PURE_ELECTRIC,
            preferred_letter="A",
            double_letter=True
        )
        
        assert sequence == "A12345"
        mock_generator.generate_small_car_sequence.assert_called_once_with(
            energy_type="pure",
            preferred_letter="A",
            double_letter=True
        )
    
    @patch('src.rules.new_energy_plate.NewEnergySequenceGenerator')
    def test_generate_sequence_failure(self, mock_generator_class):
        """测试序号生成失败"""
        mock_generator = MagicMock()
        mock_generator.generate_small_car_sequence.side_effect = Exception("生成失败")
        mock_generator_class.return_value = mock_generator
        
        rule = NewEnergyPlateRule(NewEnergyPlateSubType.SMALL_CAR)
        
        with pytest.raises(PlateGenerationError, match="新能源汽车号牌序号生成失败"):
            rule.generate_sequence("京", "A", EnergyType.PURE_ELECTRIC)
    
    def test_validate_sequence_valid(self):
        """测试有效序号验证"""
        with patch.object(
            self.small_car_rule.sequence_generator, 
            'validate_new_energy_sequence', 
            return_value=True
        ):
            with patch.object(self.small_car_rule, 'get_energy_type_from_sequence', return_value="pure"):
                result = self.small_car_rule.validate_sequence("D12345")
                assert result.is_valid == True
    
    def test_validate_sequence_invalid_length(self):
        """测试无效长度序号验证"""
        result = self.small_car_rule.validate_sequence("D1234")
        assert result.is_valid == False
        assert "长度必须为6位" in result.error_message
    
    def test_validate_sequence_forbidden_letters(self):
        """测试包含禁用字母的序号验证"""
        result = self.small_car_rule.validate_sequence("I12345")
        assert result.is_valid == False
        assert "禁用字母" in result.error_message
    
    def test_validate_sequence_invalid_format(self):
        """测试格式无效的序号验证"""
        with patch.object(
            self.small_car_rule.sequence_generator, 
            'validate_new_energy_sequence', 
            return_value=False
        ):
            result = self.small_car_rule.validate_sequence("123456")
            assert result.is_valid == False
            assert "不符合新能源汽车号牌格式" in result.error_message
    
    def test_validate_sequence_unknown_energy_type(self):
        """测试未知能源类型的序号验证"""
        with patch.object(
            self.small_car_rule.sequence_generator, 
            'validate_new_energy_sequence', 
            return_value=True
        ):
            with patch.object(self.small_car_rule, 'get_energy_type_from_sequence', return_value="unknown"):
                result = self.small_car_rule.validate_sequence("X12345")
                assert result.is_valid == False
                assert "无效的能源标识字母" in result.error_message
    
    def test_get_energy_type_from_sequence(self):
        """测试从序号识别能源类型"""
        with patch.object(
            self.small_car_rule.sequence_generator,
            'get_energy_type_from_sequence',
            return_value="pure"
        ):
            energy_type = self.small_car_rule.get_energy_type_from_sequence("D12345")
            assert energy_type == "pure"
    
    def test_get_energy_identifier_letter_small_car(self):
        """测试小型车获取能源标识字母"""
        letter = self.small_car_rule.get_energy_identifier_letter("D12345")
        assert letter == "D"
        
        # 测试无效字母
        letter = self.small_car_rule.get_energy_identifier_letter("X12345")
        assert letter is None
        
        # 测试长度不正确
        letter = self.small_car_rule.get_energy_identifier_letter("D1234")
        assert letter is None
    
    def test_get_energy_identifier_letter_large_car(self):
        """测试大型车获取能源标识字母"""
        letter = self.large_car_rule.get_energy_identifier_letter("12345D")
        assert letter == "D"
        
        # 测试无效字母
        letter = self.large_car_rule.get_energy_identifier_letter("12345X")
        assert letter is None
    
    @patch.object(NewEnergyPlateRule, 'validate_province')
    @patch.object(NewEnergyPlateRule, 'validate_regional_code')
    @patch.object(NewEnergyPlateRule, 'validate_sequence')
    def test_get_plate_info_success(self, mock_validate_sequence, mock_validate_regional, mock_validate_province):
        """测试获取车牌信息成功"""
        # 模拟所有验证都通过
        mock_validate_province.return_value = ValidationResult(is_valid=True)
        mock_validate_regional.return_value = ValidationResult(is_valid=True)
        mock_validate_sequence.return_value = ValidationResult(is_valid=True)
        
        plate_info = self.small_car_rule.get_plate_info("京", "A", "D12345")
        
        assert plate_info.plate_number == "京AD12345"
        assert plate_info.plate_type == PlateType.NEW_ENERGY_SMALL
        assert plate_info.province == "京"
        assert plate_info.regional_code == "A"
        assert plate_info.sequence == "D12345"
        assert plate_info.background_color == PlateColor.GREEN
        assert plate_info.is_double_layer == False
        assert plate_info.special_chars is None
        assert plate_info.red_chars is None
    
    @patch.object(NewEnergyPlateRule, 'generate_sequence')
    @patch.object(NewEnergyPlateRule, 'get_plate_info')
    def test_generate_plate(self, mock_get_plate_info, mock_generate_sequence):
        """测试生成完整车牌"""
        mock_generate_sequence.return_value = "D12345"
        mock_plate_info = MagicMock()
        mock_get_plate_info.return_value = mock_plate_info
        
        result = self.small_car_rule.generate_plate(
            "京", "A", 
            energy_type=EnergyType.PURE_ELECTRIC,
            preferred_letter="D"
        )
        
        assert result == mock_plate_info
        mock_generate_sequence.assert_called_once_with(
            province="京",
            regional_code="A",
            energy_type=EnergyType.PURE_ELECTRIC,
            preferred_letter="D",
            double_letter=False
        )
        mock_get_plate_info.assert_called_once_with("京", "A", "D12345")
    
    def test_get_available_energy_letters(self):
        """测试获取可用能源标识字母"""
        pure_letters = self.small_car_rule.get_available_energy_letters(EnergyType.PURE_ELECTRIC)
        assert pure_letters == ["D", "A", "B", "C", "E"]
        
        hybrid_letters = self.small_car_rule.get_available_energy_letters(EnergyType.NON_PURE_ELECTRIC)
        assert hybrid_letters == ["F", "G", "H", "J", "K"]
    
    def test_get_energy_type_description(self):
        """测试获取能源类型描述"""
        desc = self.small_car_rule.get_energy_type_description(EnergyType.PURE_ELECTRIC)
        assert desc == "纯电动车"
        
        desc = self.small_car_rule.get_energy_type_description(EnergyType.NON_PURE_ELECTRIC)
        assert "非纯电动车" in desc
    
    def test_get_plate_type_info(self):
        """测试获取车牌类型信息"""
        info = self.small_car_rule.get_plate_type_info()
        
        assert info["sub_type"] == "small_car"
        assert info["plate_type"] == "new_energy_small"
        assert info["background_color"] == "green"
        assert info["font_color"] == "black"
        assert info["is_double_layer"] == False
        assert info["sequence_length"] == 6
        assert info["pure_electric_letters"] == ["D", "A", "B", "C", "E"]
        assert info["non_pure_electric_letters"] == ["F", "G", "H", "J", "K"]
        assert len(info["energy_types"]) == 2
    
    def test_analyze_plate_number_success(self):
        """测试车牌号码分析成功"""
        with patch.object(self.small_car_rule, 'validate_plate_number', return_value=ValidationResult(is_valid=True)):
            with patch.object(self.small_car_rule, 'get_energy_type_from_sequence', return_value="pure"):
                with patch.object(self.small_car_rule, 'get_energy_identifier_letter', return_value="D"):
                    result = self.small_car_rule.analyze_plate_number("京AD12345")
                    
                    assert result["plate_number"] == "京AD12345"
                    assert result["province"] == "京"
                    assert result["regional_code"] == "A"
                    assert result["sequence"] == "D12345"
                    assert result["energy_type"] == "pure"
                    assert result["energy_identifier_letter"] == "D"
                    assert result["sub_type"] == "small_car"
    
    def test_analyze_plate_number_invalid_length(self):
        """测试分析长度不足的车牌号码"""
        result = self.small_car_rule.analyze_plate_number("京A1234")
        assert "error" in result
        assert "长度不足" in result["error"]
    
    def test_analyze_plate_number_validation_failed(self):
        """测试分析验证失败的车牌号码"""
        with patch.object(
            self.small_car_rule, 
            'validate_plate_number', 
            return_value=ValidationResult(is_valid=False, error_message="验证失败")
        ):
            result = self.small_car_rule.analyze_plate_number("京AD12345")
            assert "error" in result
            assert result["error"] == "验证失败"
    
    def test_analyze_sequence_pattern_small_car(self):
        """测试小型车序号模式分析"""
        # 单字母开头模式
        result = self.small_car_rule._analyze_sequence_pattern("D12345")
        assert result["length"] == 6
        assert result["pattern_type"] == "single_letter_start"
        assert result["description"] == "第一位字母，后五位数字"
        assert len(result["positions"]) == 6
        assert result["positions"][0]["type"] == "letter"
        assert result["positions"][0]["energy_indicator"] == "pure_electric"
        
        # 双字母开头模式
        result = self.small_car_rule._analyze_sequence_pattern("DA1234")
        assert result["pattern_type"] == "double_letter_start"
        assert result["description"] == "前两位字母，后四位数字"
    
    def test_analyze_sequence_pattern_large_car(self):
        """测试大型车序号模式分析"""
        result = self.large_car_rule._analyze_sequence_pattern("12345D")
        assert result["length"] == 6
        assert result["pattern_type"] == "digit_letter_end"
        assert result["description"] == "前五位数字，最后一位字母"
        assert len(result["positions"]) == 6
        assert result["positions"][5]["type"] == "letter"
        assert result["positions"][5]["energy_indicator"] == "pure_electric"
    
    def test_analyze_sequence_pattern_invalid_length(self):
        """测试分析无效长度序号"""
        result = self.small_car_rule._analyze_sequence_pattern("D1234")
        assert "error" in result
        assert "长度不正确" in result["error"]


class TestNewEnergyPlateRuleFactory:
    """新能源汽车号牌规则工厂测试类"""
    
    def test_create_rule(self):
        """测试创建规则"""
        rule = NewEnergyPlateRuleFactory.create_rule(NewEnergyPlateSubType.SMALL_CAR)
        assert isinstance(rule, NewEnergyPlateRule)
        assert rule.sub_type == NewEnergyPlateSubType.SMALL_CAR
    
    def test_create_small_car_rule(self):
        """测试创建小型新能源汽车规则"""
        rule = NewEnergyPlateRuleFactory.create_small_car_rule()
        assert isinstance(rule, NewEnergyPlateRule)
        assert rule.sub_type == NewEnergyPlateSubType.SMALL_CAR
    
    def test_create_large_car_rule(self):
        """测试创建大型新能源汽车规则"""
        rule = NewEnergyPlateRuleFactory.create_large_car_rule()
        assert isinstance(rule, NewEnergyPlateRule)
        assert rule.sub_type == NewEnergyPlateSubType.LARGE_CAR
    
    def test_get_all_sub_types(self):
        """测试获取所有子类型"""
        sub_types = NewEnergyPlateRuleFactory.get_all_sub_types()
        assert len(sub_types) == 2
        assert NewEnergyPlateSubType.SMALL_CAR in sub_types
        assert NewEnergyPlateSubType.LARGE_CAR in sub_types
    
    def test_get_all_energy_types(self):
        """测试获取所有能源类型"""
        energy_types = NewEnergyPlateRuleFactory.get_all_energy_types()
        assert len(energy_types) == 2
        assert EnergyType.PURE_ELECTRIC in energy_types
        assert EnergyType.NON_PURE_ELECTRIC in energy_types
    
    def test_get_sub_type_by_name(self):
        """测试根据名称获取子类型"""
        sub_type = NewEnergyPlateRuleFactory.get_sub_type_by_name("small_car")
        assert sub_type == NewEnergyPlateSubType.SMALL_CAR
        
        # 测试不存在的名称
        sub_type = NewEnergyPlateRuleFactory.get_sub_type_by_name("unknown")
        assert sub_type is None
    
    def test_get_energy_type_by_name(self):
        """测试根据名称获取能源类型"""
        energy_type = NewEnergyPlateRuleFactory.get_energy_type_by_name("pure")
        assert energy_type == EnergyType.PURE_ELECTRIC
        
        energy_type = NewEnergyPlateRuleFactory.get_energy_type_by_name("hybrid")
        assert energy_type == EnergyType.NON_PURE_ELECTRIC
        
        # 测试不存在的名称
        energy_type = NewEnergyPlateRuleFactory.get_energy_type_by_name("unknown")
        assert energy_type is None


# 集成测试
class TestNewEnergyPlateRuleIntegration:
    """新能源汽车号牌规则集成测试"""
    
    def test_complete_plate_generation_workflow(self):
        """测试完整的车牌生成流程"""
        rule = NewEnergyPlateRuleFactory.create_small_car_rule()
        
        # 模拟序号生成
        with patch.object(rule, 'generate_sequence', return_value="D12345"):
            with patch.object(rule, 'validate_province', return_value=ValidationResult(is_valid=True)):
                with patch.object(rule, 'validate_regional_code', return_value=ValidationResult(is_valid=True)):
                    with patch.object(rule, 'validate_sequence', return_value=ValidationResult(is_valid=True)):
                        plate_info = rule.generate_plate("京", "A", EnergyType.PURE_ELECTRIC)
                        
                        assert plate_info.plate_number == "京AD12345"
                        assert plate_info.plate_type == PlateType.NEW_ENERGY_SMALL
                        assert plate_info.background_color == PlateColor.GREEN
    
    def test_all_sub_types_creation(self):
        """测试所有子类型的创建"""
        sub_types = NewEnergyPlateRuleFactory.get_all_sub_types()
        
        for sub_type in sub_types:
            rule = NewEnergyPlateRuleFactory.create_rule(sub_type)
            assert isinstance(rule, NewEnergyPlateRule)
            assert rule.sub_type == sub_type
            
            # 验证基本属性设置正确
            assert rule.sequence_length == 6
            assert rule.allow_letters == True
            assert rule.forbidden_letters == ["I", "O"]
    
    def test_energy_type_logic(self):
        """测试能源类型逻辑"""
        rule = NewEnergyPlateRuleFactory.create_small_car_rule()
        
        # 纯电动车标识字母
        pure_letters = rule.get_available_energy_letters(EnergyType.PURE_ELECTRIC)
        assert all(letter in ["D", "A", "B", "C", "E"] for letter in pure_letters)
        
        # 非纯电动车标识字母
        hybrid_letters = rule.get_available_energy_letters(EnergyType.NON_PURE_ELECTRIC)
        assert all(letter in ["F", "G", "H", "J", "K"] for letter in hybrid_letters)
        
        # 确保两类字母不重复
        assert not set(pure_letters) & set(hybrid_letters)