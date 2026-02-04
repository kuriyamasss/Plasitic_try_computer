#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品开发费用统计系统 - 主启动程序
"""
import sys
import os
import tkinter as tk

# 为Windows终端设置UTF-8编码
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
    except:
        pass

def main():
    """启动GUI主程序"""
    try:
        # 导入GUI主类
        from project_gui import ProjectExpenseTrackerGUI
        
        # 创建主窗口
        root = tk.Tk()
        
        # 设置窗口属性
        root.title("产品开发费用统计系统 v2.0")
        
        # 创建应用程序实例
        app = ProjectExpenseTrackerGUI(root)
        
        # 启动主循环
        root.mainloop()
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所有依赖：pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # 显示启动信息
    print("=" * 60)
    print("产品开发费用统计系统 v2.0")
    print("=" * 60)
    print("正在启动图形界面...")
    print("如果窗口未显示，请检查系统是否支持Tkinter")
    print("=" * 60)
    
    # 启动主程序
    main()