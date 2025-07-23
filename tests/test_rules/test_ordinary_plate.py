"""
普通汽车号牌规则测试模块
测试普通汽车号牌规则类的所有功能
"""

import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.rules.ordinary_plate import (
    OrdinaryPlateRule, 
    OrdinaryPlateSubType, 
    OrdinaryPlateRuleFactory
)
from src.rules.base_rule import PlateType, PlateColor, ValidationResult
from src.core.exceptions import PlateGenerationError


class TestOrdinaryPlateRule:
    """普通汽车号牌规则测试类"""
    
    def setup_method(self):
        """测试前的准备工作"""
        self.small_car_rule = OrdinaryPlateRule(OrdinaryPlateSubType.SMALL_CAR)
        self.large_car_rule = OrdinaryPlateRule(OrdinaryPlateSubType.LARGE_CAR)
        self.police_rule = OrdinaryPlateRule(OrdinaryPlateSubType.POLICE)
    
    def test_init_small_car(self):
        """测试小型汽车号牌规则初始化"""
        rule = OrdinaryPlateRule(OrdinaryPlateSubType.SMALL_CAR)
        
        assert rule.sub_type == OrdinaryPlateSubType.SMALL_CAR
        assert rule.plate_type == PlateType.ORDINARY_SMALL
        assert rule.background_color == PlateColor.BLUE
        assert rule.font_color == "white"
        assert rule.is_double_layer == False
        assert rule.sequence_length == 5
        assert rule.allow_letters == True
        assert rule.forbidden_letters == ["I", "O"]
    
    def test_init_large_car(self):
        """测试大型汽车号牌规则初始化"""
        rule = OrdinaryPlateRule(OrdinaryPlateSubType.LARGE_CAR)
        
        assert rule.sub_type == OrdinaryPlateSubType.LARGE_CAR
        assert rule.plate_type == PlateType.ORDINARY_LARGE
        assert rule.background_color == PlateColor.YELLOW
        assert rule.font_color == "black"
        assert rule.is_double_layer == True
        assert rule.sequence_length == 5
    
    def test_init_police(self):
        """测试警用汽车号牌规则初始化"""
        rule = OrdinaryPlateRule(OrdinaryPlateSubType.POLICE)
        
        assert rule.sub_type == OrdinaryPlateSubType.POLICE
        assert rule.plate_type == PlateType.POLICE
        assert rule.background_color == PlateColor.WHITE
        assert rule.font_color == "black"
        assert rule.special_chars == ["警"]
        assert rule.red_chars == ["警"]
        assert rule.is_double_layer == False
    
    @patch('src.rules.ordinary_plate.OrdinarySequenceGenerator')
    def test_generate_sequence_success(self, mock_generator_class):
        """测试序号生成成功"""
        mock_generator = MagicMock()
        mock_generator.generate_sequence.return_value = ("12345", MagicMock())
        mock_generator_class.return_value = mock_generator
        
        rule = OrdinaryPlateRule(OrdinaryPlateSubType.SMALL_CAR)
        sequence = rule.generate_sequence("京", "A")
        
        assert sequence == "12345"
        mock_generator.generate_sequence.assert_called_once_with(
            province="京",
            regional_code="A",
            preferred_order=None,
            force_pattern=None
        )
    
    @patch('src.rules.ordinary_plate.OrdinarySequenceGenerator')
    def test_generate_sequence_with_params(self, mock_generator_class):
        """测试带参数的序号生成"""
        mock_generator = MagicMock()
        mock_generator.generate_sequence.return_value = ("A1234", MagicMock())
        mock_generator_class.return_value = mock_generator
        
        rule = OrdinaryPlateRule(OrdinaryPlateSubType.SMALL_CAR)
        sequence = rule.generate_sequence("京", "A", preferred_order=2, force_pattern="LDDDD")
        
        assert sequence == "A1234"
        mock_generator.generate_sequence.assert_called_once_with(
            province="京",
            regional_code="A",
            preferred_order=2,
            force_pattern="LDDDD"
        )
    
    @patch('src.rules.ordinary_plate.OrdinarySequenceGenerator')
    def test_generate_sequence_failure(self, mock_generator_class):
        """测试序号生成失败"""
        mock_generator = MagicMock()
        mock_generator.generate_sequence.side_effect = Exception("生成失败")
        mock_generator_class.return_value = mock_generator
        
        rule = OrdinaryPlateRule(OrdinaryPlateSubType.SMALL_CAR)
        
        with pytest.raises(PlateGenerationError, match="普通汽车号牌序号生成失败"):
            rule.generate_sequence("京", "A")
    
    def test_validate_sequence_valid(self):
        """测试有效序号验证"""
        with patch.object(self.small_car_rule.sequence_generator, 'validate_pattern', return_value=True):
            result = self.small_car_rule.validate_sequence("12345")
            assert result.is_valid == True
    
    def test_validate_sequence_invalid_length(self):
        """测试无效长度序号验证"""
        result = self.small_car_rule.validate_sequence("1234")
        assert result.is_valid == False
        assert "长度必须为5位" in result.error_message
    
    def test_validate_sequence_forbidden_letters(self):
        """测试包含禁用字母的序号验证"""
        result = self.small_car_rule.validate_sequence("I1234")
        assert result.is_valid == False
        assert "禁用字母" in result.error_message
    
    def test_validate_sequence_invalid_chars(self):
        """测试包含无效字符的序号验证"""
        result = self.small_car_rule.validate_sequence("1234@")
        assert result.is_valid == False
        assert "字符无效" in result.error_message
    
    def test_validate_sequence_invalid_pattern(self):
        """测试不符合模式的序号验证"""
        # 模拟所有模式都不匹配
        with patch.object(self.small_car_rule.sequence_generator, 'validate_pattern', return_value=False):
            result = self.small_car_rule.validate_sequence("12345")
            assert result.is_valid == False
            assert "不符合任何有效的普通汽车号牌模式" in result.error_message
    
    @patch.object(OrdinaryPlateRule, 'validate_province')
    @patch.object(OrdinaryPlateRule, 'validate_regional_code')
    @patch.object(OrdinaryPlateRule, 'validate_sequence')
    def test_get_plate_info_success(self, mock_validate_sequence, mock_validate_regional, mock_validate_province):
        """测试获取车牌信息成功"""
        # 模拟所有验证都通过
        mock_validate_province.return_value = ValidationResult(is_valid=True)
        mock_validate_regional.return_value = ValidationResult(is_valid=True)
        mock_validate_sequence.return_value = ValidationResult(is_valid=True)
        
        plate_info = self.small_car_rule.get_plate_info("京", "A", "12345")
        
        assert plate_info.plate_number == "京A12345"
        assert plate_info.plate_type == PlateType.ORDINARY_SMALL
        assert plate_info.province == "京"
        assert plate_info.regional_code == "A"
        assert plate_info.sequence == "12345"
        assert plate_info.background_color == PlateColor.BLUE
        assert plate_info.is_double_layer == False
    
    @patch.object(OrdinaryPlateRule, 'validate_province')
    def test_get_plate_info_province_invalid(self, mock_validate_province):
        """测试获取车牌信息时省份无效"""
        mock_validate_province.return_value = ValidationResult(
            is_valid=False, 
            error_message="无效省份"
        )
        
        with pytest.raises(PlateGenerationError, match="无效省份"):
            self.small_car_rule.get_plate_info("XX", "A", "12345")
    
    @patch.object(OrdinaryPlateRule, 'validate_province')
    @patch.object(OrdinaryPlateRule, 'validate_regional_code')
    def test_get_plate_info_regional_code_invalid(self, mock_validate_regional, mock_validate_province):
        """测试获取车牌信息时发牌机关代号无效"""
        mock_validate_province.return_value = ValidationResult(is_valid=True)
        mock_validate_regional.return_value = ValidationResult(
            is_valid=False, 
            error_message="无效发牌机关代号"
        )
        
        with pytest.raises(PlateGenerationError, match="无效发牌机关代号"):
            self.small_car_rule.get_plate_info("京", "X", "12345")
    
    @patch.object(OrdinaryPlateRule, 'validate_province')
    @patch.object(OrdinaryPlateRule, 'validate_regional_code')
    @patch.object(OrdinaryPlateRule, 'validate_sequence')
    def test_get_plate_info_sequence_invalid(self, mock_validate_sequence, mock_validate_regional, mock_validate_province):
        """测试获取车牌信息时序号无效"""
        mock_validate_province.return_value = ValidationResult(is_valid=True)
        mock_validate_regional.return_value = ValidationResult(is_valid=True)
        mock_validate_sequence.return_value = ValidationResult(
            is_valid=False, 
            error_message="无效序号"
        )
        
        with pytest.raises(PlateGenerationError, match="无效序号"):
            self.small_car_rule.get_plate_info("京", "A", "XXXXX")
    
    @patch.object(OrdinaryPlateRule, 'generate_sequence')
    @patch.object(OrdinaryPlateRule, 'get_plate_info')
    def test_generate_plate(self, mock_get_plate_info, mock_generate_sequence):
        """测试生成完整车牌"""
        mock_generate_sequence.return_value = "12345"
        mock_plate_info = MagicMock()
        mock_get_plate_info.return_value = mock_plate_info
        
        result = self.small_car_rule.generate_plate("京", "A", preferred_order=1)
        
        assert result == mock_plate_info
        mock_generate_sequence.assert_called_once_with(
            province="京",
            regional_code="A",
            preferred_order=1,
            force_pattern=None
        )
        mock_get_plate_info.assert_called_once_with("京", "A", "12345")
    
    def test_get_plate_type_info(self):
        """测试获取车牌类型信息"""
        info = self.small_car_rule.get_plate_type_info()
        
        assert info["sub_type"] == "small_car"
        assert info["plate_type"] == "ordinary_small"
        assert info["background_color"] == "blue"
        assert info["font_color"] == "white"
        assert info["is_double_layer"] == False
        assert info["sequence_length"] == 5
        assert info["allow_letters"] == True
        assert info["forbidden_letters"] == ["I", "O"]
    
    def test_get_available_sequence_patterns(self):
        """测试获取可用序号模式"""
        # 模拟可用模式
        mock_pattern = MagicMock()
        mock_pattern.order = 1
        mock_pattern.pattern = "DDDDD"
        mock_pattern.description = "全数字"
        mock_pattern.example = "12345"
        mock_pattern.usage_rate = 0.3
        mock_pattern.is_active = True
        
        with patch.object(
            self.small_car_rule.sequence_generator.resource_manager,
            'get_available_patterns',
            return_value=[mock_pattern]
        ):
            patterns = self.small_car_rule.get_available_sequence_patterns()
            
            assert len(patterns) == 1
            assert patterns[0]["order"] == 1
            assert patterns[0]["pattern"] == "DDDDD"
            assert patterns[0]["description"] == "全数字"
            assert patterns[0]["example"] == "12345"
            assert patterns[0]["usage_rate"] == 0.3
            assert patterns[0]["is_active"] == True
    
    def test_set_and_get_sequence_usage_rate(self):
        """测试设置和获取序号使用率"""
        mock_pattern = MagicMock()
        mock_pattern.pattern = "DDDDD"
        mock_pattern.order = 1
        
        with patch.object(
            self.small_car_rule.sequence_generator,
            'get_pattern_by_order',
            return_value=mock_pattern
        ):
            # 设置使用率
            self.small_car_rule.set_sequence_usage_rate(1, 0.5)
            
            # 获取使用率
            with patch.object(
                self.small_car_rule.sequence_generator.resource_manager,
                'get_usage_rate',
                return_value=0.5
            ):
                usage_rate = self.small_car_rule.get_sequence_usage_rate(1)
                assert usage_rate == 0.5


