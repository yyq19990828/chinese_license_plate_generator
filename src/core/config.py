"""
配置管理模块
管理车牌生成器的各种配置参数
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, validator
try:
    from ..utils.constants import (
        GeneratorConstants, 
        FontConstants, 
        PlateConstants,
        ValidationConstants
    )
except ImportError:
    # 当作为独立模块运行时的备选导入
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.constants import (
        GeneratorConstants, 
        FontConstants, 
        PlateConstants,
        ValidationConstants
    )


class GenerationConfig(BaseModel):
    """生成配置"""
    batch_size: int = Field(default=1, ge=1, le=10000, description="批量生成数量")
    allow_duplicates: bool = Field(default=False, description="是否允许重复生成")
    preferred_pattern: Optional[str] = Field(default=None, description="首选序号模式")
    region_preference: Optional[str] = Field(default=None, description="地区偏好")
    energy_type: str = Field(default="pure", description="新能源类型: pure或hybrid")
    max_retry_count: int = Field(default=1000, ge=1, description="最大重试次数")
    generation_timeout: int = Field(default=30, ge=1, description="生成超时时间（秒）")
    
    @validator('energy_type')
    def validate_energy_type(cls, v):
        if v not in ['pure', 'hybrid']:
            raise ValueError("energy_type必须是'pure'或'hybrid'")
        return v


class FontConfig(BaseModel):
    """字体配置"""
    font_directory: str = Field(default="font_model", description="字体目录路径")
    char_spacing: int = Field(default=8, ge=1, description="字符间距")
    province_font_size: int = Field(default=45, ge=20, description="省份简称字体大小")
    code_font_size: int = Field(default=45, ge=20, description="发牌机关代号字体大小")
    sequence_font_size: int = Field(default=45, ge=20, description="序号字体大小")
    special_font_size: int = Field(default=40, ge=20, description="特殊字符字体大小")


class PlateConfig(BaseModel):
    """车牌配置"""
    plate_directory: str = Field(default="plate_model", description="车牌底板目录路径")
    output_directory: str = Field(default="output", description="输出目录路径")
    output_format: str = Field(default="PNG", description="输出图像格式")
    output_quality: int = Field(default=95, ge=1, le=100, description="输出图像质量")
    
    @validator('output_format')
    def validate_output_format(cls, v):
        if v.upper() not in ['PNG', 'JPG', 'JPEG', 'BMP']:
            raise ValueError("output_format必须是PNG、JPG、JPEG或BMP")
        return v.upper()


class ValidationConfig(BaseModel):
    """验证配置"""
    strict_validation: bool = Field(default=True, description="是否启用严格验证")
    allow_forbidden_letters: bool = Field(default=False, description="是否允许禁用字母（仅限测试）")
    custom_forbidden_letters: List[str] = Field(default_factory=list, description="自定义禁用字母列表")
    
    @validator('custom_forbidden_letters')
    def validate_custom_forbidden_letters(cls, v):
        # 确保所有字母都是大写
        return [letter.upper() for letter in v if letter.isalpha()]


class LoggingConfig(BaseModel):
    """日志配置"""
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    max_log_size: int = Field(default=10, ge=1, description="最大日志文件大小（MB）")
    log_backup_count: int = Field(default=5, ge=1, description="日志备份文件数量")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level必须是以下之一: {', '.join(valid_levels)}")
        return v.upper()


class PlateGeneratorConfig(BaseModel):
    """车牌生成器主配置"""
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    font: FontConfig = Field(default_factory=FontConfig)
    plate: PlateConfig = Field(default_factory=PlateConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    class Config:
        """Pydantic配置"""
        extra = "forbid"  # 禁止额外字段
        validate_assignment = True  # 赋值时验证


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认配置
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> PlateGeneratorConfig:
        """
        加载配置
        
        Returns:
            PlateGeneratorConfig: 配置对象
        """
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return PlateGeneratorConfig(**config_data)
            except Exception as e:
                print(f"警告: 加载配置文件失败 ({e})，使用默认配置")
                return PlateGeneratorConfig()
        else:
            return PlateGeneratorConfig()
    
    def save_config(self, config_file: Optional[str] = None) -> None:
        """
        保存配置到文件
        
        Args:
            config_file: 配置文件路径，如果为None则使用初始化时的路径
        """
        file_path = config_file or self.config_file
        if not file_path:
            raise ValueError("未指定配置文件路径")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.config.dict(), f, ensure_ascii=False, indent=2)
    
    def get_generation_config(self) -> GenerationConfig:
        """获取生成配置"""
        return self.config.generation
    
    def get_font_config(self) -> FontConfig:
        """获取字体配置"""
        return self.config.font
    
    def get_plate_config(self) -> PlateConfig:
        """获取车牌配置"""
        return self.config.plate
    
    def get_validation_config(self) -> ValidationConfig:
        """获取验证配置"""
        return self.config.validation
    
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        return self.config.logging
    
    def update_config(self, **kwargs) -> None:
        """
        更新配置
        
        Args:
            **kwargs: 配置更新字典，支持嵌套更新
        """
        config_dict = self.config.dict()
        self._deep_update(config_dict, kwargs)
        self.config = PlateGeneratorConfig(**config_dict)
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """
        深度更新字典
        
        Args:
            base_dict: 基础字典
            update_dict: 更新字典
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def reset_to_default(self) -> None:
        """重置为默认配置"""
        self.config = PlateGeneratorConfig()
    
    def validate_paths(self) -> List[str]:
        """
        验证配置中的路径是否存在
        
        Returns:
            List[str]: 不存在的路径列表
        """
        missing_paths = []
        
        # 检查字体目录
        if not os.path.exists(self.config.font.font_directory):
            missing_paths.append(self.config.font.font_directory)
        
        # 检查车牌底板目录
        if not os.path.exists(self.config.plate.plate_directory):
            missing_paths.append(self.config.plate.plate_directory)
        
        return missing_paths
    
    def create_output_directories(self) -> None:
        """创建输出目录"""
        output_dir = self.config.plate.output_directory
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建日志目录（如果指定了日志文件）
        if self.config.logging.log_file:
            log_dir = os.path.dirname(self.config.logging.log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
    
    def get_font_path(self, char: str, font_type: str = "140") -> str:
        """
        获取字符对应的字体文件路径
        
        Args:
            char: 字符
            font_type: 字体类型（如"140", "220", "green"等）
            
        Returns:
            str: 字体文件路径
        """
        font_dir = self.config.font.font_directory
        
        # 特殊字符映射
        if char in PlateConstants.SPECIAL_CHARS.values():
            filename = f"{font_type}_{char}.jpg"
        elif char.isalpha():
            filename = f"{font_type}_{char.upper()}.jpg"
        elif char.isdigit():
            filename = f"{font_type}_{char}.jpg"
        else:
            raise ValueError(f"不支持的字符: {char}")
        
        return os.path.join(font_dir, filename)
    
    def get_plate_background_path(self, plate_type: str) -> str:
        """
        获取车牌背景图片路径
        
        Args:
            plate_type: 车牌类型
            
        Returns:
            str: 背景图片路径
        """
        plate_dir = self.config.plate.plate_directory
        
        # 车牌类型与背景文件映射
        background_mapping = {
            "blue": "blue_140.PNG",
            "yellow": "yellow_140.PNG",
            "white": "white_140.PNG",
            "black": "black_140.PNG",
            "green": "green_car_140.PNG",
            "yellow_green": "green_truck_140.PNG",
        }
        
        background_file = background_mapping.get(plate_type, "blue_140.PNG")
        return os.path.join(plate_dir, background_file)


# 全局配置实例
_global_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """
    获取全局配置管理器实例
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        ConfigManager: 配置管理器实例
    """
    global _global_config_manager
    
    if _global_config_manager is None or config_file:
        _global_config_manager = ConfigManager(config_file)
    
    return _global_config_manager


def load_config_from_env() -> Dict[str, Any]:
    """
    从环境变量加载配置
    
    Returns:
        Dict[str, Any]: 配置字典
    """
    config = {}
    
    # 生成配置
    if batch_size := os.getenv('PLATE_BATCH_SIZE'):
        config.setdefault('generation', {})['batch_size'] = int(batch_size)
    
    if allow_duplicates := os.getenv('PLATE_ALLOW_DUPLICATES'):
        config.setdefault('generation', {})['allow_duplicates'] = allow_duplicates.lower() == 'true'
    
    # 字体配置
    if font_dir := os.getenv('PLATE_FONT_DIR'):
        config.setdefault('font', {})['font_directory'] = font_dir
    
    # 车牌配置
    if plate_dir := os.getenv('PLATE_MODEL_DIR'):
        config.setdefault('plate', {})['plate_directory'] = plate_dir
    
    if output_dir := os.getenv('PLATE_OUTPUT_DIR'):
        config.setdefault('plate', {})['output_directory'] = output_dir
    
    # 日志配置
    if log_level := os.getenv('PLATE_LOG_LEVEL'):
        config.setdefault('logging', {})['log_level'] = log_level
    
    if log_file := os.getenv('PLATE_LOG_FILE'):
        config.setdefault('logging', {})['log_file'] = log_file
    
    return config