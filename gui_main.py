#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品开发费用统计系统 - GUI版本
基于Tkinter的图形用户界面
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

# 为Windows终端设置UTF-8编码（虽然GUI不需要，但保持兼容）
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
    except:
        pass

# 导入核心模块
from database import get_db
from expense_manager import ExpenseManager
from export_manager import ExportManager
from config import EXPENSE_TYPES

class ExpenseTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("产品开发费用统计系统 v1.0")
        self.root.geometry("900x600")
        
        # 设置图标（如果有）
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # 初始化管理器
        self.db = get_db()
        self.expense_manager = ExpenseManager()
        self.export_manager = ExportManager()
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面
        self.create_main_interface()
        
        # 加载数据
        self.load_expenses()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出数据", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 数据菜单
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="数据", menu=data_menu)
        data_menu.add_command(label="添加费用记录", command=self.add_expense)
        data_menu.add_command(label="刷新数据", command=self.load_expenses)
        data_menu.add_separator()
        data_menu.add_command(label="查看统计", command=self.show_statistics)
        
        # 公式菜单
        formula_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="公式", menu=formula_menu)
        formula_menu.add_command(label="管理计算公式", command=self.manage_formulas)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_main_interface(self):
        """创建主界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 顶部按钮栏
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 功能按钮
        ttk.Button(button_frame, text="添加记录", command=self.add_expense).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="刷新", command=self.load_expenses).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="删除选中", command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="查看统计", command=self.show_statistics).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="导出数据", command=self.export_data).pack(side=tk.LEFT, padx=2)
        
        # 搜索栏
        search_frame = ttk.Frame(button_frame)
        search_frame.pack(side=tk.RIGHT, padx=10)
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        ttk.Entry(search_frame, textvariable=self.search_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # 数据表格
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建树状视图（表格）
        columns = ('ID', '日期', '项目', '类型', '名称', '数量', '单价', '总金额', '备注')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # 定义列
        column_widths = [50, 80, 100, 80, 120, 60, 80, 100, 150]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, minwidth=50)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # 绑定双击事件
        self.tree.bind('<Double-Button-1>', self.on_item_double_click)
        
        # 底部状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_expenses(self):
        """加载费用记录到表格"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            expenses = self.db.get_all_expenses()
            
            for expense in expenses:
                exp_dict = dict(expense)
                expense_type = EXPENSE_TYPES.get(exp_dict['expense_type'], exp_dict['expense_type'])
                
                values = (
                    exp_dict['id'],
                    exp_dict['expense_date'],
                    exp_dict['project'] or '默认项目',
                    expense_type,
                    exp_dict['name'],
                    exp_dict['quantity'] or '-',
                    exp_dict['unit_price'] or '-',
                    f"{exp_dict['total_amount']:.2f}",
                    exp_dict['notes'] or ''
                )
                self.tree.insert('', tk.END, values=values)
            
            self.status_var.set(f"已加载 {len(expenses)} 条记录")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载数据失败: {str(e)}")
            self.status_var.set("加载数据失败")
    
    def on_search_changed(self, *args):
        """搜索内容改变时的处理"""
        search_text = self.search_var.get().lower()
        
        # 暂时隐藏所有行
        for item in self.tree.get_children():
            self.tree.item(item, tags=('hidden',))
        
        # 显示匹配的行
        if search_text:
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                # 检查是否匹配（所有列）
                match = False
                for value in values:
                    if search_text in str(value).lower():
                        match = True
                        break
                if match:
                    self.tree.item(item, tags=('visible',))
        else:
            # 显示所有行
            for item in self.tree.get_children():
                self.tree.item(item, tags=('visible',))
        
        # 配置标签
        self.tree.tag_configure('hidden', foreground='gray')
        self.tree.tag_configure('visible', foreground='black')
    
    def add_expense(self):
        """打开添加费用记录对话框"""
        dialog = AddExpenseDialog(self.root, self.expense_manager, self.db)
        self.root.wait_window(dialog.dialog)
        
        # 如果添加成功，刷新数据
        if dialog.result:
            self.load_expenses()
            messagebox.showinfo("成功", "费用记录添加成功！")
    
    def delete_selected(self):
        """删除选中的记录"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要删除的记录")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_items)} 条记录吗？"):
            return
        
        try:
            success_count = 0
            for item in selected_items:
                item_id = self.tree.item(item)['values'][0]  # 第一列是ID
                if self.db.delete_expense(item_id):
                    success_count += 1
            
            # 刷新数据
            self.load_expenses()
            messagebox.showinfo("成功", f"已成功删除 {success_count} 条记录")
            
        except Exception as e:
            messagebox.showerror("错误", f"删除记录失败: {str(e)}")
    
    def on_item_double_click(self, event):
        """双击记录时查看详情"""
        selected_items = self.tree.selection()
        if selected_items:
            item_id = self.tree.item(selected_items[0])['values'][0]
            self.view_expense_details(item_id)
    
    def view_expense_details(self, expense_id):
        """查看费用记录详情"""
        try:
            # 从数据库获取完整记录
            expenses = self.db.get_all_expenses()
            expense = None
            for exp in expenses:
                exp_dict = dict(exp)
                if exp_dict['id'] == expense_id:
                    expense = exp_dict
                    break
            
            if expense:
                detail_text = f"费用记录详情 (ID: {expense_id})\n"
                detail_text += "=" * 40 + "\n"
                detail_text += f"类型: {EXPENSE_TYPES.get(expense['expense_type'], expense['expense_type'])}\n"
                detail_text += f"名称: {expense['name']}\n"
                detail_text += f"日期: {expense['expense_date']}\n"
                if expense['quantity']:
                    detail_text += f"数量: {expense['quantity']}\n"
                if expense['unit_price']:
                    detail_text += f"单价: {expense['unit_price']}\n"
                detail_text += f"总金额: {expense['total_amount']:.2f}\n"
                if expense['notes']:
                    detail_text += f"备注: {expense['notes']}\n"
                detail_text += f"创建时间: {expense['created_at']}\n"
                
                messagebox.showinfo("记录详情", detail_text)
        
        except Exception as e:
            messagebox.showerror("错误", f"查看详情失败: {str(e)}")
    
    def show_statistics(self):
        """显示统计信息"""
        try:
            stats = self.db.get_expense_statistics()
            
            stats_text = "费用统计\n"
            stats_text += "=" * 50 + "\n\n"
            
            # 总体统计
            overall = stats['overall']
            if overall:
                stats_text += "📊 总体统计:\n"
                stats_text += f"  总记录数: {overall.get('total_count', 0)}\n"
                stats_text += f"  总费用: {overall.get('grand_total', 0):.2f}\n"
                stats_text += f"  平均费用: {overall.get('avg_amount', 0):.2f}\n"
                if overall.get('earliest_date'):
                    stats_text += f"  最早记录: {overall['earliest_date']}\n"
                if overall.get('latest_date'):
                    stats_text += f"  最新记录: {overall['latest_date']}\n"
                stats_text += "\n"
            
            # 按类型统计
            type_stats = stats['by_type']
            if type_stats:
                stats_text += "📈 按类型统计:\n"
                grand_total = overall.get('grand_total', 1)
                for type_stat in type_stats:
                    expense_type = EXPENSE_TYPES.get(type_stat['expense_type'], type_stat['expense_type'])
                    percentage = (type_stat['total_amount'] / grand_total * 100) if grand_total > 0 else 0
                    stats_text += f"  {expense_type}: {type_stat['count']}条, {type_stat['total_amount']:.2f}元 ({percentage:.1f}%)\n"
                stats_text += "\n"
            
            # 按项目统计
            project_stats = stats['by_project']
            if project_stats:
                stats_text += "📊 按项目统计:\n"
                grand_total = overall.get('grand_total', 1)
                for project_stat in project_stats:
                    project_name = project_stat['project'] or '默认项目'
                    percentage = (project_stat['total_amount'] / grand_total * 100) if grand_total > 0 else 0
                    stats_text += f"  {project_name}: {project_stat['count']}条, {project_stat['total_amount']:.2f}元 ({percentage:.1f}%)\n"
                stats_text += "\n"
            
            messagebox.showinfo("费用统计", stats_text)
        
        except Exception as e:
            messagebox.showerror("错误", f"获取统计信息失败: {str(e)}")
    
    def export_data(self):
        """导出数据"""
        try:
            # 创建导出对话框
            dialog = ExportDialog(self.root)
            self.root.wait_window(dialog.dialog)
            
            # 检查用户是否取消了导出
            if not dialog.result:
                return
            
            # 获取用户选择
            export_format = dialog.format_var.get()
            filename = dialog.filename
            
            # 确保文件名不为空
            if not filename:
                messagebox.showwarning("提示", "请选择保存位置")
                return
            
            # 获取数据
            df = self.export_manager.get_export_data()
            
            if df.empty:
                messagebox.showwarning("提示", "没有数据可以导出")
                return
            
            # 执行导出
            if export_format == 'excel':
                filepath, success = self.export_manager.export_to_excel(df, os.path.basename(filename))
            else:
                filepath, success = self.export_manager.export_to_csv(df, os.path.basename(filename))
            
            if success:
                messagebox.showinfo("成功", f"数据导出成功！\n文件位置: {filepath}")
                self.status_var.set(f"数据已导出到: {os.path.basename(filepath)}")
            else:
                messagebox.showerror("错误", "数据导出失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"导出数据失败: {str(e)}")
    
    def manage_formulas(self):
        """管理计算公式"""
        dialog = FormulaManagerDialog(self.root, self.db, self.expense_manager)
        self.root.wait_window(dialog.dialog)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """产品开发费用统计系统 v1.0 (GUI版)

