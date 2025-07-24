# 中国车牌模拟生成器

一个基于 Python 的中国机动车号牌生成工具，严格按照 **GA 36-2018** 标准实现。本项目采用模块化的规则引擎，支持所有类型的车牌号码和样式，适用于数据增强、机器学习训练数据生成、车辆识别系统测试等场景。

## ✨ 特性

- 严格遵循 **GA 36-2018** 标准，确保生成规则的准确性。
- **全面的车牌类型支持**：覆盖普通汽车、新能源、警车、军队、港澳、使领馆等所有主流车牌。
- **模块化规则引擎**：所有车牌的编码规则、样式、颜色均在独立的规则类中定义，易于维护和扩展。
- **高质量图像合成**：支持基于标准字体和尺寸生成高度真实的车牌图像。
- **智能增强变换系统**：内置车牌老化效果、透视变换、光照模拟等真实场景效果，支持可配置概率（默认0.3）。
- **灵活的生成方式**：
  - **随机生成**：一键生成符合真实世界分布的随机车牌。
  - **配置生成**：可指定省份、地区、车牌类型等参数。
  - **指定生成**：根据输入的车牌号码生成对应的车牌信息。
- **完善的验证机制**：内置验证器，可检查车牌号码的格式、编码规则、地区代号的有效性。

## 📦 安装要求

```bash
python >= 3.8
pydantic >= 1.8
opencv-python >= 4.0
pillow >= 8.0
numpy >= 1.20
```

### 安装依赖

```bash
pip install -r requirements.txt  # (如果提供了 requirements.txt)
# 或者手动安装
pip install pydantic opencv-python pillow numpy
```

## 🎯 使用方法

本项目提供两个主要生成器：
- `src.generator.plate_generator.PlateGenerator` - 车牌号码生成器
- `src.generator.integrated_generator.IntegratedPlateGenerator` - 集成图像生成器（包含增强变换）

### 1. 随机生成车牌

```python
from src.generator.plate_generator import PlateGenerator

# 1. 初始化生成器
generator = PlateGenerator()

# 2. 生成一个完全随机的车牌
plate_info = generator.generate_random_plate()

print(f"生成的车牌号码: {plate_info.plate_number}")
print(f"车牌类型: {plate_info.plate_type}")
print(f"背景颜色: {plate_info.background_color}")
```

### 2. 按配置生成车牌

可以指定省份、地区、车牌类型等。

```python
from src.generator.plate_generator import PlateGenerator, PlateGenerationConfig
from src.utils.constants import PlateType

generator = PlateGenerator()

# 生成一个蓝色的广东省深圳市车牌
config = PlateGenerationConfig(
    plate_type=PlateType.ORDINARY_BLUE,
    province="粤",
    regional_code="B"
)
plate_info = generator.generate_random_plate(config)
print(f"广东深圳蓝牌: {plate_info.plate_number}")

# 生成一个警车车牌
config = PlateGenerationConfig(plate_type=PlateType.POLICE_WHITE)
plate_info = generator.generate_random_plate(config)
print(f"警车车牌: {plate_info.plate_number}")
```

### 3. 生成指定号码的车牌

```python
from src.generator.plate_generator import PlateGenerator

generator = PlateGenerator()

plate_number = "沪AD12345"
plate_info = generator.generate_specific_plate(plate_number)

print(f"车牌号码: {plate_info.plate_number}")
print(f"分析出的类型: {plate_info.plate_type}")
print(f"序号: {plate_info.sequence}")
```

### 4. 批量生成

```python
from src.generator.plate_generator import PlateGenerator

generator = PlateGenerator()

plates = generator.generate_batch_plates(10)
for info in plates:
    print(info.plate_number)
```

### 5. 图像生成和增强变换

```python
from src.generator.integrated_generator import IntegratedPlateGenerator
import cv2

# 初始化集成生成器
generator = IntegratedPlateGenerator()

# 生成普通车牌图像
plate_info, normal_image = generator.generate_plate_with_image(enhance=False)
print(f"生成车牌: {plate_info.plate_number}")

# 生成增强效果车牌图像（包含老化、透视、光照等真实效果）
plate_info, enhanced_image = generator.generate_plate_with_image(enhance=True)
print(f"增强车牌: {plate_info.plate_number}")

# 保存图像
cv2.imwrite(f"normal_{plate_info.plate_number}.jpg", normal_image)
cv2.imwrite(f"enhanced_{plate_info.plate_number}.jpg", enhanced_image)
```

