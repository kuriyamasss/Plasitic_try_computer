#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试费用统计系统
"""
import sys
import os

# 设置Windows终端编码
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

print("=== 测试费用统计系统 ===")
print("1. 测试数据库连接...")

try:
    from database import get_db
    db = get_db()
    print("✅ 数据库连接成功")
    
    # 测试表创建
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = db.cursor.fetchall()
    print(f"✅ 数据库表创建成功: {[t[0] for t in tables]}")
    
    # 测试预定义公式
    formulas = db.get_all_formulas()
    print(f"✅ 预定义公式加载成功: {len(formulas)}个")
    for formula in formulas:
        formula_dict = dict(formula)
        print(f"   - {formula_dict['display_name']}: {formula_dict['expression']}")
    
    # 不关闭数据库，因为后续测试还需要
except Exception as e:
    print(f"❌ 数据库测试失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n2. 测试费用管理器...")
try:
    from expense_manager import ExpenseManager
    expense_manager = ExpenseManager()
    print("✅ 费用管理器初始化成功")
    
    # 测试公式计算
    test_params = {'hours': 8, 'hourly_rate': 200}
    try:
        result = expense_manager.calculate_expense('labor_cost', test_params)
        print(f"✅ 公式计算测试成功: 8小时 × 200元/小时 = {result}元")
    except Exception as e:
        print(f"⚠️  公式计算测试失败: {str(e)}")
    
    # 测试其他公式
    test_params2 = {'quantity': 10, 'unit_price': 50}
    try:
        result2 = expense_manager.calculate_expense('material_cost', test_params2)
        print(f"✅ 材料费计算测试成功: 10个 × 50元/个 = {result2}元")
    except Exception as e:
        print(f"⚠️  材料费计算测试失败: {str(e)}")
    
except Exception as e:
    print(f"❌ 费用管理器测试失败: {str(e)}")

print("\n3. 测试导出管理器...")
try:
    from export_manager import ExportManager
    export_manager = ExportManager()
    print("✅ 导出管理器初始化成功")
    
    # 检查导出目录
    if os.path.exists('exports'):
        print("✅ 导出目录存在")
    else:
        print("⚠️  导出目录不存在，但会在需要时自动创建")
    
    # 测试获取数据
    try:
        df = export_manager.get_export_data()
        print(f"✅ 数据获取测试成功: {len(df)} 条记录")
    except Exception as e:
        print(f"⚠️  数据获取测试失败: {str(e)}")
    
except Exception as e:
    print(f"❌ 导出管理器测试失败: {str(e)}")

print("\n4. 测试依赖包...")
try:
    import pandas
    import openpyxl
    print(f"✅ pandas版本: {pandas.__version__}")
    print(f"✅ openpyxl版本: {openpyxl.__version__}")
except ImportError as e:
    print(f"❌ 缺少依赖包: {str(e)}")

print("\n5. 测试数据操作...")
try:
    from database import get_db
    db = get_db()
    
    # 测试添加一条费用记录
    expense_data = {
        'expense_type': 'labor',
        'name': '测试开发工时',
        'quantity': 8,
        'unit_price': 200,
        'total_amount': 1600,
        'expense_date': '2025-02-03',
        'notes': '测试记录'
    }
    
    expense_id = db.add_expense(expense_data)
    print(f"✅ 添加费用记录测试成功: ID={expense_id}")
    
    # 测试查询记录
    expenses = db.get_all_expenses()
    print(f"✅ 查询费用记录测试成功: {len(expenses)} 条记录")
    
    # 测试统计
    stats = db.get_expense_statistics()
    print(f"✅ 费用统计测试成功: 总金额={stats['overall'].get('grand_total', 0):.2f}")
    
    # 清理测试数据
    if expense_id:
        db.delete_expense(expense_id)
        print(f"✅ 清理测试数据成功: 删除ID={expense_id}")
    
except Exception as e:
    print(f"❌ 数据操作测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    # 关闭数据库连接
    try:
        db.close()
        print("✅ 数据库连接已关闭")
    except:
        pass

print("\n=== 测试完成 ===")
print("如果所有测试都通过✅，系统可以正常运行！")
print("运行 'python main.py' 启动费用统计系统")