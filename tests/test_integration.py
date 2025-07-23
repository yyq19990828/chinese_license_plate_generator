# -*- coding: utf-8 -*-
import pytest
import time

from src.generator.plate_generator import PlateGenerator, PlateGenerationConfig
from src.utils.constants import PlateType


class TestIntegration:
    """
    集成测试
    """

    @pytest.fixture
    def generator(self):
        """提供一个 PlateGenerator 实例"""
        return PlateGenerator()

    def test_generate_all_plate_types(self, generator):
        """测试生成所有主要的车牌类型"""
        plate_types_to_test = [
            PlateType.ORDINARY_BLUE,
            PlateType.ORDINARY_YELLOW,
            PlateType.NEW_ENERGY_GREEN,
            PlateType.POLICE_WHITE,
            PlateType.EMBASSY_BLACK,
            PlateType.HONGKONG_BLACK,
            PlateType.MACAO_BLACK,
            PlateType.ORDINARY_COACH,
            PlateType.ORDINARY_TRAILER,
        ]

        for plate_type in plate_types_to_test:
            config = PlateGenerationConfig(plate_type=plate_type)
            plate_info = generator.generate_random_plate(config)
            assert plate_info is not None
            assert plate_info.plate_type == plate_type

    def test_high_volume_generation_performance(self, generator):
        """测试大批量生成的性能"""
        num_plates = 1000
        max_time_seconds = 10  # 10秒内完成1000个车牌的生成

        start_time = time.time()
        plates = generator.generate_batch_plates(num_plates)
        end_time = time.time()

        duration = end_time - start_time

        assert len(plates) <= num_plates
        assert duration < max_time_seconds, f"生成 {num_plates} 个车牌耗时 {duration:.2f}s, 超过了 {max_time_seconds}s 的限制"
