"""
特殊车牌规则测试模块
测试特殊车牌规则类的所有功能
"""

import pytest
from unittest.mock import patch, MagicMock

from src.rules.special_plate import (
    SpecialPlateRule, 
    SpecialPlateSubType, 
    EmbassyPlateType,
    ConsulatePlateType,
    HongKongMacaoPlateType,
    MilitaryPlateType,
    SpecialPlateRuleFactory
)
from src.rules.base_rule import PlateType, PlateColor, ValidationResult
from src.core.exceptions import PlateGenerationError


class TestSpecialPlateRule:
    """特殊车牌规则测试类"""
    
    def setup_method(self):
        """测试前的准备工作"""
        self.embassy_rule = SpecialPlateRule(SpecialPlateSubType.EMBASSY)
        self.consulate_rule = SpecialPlateRule(SpecialPlateSubType.CONSULATE)
        self.hong_kong_macao_rule = SpecialPlateRule(SpecialPlateSubType.HONG_KONG_MACAO)
        self.military_rule = SpecialPlateRule(SpecialPlateSubType.MILITARY)
    
    def test_init_embassy(self):
        """测试使馆车牌规则初始化"""
        rule = SpecialPlateRule(SpecialPlateSubType.EMBASSY)
        
        assert rule.sub_type == SpecialPlateSubType.EMBASSY
        assert rule.plate_type == PlateType.EMBASSY
        assert rule.background_color == PlateColor.BLACK
        assert rule.font_color == "white"
        assert rule.special_chars == ["使"]
        assert rule.red_chars == ["使"]
        assert rule.is_double_layer == False
        assert rule.sequence_length == 5
    
    def test_init_consulate(self):
        """测试领馆车牌规则初始化"""
        rule = SpecialPlateRule(SpecialPlateSubType.CONSULATE)
        
        assert rule.sub_type == SpecialPlateSubType.CONSULATE
        assert rule.plate_type == PlateType.CONSULATE
        assert rule.background_color == PlateColor.BLACK
        assert rule.font_color == "white"
        assert rule.special_chars == ["领"]
        assert rule.red_chars == ["领"]
        assert rule.is_double_layer == False
    
    def test_init_hong_kong_macao(self):
        """测试港澳车牌规则初始化"""
        rule = SpecialPlateRule(SpecialPlateSubType.HONG_KONG_MACAO)
        
        assert rule.sub_type == SpecialPlateSubType.HONG_KONG_MACAO
        assert rule.plate_type == PlateType.HONG_KONG_MACAO
        assert rule.background_color == PlateColor.BLACK
        assert rule.font_color == "white"
        assert rule.special_chars == []
        assert rule.red_chars == []
        assert rule.is_double_layer == False
    
    def test_init_military(self):
        """测试军队车牌规则初始化"""
        rule = SpecialPlateRule(SpecialPlateSubType.MILITARY)
        
        assert rule.sub_type == SpecialPlateSubType.MILITARY
        assert rule.plate_type == PlateType.MILITARY
        assert rule.background_color == PlateColor.WHITE
        assert rule.font_color == "red"
        assert rule.special_chars == []
        assert rule.red_chars == []
        assert rule.is_double_layer == False
        assert rule.sequence_length == 5
    
    def test_generate_embassy_sequence(self):
        """测试生成使馆车牌序号"""
        with patch('random.choice') as mock_choice:
            with patch('random.randint') as mock_randint:
                mock_choice.return_value = "001"
                mock_randint.side_effect = [1, 2, 3]  # 3位数字序号
                
                sequence = self.embassy_rule._generate_embassy_sequence()
                assert sequence == "001123"
                assert len(sequence) == 6
    
    def test_generate_consulate_sequence(self):
        """测试生成领馆车牌序号"""
        with patch('random.choice') as mock_choice:
            with patch('random.randint') as mock_randint:
                mock_choice.return_value = "002"
                mock_randint.side_effect = [4, 5, 6]  # 3位数字序号
                
                sequence = self.consulate_rule._generate_consulate_sequence()
                assert sequence == "002456"
                assert len(sequence) == 6
    
    def test_generate_hong_kong_macao_sequence(self):
        """测试生成港澳车牌序号"""
        with patch('random.choice') as mock_choice:
            with patch('random.randint') as mock_randint:
                mock_choice.return_value = "A"
                mock_randint.side_effect = [1, 2, 3, 4]  # 4位数字
                
                sequence = self.hong_kong_macao_rule._generate_hong_kong_macao_sequence()
                assert sequence == "A1234"
                assert len(sequence) == 5
    
    def test_generate_military_sequence(self):
        """测试生成军队车牌序号"""
        with patch('random.choice') as mock_choice:
            with patch('random.randint') as mock_randint:
                # 第一次choice选择军种字母，后续choice选择数字或字母
                mock_choice.side_effect = ["A", True, True, True, True]  # 全数字
                mock_randint.side_effect = [1, 2, 3, 4]
                
                sequence = self.military_rule._generate_military_sequence()
                assert sequence == "A1234"
                assert len(sequence) == 5
                assert sequence[0] == "A"  # 军种字母
    
    def test_generate_military_sequence_with_type(self):
        """测试指定军种类型生成军队车牌序号"""
        with patch('random.choice') as mock_choice:
            with patch('random.randint') as mock_randint:
                mock_choice.side_effect = [True, True, True, True]  # 全数字
                mock_randint.side_effect = [1, 2, 3, 4]
                
                sequence = self.military_rule._generate_military_sequence("navy")
                assert sequence == "N1234"
                assert sequence[0] == "N"  # 海军字母
    
    def test_generate_sequence_embassy(self):
        """测试使馆车牌序号生成"""
        with patch.object(self.embassy_rule, '_generate_embassy_sequence', return_value="001123"):
            sequence = self.embassy_rule.generate_sequence("使", "使", "embassy_staff")
            assert sequence == "001123"
    
    def test_generate_sequence_unsupported_type(self):
        """测试不支持的特殊车牌类型"""
        # 创建一个无效的子类型（通过修改对象属性模拟）
        rule = SpecialPlateRule(SpecialPlateSubType.EMBASSY)
        rule.sub_type = "invalid_type"  # 设置无效类型
        
        with pytest.raises(PlateGenerationError, match="不支持的特殊车牌类型"):
            rule.generate_sequence("使", "使")
    
    def test_generate_sequence_failure(self):
        """测试序号生成失败"""
        with patch.object(
            self.embassy_rule, 
            '_generate_embassy_sequence', 
            side_effect=Exception("生成失败")
        ):
            with pytest.raises(PlateGenerationError, match="特殊车牌序号生成失败"):
                self.embassy_rule.generate_sequence("使", "使")
    
    def test_validate_embassy_sequence_valid(self):
        """测试有效使馆车牌序号验证"""
        result = self.embassy_rule._validate_embassy_sequence("001123")
        assert result.is_valid == True
    
    def test_validate_embassy_sequence_invalid_length(self):
        """测试使馆车牌序号长度无效"""
        result = self.embassy_rule._validate_embassy_sequence("00112")
        assert result.is_valid == False
        assert "必须为6位" in result.error_message
    
    def test_validate_embassy_sequence_not_digits(self):
        """测试使馆车牌序号包含非数字"""
        result = self.embassy_rule._validate_embassy_sequence("001A23")
        assert result.is_valid == False
        assert "必须全为数字" in result.error_message
    
    def test_validate_consulate_sequence_valid(self):
        """测试有效领馆车牌序号验证"""
        # 需要修改领馆车牌的序号长度设置
        self.consulate_rule.sequence_length = 6
        result = self.consulate_rule._validate_consulate_sequence("002456")
        assert result.is_valid == True
    
    def test_validate_hong_kong_macao_sequence_valid(self):
        """测试有效港澳车牌序号验证"""
        result = self.hong_kong_macao_rule._validate_hong_kong_macao_sequence("A1234")
        assert result.is_valid == True
    
    def test_validate_hong_kong_macao_sequence_invalid_length(self):
        """测试港澳车牌序号长度无效"""
        result = self.hong_kong_macao_rule._validate_hong_kong_macao_sequence("A123")
        assert result.is_valid == False
        assert "必须为5位" in result.error_message
    
    def test_validate_hong_kong_macao_sequence_first_not_letter(self):
        """测试港澳车牌序号第一位不是字母"""
        result = self.hong_kong_macao_rule._validate_hong_kong_macao_sequence("11234")
        assert result.is_valid == False
        assert "第1位必须为字母" in result.error_message
    
    def test_validate_hong_kong_macao_sequence_digits_invalid(self):
        """测试港澳车牌序号后4位不是数字"""
        result = self.hong_kong_macao_rule._validate_hong_kong_macao_sequence("A123B")
        assert result.is_valid == False
        assert "第2-5位必须为数字" in result.error_message
    
    def test_validate_military_sequence_valid(self):
        """测试有效军队车牌序号验证"""
        result = self.military_rule._validate_military_sequence("A1234")
        assert result.is_valid == True
    
    def test_validate_military_sequence_invalid_length(self):
        """测试军队车牌序号长度无效"""
        result = self.military_rule._validate_military_sequence("A123")
        assert result.is_valid == False
        assert "必须为5位" in result.error_message
    
    def test_validate_military_sequence_first_not_letter(self):
        """测试军队车牌序号第一位不是字母"""
        result = self.military_rule._validate_military_sequence("11234")
        assert result.is_valid == False
        assert "第1位必须为军种字母" in result.error_message
    
    def test_validate_military_sequence_invalid_military_letter(self):
        """测试军队车牌序号军种字母无效"""
        result = self.military_rule._validate_military_sequence("X1234")
        assert result.is_valid == False
        assert "无效的军种字母" in result.error_message
    
    def test_validate_military_sequence_invalid_chars(self):
        """测试军队车牌序号包含无效字符"""
        result = self.military_rule._validate_military_sequence("A123@")
        assert result.is_valid == False
        assert "字符无效" in result.error_message
    
    def test_validate_sequence_invalid_length(self):
        """测试序号长度验证"""
        result = self.embassy_rule.validate_sequence("1234")
        assert result.is_valid == False
        assert "长度必须为5位" in result.error_message
    
    def test_validate_sequence_forbidden_letters(self):
        """测试禁用字母验证"""
        result = self.military_rule.validate_sequence("I1234")
        assert result.is_valid == False
        assert "禁用字母" in result.error_message
    
    def test_get_plate_info_embassy(self):
        """测试获取使馆车牌信息"""
        with patch.object(self.embassy_rule, 'validate_sequence', return_value=ValidationResult(is_valid=True)):
            # 使馆车牌需要调整序号长度
            self.embassy_rule.sequence_length = 6
            plate_info = self.embassy_rule.get_plate_info("使", "使", "001123")
            
            assert plate_info.plate_number == "使使001123"
            assert plate_info.plate_type == PlateType.EMBASSY
            assert plate_info.province == "使"
            assert plate_info.regional_code == "使"
            assert plate_info.sequence == "001123"
            assert plate_info.background_color == PlateColor.BLACK
            assert plate_info.special_chars == ["使"]
            assert plate_info.red_chars == ["使"]
    
    def test_get_plate_info_hong_kong_macao_hong_kong(self):
        """测试获取港车车牌信息"""
        with patch.object(self.hong_kong_macao_rule, 'validate_sequence', return_value=ValidationResult(is_valid=True)):
            plate_info = self.hong_kong_macao_rule.get_plate_info("港", "港", "A1234", "hong_kong")
            
            assert plate_info.plate_number == "港港A1234"
            assert plate_info.province == "港"
            assert plate_info.regional_code == "港"
            assert plate_info.special_chars == ["港"]
    
    def test_get_plate_info_hong_kong_macao_macao(self):
        """测试获取澳车车牌信息"""
        with patch.object(self.hong_kong_macao_rule, 'validate_sequence', return_value=ValidationResult(is_valid=True)):
            plate_info = self.hong_kong_macao_rule.get_plate_info("澳", "澳", "A1234", "macao")
            
            assert plate_info.plate_number == "澳澳A1234"
            assert plate_info.province == "澳"
            assert plate_info.regional_code == "澳"
            assert plate_info.special_chars == ["澳"]
    
    def test_get_plate_info_hong_kong_macao_default(self):
        """测试获取港澳车牌信息（默认港车）"""
        with patch.object(self.hong_kong_macao_rule, 'validate_sequence', return_value=ValidationResult(is_valid=True)):
            plate_info = self.hong_kong_macao_rule.get_plate_info("", "", "A1234")
            
            assert plate_info.province == "港"
            assert plate_info.regional_code == "港"
            assert plate_info.special_chars == ["港"]
    
    def test_get_plate_info_sequence_invalid(self):
        """测试获取车牌信息时序号无效"""
        with patch.object(
            self.embassy_rule, 
            'validate_sequence', 
            return_value=ValidationResult(is_valid=False, error_message="序号无效")
        ):
            with pytest.raises(PlateGenerationError, match="序号无效"):
                self.embassy_rule.get_plate_info("使", "使", "XXXXX")
    
    @patch.object(SpecialPlateRule, 'generate_sequence')
    @patch.object(SpecialPlateRule, 'get_plate_info')
    def test_generate_plate(self, mock_get_plate_info, mock_generate_sequence):
        """测试生成完整特殊车牌"""
        mock_generate_sequence.return_value = "001123"
        mock_plate_info = MagicMock()
        mock_get_plate_info.return_value = mock_plate_info
        
        result = self.embassy_rule.generate_plate("使", "使", "embassy_staff")
        
        assert result == mock_plate_info
        mock_generate_sequence.assert_called_once_with(
            province="使",
            regional_code="使",
            special_type="embassy_staff"
        )
        mock_get_plate_info.assert_called_once_with("使", "使", "001123", "embassy_staff")
    
    def test_get_plate_type_info(self):
        """测试获取车牌类型信息"""
        info = self.embassy_rule.get_plate_type_info()
        
        assert info["sub_type"] == "embassy"
        assert info["plate_type"] == "embassy"
        assert info["background_color"] == "black"
        assert info["font_color"] == "white"
        assert info["is_double_layer"] == False
        assert info["special_chars"] == ["使"]
        assert info["red_chars"] == ["使"]
        assert info["sequence_length"] == 5
        assert info["allow_letters"] == True
        assert info["forbidden_letters"] == ["I", "O"]
    
    def test_get_available_special_types_embassy(self):
        """测试获取使馆车牌可用特殊类型"""
        types = self.embassy_rule.get_available_special_types()
        expected_types = [e.value for e in EmbassyPlateType]
        assert types == expected_types
    
    def test_get_available_special_types_consulate(self):
        """测试获取领馆车牌可用特殊类型"""
        types = self.consulate_rule.get_available_special_types()
        expected_types = [c.value for c in ConsulatePlateType]
        assert types == expected_types
    
    def test_get_available_special_types_hong_kong_macao(self):
        """测试获取港澳车牌可用特殊类型"""
        types = self.hong_kong_macao_rule.get_available_special_types()
        expected_types = [h.value for h in HongKongMacaoPlateType]
        assert types == expected_types
    
    def test_get_available_special_types_military(self):
        """测试获取军队车牌可用特殊类型"""
        types = self.military_rule.get_available_special_types()
        expected_types = [m.value for m in MilitaryPlateType]
        assert types == expected_types


