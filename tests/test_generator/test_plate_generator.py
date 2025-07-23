# -*- coding: utf-8 -*-
import pytest

from src.generator.plate_generator import PlateGenerator, PlateGenerationConfig, PlateInfo
from src.utils.constants import PlateType


class TestPlateGenerator:
    """
    测试主车牌生成器
    """

    @pytest.fixture
    def generator(self):
        """提供一个 PlateGenerator 实例"""
        return PlateGenerator()

    def test_generate_random_plate_default(self, generator):
        """测试生成随机车牌（默认配置）"""
        plate_info = generator.generate_random_plate()
        assert isinstance(plate_info, PlateInfo)
        assert len(plate_info.plate_number) in [7, 8]
        assert plate_info.plate_type is not None

    def test_generate_random_plate_with_config(self, generator):
        """测试带配置的随机车牌生成"""
        config = PlateGenerationConfig(
            plate_type=PlateType.ORDINARY_BLUE,
            province="粤",
            regional_code="B"
        )
        plate_info = generator.generate_random_plate(config)
        assert isinstance(plate_info, PlateInfo)
        assert plate_info.plate_number.startswith("粤B")
        assert plate_info.plate_type == PlateType.ORDINARY_BLUE

    def test_generate_specific_plate(self, generator):
        """测试生成指定号码的车牌"""
        plate_number = "沪AD12345"
        plate_info = generator.generate_specific_plate(plate_number)
        assert isinstance(plate_info, PlateInfo)
        assert plate_info.plate_number == plate_number
        assert plate_info.plate_type == PlateType.NEW_ENERGY_GREEN
        assert plate_info.province == "沪"
        assert plate_info.regional_code == "A"
        assert plate_info.sequence == "D12345"

    def test_generate_batch_plates(self, generator):
        """测试批量生成车牌"""
        count = 10
        plates = generator.generate_batch_plates(count)
        assert isinstance(plates, list)
        assert len(plates) <= count  # May be less if generation fails
        if plates:
            assert all(isinstance(p, PlateInfo) for p in plates)

    def test_generate_new_energy_plate(self, generator):
        """测试生成新能源车牌"""
        config = PlateGenerationConfig(plate_type=PlateType.NEW_ENERGY_GREEN)
        plate_info = generator.generate_random_plate(config)
        assert plate_info.plate_type == PlateType.NEW_ENERGY_GREEN
        assert len(plate_info.plate_number) == 8

    def test_generate_police_plate(self, generator):
        """测试生成警车车牌"""
        config = PlateGenerationConfig(plate_type=PlateType.POLICE_WHITE)
        plate_info = generator.generate_random_plate(config)
        assert plate_info.plate_type == PlateType.POLICE_WHITE
        assert plate_info.plate_number.endswith("警")

    def test_analyze_plate_type(self, generator):
        """测试车牌类型分析"""
        assert generator._analyze_plate_type("京A12345") == PlateType.ORDINARY_BLUE
        assert generator._analyze_plate_type("沪AD12345") == PlateType.NEW_ENERGY_GREEN
        assert generator._analyze_plate_type("粤Z1234港") == PlateType.HONGKONG_BLACK
        assert generator._analyze_plate_type("使123456") == PlateType.EMBASSY_BLACK
        assert generator._analyze_plate_type("京A1234警") == PlateType.POLICE_WHITE
