"""
异常定义模块
定义车牌生成和验证过程中的各种异常类
"""

from typing import Optional, List, Any


class PlateGeneratorException(Exception):
    """车牌生成器基础异常类"""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """
        初始化异常
        
        Args:
            message: 异常信息
            details: 异常详细信息字典
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class InvalidProvinceException(PlateGeneratorException):
    """无效省份异常"""
    
    def __init__(self, province: str):
        message = f"无效的省份简称: '{province}'"
        details = {
            "invalid_province": province,
            "valid_provinces": "请使用有效的省份简称，如：京、津、冀等"
        }
        super().__init__(message, details)


class InvalidRegionalCodeException(PlateGeneratorException):
    """无效发牌机关代号异常"""
    
    def __init__(self, province: str, regional_code: str, valid_codes: Optional[List[str]] = None):
        message = f"省份 '{province}' 不存在发牌机关代号 '{regional_code}'"
        details = {
            "province": province,
            "invalid_code": regional_code,
            "valid_codes": valid_codes or []
        }
        super().__init__(message, details)


class InvalidSequenceException(PlateGeneratorException):
    """无效序号异常"""
    
    def __init__(self, sequence: str, reason: str, expected_pattern: Optional[str] = None):
        message = f"无效的序号 '{sequence}': {reason}"
        details = {
            "invalid_sequence": sequence,
            "reason": reason,
            "expected_pattern": expected_pattern
        }
        super().__init__(message, details)


class ForbiddenLetterException(PlateGeneratorException):
    """禁用字母异常"""
    
    def __init__(self, sequence: str, forbidden_letters: List[str]):
        message = f"序号 '{sequence}' 包含禁用字母: {', '.join(forbidden_letters)}"
        details = {
            "sequence": sequence,
            "forbidden_letters": forbidden_letters,
            "note": "根据GA 36-2018标准，车牌序号不能包含字母I和O"
        }
        super().__init__(message, details)


class InvalidPlateFormatException(PlateGeneratorException):
    """无效车牌格式异常"""
    
    def __init__(self, plate_number: str, expected_format: str):
        message = f"车牌号码 '{plate_number}' 格式不正确，期望格式: {expected_format}"
        details = {
            "invalid_plate": plate_number,
            "expected_format": expected_format
        }
        super().__init__(message, details)


class SequencePatternException(PlateGeneratorException):
    """序号模式异常"""
    
    def __init__(self, pattern: str, reason: str):
        message = f"序号模式 '{pattern}' 无效: {reason}"
        details = {
            "invalid_pattern": pattern,
            "reason": reason
        }
        super().__init__(message, details)

class SequenceGenerationError(PlateGeneratorException):
    """序号生成异常"""
    
    def __init__(self, message: str, sequence_type: Optional[str] = None, details: Optional[dict] = None):
        """
        初始化序号生成异常
        
        Args:
            message: 异常信息
            sequence_type: 序号类型
            details: 异常详细信息字典
        """
        full_message = message
        if sequence_type:
            full_message = f"序号生成失败 ({sequence_type}): {message}"
        
        exception_details = {
            "sequence_type": sequence_type,
        }
        if details:
            exception_details.update(details)
            
        super().__init__(full_message, exception_details)


class ResourceExhaustedException(PlateGeneratorException):
    """资源耗尽异常"""
    
    def __init__(self, resource_type: str, details_info: Optional[dict] = None):
        message = f"资源已耗尽: {resource_type}"
        details = {
            "resource_type": resource_type,
            "suggestion": "请尝试其他序号模式或地区代号"
        }
        if details_info:
            details.update(details_info)
        super().__init__(message, details)


class GenerationTimeoutException(PlateGeneratorException):
    """生成超时异常"""
    
    def __init__(self, timeout_seconds: int, operation: str):
        message = f"操作 '{operation}' 超时 ({timeout_seconds}秒)"
        details = {
            "operation": operation,
            "timeout_seconds": timeout_seconds,
            "suggestion": "请减少批量生成数量或检查系统性能"
        }
        super().__init__(message, details)


class ConfigurationException(PlateGeneratorException):
    """配置异常"""
    
    def __init__(self, config_key: str, config_value: Any, reason: str):
        message = f"配置项 '{config_key}' 的值 '{config_value}' 无效: {reason}"
        details = {
            "config_key": config_key,
            "config_value": config_value,
            "reason": reason
        }
        super().__init__(message, details)


class FontResourceException(PlateGeneratorException):
    """字体资源异常"""
    
    def __init__(self, font_path: str, reason: str):
        message = f"字体资源 '{font_path}' 加载失败: {reason}"
        details = {
            "font_path": font_path,
            "reason": reason,
            "suggestion": "请检查字体文件是否存在且格式正确"
        }
        super().__init__(message, details)


class PlateImageException(PlateGeneratorException):
    """车牌图像异常"""
    
    def __init__(self, operation: str, reason: str):
        message = f"车牌图像操作 '{operation}' 失败: {reason}"
        details = {
            "operation": operation,
            "reason": reason
        }
        super().__init__(message, details)


class ValidationException(PlateGeneratorException):
    """验证异常"""
    
    def __init__(self, validation_type: str, value: str, errors: List[str]):
        message = f"{validation_type} 验证失败: '{value}'"
        details = {
            "validation_type": validation_type,
            "invalid_value": value,
            "errors": errors
        }
        super().__init__(message, details)


class DataIntegrityException(PlateGeneratorException):
    """数据完整性异常"""
    
    def __init__(self, data_type: str, missing_items: List[str]):
        message = f"{data_type} 数据不完整，缺少: {', '.join(missing_items)}"
        details = {
            "data_type": data_type,
            "missing_items": missing_items,
            "suggestion": "请检查数据文件是否完整"
        }
        super().__init__(message, details)


class BatchGenerationException(PlateGeneratorException):
    """批量生成异常"""
    
    def __init__(self, batch_size: int, successful_count: int, failed_items: List[dict]):
        message = f"批量生成部分失败: 请求{batch_size}个，成功{successful_count}个，失败{len(failed_items)}个"
        details = {
            "batch_size": batch_size,
            "successful_count": successful_count,
            "failed_count": len(failed_items),
            "failed_items": failed_items
        }
        super().__init__(message, details)


class PlateTypeException(PlateGeneratorException):
    """车牌类型异常"""
    
    def __init__(self, plate_type: str, reason: str):
        message = f"车牌类型 '{plate_type}' 处理失败: {reason}"
        details = {
            "plate_type": plate_type,
            "reason": reason
        }
        super().__init__(message, details)


class PlateGenerationError(PlateGeneratorException):
    """车牌生成错误异常"""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """
        初始化车牌生成错误异常
        
        Args:
            message: 异常信息
            details: 异常详细信息字典
        """
        super().__init__(message, details)


# 异常处理工具函数
def format_exception_message(exception: PlateGeneratorException) -> str:
    """
    格式化异常消息
    
    Args:
        exception: 车牌生成器异常实例
        
    Returns:
        str: 格式化的异常消息
    """
    message = f"错误: {exception.message}"
    
    if exception.details:
        details_str = []
        for key, value in exception.details.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            details_str.append(f"{key}: {value}")
        
        if details_str:
            message += f"\n详细信息: {'; '.join(details_str)}"
    
    return message


def get_exception_suggestion(exception: PlateGeneratorException) -> Optional[str]:
    """
    获取异常的建议解决方案
    
    Args:
        exception: 车牌生成器异常实例
        
    Returns:
        Optional[str]: 建议解决方案，如果没有则返回None
    """
    if exception.details and "suggestion" in exception.details:
        return exception.details["suggestion"]
    return None