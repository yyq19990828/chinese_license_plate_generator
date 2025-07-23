# 中国车牌模拟生成器

一个基于 Python 的中国机动车号牌生成工具，严格按照 **GA 36-2018** 标准实现。本项目采用模块化的规则引擎，支持所有类型的车牌号码和样式，适用于数据增强、机器学习训练数据生成、车辆识别系统测试等场景。

## ✨ 特性

- 严格遵循 **GA 36-2018** 标准，确保生成规则的准确性。
- **全面的车牌类型支持**：覆盖普通汽车、新能源、警车、军队、港澳、使领馆等所有主流车牌。
- **模块化规则引擎**：所有车牌的编码规则、样式、颜色均在独立的规则类中定义，易于维护和扩展。
- **高质量图像合成**：支持基于标准字体和尺寸生成高度真实的车牌图像（图像合成功能待集成）。
- **灵活的生成方式**：
  - **随机生成**：一键生成符合真实世界分布的随机车牌。
  - **配置生成**：可指定省份、地区、车牌类型等参数。
  - **指定生成**：根据输入的车牌号码生成对应的车牌信息。
- **完善的验证机制**：内置验证器，可检查车牌号码的格式、编码规则、地区代号的有效性。

## 📦 安装要求

```bash
python >= 3.8
pydantic >= 1.8
```

### 安装依赖

```bash
pip install -r requirements.txt  # (如果提供了 requirements.txt)
# 或者手动安装
pip install pydantic
```

## 🎯 使用方法

本项目核心为 `src.generator.plate_generator.PlateGenerator` 类。

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

## 📁 项目结构

```
chinese_license_plate_generator/
├── src/
│   ├── core/          # 核心模块 (配置, 异常)
│   ├── generator/     # 车牌生成器模块
│   ├── rules/         # 车牌编码规则模块
│   └── validators/    # 验证器模块
├── tests/             # 单元测试和集成测试
│   ├── test_generator/
│   ├── test_rules/
│   └── test_validators/
├── font_model/        # 字体资源
├── plate_model/       # 车牌底板资源
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
```

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
- [ ] **车牌老化效果** (磨损、褪色等真实效果)
- [ ] **不同拍摄角度** (倾斜、透视变换等)
- [ ] **光照条件模拟** (阴影、反光、夜间等)
- [ ] **背景环境生成** (街道、停车场等真实场景)

### 开发优先级建议

1. **高优先级**: 摩托车号牌（使用量大，格式相对简单）
2. **中优先级**: 特殊字符车牌（"试"、"超"字车牌）
3. **低优先级**: 临时号牌和特殊尺寸（使用频率相对较低）

---

*本项目仅供学习研究使用，请勿用于违法违规用途*

