# -*- coding: utf-8 -*-
import pytest

from src.rules.province_codes import ProvinceManager, ProvinceInfo


class TestProvinceManager:
    """
    测试省份管理器
    """

    def test_get_all_abbreviations(self):
        """测试获取所有省份简称"""
        abbreviations = ProvinceManager.get_all_abbreviations()
        assert isinstance(abbreviations, list)
        assert len(abbreviations) == 31
        assert "京" in abbreviations
        assert "新" in abbreviations

    def test_get_province_info_valid(self):
        """测试获取有效的省份信息"""
        info = ProvinceManager.get_province_info("沪")
        assert isinstance(info, ProvinceInfo)
        assert info.name == "上海市"
        assert info.abbreviation == "沪"
        assert info.code == 9

    def test_get_province_info_invalid(self):
        """测试获取无效的省份信息"""
        info = ProvinceManager.get_province_info("哈")
        assert info is None

    def test_is_valid_province(self):
        """测试省份简称的有效性"""
        assert ProvinceManager.is_valid_province("粤") is True
        assert ProvinceManager.is_valid_province("琼") is True
        assert ProvinceManager.is_valid_province("ABC") is False

    def test_get_province_by_name(self):
        """测试通过省份全称获取信息"""
        info = ProvinceManager.get_province_by_name("山东省")
        assert isinstance(info, ProvinceInfo)
        assert info.abbreviation == "鲁"
        assert info.code == 15

    def test_get_provinces_by_type(self):
        """测试根据类型获取省份列表"""
        municipalities = ProvinceManager.get_provinces_by_type("municipality")
        assert len(municipalities) == 4
        assert "京" in [p.abbreviation for p in municipalities]

        provinces = ProvinceManager.get_provinces_by_type("province")
        assert len(provinces) == 22

        regions = ProvinceManager.get_provinces_by_type("autonomous_region")
        assert len(regions) == 5
        
        all_provinces = ProvinceManager.get_provinces_by_type("all")
        assert len(all_provinces) == 31
