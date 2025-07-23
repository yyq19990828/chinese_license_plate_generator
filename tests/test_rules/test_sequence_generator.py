"""
序号生成器单元测试
测试 src/rules/sequence_generator.py 的所有功能
"""

import unittest
import os
import sys

# 添加src路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.rules.sequence_generator import (
    OrdinarySequenceGenerator,
    NewEnergySequenceGenerator,
    SequenceGeneratorFactory,
    SequenceType,
    SequenceResourceManager,
    SequencePattern
)
from src.core.exceptions import SequenceGenerationError
from src.utils.constants import PlateConstants, SequenceConstants


class TestSequenceResourceManager(unittest.TestCase):
    """测试序号资源管理器"""
    
    def setUp(self):
        """测试前设置"""
        self.resource_manager = SequenceResourceManager()
    
    def test_initial_usage_rate(self):
        """测试初始使用率"""
        pattern_key = "test_pattern"
        self.assertEqual(self.resource_manager.get_usage_rate(pattern_key), 0.0)
    
    def test_update_usage_rate(self):
        """测试更新使用率"""
        pattern_key = "test_pattern"
        
        # 正常更新
        self.resource_manager.update_usage_rate(pattern_key, 0.5)
        self.assertEqual(self.resource_manager.get_usage_rate(pattern_key), 0.5)
        
        # 边界值测试
        self.resource_manager.update_usage_rate(pattern_key, 1.5)  # 超过1.0
        self.assertEqual(self.resource_manager.get_usage_rate(pattern_key), 1.0)
        
        self.resource_manager.update_usage_rate(pattern_key, -0.1)  # 小于0.0
        self.assertEqual(self.resource_manager.get_usage_rate(pattern_key), 0.0)
    
    def test_pattern_availability(self):
        """测试模式可用性"""
        pattern_key = "test_pattern"
        
        # 初始状态应该可用
        self.assertTrue(self.resource_manager.is_pattern_available(pattern_key))
        
        # 低于阈值应该可用
        self.resource_manager.update_usage_rate(pattern_key, 0.5)
        self.assertTrue(self.resource_manager.is_pattern_available(pattern_key))
        
        # 等于阈值应该可用
        self.resource_manager.update_usage_rate(pattern_key, 0.6)
        self.assertTrue(self.resource_manager.is_pattern_available(pattern_key))
        
        # 超过阈值应该不可用
        self.resource_manager.update_usage_rate(pattern_key, 0.7)
        self.assertFalse(self.resource_manager.is_pattern_available(pattern_key))
    
    def test_get_available_patterns(self):
        """测试获取可用模式"""
        patterns = [
            SequencePattern(order=1, pattern="DDDDD", description="test1", example="12345"),
            SequencePattern(order=2, pattern="LDDDD", description="test2", example="A1234"),
        ]
        
        # 初始状态都应该可用
        available = self.resource_manager.get_available_patterns(patterns)
        self.assertEqual(len(available), 2)
        
        # 将第一个模式的使用率设为超过阈值
        self.resource_manager.update_usage_rate("DDDDD_1", 0.7)
        available = self.resource_manager.get_available_patterns(patterns)
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0].order, 2)