class TestOrdinaryPlateRuleFactory:
    """普通汽车号牌规则工厂测试类"""
    
    def test_create_rule(self):
        """测试创建规则"""
        rule = OrdinaryPlateRuleFactory.create_rule(OrdinaryPlateSubType.SMALL_CAR)
        assert isinstance(rule, OrdinaryPlateRule)
        assert rule.sub_type == OrdinaryPlateSubType.SMALL_CAR
    
    def test_create_small_car_rule(self):
        """测试创建小型汽车规则"""
        rule = OrdinaryPlateRuleFactory.create_small_car_rule()
        assert isinstance(rule, OrdinaryPlateRule)
        assert rule.sub_type == OrdinaryPlateSubType.SMALL_CAR
    
    def test_create_large_car_rule(self):
        """测试创建大型汽车规则"""
        rule = OrdinaryPlateRuleFactory.create_large_car_rule()
        assert isinstance(rule, OrdinaryPlateRule)
        assert rule.sub_type == OrdinaryPlateSubType.LARGE_CAR
    
    def test_create_trailer_rule(self):
        """测试创建挂车规则"""
        rule = OrdinaryPlateRuleFactory.create_trailer_rule()
        assert isinstance(rule, OrdinaryPlateRule)
        assert rule.sub_type == OrdinaryPlateSubType.TRAILER
    
    def test_create_coach_rule(self):
        """测试创建教练汽车规则"""
        rule = OrdinaryPlateRuleFactory.create_coach_rule()
        assert isinstance(rule, OrdinaryPlateRule)
        assert rule.sub_type == OrdinaryPlateSubType.COACH
    
    def test_create_police_rule(self):
        """测试创建警用汽车规则"""
        rule = OrdinaryPlateRuleFactory.create_police_rule()
        assert isinstance(rule, OrdinaryPlateRule)
        assert rule.sub_type == OrdinaryPlateSubType.POLICE
    
    def test_get_all_sub_types(self):
        """测试获取所有子类型"""
        sub_types = OrdinaryPlateRuleFactory.get_all_sub_types()
        assert len(sub_types) == 5
        assert OrdinaryPlateSubType.SMALL_CAR in sub_types
        assert OrdinaryPlateSubType.LARGE_CAR in sub_types
        assert OrdinaryPlateSubType.TRAILER in sub_types
        assert OrdinaryPlateSubType.COACH in sub_types
        assert OrdinaryPlateSubType.POLICE in sub_types
    
    def test_get_sub_type_by_name(self):
        """测试根据名称获取子类型"""
        sub_type = OrdinaryPlateRuleFactory.get_sub_type_by_name("small_car")
        assert sub_type == OrdinaryPlateSubType.SMALL_CAR
        
        # 测试不存在的名称
        sub_type = OrdinaryPlateRuleFactory.get_sub_type_by_name("unknown")
        assert sub_type is None


