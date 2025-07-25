# 中国车牌生成器高级用法指南

## 概述

本文档详细介绍中国车牌生成器的高级用法，包括各种生成模式、配置选项、API调用以及自定义扩展方法。

## 目录

1. [生成脚本使用](#生成脚本使用)
2. [API编程接口](#api编程接口)
3. [车牌类型详解](#车牌类型详解)
4. [图像增强效果](#图像增强效果)
5. [自定义配置](#自定义配置)
6. [性能优化](#性能优化)
7. [扩展开发](#扩展开发)

---

## 生成脚本使用

### 1. 按省份生成车牌 (`generate_by_province.py`)

#### 基本用法
```bash
# 为北京生成10个车牌
python generate_by_province.py --province 京 --number 10

# 为广东生成100个车牌，20%概率生成双层车牌
python generate_by_province.py --province 粤 --number 100 --double-ratio 0.2

# 自定义保存目录
python generate_by_province.py --province 沪 --number 50 --save-dir ./my_plates
```

#### 支持的省份简称
```
京、津、冀、晋、蒙、辽、吉、黑、沪、苏、浙、皖、闽、赣、
鲁、豫、鄂、湘、粤、桂、琼、渝、川、贵、云、藏、陕、甘、青、宁、新
```

#### 双层车牌说明
- 支持双层车牌的类型：`ORDINARY_YELLOW`（黄牌大型车）、`ORDINARY_TRAILER`（挂车）
- 通过 `--double-ratio` 参数控制双层车牌生成比例（0.0-1.0）

### 2. 批量多类型生成 (`generate_multi_plate.py`)

#### 基本用法
```bash
# 生成1000个随机车牌（所有类型混合）
python generate_multi_plate.py --number 1000

# 启用图像增强效果
python generate_multi_plate.py --number 500 --enhance

# 自定义输出目录
python generate_multi_plate.py --number 200 --save-adr ./mixed_plates
```

#### 特点
- 自动随机选择车牌类型（普通、新能源、特殊等）
- 支持图像增强（老化、光照、透视等效果）
- 高效批量生成，适合数据集制作

### 3. 新能源车牌生成 (`generate_new_energy_plate.py`)

#### 基本用法
```bash
# 生成小型纯电动新能源车牌
python generate_new_energy_plate.py --size small --energy-type pure --count 100

# 生成大型非纯电动新能源车牌
python generate_new_energy_plate.py --size large --energy-type hybrid --count 50

# 指定省份和地区代码
python generate_new_energy_plate.py --size small --province 京 --regional-code A --count 20

# 使用双字母格式（仅小型车支持）
python generate_new_energy_plate.py --size small --double-letter --count 30
```

#### 高级选项
```bash
# 指定首选能源标识字母
python generate_new_energy_plate.py --size small --preferred-letter D --count 10

# 生成指定车牌号码
python generate_new_energy_plate.py --size small --plate-number 京AD12345

# 启用详细输出和统计信息
python generate_new_energy_plate.py --size small --count 1 --verbose --show-stats

# 启用图像增强
python generate_new_energy_plate.py --size small --enhance --count 50
```

#### 能源标识字母说明
- **纯电动车字母**：D、A、B、C、E
- **非纯电动车字母**：F、G、H、J、K
- **字母含义**：
  - D: 纯电动汽车
  - F: 非纯电动汽车（插电式混合动力、燃料电池等）

### 4. 特殊车牌生成 (`generate_special_plate.py`)

#### 基本用法
```bash
# 生成使馆车牌
python generate_special_plate.py --type embassy --count 50

# 生成领馆车牌
python generate_special_plate.py --type consulate --count 30

# 生成港澳入出境车牌
python generate_special_plate.py --type hong_kong_macao --count 40

# 生成军用车牌
python generate_special_plate.py --type military --count 20
```

#### 高级选项
```bash
# 指定特殊子类型
python generate_special_plate.py --type military --special-type army --count 10

# 生成指定车牌号码
python generate_special_plate.py --type embassy --plate-number 使001234

# 启用图像增强
python generate_special_plate.py --type embassy --enhance --count 25
```

---

## API编程接口

### 1. 集成生成器使用

```python
from src.generator.integrated_generator import IntegratedPlateGenerator
from src.generator.plate_generator import PlateGenerationConfig
from src.utils.constants import PlateType

# 初始化生成器
generator = IntegratedPlateGenerator(
    plate_models_dir="plate_model",
    font_models_dir="font_model"
)

# 生成随机车牌
plate_info, plate_image = generator.generate_plate_with_image(enhance=True)

# 生成指定车牌
plate_info, plate_image = generator.generate_specific_plate_with_image("京A12345")

# 批量生成
config = PlateGenerationConfig(province="粤", plate_type=PlateType.ORDINARY_BLUE)
results = generator.generate_batch_plates_with_images(count=100, config=config)
```

### 2. 配置化生成

```python
from src.generator.plate_generator import PlateGenerationConfig
from src.utils.constants import PlateType

# 创建生成配置
config = PlateGenerationConfig(
    province="京",                          # 指定省份
    plate_type=PlateType.NEW_ENERGY_SMALL,   # 车牌类型
    regional_code="A",                       # 地区代码
    preferred_sequence_pattern="DDDDD",      # 序号模式偏好
    enable_double_layer=False                # 是否启用双层
)

# 使用配置生成
generator = IntegratedPlateGenerator()
plate_info, plate_image = generator.generate_plate_with_image(config, enhance=True)
```

### 3. 新能源车牌专用API

```python
from src.rules.new_energy_plate import NewEnergyPlateRuleFactory, EnergyType

# 创建小型新能源车规则
rule = NewEnergyPlateRuleFactory.create_rule("small_car")

# 生成纯电动车牌
plate_info = rule.generate_plate(
    province="沪",
    regional_code="B",
    energy_type=EnergyType.PURE_ELECTRIC,
    preferred_letter="D",
    double_letter=True  # 双字母格式
)

# 生成图像
generator = IntegratedPlateGenerator()
plate_image = generator.image_composer.compose_plate_image(plate_info, enhance=True)
```

### 4. 特殊车牌专用API

```python
from src.rules.special_plate import SpecialPlateRuleFactory

# 创建使馆车牌规则
rule = SpecialPlateRuleFactory.create_rule("embassy")

# 生成使馆车牌
plate_info = rule.generate_plate(
    province="",
    regional_code="",
    special_type="usa"  # 美国使馆
)

# 生成图像
generator = IntegratedPlateGenerator()
plate_image = generator.image_composer.compose_plate_image(plate_info, enhance=True)
```

---

## 车牌类型详解

### 1. 普通汽车号牌

| 类型 | 常量 | 颜色 | 尺寸(mm) | 说明 |
|------|------|------|----------|------|
| 小型汽车 | `ORDINARY_BLUE` | 蓝底白字 | 440×140 | 家用轿车、SUV等 |
| 大型汽车 | `ORDINARY_YELLOW` | 黄底黑字 | 440×140/220 | 货车、客车等 |
| 教练汽车 | `ORDINARY_COACH` | 黄底黑字 | 440×140 | 驾校教练车 |
| 挂车 | `ORDINARY_TRAILER` | 黄底黑字 | 440×220 | 拖挂车辆 |

### 2. 新能源汽车号牌

| 类型 | 常量 | 颜色 | 尺寸(mm) | 说明 |
|------|------|------|----------|------|
| 小型新能源 | `NEW_ENERGY_SMALL` | 渐变绿底黑字 | 480×140 | 新能源轿车、SUV |
| 大型新能源 | `NEW_ENERGY_LARGE` | 黄绿双拼底黑字 | 480×140 | 新能源客车、货车 |

#### 新能源车牌序号规则
- **小型新能源车**：6位序号，第1位为字母（D/F开头）
- **大型新能源车**：6位序号，第6位为字母（D/F结尾）
- **双字母格式**：仅小型车支持，如"DF1234"

### 3. 特殊用途号牌

| 类型 | 常量 | 颜色 | 特殊字符 | 说明 |
|------|------|------|----------|------|
| 警用汽车 | `POLICE_WHITE` | 白底黑字 | 红色"警" | 公安执法车辆 |
| 使馆汽车 | `EMBASSY_BLACK` | 黑底白字 | 红色"使" | 外国使馆车辆 |
| 领馆汽车 | `EMBASSY_BLACK` | 黑底白字 | 红色"领" | 外国领事馆车辆 |
| 港澳入出境 | `HONGKONG_BLACK` | 黑底白字 | "港"/"澳" | 跨境车辆 |
| 军队车牌 | `MILITARY_WHITE` | 白底黑字 | 特殊格式 | 军用车辆 |

---

## 图像增强效果

### 1. 变换效果类型

#### 老化效果 (`aging_effects.py`)
```python
from src.transform.aging_effects import AgingTransform

# 创建老化变换
aging = AgingTransform(
    probability=0.8,           # 应用概率
    dirt_intensity=0.3,        # 污渍强度
    scratch_count=5,           # 划痕数量
    fade_factor=0.15           # 褪色程度
)

# 应用到图像
enhanced_image = aging.apply(original_image)
```

#### 光照效果 (`lighting_effects.py`)
```python
from src.transform.lighting_effects import LightingTransform

# 创建光照变换
lighting = LightingTransform(
    probability=0.6,
    brightness_range=(0.7, 1.3),  # 亮度范围
    contrast_range=(0.8, 1.2),    # 对比度范围
    shadow_intensity=0.2           # 阴影强度
)
```

#### 透视变换 (`perspective_transform.py`)
```python
from src.transform.perspective_transform import PerspectiveTransform

# 创建透视变换
perspective = PerspectiveTransform(
    probability=0.5,
    rotation_range=(-15, 15),     # 旋转角度范围
    perspective_factor=0.1,       # 透视强度
    distortion_level=0.05         # 畸变程度  
)
```

### 2. 组合变换配置

```python
from src.transform.composite_transform import CompositeTransform
from src.transform.transform_config import TransformConfig

# 创建变换配置
config = TransformConfig(
    enable_aging=True,
    enable_lighting=True,
    enable_perspective=True,
    aging_probability=0.4,
    lighting_probability=0.6,
    perspective_probability=0.3
)

# 应用组合变换
composite = CompositeTransform(config)
enhanced_image = composite.apply(original_image)
```

### 3. 自定义变换链

```python
from src.transform.base_transform import BaseTransform

class CustomTransform(BaseTransform):
    def apply(self, image, **kwargs):
        # 自定义变换逻辑
        return processed_image
    
    def get_transform_name(self):
        return "custom_transform"

# 创建变换链
transforms = [
    AgingTransform(probability=0.3),
    LightingTransform(probability=0.5),
    CustomTransform(probability=0.2)
]

# 依次应用变换
result_image = original_image
for transform in transforms:
    if transform.should_apply():
        result_image = transform.apply(result_image)
```

---

## 自定义配置

### 1. 字体配置

```python
from src.generator.font_manager import FontManager

# 自定义字体路径
font_manager = FontManager(
    font_models_dir="custom_fonts",
    enable_font_cache=True
)

# 添加自定义字体
font_manager.add_custom_font("custom_font.ttf", font_size=45)

# 验证字体资源
validation = font_manager.validate_font_resources()
print(f"缺失字符: {validation['missing_chars']}")
```

### 2. 车牌模板配置

```python
from src.generator.image_composer import ImageComposer

# 自定义车牌模板路径
composer = ImageComposer(
    plate_models_dir="custom_templates",
    font_models_dir="font_model"
)

# 添加自定义车牌类型
composer.add_plate_template("custom_blue", "blue_template.png")
```

### 3. 省份和地区代码自定义

```python
from src.rules.province_codes import ProvinceManager
from src.rules.regional_codes import RegionalCodeManager

# 获取省份管理器
province_mgr = ProvinceManager()

# 添加自定义地区代码
province_mgr.add_regional_code("京", "X", "新区域")

# 验证代码有效性
is_valid = province_mgr.is_valid_combination("京", "X")
```

---

## 性能优化

### 1. 内存管理

```python
from src.generator.integrated_generator import IntegratedPlateGenerator

generator = IntegratedPlateGenerator()

# 批量生成时的内存优化
for i in range(10000):
    plate_info, image = generator.generate_plate_with_image()
    
    # 每100次清理缓存
    if i % 100 == 0:
        generator.optimize_memory()

# 完成后清空所有缓存
generator.clear_cache()
```

### 2. 并发生成

```python
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor

def generate_plate_batch(batch_size):
    generator = IntegratedPlateGenerator()
    results = []
    
    for _ in range(batch_size):
        plate_info, image = generator.generate_plate_with_image()
        results.append((plate_info, image))
    
    return results

# 多进程并发生成
with mp.Pool(processes=4) as pool:
    futures = [pool.apply_async(generate_plate_batch, (250,)) for _ in range(4)]
    all_results = [future.get() for future in futures]
```

### 3. 缓存优化

```python
from src.generator.font_manager import FontManager

# 启用字体缓存
font_manager = FontManager(enable_font_cache=True)

# 获取缓存统计
stats = font_manager.get_cache_stats()
print(f"缓存命中率: {stats['hit_rate']:.2%}")
print(f"缓存大小: {stats['cache_size']} MB")

# 预加载常用字符
common_chars = "京沪粤川AB123456789"
font_manager.preload_characters(common_chars)
```

---

## 扩展开发

### 1. 自定义车牌规则

```python
from src.rules.base_rule import BaseRule
from src.generator.plate_generator import PlateInfo

class CustomPlateRule(BaseRule):
    def generate_plate(self, province, regional_code, **kwargs):
        # 自定义生成逻辑
        sequence = self.generate_custom_sequence()
        
        return PlateInfo(
            plate_number=f"{province}{regional_code}{sequence}",
            province=province,
            regional_code=regional_code,
            sequence=sequence,
            plate_type="custom_type",
            background_color="custom_color",
            is_double_layer=False
        )
    
    def generate_custom_sequence(self):
        # 自定义序号生成逻辑
        return "ABC123"
```

### 2. 自定义验证器

```python
from src.validators.base_validator import BaseValidator

class CustomValidator(BaseValidator):
    def validate_plate(self, plate_info):
        errors = []
        
        # 自定义验证逻辑
        if not self.is_valid_custom_format(plate_info.sequence):
            errors.append("序号格式不符合自定义规则")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def is_valid_custom_format(self, sequence):
        # 自定义格式验证
        return True
```

### 3. 插件化扩展

```python
from abc import ABC, abstractmethod

class PlateGeneratorPlugin(ABC):
    @abstractmethod
    def get_plugin_name(self):
        pass
    
    @abstractmethod
    def process_plate(self, plate_info, plate_image):
        pass

class WatermarkPlugin(PlateGeneratorPlugin):
    def get_plugin_name(self):
        return "watermark"
    
    def process_plate(self, plate_info, plate_image):
        # 添加水印逻辑
        return modified_image

# 注册插件
generator = IntegratedPlateGenerator()
generator.register_plugin(WatermarkPlugin())
```

---

## 常见问题解决

### 1. 资源文件缺失
```bash
# 检查字体文件
ls -la font_model/
ls -la plate_model/

# 重新下载资源
git lfs pull
```

### 2. 生成失败问题
```python
try:
    plate_info, image = generator.generate_plate_with_image()
except PlateGenerationError as e:
    print(f"生成失败: {e}")
    # 检查配置和资源
```

### 3. 内存不足
```python
# 降低批量大小
generator.generate_batch_plates_with_images(count=100)  # 替代大批量

# 定期清理缓存  
generator.optimize_memory()
```

---

如需更多技术支持，请参考源码注释或提交Issue。