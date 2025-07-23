# -*- coding: utf-8 -*-
import pytest

from src.core.exceptions import RuleError
from src.validators.rule_validator import RuleValidator, validate_rule


class TestRuleValidator:
    """
    测试规则验证器
    """

    @pytest.fixture
    def valid_rule(self):
        """一个有效的规则 fixture"""
        return {
            "type": "ordinary",
            "description": "普通小型汽车",
            "structure": [
                {"name": "province", "length": 1, "type": "fixed", "options": ["京"]},
                {"name": "regional_code", "length": 1, "type": "options", "options": ["A", "B", "C"]},
                {"name": "sequence", "length": 5, "type": "hybrid", "options": ["0-9", "A-Z"]}
            ]
        }

    def test_valid_rule(self, valid_rule):
        """测试有效的规则"""
        assert RuleValidator(valid_rule).validate() is True
        assert validate_rule(valid_rule) is True

    def test_missing_top_level_key(self, valid_rule):
        """测试缺少顶层必需字段"""
        del valid_rule["type"]
        with pytest.raises(RuleError, match="规则缺少必需的顶级字段: type"):
            RuleValidator(valid_rule).validate()
        assert validate_rule(valid_rule) is False

    def test_invalid_structure_type(self, valid_rule):
        """测试 'structure' 字段类型不正确"""
        valid_rule["structure"] = "not a list"
        with pytest.raises(RuleError, match="'structure' 字段必须是一个列表"):
            RuleValidator(valid_rule).validate()
        assert validate_rule(valid_rule) is False

    def test_missing_structure_item_key(self, valid_rule):
        """测试 'structure' 条目中缺少必需字段"""
        del valid_rule["structure"][0]["name"]
        with pytest.raises(RuleError, match="'structure' 条目缺少必需字段: name"):
            RuleValidator(valid_rule).validate()
        assert validate_rule(valid_rule) is False

    def test_invalid_structure_item_type(self, valid_rule):
        """测试 'structure' 条目类型不正确"""
        valid_rule["structure"][0] = "not a dict"
        with pytest.raises(RuleError, match="'structure' 中的每个条目都必须是字典"):
            RuleValidator(valid_rule).validate()
        assert validate_rule(valid_rule) is False
            
    def test_inconsistent_fixed_type_options(self, valid_rule):
        """测试 'fixed' 类型的 options 不一致"""
        valid_rule["structure"][0]["options"] = ["京", "沪"] # fixed 应该只有一个 option
        with pytest.raises(RuleError, match="名为 'province' 的 'fixed' 类型条目应只有一个 'option'"):
            RuleValidator(valid_rule).validate()
        assert validate_rule(valid_rule) is False

    def test_invalid_options_type(self, valid_rule):
        """测试 'options' 字段类型不正确"""
        valid_rule["structure"][1]["options"] = "not a list"
        with pytest.raises(RuleError, match="名为 'regional_code' 的条目的 'options' 必须是列表"):
            RuleValidator(valid_rule).validate()
        assert validate_rule(valid_rule) is False

    def test_empty_rule(self):
        """测试空规则"""
        with pytest.raises(RuleError):
            RuleValidator({}).validate()
        assert validate_rule({}) is False

    def test_structure_with_non_dict_item(self, valid_rule):
        """测试 structure 中包含非字典项"""
        valid_rule['structure'].append(123)
        with pytest.raises(RuleError, match="'structure' 中的每个条目都必须是字典"):
            RuleValidator(valid_rule).validate()
        assert validate_rule(valid_rule) is False
