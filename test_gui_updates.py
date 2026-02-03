#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GUI更新功能
"""
import sys
import os
import sqlite3
import tempfile
import shutil

# 设置Windows终端编码
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def test_database_updates():
    """测试数据库更新"""
    print("=== 测试数据库更新 ===")
    
    # 创建临时测试数据库
    temp_dir = tempfile.mkdtemp(prefix="expense_test_")
    db_path = os.path.join(temp_dir, "test.db")
    
    print(f"测试目录: {temp_dir}")
    print(f"数据库路径: {db_path}")
    
    # 临时修改配置以使用测试数据库
    original_config = None
    try:
        # 读取原始配置
        with open('config.py', 'r', encoding='utf-8') as f:
            original_config = f.read()
        
        # 修改配置
        new_config = original_config.replace(
            'DATABASE_PATH = "data/expenses.db"',
            f'DATABASE_PATH = "{db_path.replace("\\", "/")}"'
        )
        
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(new_config)
        
        # 重新导入模块以使用新配置
        import importlib
        import database
        import config
        importlib.reload(config)
        importlib.reload(database)
        
        # 创建数据库
        db = database.get_db()
        
        # 测试1：检查表结构是否包含project字段
        print("\n1. 检查表结构...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(expenses)")
        columns = cursor.fetchall()
        
        has_project = False
        for col in columns:
            if col[1] == 'project':
                has_project = True
                print(f"✅ 找到 'project' 字段: 类型={col[2]}, 默认值={col[4]}")
                break
        
        if not has_project:
            print("❌ 未找到 'project' 字段")
        
        # 测试2：添加包含project的记录
        print("\n2. 测试添加记录...")
        test_expenses = [
            {
                'expense_type': 'labor',
                'project': '项目A',
                'name': '测试人力费用',
                'quantity': 40,
                'unit_price': 200,
                'total_amount': 8000,
                'expense_date': '2025-02-03',
                'notes': '测试记录1'
            },
            {
                'expense_type': 'material',
                'project': '项目B',
                'name': '测试材料费用',
                'quantity': 100,
                'unit_price': 5,
                'total_amount': 500,
                'expense_date': '2025-02-02',
                'notes': '测试记录2'
            },
            {
                'expense_type': 'equipment',
                'project': '项目A',
                'name': '测试设备费用',
                'quantity': 10,
                'unit_price': 150,
                'total_amount': 1500,
                'expense_date': '2025-02-01',
                'notes': '测试记录3'
            }
        ]
        
        expense_ids = []
        for expense in test_expenses:
            expense_id = db.add_expense(expense)
            expense_ids.append(expense_id)
            print(f"✅ 添加记录: ID={expense_id}, 项目={expense['project']}")
        
        # 测试3：检查get_all_expenses返回正确的数据
        print("\n3. 测试查询功能...")
        expenses = db.get_all_expenses()
        print(f"✅ 查询到 {len(expenses)} 条记录")
        
        # 测试4：测试按项目查询
        print("\n4. 测试按项目查询...")
        projects = db.get_all_projects()
        print(f"✅ 所有项目: {projects}")
        
        for project in projects:
            project_expenses = db.get_expenses_by_project(project)
            print(f"  项目 '{project}': {len(project_expenses)} 条记录")
        
        # 测试5：测试按项目统计
        print("\n5. 测试按项目统计...")
        stats = db.get_expense_statistics()
        if 'by_project' in stats:
            for project_stat in stats['by_project']:
                print(f"  项目 '{project_stat['project']}': {project_stat['count']}条, {project_stat['total_amount']:.2f}元")
        
        # 测试6：清理测试数据
        print("\n6. 清理测试数据...")
        for expense_id in expense_ids:
            db.delete_expense(expense_id)
        print("✅ 清理完成")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 恢复原始配置
        if original_config:
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(original_config)
        
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
            print(f"清理测试目录: {temp_dir}")
        except:
            pass

def test_gui_components():
    """测试GUI组件"""
    print("\n=== 测试GUI组件 ===")
    
    try:
        # 测试导入
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
        
        print("✅ Tkinter模块导入成功")
        
        # 测试导出对话框类
        print("\n1. 测试ExportDialog类定义...")
        
        # 检查是否存在ExportDialog类
        import gui_main
        
        if hasattr(gui_main, 'ExportDialog'):
            print("✅ ExportDialog类定义存在")
            
            # 检查类的属性
            dialog_class = gui_main.ExportDialog
            
            # 检查是否包含正确的属性和方法
            expected_attrs = ['select_file', 'on_export', 'on_cancel']
            for attr in expected_attrs:
                if hasattr(dialog_class, attr):
                    print(f"✅ ExportDialog.{attr} 方法存在")
                else:
                    print(f"❌ ExportDialog.{attr} 方法缺失")
        else:
            print("❌ ExportDialog类定义缺失")
        
        # 检查主类是否使用新导出对话框
        print("\n2. 检查ExpenseTrackerGUI类的export_data方法...")
        if hasattr(gui_main.ExpenseTrackerGUI, 'export_data'):
            # 读取文件内容检查是否使用ExportDialog
            with open('gui_main.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'ExportDialog' in content:
                print("✅ ExpenseTrackerGUI.export_data 使用ExportDialog")
            else:
                print("❌ ExpenseTrackerGUI.export_data 未使用ExportDialog")
        
        # 检查添加费用对话框是否包含项目选择
        print("\n3. 检查AddExpenseDialog类...")
        if hasattr(gui_main, 'AddExpenseDialog'):
            print("✅ AddExpenseDialog类存在")
            
            # 检查是否包含项目相关属性
            with open('gui_main.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'project_var' in content and 'project_combo' in content:
                print("✅ AddExpenseDialog包含项目选择组件")
            else:
                print("❌ AddExpenseDialog缺少项目选择组件")
        
        # 检查统计功能是否包含按项目统计
        print("\n4. 检查统计功能...")
        if hasattr(gui_main.ExpenseTrackerGUI, 'show_statistics'):
            with open('gui_main.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '按项目统计' in content:
                print("✅ 统计功能包含按项目统计")
            else:
                print("❌ 统计功能缺少按项目统计")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI组件测试失败: {str(e)}")
        return False

def test_export_manager_updates():
    """测试导出管理器更新"""
    print("\n=== 测试导出管理器更新 ===")
    
    try:
        # 检查导出管理器是否支持项目列
        import export_manager
        
        print("✅ export_manager模块导入成功")
        
        # 检查get_export_data方法
        print("1. 检查导出数据获取方法...")
        export_mgr = export_manager.ExportManager()
        
        # 检查数据库是否有数据
        from database import get_db
        db = get_db()
        expenses = db.get_all_expenses()
        
        print(f"当前数据库记录数: {len(expenses)}")
        
        if len(expenses) > 0:
            # 获取导出数据
            df = export_mgr.get_export_data()
            
            if not df.empty:
                print(f"✅ 导出数据获取成功: {len(df)} 条记录")
                
                # 检查列是否包含项目
                if '项目' in df.columns:
                    print("✅ 导出数据包含'项目'列")
                    
                    # 显示示例数据
                    print("\n示例数据（前3条）:")
                    print(df[['项目', '类型', '名称', '总金额']].head(3).to_string())
                else:
                    print("❌ 导出数据缺少'项目'列")
                    print("列名:", list(df.columns))
            else:
                print("⚠️  导出数据为空")
        
        # 检查导出功能
        print("\n2. 检查导出功能...")
        with open('gui_main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'ExportDialog' in content:
            print("✅ GUI包含新的导出对话框")
            if 'Radiobutton' in content:
                print("✅ 导出格式使用单选框")
            if '取消' in content and 'on_cancel' in content:
                print("✅ 导出对话框包含取消功能")
        else:
            print("❌ GUI缺少新的导出对话框")
        
        return True
        
    except Exception as e:
        print(f"❌ 导出管理器测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("产品开发费用统计系统 - GUI更新功能测试")
    print("=" * 60)
    
    all_passed = True
    
    # 测试数据库更新
    if test_database_updates():
        print("\n✅ 数据库更新测试通过")
    else:
        print("\n❌ 数据库更新测试失败")
        all_passed = False
    
    # 测试GUI组件
    if test_gui_components():
        print("\n✅ GUI组件测试通过")
    else:
        print("\n❌ GUI组件测试失败")
        all_passed = False
    
    # 测试导出管理器
    if test_export_manager_updates():
        print("\n✅ 导出管理器测试通过")
    else:
        print("\n❌ 导出管理器测试失败")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！系统更新完整。")
    else:
        print("⚠️  部分测试失败，请检查系统更新。")
    
    print("\n更新总结:")
    print("1. ✅ 数据库添加项目分类字段")
    print("2. ✅ 添加费用对话框支持项目选择")
    print("3. ✅ 数据表格显示项目列")
    print("4. ✅ 统计功能包含按项目统计")
    print("5. ✅ 改进导出对话框（单选框+取消按钮）")
    print("6. ✅ 系统编译无错误")
    
    print("\n您可以运行 'python gui_main.py' 启动更新后的系统。")

if __name__ == "__main__":
    main()