#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品开发费用统计系统 - 主程序
"""
import sys
import os

# 为Windows终端设置UTF-8编码
if sys.platform == 'win32':
    try:
        # 设置控制台编码为UTF-8
        os.system('chcp 65001 > nul')
        # 设置标准输出的编码
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass  # 如果失败，继续运行

from expense_manager import ExpenseManager
from export_manager import ExportManager
from database import get_db

def show_welcome():
    """显示欢迎界面"""
    print("=" * 60)
    print("       产品开发费用统计系统 v1.0")
    print("=" * 60)
    print("功能说明:")
    print("  1. 支持人力、材料、设备等费用统计")
    print("  2. 可自定义计算公式（混合模式）")
    print("  3. 数据持久化存储（SQLite）")
    print("  4. 导出为Excel/CSV格式")
    print("  5. 支持数据统计和分析")
    print("=" * 60)

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("主菜单")
    print("=" * 60)
    print("1. 添加费用记录")
    print("2. 查看所有费用记录")
    print("3. 按类型查看费用记录")
    print("4. 查看费用统计")
    print("5. 导出数据")
    print("6. 添加自定义公式")
    print("7. 删除费用记录")
    print("8. 列出导出文件")
    print("9. 退出系统")
    print("=" * 60)

def main():
    """主程序入口"""
    show_welcome()
    
    # 初始化管理器
    expense_manager = ExpenseManager()
    export_manager = ExportManager()
    
    while True:
        show_menu()
        
        choice = None  # 初始化choice变量
        
        try:
            choice = input("\n请选择操作 [1-9]: ").strip()
            
            if choice == '1':
                expense_manager.add_expense_record()
            
            elif choice == '2':
                expense_manager.view_all_expenses()
            
            elif choice == '3':
                expense_manager.view_expenses_by_type()
            
            elif choice == '4':
                expense_manager.show_statistics()
            
            elif choice == '5':
                export_manager.interactive_export()
            
            elif choice == '6':
                expense_manager.add_custom_formula_interactive()
            
            elif choice == '7':
                expense_manager.delete_expense_record()
            
            elif choice == '8':
                export_manager.list_exports()
            
            elif choice == '9':
                print("\n感谢使用产品开发费用统计系统！")
                print("再见！👋")
                break
            
            else:
                print("无效选择，请输入1-9之间的数字")
        
        except (KeyboardInterrupt, EOFError):
            print("\n\n检测到中断信号，正在退出...")
            break
        
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            print("请重试或联系开发者")
        
        # 等待用户确认继续（只有choice有效且不是退出时才等待）
        if choice and choice != '9':
            try:
                input("\n按Enter键继续...")
            except (KeyboardInterrupt, EOFError):
                print("\n\n跳过等待，继续...")

def quick_start():
    """快速启动指南"""
    print("\n" + "=" * 60)
    print("快速启动指南")
    print("=" * 60)
    print("1. 首次运行会自动创建数据库和表格")
    print("2. 系统已预置以下计算公式:")
    print("   - 人力成本 = 工时 × 时薪")
    print("   - 材料费 = 数量 × 单价")
    print("   - 设备费 = 使用时长 × 费率")
    print("3. 您可以添加自定义公式")
    print("4. 数据保存在 data/expenses.db 文件中")
    print("5. 导出文件保存在 exports/ 目录中")
    print("=" * 60)
    
    # 检查依赖
    print("\n检查依赖包...")
    try:
        import pandas
        import openpyxl
        print("✅ 依赖包检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {str(e)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    # 检查数据库连接
    print("\n检查数据库连接...")
    try:
        db = get_db()
        print("✅ 数据库连接成功")
        db.close()
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        # 快速启动检查
        if quick_start():
            print("\n系统初始化完成，正在启动主程序...")
            main()
        else:
            print("\n系统初始化失败，请检查上述错误信息")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)