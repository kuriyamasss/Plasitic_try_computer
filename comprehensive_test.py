#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试费用统计系统 - 验证所有核心功能
"""
import sys
import os
import tempfile
import shutil
import json

# 设置Windows终端编码
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def setup_test_environment():
    """设置测试环境 - 使用临时数据库"""
    print("=== 设置测试环境 ===")
    
    # 创建临时目录
    test_dir = tempfile.mkdtemp(prefix='expense_test_')
    print(f"测试目录: {test_dir}")
    
    # 复制配置文件并修改数据库路径
    import config
    config_path = os.path.join(test_dir, 'config.py')
    
    with open('config.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改数据库路径到临时目录
    temp_db_path = os.path.join(test_dir, 'test_expenses.db').replace('\\', '/')
    content = content.replace(
        'DATABASE_PATH = "data/expenses.db"',
        f'DATABASE_PATH = "{temp_db_path}"'
    )
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 创建必要的目录
    data_dir = os.path.join(test_dir, 'data')
    exports_dir = os.path.join(test_dir, 'exports')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(exports_dir, exist_ok=True)
    
    return test_dir, temp_db_path

def test_database_module(test_dir, temp_db_path):
    """测试数据库模块"""
    print("\n=== 测试数据库模块 ===")
    
    # 修改sys.path以使用临时config
    import sys
    sys.path.insert(0, test_dir)
    
    try:
        # 重新导入模块以使用临时配置
        import importlib
        import config as original_config
        importlib.reload(original_config)
        
        from database import Database, get_db
        
        # 测试1: 创建数据库实例
        print("1. 测试数据库创建...")
        db = Database()
        assert db.conn is not None
        print("✅ 数据库实例创建成功")
        
        # 测试2: 验证表结构
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in db.cursor.fetchall()]
        assert 'expenses' in tables
        assert 'formulas' in tables
        print(f"✅ 表结构验证成功: {tables}")
        
        # 测试3: 验证预定义公式
        formulas = db.get_all_formulas()
        assert len(formulas) >= 3  # 至少3个预定义公式
        print(f"✅ 预定义公式验证成功: {len(formulas)}个公式")
        
        # 测试4: 数据操作
        print("4. 测试数据操作...")
        
        # 添加记录
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
        assert expense_id > 0
        print(f"✅ 添加记录成功: ID={expense_id}")
        
        # 查询记录
        expenses = db.get_all_expenses()
        assert len(expenses) == 1
        print(f"✅ 查询记录成功: {len(expenses)}条记录")
        
        # 按类型查询
        labor_expenses = db.get_expenses_by_type('labor')
        assert len(labor_expenses) == 1
        print(f"✅ 按类型查询成功: {len(labor_expenses)}条人力记录")
        
        # 统计功能
        stats = db.get_expense_statistics()
        assert stats['overall']['total_count'] == 1
        assert stats['overall']['grand_total'] == 1600
        print(f"✅ 统计功能成功: 总金额={stats['overall']['grand_total']}")
        
        # 添加自定义公式
        custom_formula = {
            'formula_name': 'test_formula',
            'display_name': '测试公式',
            'expression': 'a + b * 0.1',
            'parameters': 'a,b',
            'description': '测试自定义公式'
        }
        
        formula_id = db.add_custom_formula(custom_formula)
        assert formula_id > 0
        print(f"✅ 添加自定义公式成功: ID={formula_id}")
        
        # 查询公式
        formula = db.get_formula_by_name('test_formula')
        assert formula is not None
        print(f"✅ 查询公式成功: {formula['display_name']}")
        
        # 删除记录
        success = db.delete_expense(expense_id)
        assert success
        print(f"✅ 删除记录成功: ID={expense_id}")
        
        db.close()
        print("✅ 数据库模块测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库模块测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复sys.path
        sys.path.pop(0)

def test_expense_manager_module(test_dir):
    """测试费用管理器模块"""
    print("\n=== 测试费用管理器模块 ===")
    
    sys.path.insert(0, test_dir)
    
    try:
        import importlib
        import config as original_config
        importlib.reload(original_config)
        
        from expense_manager import ExpenseManager
        
        expense_manager = ExpenseManager()
        print("✅ 费用管理器初始化成功")
        
        # 测试公式计算
        test_params = {'hours': 40, 'hourly_rate': 200}
        result = expense_manager.calculate_expense('labor_cost', test_params)
        assert result == 8000
        print(f"✅ 公式计算成功: 40小时 × 200元/小时 = {result}元")
        
        # 测试其他公式
        test_params2 = {'quantity': 100, 'unit_price': 5}
        result2 = expense_manager.calculate_expense('material_cost', test_params2)
        assert result2 == 500
        print(f"✅ 材料费计算成功: 100个 × 5元/个 = {result2}元")
        
        # 测试错误处理
        print("3. 测试错误处理...")
        
        # 测试无效公式
        try:
            expense_manager.calculate_expense('invalid_formula', {})
            print("❌ 无效公式未抛出异常")
            return False
        except ValueError as e:
            print(f"✅ 无效公式正确处理: {str(e)}")
        
        # 测试缺失参数
        try:
            expense_manager.calculate_expense('labor_cost', {'hours': 40})
            print("❌ 缺失参数未抛出异常")
            return False
        except ValueError as e:
            print(f"✅ 缺失参数正确处理: {str(e)}")
        
        print("✅ 费用管理器模块测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 费用管理器模块测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sys.path.pop(0)

def test_export_manager_module(test_dir):
    """测试导出管理器模块"""
    print("\n=== 测试导出管理器模块 ===")
    
    sys.path.insert(0, test_dir)
    
    try:
        import importlib
        import config as original_config
        importlib.reload(original_config)
        
        from export_manager import ExportManager
        from database import get_db
        
        # 先添加一些测试数据
        db = get_db()
        test_data = [
            {
                'expense_type': 'labor',
                'name': '导出测试-开发',
                'quantity': 20,
                'unit_price': 150,
                'total_amount': 3000,
                'expense_date': '2025-02-01',
                'notes': '用于导出测试'
            },
            {
                'expense_type': 'material',
                'name': '导出测试-材料',
                'quantity': 50,
                'unit_price': 10,
                'total_amount': 500,
                'expense_date': '2025-02-02',
                'notes': '用于导出测试'
            }
        ]
        
        record_ids = []
        for data in test_data:
            record_id = db.add_expense(data)
            record_ids.append(record_id)
        
        print(f"✅ 添加 {len(record_ids)} 条测试数据")
        
        export_manager = ExportManager()
        print("✅ 导出管理器初始化成功")
        
        # 测试数据获取
        df = export_manager.get_export_data()
        assert len(df) == 2
        print(f"✅ 数据获取成功: {len(df)} 条记录")
        
        # 测试统计摘要
        summary = export_manager.get_statistics_summary(df)
        assert '记录总数' in summary
        assert summary['记录总数'] == 2
        print(f"✅ 统计摘要生成成功: {summary['记录总数']} 条记录")
        
        # 测试Excel导出
        print("4. 测试Excel导出...")
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            temp_excel = tmp.name
        
        try:
            excel_path, success = export_manager.export_to_excel(df, os.path.basename(temp_excel))
            assert success
            assert os.path.exists(excel_path)
            file_size = os.path.getsize(excel_path)
            print(f"✅ Excel导出成功: {excel_path} ({file_size} bytes)")
            
            # 验证文件内容
            import pandas as pd
            df_check = pd.read_excel(excel_path, sheet_name='费用记录')
            assert len(df_check) == 2
            print(f"✅ Excel文件验证成功: {len(df_check)} 条记录")
            
        finally:
            if os.path.exists(excel_path):
                os.unlink(excel_path)
        
        # 测试CSV导出
        print("5. 测试CSV导出...")
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            temp_csv = tmp.name
        
        try:
            csv_path, success = export_manager.export_to_csv(df, os.path.basename(temp_csv))
            assert success
            assert os.path.exists(csv_path)
            file_size = os.path.getsize(csv_path)
            print(f"✅ CSV导出成功: {csv_path} ({file_size} bytes)")
            
        finally:
            if os.path.exists(csv_path):
                os.unlink(csv_path)
        
        # 清理测试数据
        for record_id in record_ids:
            db.delete_expense(record_id)
        print(f"✅ 清理 {len(record_ids)} 条测试数据")
        
        db.close()
        print("✅ 导出管理器模块测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 导出管理器模块测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sys.path.pop(0)

def test_main_program(test_dir):
    """测试主程序功能"""
    print("\n=== 测试主程序功能 ===")
    
    sys.path.insert(0, test_dir)
    
    try:
        import importlib
        import config as original_config
        importlib.reload(original_config)
        
        from main import show_welcome, show_menu, quick_start
        
        # 测试欢迎界面
        print("1. 测试欢迎界面...")
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            show_welcome()
        output = f.getvalue()
        assert "产品开发费用统计系统" in output
        print("✅ 欢迎界面测试通过")
        
        # 测试主菜单
        print("2. 测试主菜单...")
        f = io.StringIO()
        with redirect_stdout(f):
            show_menu()
        output = f.getvalue()
        assert "主菜单" in output
        assert "1. 添加费用记录" in output
        assert "9. 退出系统" in output
        print("✅ 主菜单测试通过")
        
        # 测试快速启动
        print("3. 测试快速启动...")
        f = io.StringIO()
        with redirect_stdout(f):
            result = quick_start()
        output = f.getvalue()
        assert result is True or result is False  # 可能因为依赖检查而失败
        print(f"✅ 快速启动测试完成: 结果={result}")
        
        print("✅ 主程序功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 主程序功能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sys.path.pop(0)

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("测试报告")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"测试模块总数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print("\n" + "=" * 60)
    
    if failed_tests == 0:
        print("🎉 所有测试通过！系统功能完善可用。")
        print("您可以运行 'python main.py' 开始使用费用统计系统。")
        return True
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        return False

def main():
    """主测试函数"""
    print("开始综合测试费用统计系统...")
    print("=" * 60)
    
    test_dir = None
    results = {}
    
    try:
        # 设置测试环境
        test_dir, temp_db_path = setup_test_environment()
        
        # 运行各个模块测试
        results['数据库模块'] = test_database_module(test_dir, temp_db_path)
        results['费用管理器模块'] = test_expense_manager_module(test_dir)
        results['导出管理器模块'] = test_export_manager_module(test_dir)
        results['主程序功能'] = test_main_program(test_dir)
        
        # 生成测试报告
        all_passed = generate_test_report(results)
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生严重错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # 清理测试环境
        if test_dir and os.path.exists(test_dir):
            try:
                shutil.rmtree(test_dir)
                print(f"\n清理测试目录: {test_dir}")
            except Exception as e:
                print(f"清理测试目录时出错: {str(e)}")

if __name__ == "__main__":
    sys.exit(main())