# 集成测试
class TestOrdinaryPlateRuleIntegration:
    """普通汽车号牌规则集成测试"""
    
    def test_complete_plate_generation_workflow(self):
        """测试完整的车牌生成流程"""
        rule = OrdinaryPlateRuleFactory.create_small_car_rule()
        
        # 模拟序号生成
        with patch.object(rule, 'generate_sequence', return_value="12345"):
            with patch.object(rule, 'validate_province', return_value=ValidationResult(is_valid=True)):
                with patch.object(rule, 'validate_regional_code', return_value=ValidationResult(is_valid=True)):
                    with patch.object(rule, 'validate_sequence', return_value=ValidationResult(is_valid=True)):
                        plate_info = rule.generate_plate("京", "A")
                        
                        assert plate_info.plate_number == "京A12345"
                        assert plate_info.plate_type == PlateType.ORDINARY_SMALL
                        assert plate_info.background_color == PlateColor.BLUE
    
    def test_all_sub_types_creation(self):
        """测试所有子类型的创建"""
        sub_types = OrdinaryPlateRuleFactory.get_all_sub_types()
        
        for sub_type in sub_types:
            rule = OrdinaryPlateRuleFactory.create_rule(sub_type)
            assert isinstance(rule, OrdinaryPlateRule)
            assert rule.sub_type == sub_type
            
            # 验证基本属性设置正确
            assert rule.sequence_length == 5
            assert rule.allow_letters == True
            assert rule.forbidden_letters == ["I", "O"]