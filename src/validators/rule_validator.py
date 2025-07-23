from typing import Dict, Any, List

from src.core.exceptions import RuleError


class RuleValidator:
    """
    规则验证器
    
    用于验证车牌生成规则的配置和数据完整性。
    确保规则定义文件本身是正确和一致的。
    """

    def __init__(self, rule: Dict[str, Any]):
        """
        初始化验证器。

        Args:
            rule (Dict[str, Any]): 待验证的规则配置。
        """
        self.rule = rule

    def validate(self) -> bool:
        """
        执行所有验证。

        Returns:
            bool: 如果规则有效，则返回 True。
        
        Raises:
            RuleError: 如果验证失败。
        """
        self.validate_completeness()
        self.validate_structure()
        self.validate_consistency()
        return True

    def validate_completeness(self) -> bool:
        """
        验证规则的完整性，检查是否包含所有必需的顶级字段。

        Returns:
            bool: 如果规则完整，则返回 True。
        
        Raises:
            RuleError: 如果规则不完整。
        """
        required_keys = ['type', 'description', 'structure']
        for key in required_keys:
            if key not in self.rule:
                raise RuleError(f"规则缺少必需的顶级字段: {key}")

        if not isinstance(self.rule.get('structure'), list):
            raise RuleError("'structure' 字段必须是一个列表")
            
        return True

    def validate_structure(self) -> bool:
        """
        验证 'structure' 字段内部的每个条目是否符合规范。

        Returns:
            bool: 如果结构有效，则返回 True。

        Raises:
            RuleError: 如果结构中的条目无效。
        """
        for item in self.rule['structure']:
            if not isinstance(item, dict):
                raise RuleError("'structure' 中的每个条目都必须是字典")
            
            required_keys = ['name', 'length', 'type', 'options']
            for key in required_keys:
                if key not in item:
                    raise RuleError(f"'structure' 条目缺少必需字段: {key}")
        return True

    def validate_consistency(self) -> bool:
        """
        验证规则的内部一致性。

        - 例如，'length' 字段是否与 'options' 的内容相符。

        Returns:
            bool: 如果规则一致，则返回 True。
        
        Raises:
            RuleError: 如果规则不一致。
        """
        total_length = 0
        for item in self.rule['structure']:
            total_length += item['length']
            
            # 示例：如果类型是 'fixed', 'options' 列表的长度应为1
            if item['type'] == 'fixed' and len(item['options']) != 1:
                raise RuleError(f"名为 '{item['name']}' 的 'fixed' 类型条目应只有一个 'option'")

            # 示例：检查 options 是否为列表
            if not isinstance(item['options'], list):
                raise RuleError(f"名为 '{item['name']}' 的条目的 'options' 必须是列表")

        # 可以在此添加总长度的验证，如果规则中有定义的话
        # if 'total_length' in self.rule and total_length != self.rule['total_length']:
        #     raise RuleError("结构中定义的总长度与规则不匹配")
        
        return True


def validate_rule(rule: Dict[str, Any]) -> bool:
    """
    便捷函数，用于快速验证单个规则。

    Args:
        rule (Dict[str, Any]): 待验证的规则。

    Returns:
        bool: 如果规则有效，则返回 True。
    """
    try:
        validator = RuleValidator(rule)
        return validator.validate()
    except RuleError:
        return False

