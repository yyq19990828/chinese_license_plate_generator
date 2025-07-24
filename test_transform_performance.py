#!/usr/bin/env python3
"""
车牌变换效果性能测试脚本

测试变换系统的性能，包括内存使用、处理时间和吞吐量。
"""

import time
import sys
import os
import gc
import psutil
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

# 添加项目路径
sys.path.append('.')

from src.transform import (
    WearEffect, FadeEffect, DirtEffect,
    TiltTransform, PerspectiveTransform, RotationTransform,
    ShadowEffect, ReflectionEffect, NightEffect, BacklightEffect,
    CompositeTransform, TransformConfig, quick_enhance
)


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.results = []
        self.process = psutil.Process()
    
    def measure_memory(self) -> float:
        """测量当前内存使用量（MB）"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def measure_time_and_memory(self, func, *args, **kwargs) -> Tuple[Any, float, float, float]:
        """
        测量函数执行时间和内存使用
        
        Returns:
            Tuple[Any, float, float, float]: (结果, 执行时间, 开始内存, 结束内存)
        """
        gc.collect()  # 强制垃圾回收
        start_memory = self.measure_memory()
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self.measure_memory()
        
        execution_time = end_time - start_time
        return result, execution_time, start_memory, end_memory
    
    def record_result(self, test_name: str, execution_time: float, 
                     start_memory: float, end_memory: float, 
                     additional_data: Dict[str, Any] = None):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'execution_time': execution_time,
            'start_memory': start_memory,
            'end_memory': end_memory,
            'memory_delta': end_memory - start_memory,
            'timestamp': time.time()
        }
        if additional_data:
            result.update(additional_data)
        
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取性能测试摘要"""
        if not self.results:
            return {}
        
        execution_times = [r['execution_time'] for r in self.results]
        memory_deltas = [r['memory_delta'] for r in self.results]
        
        return {
            'total_tests': len(self.results),
            'avg_execution_time': np.mean(execution_times),
            'min_execution_time': np.min(execution_times),
            'max_execution_time': np.max(execution_times),
            'avg_memory_delta': np.mean(memory_deltas),
            'max_memory_delta': np.max(memory_deltas),
            'total_time': np.sum(execution_times)
        }