class TestOrdinarySequenceGenerator(unittest.TestCase):
    """测试普通汽车序号生成器"""
    
    def setUp(self):
        """测试前设置"""
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
        self.assertTrue(self.generator.validate_pattern("1A234", "DLDDD"))
        
        # 错误的模式
        self.assertFalse(self.generator.validate_pattern("A123", "DDDDD"))  # 长度不匹配
        self.assertFalse(self.generator.validate_pattern("1234A", "DDDDD"))  # 类型不匹配
        self.assertFalse(self.generator.validate_pattern("12I34", "DDLDD"))  # 包含禁用字母
        self.assertFalse(self.generator.validate_pattern("12O34", "DDLDD"))  # 包含禁用字母
    
    def test_generate_sequence_basic(self):
        """测试基本序号生成"""
        sequence, pattern = self.generator.generate_sequence("湘", "A")
        
        self.assertIsInstance(sequence, str)
        self.assertEqual(len(sequence), 5)
        self.assertIsInstance(pattern, SequencePattern)
        self.assertTrue(self.generator.validate_pattern(sequence, pattern.pattern))
    
    def test_generate_sequence_with_preferred_order(self):
        """测试指定首选顺序生成"""
        for order in range(1, 6):  # 测试前5个顺序
            sequence, pattern = self.generator.generate_sequence("京", "A", preferred_order=order)
            self.assertEqual(pattern.order, order)
            self.assertTrue(self.generator.validate_pattern(sequence, pattern.pattern))
    
    def test_generate_sequence_with_force_pattern(self):
        """测试强制模式生成"""
        test_patterns = ["DDDDD", "LDDDD", "LLDDD", "DLDDD"]
        
        for pattern_str in test_patterns:
            sequence, pattern = self.generator.generate_sequence("粤", "B", force_pattern=pattern_str)
            self.assertEqual(pattern.pattern, pattern_str)
            self.assertTrue(self.generator.validate_pattern(sequence, pattern.pattern))
    
    def test_generate_sequence_invalid_force_pattern(self):
        """测试无效强制模式"""
        with self.assertRaises(SequenceGenerationError):
            self.generator.generate_sequence("川", "A", force_pattern="INVALID")
    
    def test_get_pattern_by_order(self):
        """测试根据顺序获取模式"""
        pattern = self.generator.get_pattern_by_order(1)
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.order, 1)
        self.assertEqual(pattern.pattern, "DDDDD")
        
        # 测试不存在的顺序
        pattern = self.generator.get_pattern_by_order(999)
        self.assertIsNone(pattern)
    
    def test_get_available_orders(self):
        """测试获取可用顺序"""
        orders = self.generator.get_available_orders()
        self.assertEqual(orders, list(range(1, 11)))  # 初始状态所有顺序都可用
        
        # 将某些模式标记为不可用
        self.generator.resource_manager.update_usage_rate("DDDDD_1", 0.7)
        self.generator.resource_manager.update_usage_rate("LDDDD_2", 0.8)
        
        orders = self.generator.get_available_orders()
        self.assertNotIn(1, orders)
        self.assertNotIn(2, orders)
        self.assertIn(3, orders)