class TestSpecialPlateRuleFactory:
    """特殊车牌规则工厂测试类"""
    
    def test_create_rule(self):
        """测试创建规则"""
        rule = SpecialPlateRuleFactory.create_rule(SpecialPlateSubType.EMBASSY)
        assert isinstance(rule, SpecialPlateRule)
        assert rule.sub_type == SpecialPlateSubType.EMBASSY
    
    def test_create_embassy_rule(self):
        """测试创建使馆车牌规则"""
        rule = SpecialPlateRuleFactory.create_embassy_rule()
        assert isinstance(rule, SpecialPlateRule)
        assert rule.sub_type == SpecialPlateSubType.EMBASSY
    
    def test_create_consulate_rule(self):
        """测试创建领馆车牌规则"""
        rule = SpecialPlateRuleFactory.create_consulate_rule()
        assert isinstance(rule, SpecialPlateRule)
        assert rule.sub_type == SpecialPlateSubType.CONSULATE
    
    def test_create_hong_kong_macao_rule(self):
        """测试创建港澳车牌规则"""
        rule = SpecialPlateRuleFactory.create_hong_kong_macao_rule()
        assert isinstance(rule, SpecialPlateRule)
        assert rule.sub_type == SpecialPlateSubType.HONG_KONG_MACAO
    
    def test_create_military_rule(self):
        """测试创建军队车牌规则"""
        rule = SpecialPlateRuleFactory.create_military_rule()
        assert isinstance(rule, SpecialPlateRule)
        assert rule.sub_type == SpecialPlateSubType.MILITARY
    
    def test_get_all_sub_types(self):
        """测试获取所有子类型"""
        sub_types = SpecialPlateRuleFactory.get_all_sub_types()
        assert len(sub_types) == 4
        assert SpecialPlateSubType.EMBASSY in sub_types
        assert SpecialPlateSubType.CONSULATE in sub_types
        assert SpecialPlateSubType.HONG_KONG_MACAO in sub_types
        assert SpecialPlateSubType.MILITARY in sub_types
    
    def test_get_sub_type_by_name(self):
        """测试根据名称获取子类型"""
        sub_type = SpecialPlateRuleFactory.get_sub_type_by_name("embassy")
        assert sub_type == SpecialPlateSubType.EMBASSY
        
        # 测试不存在的名称
        sub_type = SpecialPlateRuleFactory.get_sub_type_by_name("unknown")
        assert sub_type is None