### 6. 独立使用变换效果

```python
from src.transform import WearEffect, quick_enhance, CompositeTransform
from PIL import Image

# 加载车牌图像
plate_image = Image.open("your_plate.jpg")

# 方法1: 使用单个效果
wear_effect = WearEffect(probability=1.0)
worn_image = wear_effect.apply(plate_image, intensity=0.7)

# 方法2: 使用快速增强
enhanced_image, applied_transforms = quick_enhance(
    plate_image, 
    intensity="medium",  # "light", "medium", "heavy"
    style="balanced"     # "aging", "perspective", "lighting", "balanced"
)
print(f"应用的变换: {applied_transforms}")

# 方法3: 使用复合变换管理器
transformer = CompositeTransform()
result_image, transforms = transformer.apply(
    plate_image,
    max_transforms=3,
    intensity_scale=0.8
)
print(f"应用了 {len(transforms)} 种变换效果")
```

### 7. 自定义变换配置

```python
from src.transform import TransformConfig, CompositeTransform
from src.generator.integrated_generator import IntegratedPlateGenerator

# 创建自定义变换配置
config = TransformConfig()
config.set_global_probability(0.5)  # 提高变换概率到50%
config.update_transform_probability('wear_effect', 0.8)  # 磨损效果80%概率
config.disable_transform('night_effect')  # 禁用夜间效果

# 使用自定义配置的生成器
generator = IntegratedPlateGenerator(transform_config=config)
plate_info, image = generator.generate_plate_with_image(enhance=True)
```

## 📁 项目结构

```
chinese_license_plate_generator/
├── src/
│   ├── core/          # 核心模块 (配置, 异常)
│   ├── generator/     # 车牌生成器模块
│   ├── rules/         # 车牌编码规则模块
│   ├── transform/     # 图像增强变换模块
│   ├── utils/         # 工具模块
│   └── validators/    # 验证器模块
├── tests/             # 单元测试和集成测试
│   ├── test_generator/
│   ├── test_rules/
│   ├── test_transform/
│   └── test_validators/
├── font_model/        # 字体资源
├── plate_model/       # 车牌底板资源
├── demo_transform_effects.py     # 变换效果演示脚本
├── performance_test_transform.py # 性能测试脚本
├── CLAUDE.md          # AI 协作指南
├── PLANNING.md        # 项目规划
├── TASK.md            # 任务跟踪
└── README.md
```

## 🧪 运行测试

本项目包含一套完整的单元测试和集成测试，以确保代码质量和规则的准确性。

```bash
# 安装测试依赖
pip install pytest

# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_transform/  # 测试变换效果
pytest tests/test_rules/      # 测试编码规则
pytest tests/test_generator/  # 测试生成器
```

## 🎨 演示和工具

### 变换效果演示

运行演示脚本查看各种增强变换效果：

```bash
# 演示所有效果类型
python demo_transform_effects.py

# 演示特定效果
python demo_transform_effects.py --effects aging perspective lighting

# 指定输出目录
python demo_transform_effects.py --output my_demo_results
```

### 性能测试

运行性能测试评估系统性能：

```bash
python performance_test_transform.py
```

性能测试包括：
- 单个变换效果性能测试
- 不同图像尺寸缩放性能
- 复合变换性能测试  
- 内存使用监控
- 并发处理性能

## 🔧 变换系统技术细节

### 支持的变换效果

#### 🎯 老化效果 (Aging Effects)
- **磨损效果** (WearEffect): 模拟车牌边缘磨损和字符模糊
- **褪色效果** (FadeEffect): 模拟长期日晒导致的颜色褪色  
- **污渍效果** (DirtEffect): 模拟表面灰尘、泥点等污渍

#### 📐 透视变换 (Perspective Transform)
- **倾斜变换** (TiltTransform): 模拟不同水平/垂直倾斜角度
- **透视变换** (PerspectiveTransform): 模拟不同视角的透视效果
- **旋转变换** (RotationTransform): 模拟小角度旋转
- **几何扭曲** (GeometricDistortion): 模拟网格变形

