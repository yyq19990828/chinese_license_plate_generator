# -*- coding: utf-8 -*-
import pytest

from src.rules.regional_codes import RegionalCodeManager, RegionalInfo


class TestRegionalCodeManager:
    """
    测试发牌机关代号管理器
    """

    def test_get_regional_codes_valid(self):
        """测试获取有效省份的地区代号"""
        codes = RegionalCodeManager.get_regional_codes("粤")
        assert isinstance(codes, list)
        assert len(codes) > 0
        assert all(isinstance(c, RegionalInfo) for c in codes)

    def test_get_regional_codes_invalid(self):
        """测试获取无效省份的地区代号"""
        codes = RegionalCodeManager.get_regional_codes("哈哈")
        assert isinstance(codes, list)
        assert len(codes) == 0

    def test_get_all_codes_for_province(self):
        """测试获取指定省份的所有代号字母"""
        codes = RegionalCodeManager.get_all_codes_for_province("冀")
        assert isinstance(codes, list)
        assert "A" in codes
        assert "T" in codes
        assert "Z" not in codes

    def test_is_valid_regional_code(self):
        """测试省份和代号组合的有效性"""
        assert RegionalCodeManager.is_valid_regional_code("苏", "A") is True
        assert RegionalCodeManager.is_valid_regional_code("苏", "Z") is False
        assert RegionalCodeManager.is_valid_regional_code("京", "Z") is True # 北京有Z
        assert RegionalCodeManager.is_valid_regional_code("鲁", "Z") is False # 山东没有Z

    def test_get_city_info(self):
        """测试获取城市信息"""
        info = RegionalCodeManager.get_city_info("湘", "A")
        assert isinstance(info, RegionalInfo)
        assert info.city_name == "长沙市"
        assert info.is_multiple is True

    def test_get_available_codes(self):
        """测试获取所有可用的代号字母"""
        codes = RegionalCodeManager.get_available_codes()
        assert isinstance(codes, set)
        assert "I" not in codes
        assert "O" not in codes
        assert "Z" in codes
        
        codes_with_io = RegionalCodeManager.get_available_codes(exclude_io=False)
        assert "I" in codes_with_io
        assert "O" in codes_with_io