功能特点:
• 支持多种费用类型统计
• 可自定义计算公式
• 数据持久化存储 (SQLite)
• 导出为Excel/CSV格式
• 完整的统计分析

基于Python + Tkinter开发

使用说明:
1. 点击"添加记录"按钮添加费用
2. 双击记录查看详情
3. 使用"导出数据"功能保存
4. 点击"查看统计"了解费用分布"""
        
        messagebox.showinfo("关于", about_text)
    
    def on_closing(self):
        """关闭窗口时的处理"""
        try:
            self.db.close()
        except:
            pass
        self.root.destroy()

class AddExpenseDialog:
    """添加费用记录对话框"""
    def __init__(self, parent, expense_manager, db):
        self.expense_manager = expense_manager
        self.db = db
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加费用记录")
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_interface()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        """创建对话框界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 费用类型
        ttk.Label(main_frame, text="费用类型:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value=list(EXPENSE_TYPES.keys())[0])
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, 
                                  values=list(EXPENSE_TYPES.keys()), state='readonly')
        type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 项目名称
        ttk.Label(main_frame, text="项目名称:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.project_var = tk.StringVar(value='默认项目')
        
        # 获取现有项目列表
        try:
            projects = self.db.get_all_projects()
            if not projects:
                projects = ['默认项目', '项目A', '项目B', '项目C']
        except Exception as e:
            projects = ['默认项目', '项目A', '项目B', '项目C']
        
        self.project_combo = ttk.Combobox(main_frame, textvariable=self.project_var, 
                                         values=projects, width=28)
        self.project_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 费用名称
        ttk.Label(main_frame, text="费用名称:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=2, column=1, 
                                                                         sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 公式选择
        ttk.Label(main_frame, text="计算公式:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.formula_var = tk.StringVar()
        self.formula_combo = ttk.Combobox(main_frame, textvariable=self.formula_var, state='readonly')
        self.formula_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.formula_combo.bind('<<ComboboxSelected>>', self.on_formula_selected)
        
        # 参数输入框架
        self.param_frame = ttk.Frame(main_frame)
        self.param_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 手动金额输入
        ttk.Label(main_frame, text="或直接输入金额:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.manual_amount_var = tk.StringVar()
        self.manual_amount_entry = ttk.Entry(main_frame, textvariable=self.manual_amount_var, width=20)
        self.manual_amount_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 其他信息
        ttk.Label(main_frame, text="数量 (可选):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.quantity_var, width=20).grid(row=6, column=1, 
                                                                            sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="单价 (可选):").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.unit_price_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.unit_price_var, width=20).grid(row=7, column=1, 
                                                                              sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="日期 (YYYY-MM-DD):").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.date_var, width=20).grid(row=8, column=1, 
                                                                        sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="备注 (可选):").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.notes_var, width=30).grid(row=9, column=1, 
                                                                         sticky=tk.W, pady=5, padx=(10, 0))
        
        # 计算结果显示
        self.result_var = tk.StringVar(value="总金额: 0.00")
        ttk.Label(main_frame, textvariable=self.result_var, font=('Arial', 10, 'bold')).grid(
            row=10, column=0, columnspan=2, pady=15)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="计算", command=self.calculate_amount).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=self.save_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 加载公式
        self.load_formulas()
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
    
    def load_formulas(self):
        """加载公式列表"""
        try:
            formulas = self.db.get_all_formulas()
            formula_list = []
            for formula in formulas:
                formula_dict = dict(formula)
                display_name = formula_dict['display_name']
                if formula_dict['is_custom']:
                    display_name += " [自定义]"
                formula_list.append(display_name)
            
            self.formula_combo['values'] = formula_list
            if formula_list:
                self.formula_combo.current(0)
                self.on_formula_selected()
        
        except Exception as e:
            messagebox.showerror("错误", f"加载公式失败: {str(e)}")
    
    def on_formula_selected(self, event=None):
        """公式选择改变时的处理"""
        # 清空参数输入框
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        selected_formula = self.formula_combo.get()
        if not selected_formula:
            return
        
        try:
            # 获取公式详情
            formulas = self.db.get_all_formulas()
            formula_data = None
            for formula in formulas:
                formula_dict = dict(formula)
                display_name = formula_dict['display_name']
                if formula_dict['is_custom']:
                    display_name += " [自定义]"
                if display_name == selected_formula:
                    formula_data = formula_dict
                    break
            
            if formula_data:
                # 创建参数输入框
                params = formula_data['parameters'].split(',')
                self.param_vars = {}
                
                for i, param in enumerate(params):
                    ttk.Label(self.param_frame, text=f"{param}:").grid(row=i, column=0, sticky=tk.W, pady=2)
                    var = tk.StringVar()
                    var.trace('w', self.calculate_amount)
                    entry = ttk.Entry(self.param_frame, textvariable=var, width=15)
                    entry.grid(row=i, column=1, sticky=tk.W, pady=2, padx=(5, 0))
                    self.param_vars[param] = var
        
        except Exception as e:
            messagebox.showerror("错误", f"加载公式参数失败: {str(e)}")
    
    def calculate_amount(self, *args):
        """计算总金额"""
        try:
            selected_formula = self.formula_combo.get()
            
            # 如果选择了公式
            if selected_formula and hasattr(self, 'param_vars'):
                # 收集参数值
                params = {}
                all_valid = True
                
                for param_name, var in self.param_vars.items():
                    value = var.get().strip()
                    if not value:
                        all_valid = False
                        break
                    try:
                        params[param_name] = float(value)
                    except ValueError:
                        all_valid = False
                        break
                
                if all_valid and params:
                    # 获取公式代号
                    formulas = self.db.get_all_formulas()
                    formula_key = None
                    for formula in formulas:
                        formula_dict = dict(formula)
                        display_name = formula_dict['display_name']
                        if formula_dict['is_custom']:
                            display_name += " [自定义]"
                        if display_name == selected_formula:
                            formula_key = formula_dict['formula_name']
                            break
                    
                    if formula_key:
                        amount = self.expense_manager.calculate_expense(formula_key, params)
                        self.result_var.set(f"总金额: {amount:.2f}")
                        return
            
            # 如果手动输入了金额
            manual_amount = self.manual_amount_var.get().strip()
            if manual_amount:
                try:
                    amount = float(manual_amount)
                    self.result_var.set(f"总金额: {amount:.2f}")
                except ValueError:
                    self.result_var.set("总金额: 0.00")
            
        except Exception as e:
            self.result_var.set("计算错误")
    
    def save_expense(self):
        """保存费用记录"""
        try:
            # 验证必填字段
            if not self.name_var.get().strip():
                messagebox.showwarning("提示", "请输入费用名称")
                return
            
            # 获取总金额
            result_text = self.result_var.get()
            if not result_text.startswith("总金额: "):
                messagebox.showwarning("提示", "请先计算总金额")
                return
            
            try:
                total_amount = float(result_text[5:])
            except ValueError:
                messagebox.showwarning("提示", "总金额格式错误")
                return
            
            # 准备数据
            expense_data = {
                'expense_type': self.type_var.get(),
                'project': self.project_var.get().strip(),
                'name': self.name_var.get().strip(),
                'total_amount': total_amount,
                'notes': self.notes_var.get().strip()
            }
            
            # 可选字段
            quantity = self.quantity_var.get().strip()
            if quantity:
                try:
                    expense_data['quantity'] = float(quantity)
                except ValueError:
                    messagebox.showwarning("提示", "数量格式错误，已忽略")
            
            unit_price = self.unit_price_var.get().strip()
            if unit_price:
                try:
                    expense_data['unit_price'] = float(unit_price)
                except ValueError:
                    messagebox.showwarning("提示", "单价格式错误，已忽略")
            
            date = self.date_var.get().strip()
            if date:
                # 简单日期验证（实际应该更严格）
                if len(date) == 10 and date[4] == '-' and date[7] == '-':
                    expense_data['expense_date'] = date
                else:
                    messagebox.showwarning("提示", "日期格式错误，使用今天日期")
            
            # 保存到数据库
            expense_id = self.db.add_expense(expense_data)
            if expense_id:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "保存失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