# 集成测试
class TestSpecialPlateRuleIntegration:
    """特殊车牌规则集成测试"""
    
    def test_complete_embassy_plate_generation_workflow(self):
        """测试完整的使馆车牌生成流程"""
        rule = SpecialPlateRuleFactory.create_embassy_rule()
        
        # 模拟序号生成
        with patch.object(rule, 'generate_sequence', return_value="001123"):
            with patch.object(rule, 'validate_sequence', return_value=ValidationResult(is_valid=True)):
                # 调整序号长度以匹配生成的序号
                rule.sequence_length = 6
                plate_info = rule.generate_plate()
                
                assert plate_info.plate_number == "使使001123"
                assert plate_info.plate_type == PlateType.EMBASSY
                assert plate_info.background_color == PlateColor.BLACK
                assert plate_info.special_chars == ["使"]
                assert plate_info.red_chars == ["使"]
    
    def test_complete_military_plate_generation_workflow(self):
        """测试完整的军队车牌生成流程"""
        rule = SpecialPlateRuleFactory.create_military_rule()
        
        # 模拟序号生成
        with patch.object(rule, 'generate_sequence', return_value="A1234"):
            with patch.object(rule, 'validate_sequence', return_value=ValidationResult(is_valid=True)):
                plate_info = rule.generate_plate(special_type="army")
                
                assert len(plate_info.plate_number) >= 5
                assert plate_info.plate_type == PlateType.MILITARY
                assert plate_info.background_color == PlateColor.WHITE
                assert plate_info.font_color == "red"
    
    def test_all_sub_types_creation(self):
        """测试所有子类型的创建"""
        sub_types = SpecialPlateRuleFactory.get_all_sub_types()
        
        for sub_type in sub_types:
            rule = SpecialPlateRuleFactory.create_rule(sub_type)
            assert isinstance(rule, SpecialPlateRule)
            assert rule.sub_type == sub_type
            
            # 验证基本属性设置正确
            assert rule.sequence_length == 5
            assert rule.allow_letters == True
            assert rule.forbidden_letters == ["I", "O"]
    
    def test_sequence_validation_for_all_types(self):
        """测试所有类型的序号验证"""
        # 使馆车牌
        embassy_rule = SpecialPlateRuleFactory.create_embassy_rule()
        embassy_rule.sequence_length = 6  # 调整长度
        result = embassy_rule.validate_sequence("001123")
        assert result.is_valid == True
        
        # 领馆车牌
        consulate_rule = SpecialPlateRuleFactory.create_consulate_rule()
        consulate_rule.sequence_length = 6  # 调整长度
        result = consulate_rule.validate_sequence("002456")
        assert result.is_valid == True
        
        # 港澳车牌
        hk_macao_rule = SpecialPlateRuleFactory.create_hong_kong_macao_rule()
        result = hk_macao_rule.validate_sequence("A1234")
        assert result.is_valid == True
        
        # 军队车牌
        military_rule = SpecialPlateRuleFactory.create_military_rule()
        result = military_rule.validate_sequence("A1234")
        assert result.is_valid == True