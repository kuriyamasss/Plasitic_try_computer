"""
费用统计系统配置文件 - 新版（文件存储版）
"""

# 项目文件配置
PROJECTS_DIR = "projects"
PROJECT_FILE_EXTENSION = ".json"

# 费用类型定义
EXPENSE_TYPES = {
    "labor": "人力成本",
    "material": "材料费", 
    "equipment": "设备费",
    "other": "其他费用"
}

# 预定义公式
PREDEFINED_FORMULAS = {
    "labor_cost": {
        "name": "人力成本",
        "expression": "hours * hourly_rate",
        "params": ["hours", "hourly_rate"],
        "description": "人力成本 = 工时 × 时薪"
    },
    "material_cost": {
        "name": "材料费",
        "expression": "quantity * unit_price",
        "params": ["quantity", "unit_price"],
        "description": "材料费 = 数量 × 单价"
    },
    "equipment_cost": {
        "name": "设备费",
        "expression": "usage_time * rate",
        "params": ["usage_time", "rate"],
        "description": "设备费 = 使用时长 × 费率"
    }
}

# 导出配置
EXPORT_FORMATS = ["excel", "csv"]
EXPORT_DIR = "exports"

# 默认项目结构模板
DEFAULT_PROJECT_TEMPLATE = {
    "project_info": {
        "name": "",
        "created_date": "",
        "last_modified": "",
        "description": ""
    },
    "custom_expense_types": [],
    "formulas": [],
    "expenses": []
}
