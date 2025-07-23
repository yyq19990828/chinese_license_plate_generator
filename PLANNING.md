# 项目规划：中国车牌生成器 (chinese_license_plate_generator)

## 1. 项目目标

基于 GA 36-2018 标准，开发一个严格遵循中国机动车号牌编码规则的车牌生成器。该项目旨在提供：
- 准确的车牌号码生成，完全符合国家标准
- 支持所有车牌类型（普通汽车、新能源、特殊用途等）
- 模块化的车牌规则系统，便于维护和扩展
- 高质量的车牌图像生成

## 2. 技术架构

### 2.1. 目录结构
```
src/
├── rules/                  # 车牌编码规则模块
│   ├── __init__.py
│   ├── base_rule.py       # 基础规则类
│   ├── province_codes.py  # 省份代码管理
│   ├── regional_codes.py  # 发牌机关代号管理
│   ├── ordinary_plate.py  # 普通汽车号牌规则
│   ├── new_energy_plate.py # 新能源汽车号牌规则
│   ├── special_plate.py   # 特殊车牌规则(使、领、警、港澳等)
│   └── sequence_generator.py # 序号生成器
├── generator/             # 车牌生成器模块
│   ├── __init__.py
│   ├── plate_generator.py # 主生成器
│   ├── image_composer.py  # 图像合成器
│   └── font_manager.py    # 字体管理器
├── validators/            # 验证器模块
│   ├── __init__.py
│   ├── plate_validator.py # 车牌号码验证器
│   └── rule_validator.py  # 规则验证器
├── utils/                 # 工具模块
│   ├── __init__.py
│   ├── constants.py       # 常量定义
│   └── helpers.py         # 辅助函数
└── core/                  # 核心模块
    ├── __init__.py
    ├── config.py          # 配置管理
    └── exceptions.py      # 异常定义

tests/                     # 测试模块
├── test_rules/
├── test_generator/
├── test_validators/
└── fixtures/

font_model/                # 字体资源(保持现有)
plate_model/               # 车牌底板资源(保持现有)
```

### 2.2. 核心组件

#### 2.2.1. 车牌规则系统 (rules/)
- **BaseRule**: 所有车牌规则的基类，定义通用接口
- **ProvinceManager**: 管理31个省份的简称和编码
- **RegionalCodeManager**: 管理各地级市发牌机关代号
- **SequenceGenerator**: 按照启用顺序生成序号
- **专用规则类**: 每种车牌类型独立的规则实现

#### 2.2.2. 车牌生成器 (generator/)
- **PlateGenerator**: 主生成器，协调各个组件
- **ImageComposer**: 负责车牌图像合成
- **FontManager**: 管理字体资源和渲染

#### 2.2.3. 验证系统 (validators/)
- **PlateValidator**: 验证生成的车牌号码是否符合规则
- **RuleValidator**: 验证规则配置的正确性

## 3. 编码风格与约束

### 3.1. Python 编码规范
- 遵循 PEP8 标准
- 使用 type hints 进行类型注解
- 使用 pydantic 进行数据验证
- 每个函数必须包含 Google 风格的 docstring

### 3.2. 模块化原则
- 单个文件不超过 500 行代码
- 功能明确的类和函数分离
- 使用依赖注入提高可测试性
- 配置与逻辑分离

### 3.3. 数据结构规范
```python
from pydantic import BaseModel
from typing import List, Optional

class PlateInfo(BaseModel):
    """车牌信息数据结构"""
    plate_number: str
    plate_type: str
    province: str
    regional_code: str
    sequence: str
    background_color: str
    is_double_layer: bool
    special_chars: Optional[List[str]] = None
```

## 4. 约束条件

### 4.1. 技术约束
- Python 3.8+ 兼容性
- 严格按照 GA 36-2018 标准实现
- 不使用 I、O 字母（按标准要求）
- 支持所有31个省份及其发牌机关代号

### 4.2. 业务约束
- 生成的车牌号码必须符合真实编码规则
- 序号生成按照启用顺序进行
- 新能源车牌严格区分纯电动和非纯电动
- 特殊车牌（警、使、领等）按规定格式生成

### 4.3. 性能约束
- 单次车牌生成时间 < 100ms
- 支持批量生成（1000+车牌）
- 内存使用优化，避免字体资源重复加载

## 5. 自动化工具与命令

### 5.1. 开发环境
```bash
# 虚拟环境
python -m venv venv_linux
source venv_linux/bin/activate

# 依赖安装
pip install -r requirements.txt

# 代码格式化
black src/ tests/
flake8 src/ tests/

# 类型检查
mypy src/
```

### 5.2. 测试命令
```bash
# 运行所有测试
pytest tests/ -v

# 测试覆盖率
pytest --cov=src tests/

# 特定模块测试
pytest tests/test_rules/ -v
```

### 5.3. 车牌生成命令
```bash
# 生成普通车牌
python -m src.generator --type ordinary --count 100

# 生成新能源车牌
python -m src.generator --type new_energy --count 50

# 生成特定省份车牌
python -m src.generator --province 京 --count 20
```

## 6. 重构策略

### 6.1. 现有代码分析
当前项目存在以下问题：
1. 车牌规则硬编码在生成函数中
2. 缺乏对 GA 36-2018 标准的完整支持
3. 发牌机关代号不完整
4. 序号生成不按标准启用顺序

### 6.2. 重构步骤
1. **规则提取**: 将硬编码规则提取到独立的规则类
2. **数据标准化**: 基于 plate_rules.md 创建完整的省份和地区编码
3. **接口统一**: 创建统一的车牌生成接口
4. **测试完善**: 为每个规则类编写完整测试
5. **向后兼容**: 保持现有接口可用性

### 6.3. 迁移计划
- **第一阶段**: 创建新的规则系统，与现有代码并行
- **第二阶段**: 重构车牌生成器使用新规则
- **第三阶段**: 移除旧代码，完成迁移

## 7. 质量保证

### 7.1. 单元测试覆盖率要求
- 规则类测试覆盖率 > 95%
- 生成器测试覆盖率 > 90%
- 验证器测试覆盖率 > 95%

### 7.2. 集成测试
- 验证所有车牌类型的生成正确性
- 验证生成的车牌号码符合标准
- 性能测试确保生成效率

### 7.3. 文档要求
- API 文档自动生成
- 使用示例完整
- 规则变更记录

---

该规划基于严格的国家标准 GA 36-2018，确保生成的车牌号码完全符合实际编码规则。通过模块化设计，使系统具有良好的可维护性和扩展性。