#### 💡 光照效果 (Lighting Effects)  
- **阴影效果** (ShadowEffect): 模拟投影和遮挡阴影
- **反光效果** (ReflectionEffect): 模拟镜面反射和局部高光
- **夜间效果** (NightEffect): 模拟低光照和颜色偏移
- **背光效果** (BacklightEffect): 模拟逆光和轮廓强化

### 配置参数

```python
# 变换配置示例
config = TransformConfig()

# 全局设置
config.set_global_probability(0.3)          # 全局应用概率
config.set_max_concurrent_transforms(3)     # 最大并发变换数

# 单个效果设置
config.update_transform_probability('wear_effect', 0.5)  # 设置特定效果概率
config.enable_transform('fade_effect')       # 启用效果
config.disable_transform('night_effect')     # 禁用效果

# 按类型控制
from src.transform import TransformType
config.disable_transform_type(TransformType.LIGHTING)  # 禁用所有光照效果
```

### 性能指标

基于标准440×140像素车牌图像的性能测试结果：

| 效果类型 | 平均处理时间 | 吞吐量 | 内存占用 |
|---------|-------------|-------|---------|
| 单个老化效果 | ~3.7ms | 270 图像/秒 | <5MB |
| 单个透视变换 | ~5.2ms | 190 图像/秒 | <8MB |
| 单个光照效果 | ~4.1ms | 240 图像/秒 | <6MB |
| 复合变换(3个) | ~12ms | 83 图像/秒 | <15MB |
| 完整生成+增强 | ~10ms | 100 车牌/秒 | <20MB |

## 🤝 贡献

欢迎通过提交 Issue 和 Pull Request 来改进本项目。在提交代码前，请确保所有测试都能通过。

## 📄 许可证

本项目基于开源许可证发布，详见 [LICENSE](LICENSE) 文件。

## 📋 TODO 清单

### 目前暂时无法生成的车牌类型

根据 [GA 36-2018标准](plate_rules.md) 对比分析，以下车牌类型当前项目尚未支持：

#### 🛵 摩托车号牌
- [ ] **普通摩托车号牌** (220×140mm, 黄底黑字)
- [ ] **轻便摩托车号牌** (220×140mm, 蓝底白字)
- [ ] **使馆摩托车号牌** (220×140mm, 黑底白字+红"使"字)
- [ ] **领馆摩托车号牌** (220×140mm, 黑底白字+红"领"字)
- [ ] **教练摩托车号牌** (220×140mm, 黄底黑字)
- [ ] **警用摩托车号牌** (220×140mm, 白底黑字+红"警"字)

#### 🚜 特殊车辆号牌
- [ ] **低速车号牌** (300×165mm, 黄底黑字)
- [ ] **临时行驶车号牌** (220×140mm, 天蓝底纹黑字/棕黄底纹黑字)
- [ ] **临时入境汽车号牌** (220×140mm, 白底棕蓝纹黑字)
- [ ] **临时入境摩托车号牌** (88×60mm, 白底棕蓝纹黑字)

#### 🔤 特殊字符车牌
- [ ] **"试"字车牌** (试验用临时行驶车)
- [ ] **"超"字车牌** (特型车临时行驶车)

#### 🎨 特殊颜色和格式
- [ ] **军用车牌完整支持** (当前仅部分支持)
- [ ] **武警车牌** (WJ开头的完整格式)
- [ ] **领馆车牌红色"领"字** (当前"领"字为黑色)
- [ ] **使馆车牌红色"使"字** (当前"使"字为黑色)

#### 📐 特殊尺寸规格
- [ ] **300×165mm 低速车尺寸**
- [ ] **88×60mm 临时入境摩托车尺寸**
- [ ] **220×140mm 各类摩托车尺寸**

#### 🚀 增强功能
- [x] **车牌老化效果** (磨损、褪色等真实效果) ✅ 已完成
- [x] **不同拍摄角度** (倾斜、透视变换等) ✅ 已完成  
- [x] **光照条件模拟** (阴影、反光、夜间等) ✅ 已完成
- [ ] **背景环境生成** (街道、停车场等真实场景)

### 开发优先级建议

1. **高优先级**: 摩托车号牌（使用量大，格式相对简单）
2. **中优先级**: 特殊字符车牌（"试"、"超"字车牌）
3. **低优先级**: 临时号牌和特殊尺寸（使用频率相对较低）

---

*本项目仅供学习研究使用，请勿用于违法违规用途*

