"""
字体管理器模块

负责车牌字体资源的管理和优化，包括：
1. 字体资源的预加载和缓存
2. 不同车牌尺寸的字体适配
3. 字体图像的预处理和优化
4. 内存使用优化
"""

from typing import Dict, Optional, Tuple, List
import os
import cv2
import numpy as np
from glob import glob
from threading import Lock

from ..utils.constants import DIGITS, LETTERS, PROVINCE_CODES
from ..core.exceptions import PlateGenerationError


class FontCache:
    """
    字体缓存类
    
    Args:
        max_size: 最大缓存大小
    """
    
    def __init__(self, max_size: int = 1000):
        """
        初始化字体缓存
        
        Args:
            max_size: 最大缓存大小
        """
        self.cache: Dict[str, np.ndarray] = {}
        self.access_count: Dict[str, int] = {}
        self.max_size = max_size
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[np.ndarray]:
        """获取缓存的字体图像"""
        with self.lock:
            if key in self.cache:
                self.access_count[key] = self.access_count.get(key, 0) + 1
                return self.cache[key].copy()  # 返回副本避免修改原始数据
            return None
    
    def put(self, key: str, image: np.ndarray) -> None:
        """添加字体图像到缓存"""
        with self.lock:
            if len(self.cache) >= self.max_size:
                self._evict_least_used()
            
            self.cache[key] = image.copy()
            self.access_count[key] = 1
    
    def _evict_least_used(self) -> None:
        """淘汰最少使用的缓存项"""
        if not self.cache:
            return
        
        least_used_key = min(self.access_count.keys(), key=lambda k: self.access_count[k])
        del self.cache[least_used_key]
        del self.access_count[least_used_key]
    
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.access_count.clear()
    
    def get_cache_info(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        with self.lock:
            return {
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'total_access': sum(self.access_count.values())
            }


class FontManager:
    """
    字体管理器
    
    负责车牌字体资源的管理和优化。
    
    Args:
        font_dir: 字体资源目录
        enable_cache: 是否启用缓存
        cache_size: 缓存大小
    """
    
    def __init__(self, font_dir: str, enable_cache: bool = True, cache_size: int = 1000):
        """
        初始化字体管理器
        
        Args:
            font_dir: 字体资源目录
            enable_cache: 是否启用缓存
            cache_size: 缓存大小
        """
        self.font_dir = font_dir
        self.enable_cache = enable_cache
        self.cache = FontCache(cache_size) if enable_cache else None
        
        # 字体文件映射
        self.font_files: Dict[str, str] = {}
        
        # 预定义的字体尺寸配置
        self.font_size_configs = {
            "140": {"width": 45, "height": 90},      # 单层车牌字体
            "220_up": {"width": 65, "height": 110},  # 双层车牌上层
            "220_down": {"width": 65, "height": 110}, # 双层车牌下层
            "green": {"width": 43, "height": 90},    # 新能源车牌字体
        }
        
        # 支持的字符集合
        self.supported_chars = set(DIGITS + LETTERS + PROVINCE_CODES + 
                                 ['使', '领', '港', '澳', '警', '学', '挂'])
        
        # 初始化字体文件映射
        self._initialize_font_mapping()
        
        # 预加载常用字体
        if enable_cache:
            self._preload_common_fonts()
    
    def get_character_image(self, char: str, font_type: str, 
                          target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        获取字符图像
        
        Args:
            char: 字符
            font_type: 字体类型 (140/220_up/220_down/green)
            target_size: 目标尺寸，None表示使用默认尺寸
            
        Returns:
            np.ndarray: 字符图像 (灰度图)
            
        Raises:
            PlateGenerationError: 字符不存在或加载失败
        """
        # 构建缓存键
        cache_key = f"{font_type}_{char}"
        if target_size:
            cache_key += f"_{target_size[0]}x{target_size[1]}"
        
        # 尝试从缓存获取
        if self.enable_cache:
            cached_image = self.cache.get(cache_key)
            if cached_image is not None:
                return cached_image
        
        # 加载字符图像
        char_image = self._load_character_image(char, font_type)
        
        # 调整尺寸
        if target_size:
            char_image = cv2.resize(char_image, target_size)
        else:
            # 使用默认尺寸
            default_size = self._get_default_size(font_type)
            if default_size:
                char_image = cv2.resize(char_image, default_size)
        
        # 应用预处理
        char_image = self._preprocess_character_image(char_image)
        
        # 缓存结果
        if self.enable_cache:
            self.cache.put(cache_key, char_image)
        
        return char_image
    
    def get_font_metrics(self, font_type: str) -> Dict[str, int]:
        """
        获取字体度量信息
        
        Args:
            font_type: 字体类型
            
        Returns:
            Dict: 包含width和height的字典
        """
        return self.font_size_configs.get(font_type, {"width": 45, "height": 90})
    
    def preload_characters(self, chars: List[str], font_types: List[str]) -> None:
        """
        预加载指定字符
        
        Args:
            chars: 字符列表
            font_types: 字体类型列表
        """
        if not self.enable_cache:
            return
        
        for char in chars:
            for font_type in font_types:
                try:
                    self.get_character_image(char, font_type)
                except PlateGenerationError:
                    # 忽略无法加载的字符
                    continue
    
    def get_cache_stats(self) -> Optional[Dict[str, int]]:
        """获取缓存统计信息"""
        if self.cache:
            return self.cache.get_cache_info()
        return None
    
    def clear_cache(self) -> None:
        """清空缓存"""
        if self.cache:
            self.cache.clear()
    
    def _initialize_font_mapping(self) -> None:
        """初始化字体文件映射"""
        if not os.path.exists(self.font_dir):
            raise PlateGenerationError(f"字体目录不存在: {self.font_dir}")
        
        # 扫描所有字体文件
        font_files = glob(os.path.join(self.font_dir, "*.jpg"))
        
        for font_file in font_files:
            filename = os.path.basename(font_file)
            # 解析文件名格式: {prefix}_{char}.jpg
            name_parts = filename.replace('.jpg', '').split('_')
            
            if len(name_parts) >= 2:
                prefix = '_'.join(name_parts[:-1])
                char = name_parts[-1]
                key = f"{prefix}_{char}"
                self.font_files[key] = font_file
    
    def _load_character_image(self, char: str, font_type: str) -> np.ndarray:
        """加载字符图像文件"""
        # 构建文件键
        file_key = f"{font_type}_{char}"
        
        if file_key not in self.font_files:
            raise PlateGenerationError(f"字符图像不存在: {file_key}")
        
        font_path = self.font_files[file_key]
        
        # 使用中文文件名兼容的方式读取
        char_image = cv2.imdecode(np.fromfile(font_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        
        if char_image is None:
            raise PlateGenerationError(f"无法加载字符图像: {font_path}")
        
        return char_image
    
    def _get_default_size(self, font_type: str) -> Optional[Tuple[int, int]]:
        """获取字体类型的默认尺寸"""
        config = self.font_size_configs.get(font_type)
        if config:
            return (config["width"], config["height"])
        return None
    
    def _preprocess_character_image(self, image: np.ndarray) -> np.ndarray:
        """预处理字符图像"""
        # 确保图像为uint8格式
        if image.dtype != np.uint8:
            image = image.astype(np.uint8)
        
        # 应用轻微的去噪
        image = cv2.medianBlur(image, 3)
        
        # 增强对比度
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        image = clahe.apply(image)
        
        return image
    
    def _preload_common_fonts(self) -> None:
        """预加载常用字体"""
        # 常用字符(高频省份简称和字母数字)
        common_chars = ['京', '沪', '粤', '苏', '浙', '鲁', '豫', '川', 'A', 'B', 'C', 'D', 'E', 
                       '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        
        # 常用字体类型
        common_font_types = ['140', 'green']
        
        self.preload_characters(common_chars, common_font_types)
    
    def optimize_memory(self) -> None:
        """优化内存使用"""
        if self.cache:
            # 清理访问次数少的缓存项
            cache_info = self.cache.get_cache_info()
            if cache_info['cache_size'] > cache_info['max_size'] * 0.8:
                # 如果缓存使用率超过80%，清理一半
                with self.cache.lock:
                    sorted_items = sorted(self.cache.access_count.items(), 
                                        key=lambda x: x[1])
                    items_to_remove = len(sorted_items) // 2
                    
                    for key, _ in sorted_items[:items_to_remove]:
                        del self.cache.cache[key]
                        del self.cache.access_count[key]
    
    def validate_font_resources(self) -> Dict[str, List[str]]:
        """
        验证字体资源完整性
        
        Returns:
            Dict: 包含missing_chars和invalid_files的字典
        """
        missing_chars = []
        invalid_files = []
        
        # 检查必需字符是否存在
        required_font_types = ['140', 'green']
        
        for font_type in required_font_types:
            for char in self.supported_chars:
                file_key = f"{font_type}_{char}"
                if file_key not in self.font_files:
                    missing_chars.append(file_key)
                else:
                    # 验证文件是否可读
                    try:
                        self._load_character_image(char, font_type)
                    except PlateGenerationError:
                        invalid_files.append(self.font_files[file_key])
        
        return {
            'missing_chars': missing_chars,
            'invalid_files': invalid_files
        }
    
    def get_supported_characters(self) -> List[str]:
        """获取支持的字符列表"""
        return list(self.supported_chars)
    
    def add_custom_character(self, char: str, font_type: str, image_path: str) -> None:
        """
        添加自定义字符
        
        Args:
            char: 字符
            font_type: 字体类型
            image_path: 图像文件路径
        """
        if not os.path.exists(image_path):
            raise PlateGenerationError(f"自定义字符图像不存在: {image_path}")
        
        file_key = f"{font_type}_{char}"
        self.font_files[file_key] = image_path
        self.supported_chars.add(char)
        
        # 清除相关缓存
        if self.enable_cache:
            keys_to_remove = [key for key in self.cache.cache.keys() if key.startswith(file_key)]
            with self.cache.lock:
                for key in keys_to_remove:
                    if key in self.cache.cache:
                        del self.cache.cache[key]
                        del self.cache.access_count[key]