class FormulaManagerDialog:
    """公式管理对话框"""
    def __init__(self, parent, db, expense_manager):
        self.db = db
        self.expense_manager = expense_manager
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("管理计算公式")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_interface()
        
        # 加载公式
        self.load_formulas()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        """创建对话框界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 公式列表
        list_frame = ttk.LabelFrame(main_frame, text="公式列表", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 树状视图
        columns = ('名称', '表达式', '参数', '类型')
        self.formula_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.formula_tree.heading(col, text=col)
            self.formula_tree.column(col, width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.formula_tree.yview)
        self.formula_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.formula_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="添加公式", command=self.add_formula).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除公式", command=self.delete_formula).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.load_formulas).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def load_formulas(self):
        """加载公式列表"""
        # 清空现有数据
        for item in self.formula_tree.get_children():
            self.formula_tree.delete(item)
        
        try:
            formulas = self.db.get_all_formulas()
            
            for formula in formulas:
                formula_dict = dict(formula)
                formula_type = "自定义" if formula_dict['is_custom'] else "预定义"
                
                values = (
                    formula_dict['display_name'],
                    formula_dict['expression'],
                    formula_dict['parameters'],
                    formula_type
                )
                self.formula_tree.insert('', tk.END, values=values, tags=(formula_dict['formula_name'],))
        
        except Exception as e:
            messagebox.showerror("错误", f"加载公式失败: {str(e)}")
    
    def add_formula(self):
        """添加新公式"""
        # 这里可以扩展为完整的公式编辑对话框
        # 现在先显示一个简单的提示
        messagebox.showinfo("提示", "添加自定义公式功能将在后续版本中完善。\n\n您可以在命令行版本中使用此功能。")
    
    def delete_formula(self):
        """删除选中的公式"""
        selected_items = self.formula_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要删除的公式")
            return
        
        # 注意：这里只是演示，实际删除需要更多逻辑
        messagebox.showinfo("提示", "删除公式功能将在后续版本中完善。\n\n目前只能删除自定义公式，且需要数据库直接操作。")

class ExportDialog:
    """导出对话框"""
    def __init__(self, parent):
        self.parent = parent
        self.result = False
        self.filename = None
        self.format_var = tk.StringVar(value='excel')
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("导出数据")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_interface()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # 绑定窗口关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def create_interface(self):
        """创建对话框界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 格式选择
        format_frame = ttk.LabelFrame(main_frame, text="选择导出格式", padding="10")
        format_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Excel单选框
        excel_radio = ttk.Radiobutton(format_frame, text="Excel (.xlsx)", 
                                      variable=self.format_var, value='excel')
        excel_radio.pack(side=tk.LEFT, padx=10)
        
        # CSV单选框
        csv_radio = ttk.Radiobutton(format_frame, text="CSV (.csv)", 
                                    variable=self.format_var, value='csv')
        csv_radio.pack(side=tk.LEFT, padx=10)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="选择保存位置", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 文件路径显示
        self.path_var = tk.StringVar(value="请选择保存位置...")
        path_label = ttk.Label(file_frame, textvariable=self.path_var, 
                              relief=tk.SUNKEN, padding="5", width=40)
        path_label.pack(fill=tk.X, padx=(0, 5))
        
        # 选择文件按钮
        select_button = ttk.Button(file_frame, text="浏览...", command=self.select_file)
        select_button.pack(pady=(10, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 导出按钮
        ttk.Button(button_frame, text="导出", command=self.on_export).pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.RIGHT, padx=5)
    
    def select_file(self):
        """选择保存文件"""
        export_format = self.format_var.get()
        file_ext = '.xlsx' if export_format == 'excel' else '.csv'
        file_type = "Excel文件" if export_format == 'excel' else "CSV文件"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            filetypes=[(f"{file_type}", f"*{file_ext}"), ("所有文件", "*.*")],
            title="选择导出位置"
        )
        
        if filename:
            self.filename = filename
            self.path_var.set(os.path.basename(filename))
    
    def on_export(self):
        """导出按钮点击"""
        if not self.filename:
            messagebox.showwarning("提示", "请先选择保存位置")
            return
        
        self.result = True
        self.dialog.destroy()
    
    def on_cancel(self):
        """取消按钮点击"""
        self.result = False
        self.dialog.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()