#!/usr/bin/env python3
"""
序号生成器单元测试（简化版）
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rules.sequence_generator import (
    OrdinarySequenceGenerator,
    NewEnergySequenceGenerator,
    SequenceGeneratorFactory,
    SequenceType,
    SequenceResourceManager,
    SequencePattern
)
from src.core.exceptions import SequenceGenerationError
from src.utils.constants import PlateConstants


class TestSequenceResourceManager(unittest.TestCase):
    """测试序号资源管理器"""
    
    def setUp(self):
        self.resource_manager = SequenceResourceManager()
    
    def test_usage_rate_management(self):
        """测试使用率管理"""
        pattern_key = "test_pattern"
        
        # 初始使用率应该为0
        self.assertEqual(self.resource_manager.get_usage_rate(pattern_key), 0.0)
        
        # 测试更新使用率
        self.resource_manager.update_usage_rate(pattern_key, 0.5)
        self.assertEqual(self.resource_manager.get_usage_rate(pattern_key), 0.5)
        
        # 测试边界值
        self.resource_manager.update_usage_rate(pattern_key, 1.5)  # 应该被限制为1.0
        self.assertEqual(self.resource_manager.get_usage_rate(pattern_key), 1.0)
        
        self.resource_manager.update_usage_rate(pattern_key, -0.1)  # 应该被限制为0.0
        self.assertEqual(self.resource_manager.get_usage_rate(pattern_key), 0.0)
    
    def test_pattern_availability(self):
        """测试模式可用性"""
        pattern_key = "test_pattern"
        
        # 初始状态应该可用
        self.assertTrue(self.resource_manager.is_pattern_available(pattern_key))
        
        # 低于阈值应该可用
        self.resource_manager.update_usage_rate(pattern_key, 0.5)
        self.assertTrue(self.resource_manager.is_pattern_available(pattern_key))
        
        # 超过阈值应该不可用
        self.resource_manager.update_usage_rate(pattern_key, 0.7)
        self.assertFalse(self.resource_manager.is_pattern_available(pattern_key))


class TestOrdinarySequenceGenerator(unittest.TestCase):
    """测试普通汽车序号生成器"""
    
    def setUp(self):
        self.generator = OrdinarySequenceGenerator()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.generator.patterns)
        self.assertEqual(len(self.generator.patterns), 10)  # 10种启用顺序
        self.assertIsNotNone(self.generator.resource_manager)
    
    def test_pattern_validation(self):
        """测试模式验证"""
        # 正确的模式
        self.assertTrue(self.generator.validate_pattern("12345", "DDDDD"))
        self.assertTrue(self.generator.validate_pattern("A1234", "LDDDD"))
        self.assertTrue(self.generator.validate_pattern("AB123", "LLDDD"))
        
        # 错误的模式
        self.assertFalse(self.generator.validate_pattern("A123", "DDDDD"))  # 长度不匹配
        self.assertFalse(self.generator.validate_pattern("12I34", "DDLDD"))  # 包含禁用字母I
        self.assertFalse(self.generator.validate_pattern("12O34", "DDLDD"))  # 包含禁用字母O
    
    def test_basic_sequence_generation(self):
        """测试基本序号生成"""
        sequence, pattern = self.generator.generate_sequence("湘", "A")
        
        self.assertIsInstance(sequence, str)
        self.assertEqual(len(sequence), 5)
        self.assertIsInstance(pattern, SequencePattern)
        self.assertTrue(self.generator.validate_pattern(sequence, pattern.pattern))
    
    def test_preferred_order_generation(self):
        """测试指定首选顺序生成"""
        for order in range(1, 6):  # 测试前5个顺序
            sequence, pattern = self.generator.generate_sequence("京", "A", preferred_order=order)
            self.assertEqual(pattern.order, order)
            self.assertTrue(self.generator.validate_pattern(sequence, pattern.pattern))
    
    def test_force_pattern_generation(self):
        """测试强制模式生成"""
        test_patterns = ["DDDDD", "LDDDD", "LLDDD"]
        
        for pattern_str in test_patterns:
            sequence, pattern = self.generator.generate_sequence("粤", "B", force_pattern=pattern_str)
            self.assertEqual(pattern.pattern, pattern_str)
            self.assertTrue(self.generator.validate_pattern(sequence, pattern.pattern))
    
    def test_invalid_force_pattern(self):
        """测试无效强制模式"""
        with self.assertRaises(SequenceGenerationError):
            self.generator.generate_sequence("川", "A", force_pattern="INVALID")
    
    def test_get_available_orders(self):
        """测试获取可用顺序"""
        orders = self.generator.get_available_orders()
        self.assertEqual(orders, list(range(1, 11)))  # 初始状态所有顺序都可用
        
        # 将某些模式标记为不可用
        self.generator.resource_manager.update_usage_rate("DDDDD_1", 0.7)
        
        orders = self.generator.get_available_orders()
        self.assertNotIn(1, orders)
        self.assertIn(3, orders)


class TestNewEnergySequenceGenerator(unittest.TestCase):
    """测试新能源汽车序号生成器"""
    
    def setUp(self):
        self.generator = NewEnergySequenceGenerator()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.generator.pure_electric_letters, ["D", "A", "B", "C", "E"])
        self.assertEqual(self.generator.non_pure_electric_letters, ["F", "G", "H", "J", "K"])
    
    def test_small_car_sequence_generation(self):
        """测试小型车序号生成"""
        # 纯电动
        sequence, energy_letter = self.generator.generate_small_car_sequence("pure")
        self.assertEqual(len(sequence), 6)
        self.assertIn(energy_letter, self.generator.pure_electric_letters)
        self.assertEqual(sequence[0], energy_letter)
        
        # 非纯电动
        sequence, energy_letter = self.generator.generate_small_car_sequence("hybrid")
        self.assertEqual(len(sequence), 6)
        self.assertIn(energy_letter, self.generator.non_pure_electric_letters)
        self.assertEqual(sequence[0], energy_letter)
    
    def test_large_car_sequence_generation(self):
        """测试大型车序号生成"""
        # 纯电动
        sequence, energy_letter = self.generator.generate_large_car_sequence("pure")
        self.assertEqual(len(sequence), 6)
        self.assertTrue(sequence[:-1].isdigit())
        self.assertIn(energy_letter, self.generator.pure_electric_letters)
        self.assertEqual(sequence[-1], energy_letter)
        
        # 非纯电动
        sequence, energy_letter = self.generator.generate_large_car_sequence("hybrid")
        self.assertEqual(len(sequence), 6)
        self.assertTrue(sequence[:-1].isdigit())
        self.assertIn(energy_letter, self.generator.non_pure_electric_letters)
        self.assertEqual(sequence[-1], energy_letter)
    
    def test_energy_type_detection(self):
        """测试能源类型检测"""
        # 小型车
        self.assertEqual(self.generator.get_energy_type_from_sequence("D12345", "small"), "pure")
        self.assertEqual(self.generator.get_energy_type_from_sequence("F12345", "small"), "hybrid")
        
        # 大型车
        self.assertEqual(self.generator.get_energy_type_from_sequence("12345D", "large"), "pure")
        self.assertEqual(self.generator.get_energy_type_from_sequence("12345F", "large"), "hybrid")
    
    def test_sequence_validation(self):
        """测试序号验证"""
        # 有效序号
        self.assertTrue(self.generator.validate_new_energy_sequence("D12345", "small"))
        self.assertTrue(self.generator.validate_new_energy_sequence("12345D", "large"))
        
        # 无效序号
        self.assertFalse(self.generator.validate_new_energy_sequence("I12345", "small"))  # 禁用字母
        self.assertFalse(self.generator.validate_new_energy_sequence("D1234", "small"))   # 长度错误
        self.assertFalse(self.generator.validate_new_energy_sequence("X12345", "small"))  # 无效能源标识


class TestSequenceGeneratorFactory(unittest.TestCase):
    """测试序号生成器工厂"""
    
    def test_create_generator_by_sequence_type(self):
        """测试按序号类型创建生成器"""
        # 普通5位序号
        generator = SequenceGeneratorFactory.create_generator(SequenceType.ORDINARY_5_DIGIT)
        self.assertIsInstance(generator, OrdinarySequenceGenerator)
        
        # 新能源序号
        generator = SequenceGeneratorFactory.create_generator(SequenceType.NEW_ENERGY_SMALL_6_DIGIT)
        self.assertIsInstance(generator, NewEnergySequenceGenerator)
    
    def test_get_generator_for_plate_type(self):
        """测试按车牌类型获取生成器"""
        # 普通车牌类型
        generator = SequenceGeneratorFactory.get_generator_for_plate_type("ordinary_small")
        self.assertIsInstance(generator, OrdinarySequenceGenerator)
        
        # 新能源车牌类型
        generator = SequenceGeneratorFactory.get_generator_for_plate_type("new_energy_small")
        self.assertIsInstance(generator, NewEnergySequenceGenerator)
    
    def test_invalid_plate_type(self):
        """测试无效车牌类型"""
        with self.assertRaises(SequenceGenerationError):
            SequenceGeneratorFactory.get_generator_for_plate_type("invalid_type")


class TestForbiddenLetters(unittest.TestCase):
    """测试禁用字母功能"""
    
    def setUp(self):
        self.generator = OrdinarySequenceGenerator()
    
    def test_forbidden_letters_in_patterns(self):
        """测试模式中的禁用字母检测"""
        # 测试包含I的序号
        self.assertFalse(self.generator.validate_pattern("I1234", "LDDDD"))
        self.assertFalse(self.generator.validate_pattern("1I234", "DLDDD"))
        self.assertFalse(self.generator.validate_pattern("12I34", "DDLDD"))
        
        # 测试包含O的序号
        self.assertFalse(self.generator.validate_pattern("O1234", "LDDDD"))
        self.assertFalse(self.generator.validate_pattern("1O234", "DLDDD"))
        self.assertFalse(self.generator.validate_pattern("12O34", "DDLDD"))
        
        # 测试不包含禁用字母的序号
        self.assertTrue(self.generator.validate_pattern("A1234", "LDDDD"))
        self.assertTrue(self.generator.validate_pattern("1A234", "DLDDD"))
        self.assertTrue(self.generator.validate_pattern("12A34", "DDLDD"))


def run_tests():
    """运行所有测试"""
    print("开始运行序号生成器单元测试...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestSequenceResourceManager,
        TestOrdinarySequenceGenerator,
        TestNewEnergySequenceGenerator,
        TestSequenceGeneratorFactory,
        TestForbiddenLetters,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)