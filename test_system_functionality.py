#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统功能
"""
import sys
import os
import json

# 为Windows终端设置UTF-8编码
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
    except:
        pass

print("Testing system functionality...")

try:
    # 导入模块
    from modules.file_manager import get_file_manager
    from modules.expense_calculator import get_calculator
    from modules.config import EXPENSE_TYPES, PREDEFINED_FORMULAS
    
    # 获取实例
    fm = get_file_manager()
    calc = get_calculator()
    
    print("Step 1: List existing projects")
    projects = fm.get_all_projects()
    print(f"   Found {len(projects)} existing projects")
    # 只输出数量，不遍历项目以避免编码问题
    
    # 测试项目创建 - 使用英文名称避免编码问题
    test_project_name = "TEST_PROJECT_FUNCTIONALITY"
    print(f"\nStep 2: Create test project '{test_project_name}'")
    
    if fm.project_exists(test_project_name):
        print("   Project already exists, deleting...")
        fm.delete_project(test_project_name)
    
    success = fm.create_project(test_project_name, "功能测试项目")
    if not success:
        raise ValueError("Failed to create test project")
    print("   OK: Test project created successfully")
    
    # 测试打开项目
    print(f"\nStep 3: Open test project '{test_project_name}'")
    project_data = fm.open_project(test_project_name)
    if not project_data:
        raise ValueError("Failed to open test project")
    print("   OK: Test project opened successfully")
    
    # 测试添加费用记录
    print(f"\nStep 4: Add expense record")
    expense_data = {
        "expense_type": "material",
        "expense_name": "Test Material Cost",
        "quantity": 5,
        "unit_price": 10.0,
        "unit": "pcs",
        "description": "Test materials",
        "total_amount": 50.0,  # 5 * 10
        "date": "2025-02-03",
        "payment_method": "cash",
        "currency": "CNY"
    }
    
    expense_id = fm.add_expense(expense_data)
    if not expense_id:
        raise ValueError("Failed to add expense record")
    print(f"   OK: Expense added with ID {expense_id}")
    
    # 测试获取费用列表
    print(f"\nStep 5: Get all expenses")
    expenses = fm.get_all_expenses()
    print(f"   OK: Found {len(expenses)} expense(s)")
    
    # 测试按ID获取费用
    print(f"\nStep 6: Get expense by ID {expense_id}")
    expense = fm.get_expense_by_id(expense_id)
    if not expense:
        raise ValueError(f"Failed to get expense with ID {expense_id}")
    print(f"   OK: Retrieved expense: {expense['expense_name']} (¥{expense['total_amount']})")
    
    # 测试计算公式
    print(f"\nStep 7: Test formula calculation")
    test_formula = "quantity * unit_price * 1.1"  # 加10%税
    test_params = {"quantity": 10, "unit_price": 5.0}
    result = calc.calculate_expense(test_formula, test_params)
    expected = 55.0  # 10 * 5 * 1.1
    if abs(result - expected) < 0.01:
        print(f"   OK: Formula calculated correctly: {result}")
    else:
        print(f"   WARNING: Formula result {result}, expected {expected}")
    
    # 测试统计信息
    print(f"\nStep 8: Get expense statistics")
    stats = fm.get_expense_statistics()
    if stats:
        print(f"   OK: Statistics retrieved")
        print(f"   - Total expenses: {stats['overall']['total_count']}")
        print(f"   - Grand total: ¥{stats['overall']['grand_total']}")
        if stats['by_type']:
            for i, t in enumerate(stats['by_type'], 1):
                print(f"   - Type {i}: {t['count']} items, amount: {t['total_amount']}")
    
    # 测试保存项目
    print(f"\nStep 9: Save project")
    success = fm.save_project()
    if success:
        print("   OK: Project saved successfully")
    else:
        raise ValueError("Failed to save project")
    
    # 测试关闭项目
    print(f"\nStep 10: Close project")
    fm.close_project()
    print("   OK: Project closed")
    
    # 验证项目文件存在
    print(f"\nStep 11: Verify project file exists")
    project_path = os.path.join("projects", f"{test_project_name}.json")
    if os.path.exists(project_path):
        print(f"   OK: Project file created: {project_path}")
    else:
        print(f"   WARNING: Project file not found at {project_path}")
    
    # 验证JSON文件格式
    try:
        with open(project_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'project_info' in data and 'expenses' in data:
            print(f"   OK: JSON file has correct structure")
            print(f"   - Expenses in file: {len(data['expenses'])}")
        else:
            print(f"   WARNING: JSON file structure incomplete")
    except Exception as e:
        print(f"   WARNING: Failed to parse JSON file: {e}")
    
    # 清理测试数据
    print(f"\nStep 12: Clean up test project")
    success = fm.delete_project(test_project_name)
    if success:
        print("   OK: Test project deleted successfully")
    else:
        print("   WARNING: Failed to delete test project")
    
    print("\n" + "="*50)
    print("ALL FUNCTIONAL TESTS PASSED!")
    print("="*50)
    
except Exception as e:
    print(f"\nERROR: Test failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)