def create_test_images(sizes: List[Tuple[int, int]]) -> Dict[str, Image.Image]:
    """创建不同尺寸的测试图像"""
    test_images = {}
    
    for width, height in sizes:
        # 创建车牌样式的测试图像
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        
        # 添加一些内容以使变换效果更明显
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # 绘制边框
        border_width = max(1, min(width, height) // 50)
        draw.rectangle([border_width, border_width, 
                       width - border_width, height - border_width], 
                      outline=(0, 0, 0), width=border_width)
        
        # 添加一些矩形来模拟字符
        char_width = width // 8
        char_height = height // 3
        for i in range(6):
            x = (i + 1) * width // 8
            y = height // 3
            draw.rectangle([x, y, x + char_width//2, y + char_height], 
                          fill=(0, 0, 0))
        
        size_name = f"{width}x{height}"
        test_images[size_name] = image
    
    return test_images


def test_single_transform_performance(profiler: PerformanceProfiler):
    """测试单个变换的性能"""
    print("测试单个变换性能...")
    
    # 创建测试图像
    test_image = Image.new('RGB', (440, 140), color=(255, 255, 255))
    
    # 测试各种变换效果
    transforms = [
        ('WearEffect', WearEffect(probability=1.0)),
        ('FadeEffect', FadeEffect(probability=1.0)),
        ('DirtEffect', DirtEffect(probability=1.0)),
        ('TiltTransform', TiltTransform(probability=1.0)),
        ('PerspectiveTransform', PerspectiveTransform(probability=1.0)),
        ('RotationTransform', RotationTransform(probability=1.0)),
        ('ShadowEffect', ShadowEffect(probability=1.0)),
        ('ReflectionEffect', ReflectionEffect(probability=1.0)),
        ('NightEffect', NightEffect(probability=1.0)),
        ('BacklightEffect', BacklightEffect(probability=1.0)),
    ]
    
    # 测试每个变换多次
    iterations = 10
    
    for transform_name, transform in transforms:
        print(f"  测试 {transform_name}...")
        
        times = []
        for i in range(iterations):
            result, exec_time, start_mem, end_mem = profiler.measure_time_and_memory(
                transform.apply, test_image, intensity=0.7
            )
            times.append(exec_time)
            
            profiler.record_result(
                f"{transform_name}_single",
                exec_time,
                start_mem,
                end_mem,
                {'iteration': i, 'success': result is not None}
            )
        
        avg_time = np.mean(times)
        std_time = np.std(times)
        print(f"    平均时间: {avg_time:.4f}s ± {std_time:.4f}s")


def test_image_size_scaling(profiler: PerformanceProfiler):
    """测试不同图像尺寸的性能缩放"""
    print("测试图像尺寸缩放性能...")
    
    # 不同的图像尺寸
    sizes = [
        (220, 70),   # 小尺寸
        (440, 140),  # 标准尺寸
        (880, 280),  # 大尺寸
        (1320, 420), # 特大尺寸
    ]
    
    test_images = create_test_images(sizes)
    
    # 选择一个中等复杂度的变换进行测试
    transform = CompositeTransform()
    
    for size_name, test_image in test_images.items():
        print(f"  测试尺寸 {size_name}...")
        
        # 测试多次取平均值
        times = []
        for i in range(5):
            result, exec_time, start_mem, end_mem = profiler.measure_time_and_memory(
                transform.apply, test_image, max_transforms=3, intensity_scale=0.7
            )
            times.append(exec_time)
            
            profiler.record_result(
                f"size_scaling_{size_name}",
                exec_time,
                start_mem,
                end_mem,
                {'image_size': size_name, 'iteration': i}
            )
        
        avg_time = np.mean(times)
        pixels = test_image.width * test_image.height
        pixels_per_second = pixels / avg_time
        
        print(f"    平均时间: {avg_time:.4f}s")
        print(f"    处理速度: {pixels_per_second:.0f} 像素/秒")


def test_composite_transform_performance(profiler: PerformanceProfiler):
    """测试复合变换性能"""
    print("测试复合变换性能...")
    
    test_image = Image.new('RGB', (440, 140), color=(255, 255, 255))
    
    # 测试不同数量的变换组合
    max_transforms_list = [1, 2, 3, 5, 8]
    
    for max_transforms in max_transforms_list:
        print(f"  测试最多 {max_transforms} 个变换...")
        
        transformer = CompositeTransform()
        
        times = []
        applied_counts = []
        
        for i in range(10):
            start_time = time.time()
            result, applied_transforms = transformer.apply(
                test_image, 
                max_transforms=max_transforms,
                intensity_scale=0.7
            )
            end_time = time.time()
            
            exec_time = end_time - start_time
            times.append(exec_time)
            applied_counts.append(len(applied_transforms))
            
            profiler.record_result(
                f"composite_{max_transforms}_transforms",
                exec_time,
                0, 0,  # 简化内存测量
                {
                    'max_transforms': max_transforms,
                    'applied_transforms': len(applied_transforms),
                    'iteration': i
                }
            )
        
        avg_time = np.mean(times)
        avg_applied = np.mean(applied_counts)
        print(f"    平均时间: {avg_time:.4f}s")
        print(f"    平均应用变换数: {avg_applied:.1f}")


def test_memory_usage_over_time(profiler: PerformanceProfiler):
    """测试长时间运行的内存使用情况"""
    print("测试长时间运行内存使用...")
    
    test_image = Image.new('RGB', (440, 140), color=(255, 255, 255))
    transformer = CompositeTransform()
    
    # 连续运行大量变换
    iterations = 100
    memory_samples = []
    
    for i in range(iterations):
        if i % 10 == 0:
            print(f"  迭代 {i}/{iterations}")
        
        start_memory = profiler.measure_memory()
        
        result, applied_transforms = transformer.apply(
            test_image,
            max_transforms=3,
            intensity_scale=0.7
        )
        
        end_memory = profiler.measure_memory()
        memory_samples.append(end_memory)
        
        profiler.record_result(
            "memory_stress_test",
            0,  # 不关注时间
            start_memory,
            end_memory,
            {'iteration': i}
        )
        
        # 每25次迭代强制垃圾回收
        if i % 25 == 0:
            gc.collect()
    
    # 分析内存趋势
    memory_trend = np.polyfit(range(len(memory_samples)), memory_samples, 1)[0]
    print(f"  内存趋势: {memory_trend:.4f} MB/迭代")
    
    if abs(memory_trend) > 0.1:
        print("  警告: 检测到潜在的内存泄漏!")
    else:
        print("  内存使用稳定")


def test_concurrent_performance(profiler: PerformanceProfiler):
    """测试并发性能"""
    print("测试并发性能...")
    
    test_image = Image.new('RGB', (440, 140), color=(255, 255, 255))
    
    def worker_function(worker_id: int) -> float:
        """工作线程函数"""
        transformer = CompositeTransform()
        start_time = time.time()
        
        for i in range(10):
            result, applied_transforms = transformer.apply(
                test_image,
                max_transforms=2,
                intensity_scale=0.7
            )
        
        return time.time() - start_time
    
    # 测试不同的并发级别
    thread_counts = [1, 2, 4, 8]
    
    for thread_count in thread_counts:
        print(f"  测试 {thread_count} 个线程...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [executor.submit(worker_function, i) for i in range(thread_count)]
            worker_times = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        avg_worker_time = np.mean(worker_times)
        
        print(f"    总时间: {total_time:.4f}s")
        print(f"    平均工作时间: {avg_worker_time:.4f}s")
        print(f"    并行效率: {(avg_worker_time * thread_count / total_time):.2f}")
        
        profiler.record_result(
            f"concurrent_{thread_count}_threads",
            total_time,
            0, 0,
            {
                'thread_count': thread_count,
                'avg_worker_time': avg_worker_time,
                'efficiency': avg_worker_time * thread_count / total_time
            }
        )


def test_quick_enhance_performance(profiler: PerformanceProfiler):
    """测试快速增强功能性能"""
    print("测试快速增强性能...")
    
    test_image = Image.new('RGB', (440, 140), color=(255, 255, 255))
    
    # 测试不同的强度级别
    intensities = ["light", "medium", "heavy"]
    styles = ["balanced", "aging", "perspective", "lighting"]
    
    for intensity in intensities:
        print(f"  测试强度: {intensity}")
        
        times = []
        for i in range(10):
            result, exec_time, start_mem, end_mem = profiler.measure_time_and_memory(
                quick_enhance, test_image, intensity=intensity
            )
            times.append(exec_time)
            
            profiler.record_result(
                f"quick_enhance_intensity_{intensity}",
                exec_time,
                start_mem,
                end_mem,
                {'intensity': intensity, 'iteration': i}
            )
        
        avg_time = np.mean(times)
        print(f"    平均时间: {avg_time:.4f}s")
    
    for style in styles:
        print(f"  测试风格: {style}")
        
        times = []
        for i in range(10):
            result, exec_time, start_mem, end_mem = profiler.measure_time_and_memory(
                quick_enhance, test_image, style=style
            )
            times.append(exec_time)
            
            profiler.record_result(
                f"quick_enhance_style_{style}",
                exec_time,
                start_mem,
                end_mem,
                {'style': style, 'iteration': i}
            )
        
        avg_time = np.mean(times)
        print(f"    平均时间: {avg_time:.4f}s")


def run_performance_benchmark():
    """运行完整的性能基准测试"""
    print("开始车牌变换系统性能测试")
    print("=" * 60)
    
    profiler = PerformanceProfiler()
    
    # 运行各种性能测试
    test_functions = [
        test_single_transform_performance,
        test_image_size_scaling,
        test_composite_transform_performance,
        test_quick_enhance_performance,
        test_memory_usage_over_time,
        test_concurrent_performance,
    ]
    
    for test_func in test_functions:
        try:
            print(f"\n{'-' * 40}")
            test_func(profiler)
        except Exception as e:
            print(f"测试 {test_func.__name__} 失败: {e}")
    
    print(f"\n{'=' * 60}")
    print("性能测试完成")
    
    # 生成摘要报告
    summary = profiler.get_summary()
    if summary:
        print(f"\n摘要报告:")
        print(f"  总测试数: {summary['total_tests']}")
        print(f"  平均执行时间: {summary['avg_execution_time']:.4f}s")
        print(f"  最快执行时间: {summary['min_execution_time']:.4f}s")
        print(f"  最慢执行时间: {summary['max_execution_time']:.4f}s")
        print(f"  平均内存变化: {summary['avg_memory_delta']:.2f}MB")
        print(f"  最大内存变化: {summary['max_memory_delta']:.2f}MB")
        print(f"  总测试时间: {summary['total_time']:.2f}s")
    
    # 生成详细报告
    generate_detailed_report(profiler.results)
    
    return profiler.results


def generate_detailed_report(results: List[Dict[str, Any]]):
    """生成详细的性能报告"""
    print(f"\n{'=' * 60}")
    print("详细性能报告")
    print("=" * 60)
    
    # 按测试类型分组
    grouped_results = {}
    for result in results:
        test_name = result['test_name'].split('_')[0]  # 取第一部分作为分组键
        if test_name not in grouped_results:
            grouped_results[test_name] = []
        grouped_results[test_name].append(result)
    
    # 为每个分组生成统计信息
    for group_name, group_results in grouped_results.items():
        if len(group_results) < 2:
            continue
            
        execution_times = [r['execution_time'] for r in group_results]
        memory_deltas = [r['memory_delta'] for r in group_results]
        
        print(f"\n{group_name} 性能统计:")
        print(f"  测试次数: {len(group_results)}")
        print(f"  执行时间 - 平均: {np.mean(execution_times):.4f}s, "
              f"标准差: {np.std(execution_times):.4f}s")
        print(f"  内存变化 - 平均: {np.mean(memory_deltas):.2f}MB, "
              f"最大: {np.max(memory_deltas):.2f}MB")
        
        # 计算吞吐量（假设标准车牌图像）
        if np.mean(execution_times) > 0:
            throughput = 1.0 / np.mean(execution_times)
            print(f"  吞吐量: {throughput:.1f} 图像/秒")


def identify_performance_bottlenecks(results: List[Dict[str, Any]]):
    """识别性能瓶颈"""
    print(f"\n{'=' * 60}")
    print("性能瓶颈分析")
    print("=" * 60)
    
    # 找出最慢的操作
    slowest_operations = sorted(results, key=lambda x: x['execution_time'], reverse=True)[:5]
    
    print("最慢的操作:")
    for i, op in enumerate(slowest_operations, 1):
        print(f"  {i}. {op['test_name']}: {op['execution_time']:.4f}s")
    
    # 找出内存使用最多的操作
    memory_intensive = sorted(results, key=lambda x: x['memory_delta'], reverse=True)[:5]
    
    print("\n内存使用最多的操作:")
    for i, op in enumerate(memory_intensive, 1):
        print(f"  {i}. {op['test_name']}: +{op['memory_delta']:.2f}MB")
    
    # 性能建议
    print("\n性能优化建议:")
    
    avg_time = np.mean([r['execution_time'] for r in results])
    if avg_time > 0.1:
        print("  - 考虑优化算法或使用更高效的图像处理库")
    
    max_memory = max([r['memory_delta'] for r in results])
    if max_memory > 50:
        print("  - 考虑减少内存使用或实现内存池")
    
    # 检查内存泄漏迹象
    memory_stress_results = [r for r in results if 'memory_stress' in r['test_name']]
    if memory_stress_results:
        memory_trend = np.polyfit(
            range(len(memory_stress_results)), 
            [r['end_memory'] for r in memory_stress_results], 
            1
        )[0]
        
        if abs(memory_trend) > 0.1:
            print("  - 检测到潜在内存泄漏，建议检查对象生命周期管理")


if __name__ == "__main__":
    # 检查系统信息
    print("系统信息:")
    print(f"  CPU核心数: {multiprocessing.cpu_count()}")
    print(f"  可用内存: {psutil.virtual_memory().available / 1024 / 1024:.0f}MB")
    print(f"  Python版本: {sys.version}")
    
    # 运行性能测试
    results = run_performance_benchmark()
    
    # 分析性能瓶颈
    identify_performance_bottlenecks(results)
    
    print(f"\n性能测试完成！")