class TestNewEnergySequenceGenerator(unittest.TestCase):
    """测试新能源汽车序号生成器"""
    
    def setUp(self):
        """测试前设置"""
        self.generator = NewEnergySequenceGenerator()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.generator.pure_electric_letters, ["D", "A", "B", "C", "E"])
        self.assertEqual(self.generator.non_pure_electric_letters, ["F", "G", "H", "J", "K"])
    
    def test_generate_small_car_sequence_pure(self):
        """测试小型纯电动车序号生成"""
        sequence, energy_letter = self.generator.generate_small_car_sequence("pure")
        
        self.assertEqual(len(sequence), 6)
        self.assertIn(energy_letter, self.generator.pure_electric_letters)
        self.assertEqual(sequence[0], energy_letter)
        self.assertTrue(sequence[1:].isdigit() or (sequence[1].isalpha() and sequence[2:].isdigit()))
    
    def test_generate_small_car_sequence_hybrid(self):
        """测试小型非纯电动车序号生成"""
        sequence, energy_letter = self.generator.generate_small_car_sequence("hybrid")
        
        self.assertEqual(len(sequence), 6)
        self.assertIn(energy_letter, self.generator.non_pure_electric_letters)
        self.assertEqual(sequence[0], energy_letter)
        self.assertTrue(sequence[1:].isdigit() or (sequence[1].isalpha() and sequence[2:].isdigit()))
    
    def test_generate_small_car_sequence_double_letter(self):
        """测试小型车双字母序号生成"""
        sequence, energy_letter = self.generator.generate_small_car_sequence("pure", double_letter=True)
        
        self.assertEqual(len(sequence), 6)
        self.assertTrue(sequence[0].isalpha())
        self.assertTrue(sequence[1].isalpha())
        self.assertTrue(sequence[2:].isdigit())
        self.assertEqual(sequence[0], energy_letter)
    
    def test_generate_small_car_sequence_preferred_letter(self):
        """测试指定首选字母"""
        preferred_letter = "D"
        sequence, energy_letter = self.generator.generate_small_car_sequence("pure", preferred_letter=preferred_letter)
        
        self.assertEqual(energy_letter, preferred_letter)
        self.assertEqual(sequence[0], preferred_letter)
    
    def test_generate_large_car_sequence_pure(self):
        """测试大型纯电动车序号生成"""
        sequence, energy_letter = self.generator.generate_large_car_sequence("pure")
        
        self.assertEqual(len(sequence), 6)
        self.assertTrue(sequence[:-1].isdigit())
        self.assertTrue(sequence[-1].isalpha())
        self.assertIn(energy_letter, self.generator.pure_electric_letters)
        self.assertEqual(sequence[-1], energy_letter)
    
    def test_generate_large_car_sequence_hybrid(self):
        """测试大型非纯电动车序号生成"""
        sequence, energy_letter = self.generator.generate_large_car_sequence("hybrid")
        
        self.assertEqual(len(sequence), 6)
        self.assertTrue(sequence[:-1].isdigit())
        self.assertTrue(sequence[-1].isalpha())
        self.assertIn(energy_letter, self.generator.non_pure_electric_letters)
        self.assertEqual(sequence[-1], energy_letter)
    
    def test_get_energy_type_from_sequence(self):
        """测试从序号判断能源类型"""
        # 小型车测试
        self.assertEqual(self.generator.get_energy_type_from_sequence("D12345", "small"), "pure")
        self.assertEqual(self.generator.get_energy_type_from_sequence("F12345", "small"), "hybrid")
        self.assertEqual(self.generator.get_energy_type_from_sequence("X12345", "small"), "unknown")
        
        # 大型车测试
        self.assertEqual(self.generator.get_energy_type_from_sequence("12345D", "large"), "pure")
        self.assertEqual(self.generator.get_energy_type_from_sequence("12345F", "large"), "hybrid")
        self.assertEqual(self.generator.get_energy_type_from_sequence("12345X", "large"), "unknown")
    
    def test_validate_new_energy_sequence(self):
        """测试新能源序号验证"""
        # 小型车有效序号
        self.assertTrue(self.generator.validate_new_energy_sequence("D12345", "small"))
        self.assertTrue(self.generator.validate_new_energy_sequence("F12345", "small"))
        self.assertTrue(self.generator.validate_new_energy_sequence("AB1234", "small"))
        
        # 大型车有效序号
        self.assertTrue(self.generator.validate_new_energy_sequence("12345D", "large"))
        self.assertTrue(self.generator.validate_new_energy_sequence("12345F", "large"))
        
        # 无效序号
        self.assertFalse(self.generator.validate_new_energy_sequence("I12345", "small"))  # 禁用字母
        self.assertFalse(self.generator.validate_new_energy_sequence("D1234", "small"))   # 长度错误
        self.assertFalse(self.generator.validate_new_energy_sequence("1234AD", "large"))  # 大型车格式错误
        self.assertFalse(self.generator.validate_new_energy_sequence("X12345", "small"))  # 无效能源标识


