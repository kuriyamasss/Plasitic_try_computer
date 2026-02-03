#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试GUI启动
"""
import sys
import os

# 为Windows终端设置UTF-8编码
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
    except:
        pass

print("Testing GUI startup...")

try:
    # 测试导入模块
    from modules.file_manager import get_file_manager
    from modules.expense_calculator import get_calculator
    from modules.config import EXPENSE_TYPES
    print("OK: All modules imported successfully")
    
    # 测试管理器实例化
    fm = get_file_manager()
    calc = get_calculator()
    print("OK: Managers instantiated")
    
    # 测试tkinter导入
    import tkinter as tk
    from tkinter import ttk, messagebox
    print("OK: tkinter imported successfully")
    
    # 测试创建简单窗口（不显示）
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    print("OK: tkinter root created")
    
    # 测试GUI类导入
    from project_gui import ProjectExpenseTrackerGUI
    print("OK: GUI class imported successfully")
    
    # 测试创建GUI实例（不显示窗口）
    app = ProjectExpenseTrackerGUI(root)
    print("OK: GUI instance created")
    
    # 清理
    root.destroy()
    print("OK: tkinter root destroyed")
    
    print("\n[SUCCESS] GUI startup test PASSED!")
    
except Exception as e:
    print(f"\n[FAILED] GUI startup test FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)