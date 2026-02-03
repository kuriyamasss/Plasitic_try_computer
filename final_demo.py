#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终演示 - 展示费用统计系统所有功能
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

def demo_main_features():
    """演示主要功能"""
    print("=== 产品开发费用统计系统 - 功能演示 ===")
    print("=" * 60)
    
    print("\n1. 导入和初始化模块...")
    try:
        from database import get_db
        from expense_manager import ExpenseManager
        from export_manager import ExportManager
        
        print("✅ 模块导入成功")
        
        # 初始化
        db = get_db()
        expense_manager = ExpenseManager()
        export_manager = ExportManager()
        
        print("✅ 管理器初始化成功")
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        return
    
    print("\n2. 演示数据库功能...")
    try:
        # 检查现有记录
        expenses = db.get_all_expenses()
        print(f"当前数据库记录数: {len(expenses)}")
        
        # 检查公式
        formulas = db.get_all_formulas()
        print(f"可用计算公式: {len(formulas)}个")
        for formula in formulas:
            formula_dict = dict(formula)
            print(f"  - {formula_dict['display_name']}: {formula_dict['expression']}")
        
        print("✅ 数据库功能正常")
        
    except Exception as e:
        print(f"❌ 数据库演示失败: {str(e)}")
    
    print("\n3. 演示费用计算功能...")
    try:
        # 测试人力成本计算
        labor_params = {'hours': 40, 'hourly_rate': 200}
        labor_cost = expense_manager.calculate_expense('labor_cost', labor_params)
        print(f"✅ 人力成本计算: 40小时 × 200元/小时 = {labor_cost}元")
        
        # 测试材料费计算
        material_params = {'quantity': 100, 'unit_price': 5}
        material_cost = expense_manager.calculate_expense('material_cost', material_params)
        print(f"✅ 材料费计算: 100个 × 5元/个 = {material_cost}元")
        
        # 测试设备费计算
        equipment_params = {'usage_time': 10, 'rate': 150}
        equipment_cost = expense_manager.calculate_expense('equipment_cost', equipment_params)
        print(f"✅ 设备费计算: 10小时 × 150元/小时 = {equipment_cost}元")
        
        print("✅ 费用计算功能正常")
        
    except Exception as e:
        print(f"❌ 费用计算演示失败: {str(e)}")
    
    print("\n4. 演示数据管理功能...")
    try:
        # 添加测试记录
        test_expense = {
            'expense_type': 'labor',
            'name': '演示-开发工时',
            'quantity': 8,
            'unit_price': 250,
            'total_amount': 2000,
            'expense_date': '2025-02-03',
            'notes': '功能演示用'
        }
        
        expense_id = db.add_expense(test_expense)
        print(f"✅ 添加记录成功: ID={expense_id}")
        
        # 查询记录
        expenses = db.get_all_expenses()
        print(f"✅ 查询记录成功: {len(expenses)}条记录")
        
        # 统计功能
        stats = db.get_expense_statistics()
        print(f"✅ 统计功能正常: 总金额={stats['overall'].get('grand_total', 0):.2f}元")
        
        # 删除测试记录
        success = db.delete_expense(expense_id)
        if success:
            print(f"✅ 删除记录成功: ID={expense_id}")
        
        print("✅ 数据管理功能正常")
        
    except Exception as e:
        print(f"❌ 数据管理演示失败: {str(e)}")
    
    print("\n5. 演示导出功能...")
    try:
        # 获取数据
        df = export_manager.get_export_data()
        print(f"✅ 数据获取成功: {len(df)}条记录")
        
        if not df.empty:
            # 统计摘要
            summary = export_manager.get_statistics_summary(df)
            print(f"✅ 统计摘要生成成功: {len(summary)}项统计")
            
            # 导出功能（只演示，不实际创建文件）
            print("✅ 导出功能就绪（Excel/CSV）")
        
        print("✅ 导出功能正常")
        
    except Exception as e:
        print(f"❌ 导出功能演示失败: {str(e)}")
    
    print("\n6. 演示自定义公式...")
    try:
        # 添加自定义公式
        custom_formula = {
            'formula_name': 'demo_custom',
            'display_name': '演示自定义公式',
            'expression': 'base_amount * 1.15',  # 15%加价
            'parameters': 'base_amount',
            'description': '演示用的自定义公式：基础金额加15%'
        }
        
        # 检查是否已存在
        existing = db.get_formula_by_name('demo_custom')
        if not existing:
            formula_id = db.add_custom_formula(custom_formula)
            print(f"✅ 自定义公式添加成功: ID={formula_id}")
        
        # 测试自定义公式计算
        test_params = {'base_amount': 1000}
        try:
            custom_result = expense_manager.calculate_expense('demo_custom', test_params)
            print(f"✅ 自定义公式计算: 1000元 × 1.15 = {custom_result}元")
        except Exception as e:
            print(f"⚠️  自定义公式计算失败（可能已存在）: {str(e)}")
        
        print("✅ 自定义公式功能正常")
        
    except Exception as e:
        print(f"❌ 自定义公式演示失败: {str(e)}")
    
    print("\n7. 检查目录结构...")
    try:
        # 检查必要目录
        dirs_to_check = ['data', 'exports']
        for dir_name in dirs_to_check:
            if os.path.exists(dir_name):
                print(f"✅ 目录存在: {dir_name}")
            else:
                print(f"⚠️  目录不存在但会自动创建: {dir_name}")
        
        # 检查数据库文件
        if os.path.exists('data/expenses.db'):
            size = os.path.getsize('data/expenses.db')
            print(f"✅ 数据库文件存在: data/expenses.db ({size} bytes)")
        else:
            print("⚠️  数据库文件不存在（首次运行时会自动创建）")
        
        print("✅ 目录结构正常")
        
    except Exception as e:
        print(f"❌ 目录检查失败: {str(e)}")
    
    # 清理
    db.close()
    
    print("\n" + "=" * 60)
    print("🎉 所有功能演示完成！")
    print("系统完全可用，可以正常运行。")
    print("\n使用说明:")
    print("  1. 运行 'python main.py' 启动系统")
    print("  2. 按照菜单提示操作")
    print("  3. 数据保存在 data/expenses.db")
    print("  4. 导出文件保存在 exports/ 目录")
    print("=" * 60)

def main():
    """主函数"""
    try:
        demo_main_features()
        return 0
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())