class TestSequenceGeneratorFactory(unittest.TestCase):
    """测试序号生成器工厂"""
    
    def test_create_generator_by_sequence_type(self):
        """测试按序号类型创建生成器"""
        # 普通5位序号
        generator = SequenceGeneratorFactory.create_generator(SequenceType.ORDINARY_5_DIGIT)
        self.assertIsInstance(generator, OrdinarySequenceGenerator)
        
        # 小型新能源6位序号
        generator = SequenceGeneratorFactory.create_generator(SequenceType.NEW_ENERGY_SMALL_6_DIGIT)
        self.assertIsInstance(generator, NewEnergySequenceGenerator)
        
        # 大型新能源6位序号
        generator = SequenceGeneratorFactory.create_generator(SequenceType.NEW_ENERGY_LARGE_6_DIGIT)
        self.assertIsInstance(generator, NewEnergySequenceGenerator)
    
    def test_get_generator_for_plate_type(self):
        """测试按车牌类型获取生成器"""
        # 普通车牌类型
        ordinary_types = ["ordinary_large", "ordinary_small", "trailer", "coach", "police"]
        for plate_type in ordinary_types:
            generator = SequenceGeneratorFactory.get_generator_for_plate_type(plate_type)
            self.assertIsInstance(generator, OrdinarySequenceGenerator)
        
        # 新能源车牌类型
        generator = SequenceGeneratorFactory.get_generator_for_plate_type("new_energy_small")
        self.assertIsInstance(generator, NewEnergySequenceGenerator)
        
        generator = SequenceGeneratorFactory.get_generator_for_plate_type("new_energy_large")
        self.assertIsInstance(generator, NewEnergySequenceGenerator)
    
    def test_invalid_sequence_type(self):
        """测试无效序号类型"""
        with self.assertRaises(SequenceGenerationError):
            # 使用字符串而不是枚举值，应该抛出异常
            SequenceGeneratorFactory.create_generator("invalid_type")
    
    def test_invalid_plate_type(self):
        """测试无效车牌类型"""
        with self.assertRaises(SequenceGenerationError):
            SequenceGeneratorFactory.get_generator_for_plate_type("invalid_plate_type")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_sequence_generation_integration(self):
        """测试序号生成集成功能"""
        # 测试普通车牌序号生成
        ordinary_gen = SequenceGeneratorFactory.get_generator_for_plate_type("ordinary_small")
        sequence, pattern = ordinary_gen.generate_sequence("湘", "A")
        
        self.assertEqual(len(sequence), 5)
        self.assertTrue(ordinary_gen.validate_pattern(sequence, pattern.pattern))
        
        # 测试新能源车牌序号生成
        new_energy_gen = SequenceGeneratorFactory.get_generator_for_plate_type("new_energy_small")
        sequence, energy_letter = new_energy_gen.generate_small_car_sequence("pure")
        
        self.assertEqual(len(sequence), 6)
        self.assertTrue(new_energy_gen.validate_new_energy_sequence(sequence, "small"))
        self.assertEqual(new_energy_gen.get_energy_type_from_sequence(sequence, "small"), "pure")
    
    def test_resource_exhaustion_simulation(self):
        """测试资源耗尽模拟"""
        generator = OrdinarySequenceGenerator()
        
        # 模拟所有模式都被标记为使用率过高
        for pattern in generator.patterns:
            pattern_key = f"{pattern.pattern}_{pattern.order}"
            generator.resource_manager.update_usage_rate(pattern_key, 0.8)
        
        # 此时应该没有可用模式
        available_orders = generator.get_available_orders()
        self.assertEqual(len(available_orders), 0)
        
        # 生成序号应该抛出异常
        with self.assertRaises(SequenceGenerationError):
            generator.generate_sequence("京", "A")
    
    def test_forbidden_letters_comprehensive(self):
        """测试禁用字母的全面检查"""
        generator = OrdinarySequenceGenerator()
        
        # 测试所有禁用字母
        for forbidden_letter in PlateConstants.FORBIDDEN_LETTERS:
            # 在不同位置测试禁用字母
            test_sequences = [
                f"{forbidden_letter}1234",  # 第1位
                f"1{forbidden_letter}234",  # 第2位
                f"12{forbidden_letter}34",  # 第3位
                f"123{forbidden_letter}4",  # 第4位
                f"1234{forbidden_letter}",  # 第5位
            ]
            
            for seq in test_sequences:
                # 找到对应的模式
                pattern = "L" if seq[0].isalpha() else "D"
                for i in range(1, len(seq)):
                    pattern += "L" if seq[i].isalpha() else "D"
                
                # 验证包含禁用字母的序号应该无效
                is_valid = generator.validate_pattern(seq, pattern)
                self.assertFalse(is_valid, f"序号 {seq} 包含禁用字母 {forbidden_letter}，应该无效")


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)