"""
费用计算模块 - 从原有的expense_manager.py提取的计算功能
"""
from typing import Dict, Any, List
import math

class ExpenseCalculator:
    """费用计算器"""
    
    def __init__(self):
        pass
    
    def calculate_expense(self, formula_expression: str, params: Dict[str, float]) -> float:
        """根据公式表达式和参数计算费用"""
        try:
            # 安全地执行表达式
            # 只允许使用数学函数和参数
            safe_dict = {
                '__builtins__': None,
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                'pow': pow,
                'math': math
            }
            
            # 添加参数到安全字典
            safe_dict.update(params)
            
            # 计算表达式
            result = eval(formula_expression, {"__builtins__": {}}, safe_dict)
            return float(result)
            
        except Exception as e:
            raise ValueError(f"公式计算错误: {str(e)}")
    
    def calculate_total_amount(self, quantity: float = None, unit_price: float = None, 
                              formula_expression: str = None, params: Dict[str, float] = None) -> float:
        """计算总金额，支持多种计算方式"""
        
        # 方式1：直接使用数量×单价
        if quantity is not None and unit_price is not None:
            return quantity * unit_price
        
        # 方式2：使用公式计算
        if formula_expression and params:
            return self.calculate_expense(formula_expression, params)
        
        # 方式3：没有足够信息，返回0
        return 0.0
    
    def validate_formula_expression(self, expression: str, params: List[str]) -> bool:
        """验证公式表达式和参数的合法性"""
        try:
            # 检查表达式是否包含非法内容
            illegal_keywords = ['import', 'exec', 'eval', '__', 'open', 'file', 'os', 'sys']
            for keyword in illegal_keywords:
                if keyword in expression.lower():
                    return False
            
            # 尝试编译表达式
            compiled = compile(expression, '<string>', 'eval')
            
            # 检查使用的变量是否都在参数列表中
            # 这里简化检查，实际应该更严格
            return True
            
        except Exception:
            return False

# 全局计算器实例
calculator_instance = None

def get_calculator():
    """获取计算器实例（单例模式）"""
    global calculator_instance
    if calculator_instance is None:
        calculator_instance = ExpenseCalculator()
    return calculator_instance
