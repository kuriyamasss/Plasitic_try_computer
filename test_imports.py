#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模块导入
"""
import sys
import os

# 为Windows终端设置UTF-8编码
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
    except:
        pass

print("Testing module imports...")

try:
    # Test importing modules
    from modules.file_manager import get_file_manager
    print("OK: file_manager imported successfully")
    
    from modules.expense_calculator import get_calculator
    print("OK: expense_calculator imported successfully")
    
    from modules.config import EXPENSE_TYPES, PREDEFINED_FORMULAS
    print("OK: config imported successfully")
    
    # Create file manager instance
    fm = get_file_manager()
    print("OK: file manager instance created")
    
    # Create calculator instance
    calc = get_calculator()
    print("OK: calculator instance created")
    
    # Test getting all projects
    projects = fm.get_all_projects()
    print(f"OK: got project list, total {len(projects)} projects")
    
    # Test formula calculation
    test_params = {"quantity": 10, "unit_price": 5.5}
    result = calc.calculate_expense("quantity * unit_price", test_params)
    print(f"OK: formula calculated: 10 * 5.5 = {result}")
    
    print("\nOK: All tests passed!")
    
except Exception as e:
    print(f"ERROR: Test failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
