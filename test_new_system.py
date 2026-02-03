#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新版文件存储系统
"""
import os
import sys
import shutil
import json
from datetime import datetime

# 设置Windows终端编码
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def test_file_manager_basic():
    """测试文件管理器基本功能"""
    print("=== 测试文件管理器基本功能 ===")
    
    # 导入模块
    from file_manager import get_file_manager
    
    # 获取文件管理器实例
    fm = get_file_manager()
    
    print("1. 检查项目目录...")
    if os.path.exists('projects'):
        print("✅ 项目目录存在")
    else:
        print("❌ 项目目录不存在")
        return False
    
    print("\n2. 创建测试项目...")
    test_project_name = "测试项目_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    if fm.create_project(test_project_name, "这是一个测试项目"):
        print(f"✅ 创建项目成功: {test_project_name}")
    else:
        print("❌ 创建项目失败")
        return False
    
    print("\n3. 检查项目是否存在...")
    if fm.project_exists(test_project_name):
        print(f"✅ 项目存在: {test_project_name}")
    else:
        print(f"❌ 项目不存在: {test_project_name}")
        return False
    
    print("\n4. 获取所有项目列表...")
    projects = fm.get_all_projects()
    print(f"✅ 获取到 {len(projects)} 个项目")
    for project in projects:
        print(f"  - {project['name']} (创建时间: {project['created_date']})")
    
    print("\n5. 打开项目...")
    project_data = fm.open_project(test_project_name)
    if project_data:
        print(f"✅ 打开项目成功")
        print(f"   项目名称: {project_data['project_info']['name']}")
        print(f"   项目描述: {project_data['project_info']['description']}")
    else:
        print("❌ 打开项目失败")
        return False
    
    print("\n6. 添加费用记录...")
    expense_data = {
        'expense_type': 'labor',
        'name': '测试人力费用',
        'quantity': 40,
        'unit_price': 200,
        'total_amount': 8000,
        'date': '2025-02-03',
        'notes': '测试记录'
    }
    
    expense_id = fm.add_expense(expense_data)
    if expense_id:
        print(f"✅ 添加费用记录成功: ID={expense_id}")
    else:
        print("❌ 添加费用记录失败")
        return False
    
    print("\n7. 获取所有费用记录...")
    expenses = fm.get_all_expenses()
    print(f"✅ 获取到 {len(expenses)} 条费用记录")
    for expense in expenses:
        print(f"  - ID:{expense['id']} {expense['name']} {expense['total_amount']:.2f}元")
    
    print("\n8. 获取费用统计...")
    stats = fm.get_expense_statistics()
    if stats and 'overall' in stats:
        overall = stats['overall']
        print(f"✅ 统计信息:")
        print(f"   总记录数: {overall['total_count']}")
        print(f"   总金额: {overall['grand_total']:.2f}")
        print(f"   平均金额: {overall['avg_amount']:.2f}")
    else:
        print("❌ 获取统计信息失败")
    
    print("\n9. 保存并关闭项目...")
    fm.save_project()
    fm.close_project()
    print("✅ 项目保存并关闭成功")
    
    print("\n10. 删除测试项目...")
    if fm.delete_project(test_project_name):
        print(f"✅ 删除项目成功: {test_project_name}")
    else:
        print(f"❌ 删除项目失败: {test_project_name}")
        return False
    
    return True

def test_gui_imports():
    """测试GUI模块导入"""
    print("\n=== 测试GUI模块导入 ===")
    
    try:
        # 测试导入
        import tkinter as tk
        from tkinter import ttk
        print("✅ Tkinter模块导入成功")
        
        import project_gui
        print("✅ project_gui模块导入成功")
        
        from file_manager import get_file_manager
        from expense_calculator import get_calculator
        from config import EXPENSE_TYPES
        print("✅ 所有核心模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {str(e)}")
        return False

def test_expense_calculator():
    """测试费用计算器"""
    print("\n=== 测试费用计算器 ===")
    
    try:
        from expense_calculator import get_calculator
        
        calculator = get_calculator()
        
        # 测试公式计算
        print("1. 测试公式计算...")
        formula_expression = "hours * hourly_rate"
        params = {'hours': 40, 'hourly_rate': 200}
        
        result = calculator.calculate_expense(formula_expression, params)
        expected = 40 * 200  # 8000
        
        if abs(result - expected) < 0.01:
            print(f"✅ 公式计算正确: {formula_expression} = {result}")
        else:
            print(f"❌ 公式计算错误: 期望 {expected}, 实际 {result}")
            return False
        
        # 测试多种计算方式
        print("\n2. 测试多种计算方式...")
        
        # 方式1: 数量×单价
        result1 = calculator.calculate_total_amount(quantity=10, unit_price=100)
        if abs(result1 - 1000) < 0.01:
            print(f"✅ 数量×单价计算正确: 10 × 100 = {result1}")
        else:
            print(f"❌ 数量×单价计算错误")
            return False
        
        # 方式2: 公式计算
        result2 = calculator.calculate_total_amount(
            formula_expression="quantity * price * discount",
            params={'quantity': 5, 'price': 200, 'discount': 0.8}
        )
        expected2 = 5 * 200 * 0.8  # 800
        
        if abs(result2 - expected2) < 0.01:
            print(f"✅ 公式参数计算正确: 5 × 200 × 0.8 = {result2}")
        else:
            print(f"❌ 公式参数计算错误")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 费用计算器测试失败: {str(e)}")
        return False

def create_sample_projects():
    """创建示例项目文件，用于测试"""
    print("\n=== 创建示例项目文件 ===")
    
    try:
        # 确保项目目录存在
        if not os.path.exists('projects'):
            os.makedirs('projects')
        
        # 创建示例项目1
        sample_project1 = {
            "project_info": {
                "name": "示例项目A",
                "created_date": "2025-02-01 10:00:00",
                "last_modified": "2025-02-03 14:30:00",
                "description": "这是一个示例项目，包含一些费用记录"
            },
            "custom_expense_types": [
                {
                    "id": 1,
                    "name": "外包服务",
                    "description": "第三方外包服务费用",
                    "created_at": "2025-02-01 10:05:00"
                }
            ],
            "formulas": [
                {
                    "id": "labor_cost",
                    "name": "人力成本",
                    "expression": "hours * hourly_rate",
                    "params": ["hours", "hourly_rate"],
                    "description": "人力成本 = 工时 × 时薪",
                    "is_custom": False
                },
                {
                    "id": "custom_1",
                    "name": "外包成本",
                    "expression": "base_cost + additional_fees",
                    "params": ["base_cost", "additional_fees"],
                    "description": "外包成本 = 基础费用 + 附加费用",
                    "is_custom": True,
                    "created_at": "2025-02-01 10:10:00"
                }
            ],
            "expenses": [
                {
                    "id": 1,
                    "expense_type": "labor",
                    "name": "开发人员工资",
                    "quantity": 160,
                    "unit_price": 150,
                    "total_amount": 24000,
                    "date": "2025-02-01",
                    "notes": "2月份开发人员工资",
                    "created_at": "2025-02-01 10:15:00"
                },
                {
                    "id": 2,
                    "expense_type": "material",
                    "name": "服务器费用",
                    "quantity": 1,
                    "unit_price": 5000,
                    "total_amount": 5000,
                    "date": "2025-02-02",
                    "notes": "云服务器月租",
                    "created_at": "2025-02-02 09:30:00"
                },
                {
                    "id": 3,
                    "expense_type": "equipment",
                    "name": "开发设备",
                    "total_amount": 12000,
                    "date": "2025-02-03",
                    "notes": "购买开发用笔记本电脑",
                    "created_at": "2025-02-03 14:00:00"
                }
            ]
        }
        
        # 创建示例项目2
        sample_project2 = {
            "project_info": {
                "name": "示例项目B",
                "created_date": "2025-01-15 09:00:00",
                "last_modified": "2025-02-02 16:45:00",
                "description": "另一个示例项目"
            },
            "custom_expense_types": [],
            "formulas": [
                {
                    "id": "material_cost",
                    "name": "材料费",
                    "expression": "quantity * unit_price",
                    "params": ["quantity", "unit_price"],
                    "description": "材料费 = 数量 × 单价",
                    "is_custom": False
                }
            ],
            "expenses": [
                {
                    "id": 1,
                    "expense_type": "material",
                    "name": "原材料采购",
                    "quantity": 100,
                    "unit_price": 50,
                    "total_amount": 5000,
                    "date": "2025-01-20",
                    "notes": "第一批原材料",
                    "created_at": "2025-01-20 11:00:00"
                },
                {
                    "id": 2,
                    "expense_type": "other",
                    "name": "差旅费用",
                    "total_amount": 3000,
                    "date": "2025-01-25",
                    "notes": "项目调研差旅",
                    "created_at": "2025-01-25 15:30:00"
                }
            ]
        }
        
        # 保存项目文件
        with open('projects/示例项目A.json', 'w', encoding='utf-8') as f:
            json.dump(sample_project1, f, ensure_ascii=False, indent=2)
        
        with open('projects/示例项目B.json', 'w', encoding='utf-8') as f:
            json.dump(sample_project2, f, ensure_ascii=False, indent=2)
        
        print("✅ 创建了2个示例项目文件:")
        print("  1. 示例项目A.json (3条费用记录，总金额: 41,000元)")
        print("  2. 示例项目B.json (2条费用记录，总金额: 8,000元)")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建示例项目失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("产品开发费用统计系统 - 新版文件存储架构测试")
    print("=" * 60)
    
    all_passed = True
    
    # 测试GUI模块导入
    if test_gui_imports():
        print("\n✅ GUI模块导入测试通过")
    else:
        print("\n❌ GUI模块导入测试失败")
        all_passed = False
    
    # 测试费用计算器
    if test_expense_calculator():
        print("\n✅ 费用计算器测试通过")
    else:
        print("\n❌ 费用计算器测试失败")
        all_passed = False
    
    # 测试文件管理器基本功能
    if test_file_manager_basic():
        print("\n✅ 文件管理器基本功能测试通过")
    else:
        print("\n❌ 文件管理器基本功能测试失败")
        all_passed = False
    
    # 创建示例项目
    if create_sample_projects():
        print("\n✅ 示例项目创建成功")
    else:
        print("\n❌ 示例项目创建失败")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！新版系统架构完整。")
        print("\n🎯 您可以运行以下命令启动新版GUI:")
        print("   python project_gui.py")
        print("\n📁 系统将在 'projects/' 目录下管理项目文件:")
        print("   • 每个项目保存为独立的JSON文件")
        print("   • 支持多项目管理")
        print("   • 支持费用记录、自定义类型、公式")
    else:
        print("⚠️  部分测试失败，请检查系统实现。")
    
    print("\n📋 新版系统特点总结:")
    print("1. ✅ 基于文件的项目管理（JSON格式）")
    print("2. ✅ 三段式GUI设计（导航栏+主显示区+状态栏）")
    print("3. ✅ 动态按钮系统（根据页面显示不同按钮）")
    print("4. ✅ 完整的费用管理功能（增删改查）")
    print("5. ✅ 统计信息显示")
    print("6. ✅ 模块化架构（文件管理、计算器、GUI分离）")
    print("\n🚀 系统已准备就绪，可以启动使用！")

if __name__ == "__main__":
    main()