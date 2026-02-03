#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品开发费用统计系统 - 新版GUI版本（三段式设计）
基于Tkinter的图形用户界面，文件存储架构
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import json
from datetime import datetime

# 为Windows终端设置UTF-8编码
if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
    except:
        pass

# 导入新架构模块
from modules.file_manager import get_file_manager
from modules.expense_calculator import get_calculator
from modules.config import EXPENSE_TYPES

class ProjectExpenseTrackerGUI:
    """新版GUI主类 - 三段式设计"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("产品开发费用统计系统 v2.0")
        self.root.geometry("1000x700")
        
        # 设置图标（如果有）
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # 初始化管理器
        self.file_manager = get_file_manager()
        self.calculator = get_calculator()
        
        # 当前状态
        self.current_page = "projects"  # 当前页面：projects, expense_list, expense_detail
        self.current_project = None     # 当前打开的项目
        
        # 创建三段式布局
        self.create_three_section_layout()
        
        # 加载初始数据
        self.load_projects_list()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_three_section_layout(self):
        """创建三段式布局"""
        
        # ===== 第一段：导航栏和动态按钮区 =====
        self.create_top_section()
        
        # ===== 第二段：主显示区域 =====
        self.create_middle_section()
        
        # ===== 第三段：状态/统计信息区 =====
        self.create_bottom_section()
        
        # 配置网格权重，使中间区域可扩展
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)  # 中间区域可扩展
    
    def create_top_section(self):
        """创建顶部区域（第一段）"""
        # 顶部主框架
        top_frame = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 5))
        
        # 配置网格权重
        top_frame.columnconfigure(1, weight=1)
        
        # 1. 菜单栏（左侧）
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入项目", command=self.import_project)
        file_menu.add_command(label="导出项目", command=self.export_project)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 数据菜单
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="数据", menu=data_menu)
        data_menu.add_command(label="自定义数据类型", command=self.manage_custom_types)
        data_menu.add_command(label="刷新数据", command=self.refresh_current_page)
        
        # 公式菜单
        formula_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="公式", menu=formula_menu)
        formula_menu.add_command(label="管理计算公式", command=self.manage_formulas)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
        # 2. 动态按钮区（右侧）
        self.dynamic_button_frame = ttk.Frame(top_frame)
        self.dynamic_button_frame.grid(row=0, column=1, sticky=tk.E, padx=10, pady=5)
        
        # 初始显示项目管理按钮
        self.update_dynamic_buttons()
    
    def create_middle_section(self):
        """创建中间区域（第二段）"""
        # 中间主框架
        middle_frame = ttk.Frame(self.root)
        middle_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # 配置网格权重
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.rowconfigure(0, weight=1)
        
        # 创建笔记本（选项卡）控件，用于切换不同页面
        self.notebook = ttk.Notebook(middle_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 项目列表页面
        self.projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.projects_frame, text="项目管理")
        
        # 费用管理页面
        self.expenses_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.expenses_frame, text="费用管理", state='disabled')  # 初始禁用
        
        # 创建两个页面的内容
        self.create_projects_page()
        self.create_expenses_page()
        
        # 绑定选项卡切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_bottom_section(self):
        """创建底部区域（第三段）"""
        # 底部主框架
        bottom_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.S), pady=(5, 0))
        
        # 配置网格权重
        bottom_frame.columnconfigure(0, weight=1)
        
        # 左侧：状态信息
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_label = ttk.Label(bottom_frame, textvariable=self.status_var, 
                                relief=tk.SUNKEN, padding=(5, 2))
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        # 右侧：统计信息
        self.stats_var = tk.StringVar()
        self.stats_var.set("请选择项目")
        stats_label = ttk.Label(bottom_frame, textvariable=self.stats_var,
                               relief=tk.SUNKEN, padding=(5, 2), foreground='blue')
        stats_label.grid(row=0, column=1, sticky=tk.E, padx=(5, 10), pady=5)
    
    def create_projects_page(self):
        """创建项目管理页面"""
        # 主框架
        main_frame = ttk.Frame(self.projects_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部：项目操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="新建项目", command=self.create_new_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新列表", command=self.load_projects_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除项目", command=self.delete_selected_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重命名项目", command=self.rename_selected_project).pack(side=tk.LEFT, padx=5)
        
        # 项目列表表格
        list_frame = ttk.LabelFrame(main_frame, text="项目列表", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树状视图
        columns = ('名称', '创建时间', '最后修改', '费用记录数', '总金额', '描述')
        self.projects_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 定义列
        column_widths = [150, 120, 120, 100, 100, 200]
        for col, width in zip(columns, column_widths):
            self.projects_tree.heading(col, text=col)
            self.projects_tree.column(col, width=width, minwidth=50)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.projects_tree.yview)
        self.projects_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.projects_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 绑定双击事件（打开项目）
        self.projects_tree.bind('<Double-Button-1>', self.on_project_double_click)
    
    def create_expenses_page(self):
        """创建费用管理页面"""
        # 主框架
        main_frame = ttk.Frame(self.expenses_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 顶部：项目信息显示
        self.project_info_frame = ttk.LabelFrame(main_frame, text="项目信息", padding="10")
        self.project_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 项目名称标签
        self.project_name_var = tk.StringVar(value="未选择项目")
        ttk.Label(self.project_info_frame, textvariable=self.project_name_var, 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        # 返回项目列表按钮
        ttk.Button(self.project_info_frame, text="← 返回项目列表", 
                  command=self.back_to_projects).grid(row=0, column=1, sticky=tk.E)
        
        # 配置网格权重
        self.project_info_frame.columnconfigure(0, weight=1)
        
        # 中间：费用记录表格
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建树状视图
        columns = ('ID', '日期', '类型', '名称', '数量', '单价', '总金额', '备注')
        self.expenses_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # 定义列
        column_widths = [50, 100, 80, 150, 60, 80, 100, 200]
        for col, width in zip(columns, column_widths):
            self.expenses_tree.heading(col, text=col)
            self.expenses_tree.column(col, width=width, minwidth=50)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.expenses_tree.yview)
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.expenses_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # 绑定双击事件（查看详情）
        self.expenses_tree.bind('<Double-Button-1>', self.on_expense_double_click)
    
    def update_dynamic_buttons(self):
        """更新动态按钮区域，根据当前页面显示不同的按钮"""
        # 清空现有按钮
        for widget in self.dynamic_button_frame.winfo_children():
            widget.destroy()
        
        if self.current_page == "projects":
            # 项目管理页面的按钮
            ttk.Button(self.dynamic_button_frame, text="新建项目", 
                      command=self.create_new_project).pack(side=tk.LEFT, padx=2)
            ttk.Button(self.dynamic_button_frame, text="导入项目", 
                      command=self.import_project).pack(side=tk.LEFT, padx=2)
            
        elif self.current_page == "expense_list":
            # 费用管理页面的按钮
            ttk.Button(self.dynamic_button_frame, text="添加费用", 
                      command=self.add_expense).pack(side=tk.LEFT, padx=2)
            ttk.Button(self.dynamic_button_frame, text="删除选中", 
                      command=self.delete_selected_expense).pack(side=tk.LEFT, padx=2)
            ttk.Button(self.dynamic_button_frame, text="查看统计", 
                      command=self.show_statistics).pack(side=tk.LEFT, padx=2)
            ttk.Button(self.dynamic_button_frame, text="导出数据", 
                      command=self.export_data).pack(side=tk.LEFT, padx=2)
    
    def on_tab_changed(self, event):
        """选项卡切换事件处理"""
        selected_tab = self.notebook.index(self.notebook.select())
        
        if selected_tab == 0:  # 项目管理
            self.current_page = "projects"
            self.update_dynamic_buttons()
            self.stats_var.set("项目管理模式")
            
        elif selected_tab == 1:  # 费用管理
            self.current_page = "expense_list"
            self.update_dynamic_buttons()
            self.update_stats_display()
    
    def load_projects_list(self):
        """加载项目列表到表格"""
        # 清空现有数据
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
        
        try:
            projects = self.file_manager.get_all_projects()
            
            for project in projects:
                values = (
                    project['name'],
                    project['created_date'],
                    project['last_modified'],
                    project['expense_count'],
                    f"{project['total_amount']:.2f}",
                    project['description']
                )
                self.projects_tree.insert('', tk.END, values=values, tags=(project['name'],))
            
            self.status_var.set(f"已加载 {len(projects)} 个项目")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载项目列表失败: {str(e)}")
            self.status_var.set("加载项目列表失败")
    
    
    
    def create_new_project(self):
        """创建新项目"""
        dialog = CreateProjectDialog(self.root, self.file_manager)
        self.root.wait_window(dialog.dialog)
        
        # 如果创建成功，刷新列表
        if dialog.result:
            self.load_projects_list()
            messagebox.showinfo("成功", "项目创建成功！")
    
    def delete_selected_project(self):
        """删除选中的项目"""
        selected_items = self.projects_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要删除的项目")
            return
        
        project_name = self.projects_tree.item(selected_items[0])['values'][0]
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除项目 '{project_name}' 吗？\n\n此操作无法撤销！"):
            return
        
        try:
            if self.file_manager.delete_project(project_name):
                self.load_projects_list()
                messagebox.showinfo("成功", f"项目 '{project_name}' 删除成功")
            else:
                messagebox.showerror("错误", "删除项目失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"删除项目失败: {str(e)}")
    
    def rename_selected_project(self):
        """重命名选中的项目"""
        selected_items = self.projects_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要重命名的项目")
            return
        
        old_name = self.projects_tree.item(selected_items[0])['values'][0]
        
        # 获取新名称
        new_name = tk.simpledialog.askstring("重命名项目", "请输入新项目名称:", 
                                           initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
        
        try:
            if self.file_manager.rename_project(old_name, new_name):
                self.load_projects_list()
                messagebox.showinfo("成功", f"项目重命名成功: {old_name} -> {new_name}")
            else:
                messagebox.showerror("错误", "重命名项目失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"重命名项目失败: {str(e)}")
    
    def on_project_double_click(self, event):
        """双击项目时打开项目"""
        selected_items = self.projects_tree.selection()
        if selected_items:
            project_name = self.projects_tree.item(selected_items[0])['values'][0]
            self.open_project(project_name)
    
    def open_project(self, project_name):
        """打开项目并切换到费用管理页面"""
        try:
            # 打开项目
            project_data = self.file_manager.open_project(project_name)
            if not project_data:
                raise ValueError("打开项目失败")
            
            self.current_project = project_name
            
            # 更新项目信息显示
            self.project_name_var.set(f"当前项目: {project_name}")
            
            # 切换到费用管理页面
            self.notebook.tab(1, state='normal')  # 启用费用管理选项卡
            self.notebook.select(1)  # 切换到费用管理
            
            # 加载费用记录
            self.load_expenses()
            
            # 更新状态
            self.status_var.set(f"已打开项目: {project_name}")
            
        except Exception as e:
            messagebox.showerror("错误", f"打开项目失败: {str(e)}")
    
    def back_to_projects(self):
        """返回到项目管理页面"""
        # 关闭当前项目
        if self.current_project:
            self.file_manager.close_project()
            self.current_project = None
        
        # 切换到项目管理页面
        self.notebook.select(0)
        self.project_name_var.set("未选择项目")
        self.status_var.set("已返回项目管理")
    
    def load_expenses(self):
        """加载费用记录到表格"""
        # 清空现有数据
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        try:
            expenses = self.file_manager.get_all_expenses()
            
            for expense in expenses:
                expense_type = EXPENSE_TYPES.get(expense.get('expense_type', 'other'), 
                                               expense.get('expense_type', '其他费用'))
                
                values = (
                    expense['id'],
                    expense.get('date', expense.get('expense_date', '')),
                    expense_type,
                    expense['name'],
                    expense.get('quantity', '') or '-',
                    expense.get('unit_price', '') or '-',
                    f"{expense['total_amount']:.2f}",
                    expense.get('notes', '') or ''
                )
                self.expenses_tree.insert('', tk.END, values=values, tags=(expense['id'],))
            
            # 更新统计显示
            self.update_stats_display()
            
        except Exception as e:
            messagebox.showerror("错误", f"加载费用记录失败: {str(e)}")
            self.status_var.set("加载费用记录失败")
    
    def update_stats_display(self):
        """更新底部统计信息显示"""
        if not self.current_project:
            self.stats_var.set("请选择项目")
            return
        
        try:
            stats = self.file_manager.get_expense_statistics()
            
            if stats and 'overall' in stats:
                overall = stats['overall']
                self.stats_var.set(f"当前项目: {self.current_project} | 记录数: {overall['total_count']} | 总金额: {overall['grand_total']:.2f}")
            else:
                self.stats_var.set(f"当前项目: {self.current_project} | 暂无费用记录")
        
        except Exception as e:
            self.stats_var.set(f"当前项目: {self.current_project} | 统计信息获取失败")
    
    def add_expense(self):
        """添加费用记录"""
        if not self.current_project:
            messagebox.showwarning("提示", "请先打开一个项目")
            return
        
        dialog = AddExpenseDialog(self.root, self.file_manager, self.calculator)
        self.root.wait_window(dialog.dialog)
        
        # 如果添加成功，刷新数据
        if dialog.result:
            self.load_expenses()
            messagebox.showinfo("成功", "费用记录添加成功！")
    
    def delete_selected_expense(self):
        """删除选中的费用记录"""
        if not self.current_project:
            messagebox.showwarning("提示", "请先打开一个项目")
            return
        
        selected_items = self.expenses_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要删除的费用记录")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_items)} 条费用记录吗？"):
            return
        
        try:
            success_count = 0
            for item in selected_items:
                expense_id = self.expenses_tree.item(item)['values'][0]  # 第一列是ID
                if self.file_manager.delete_expense(expense_id):
                    success_count += 1
            
            # 刷新数据
            self.load_expenses()
            messagebox.showinfo("成功", f"已成功删除 {success_count} 条费用记录")
            
        except Exception as e:
            messagebox.showerror("错误", f"删除费用记录失败: {str(e)}")
    
    def on_expense_double_click(self, event):
        """双击费用记录时查看详情"""
        if not self.current_project:
            return
        
        selected_items = self.expenses_tree.selection()
        if selected_items:
            expense_id = self.expenses_tree.item(selected_items[0])['values'][0]
            self.view_expense_details(expense_id)
    
    def view_expense_details(self, expense_id):
        """查看费用记录详情"""
        try:
            expense = self.file_manager.get_expense_by_id(expense_id)
            if not expense:
                messagebox.showwarning("提示", "找不到该费用记录")
                return
            
            detail_text = f"费用记录详情 (ID: {expense_id})\n"
            detail_text += "=" * 40 + "\n"
            detail_text += f"类型: {EXPENSE_TYPES.get(expense.get('expense_type', 'other'), expense.get('expense_type', '其他费用'))}\n"
            detail_text += f"名称: {expense.get('name', '')}\n"
            detail_text += f"日期: {expense.get('date', expense.get('expense_date', ''))}\n"
            
            if expense.get('quantity'):
                detail_text += f"数量: {expense['quantity']}\n"
            if expense.get('unit_price'):
                detail_text += f"单价: {expense['unit_price']}\n"
            
            detail_text += f"总金额: {expense.get('total_amount', 0):.2f}\n"
            
            if expense.get('notes'):
                detail_text += f"备注: {expense['notes']}\n"
            
            detail_text += f"创建时间: {expense.get('created_at', '')}\n"
            
            messagebox.showinfo("记录详情", detail_text)
        
        except Exception as e:
            messagebox.showerror("错误", f"查看详情失败: {str(e)}")
    
    def show_statistics(self):
        """显示统计信息"""
        if not self.current_project:
            messagebox.showwarning("提示", "请先打开一个项目")
            return
        
        try:
            stats = self.file_manager.get_expense_statistics()
            
            if not stats or 'overall' not in stats:
                messagebox.showinfo("统计信息", "暂无统计数据")
                return
            
            stats_text = f"项目: {self.current_project}\n"
            stats_text += "=" * 40 + "\n\n"
            
            overall = stats['overall']
            stats_text += "📊 总体统计:\n"
            stats_text += f"  总记录数: {overall.get('total_count', 0)}\n"
            stats_text += f"  总费用: {overall.get('grand_total', 0):.2f}\n"
            stats_text += f"  平均费用: {overall.get('avg_amount', 0):.2f}\n"
            stats_text += "\n"
            
            if stats['by_type']:
                stats_text += "📈 按类型统计:\n"
                grand_total = overall.get('grand_total', 1)
                for type_stat in stats['by_type']:
                    expense_type = type_stat['expense_type']
                    percentage = (type_stat['total_amount'] / grand_total * 100) if grand_total > 0 else 0
                    stats_text += f"  {expense_type}: {type_stat['count']}条, {type_stat['total_amount']:.2f}元 ({percentage:.1f}%)\n"
                stats_text += "\n"
            
            if stats['by_custom_type']:
                stats_text += "🏷️  按自定义类型统计:\n"
                for custom_stat in stats['by_custom_type']:
                    stats_text += f"  {custom_stat['type_name']}: {custom_stat['count']}条, {custom_stat['total_amount']:.2f}元\n"
            
            messagebox.showinfo("费用统计", stats_text)
        
        except Exception as e:
            messagebox.showerror("错误", f"获取统计信息失败: {str(e)}")
    
    def import_project(self):
        """导入项目"""
        try:
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择项目文件",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir=os.path.abspath(".")
            )
            
            if not file_path:
                return
            
            # 检查是否为目标目录下的项目文件
            filename = os.path.basename(file_path)
            if not filename.endswith(".json"):
                if not messagebox.askyesno("确认", "选择的文件不是JSON格式，是否继续导入？"):
                    return
            
            # 获取项目名称（从文件名或文件内容中读取）
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                project_name = import_data.get('project_info', {}).get('name')
                if not project_name:
                    # 从文件名提取项目名称
                    project_name = os.path.splitext(filename)[0]
            except:
                project_name = os.path.splitext(filename)[0]
            
            # 检查是否已存在同名项目
            if self.file_manager.project_exists(project_name):
                choice = messagebox.askyesnocancel("项目已存在", 
                    f"项目 '{project_name}' 已存在。请选择：\n"
                    f"• 是(Y): 覆盖现有项目\n"
                    f"• 否(N): 重命名项目\n"
                    f"• 取消: 放弃导入")
                
                if choice is None:  # 取消
                    return
                elif choice:  # 是 - 覆盖
                    # 删除现有项目
                    self.file_manager.delete_project(project_name)
                else:  # 否 - 重命名
                    new_name = tk.simpledialog.askstring("重命名项目", 
                        f"请输入新项目名称:", initialvalue=f"{project_name}_导入")
                    if not new_name or new_name == project_name:
                        return
                    project_name = new_name
            
            # 执行导入
            if self.file_manager.import_project(file_path):
                self.load_projects_list()
                self.status_var.set(f"导入项目成功: {project_name}")
                messagebox.showinfo("成功", f"项目 '{project_name}' 导入成功！")
            else:
                messagebox.showerror("错误", "导入项目失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"导入项目失败: {str(e)}")
    
    def export_project(self):
        """导出项目"""
        try:
            # 检查是否有项目选择
            if not self.current_page == "projects":
                messagebox.showwarning("提示", "请在项目管理页面选择要导出的项目")
                return
            
            selected_items = self.projects_tree.selection()
            if not selected_items:
                messagebox.showwarning("提示", "请先选择要导出的项目")
                return
            
            project_name = self.projects_tree.item(selected_items[0])['values'][0]
            
            # 打开文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title="导出项目文件",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialfile=f"{project_name}_备份.json",
                initialdir=os.path.abspath(".")
            )
            
            if not file_path:
                return
            
            # 执行导出
            if self.file_manager.export_project(project_name, file_path):
                self.status_var.set(f"导出项目成功: {project_name}")
                messagebox.showinfo("成功", f"项目 '{project_name}' 导出成功！\n保存到: {file_path}")
            else:
                messagebox.showerror("错误", "导出项目失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"导出项目失败: {str(e)}")
    
    def export_data(self):
        """导出数据"""
        if not self.current_project:
            messagebox.showwarning("提示", "请先打开一个项目")
            return
        
        # TODO: 实现导出数据功能
        messagebox.showinfo("提示", "导出数据功能将在后续版本中实现")
    
    def manage_custom_types(self):
        """管理自定义数据类型"""
        if not self.current_project:
            messagebox.showwarning("提示", "请先打开一个项目")
            return
        
        dialog = CustomTypeManagementDialog(self.root, self.file_manager)
        self.root.wait_window(dialog.dialog)
        
        # 如果管理成功，可能需要刷新相关数据
        if dialog.result:
            self.status_var.set("自定义类型已更新")
            # 刷新费用类型选择（如果需要）
            if self.current_page == "expense_list":
                # 重新加载费用记录，因为类型显示可能会改变
                self.load_expenses()
    
    def manage_formulas(self):
        """管理计算公式"""
        if not self.current_project:
            messagebox.showwarning("提示", "请先打开一个项目")
            return
        
        dialog = FormulaManagementDialog(self.root, self.file_manager)
        self.root.wait_window(dialog.dialog)
        
        # 如果管理成功，可能需要刷新相关数据
        if dialog.result:
            self.status_var.set("计算公式已更新")
            # 刷新公式选择（如果需要）
            if self.current_page == "expense_list":
                # 重新加载费用记录对话框中的公式列表
                # 这里可以提示用户重新打开添加费用对话框
                pass
    
    def refresh_current_page(self):
        """刷新当前页面"""
        if self.current_page == "projects":
            self.load_projects_list()
            self.status_var.set("项目列表已刷新")
        elif self.current_page == "expense_list" and self.current_project:
            self.load_expenses()
            self.status_var.set("费用记录已刷新")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """产品开发费用统计系统 v2.0 (文件存储版)

功能特点:
• 基于文件的项目管理（JSON格式）
• 三段式GUI设计，操作更直观
• 支持多项目管理
• 可自定义费用类型和计算公式
• 完整的统计分析功能

基于Python + Tkinter开发

使用说明:
1. 在项目管理页面创建或打开项目
2. 在费用管理页面添加和管理费用记录
3. 使用统计功能了解费用分布
4. 支持导入导出项目文件"""
        
        messagebox.showinfo("关于", about_text)
    
    def on_closing(self):
        """关闭窗口时的处理"""
        try:
            if self.current_project:
                self.file_manager.close_project()
        except:
            pass
        self.root.destroy()

# ===== 对话框类 =====

class CreateProjectDialog:
    """创建项目对话框"""
    def __init__(self, parent, file_manager):
        self.file_manager = file_manager
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("创建新项目")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_interface()
        
        # 居中显示
        self.center_dialog(parent)
    
    def create_interface(self):
        """创建对话框界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 项目名称
        ttk.Label(main_frame, text="项目名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, 
                                                                        sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 项目描述
        ttk.Label(main_frame, text="项目描述:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.desc_var, width=30).grid(row=1, column=1, 
                                                                        sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="创建", command=self.create_project).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
    
    def center_dialog(self, parent):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_project(self):
        """创建项目"""
        try:
            project_name = self.name_var.get().strip()
            description = self.desc_var.get().strip()
            
            if not project_name:
                messagebox.showwarning("提示", "请输入项目名称")
                return
            
            if self.file_manager.create_project(project_name, description):
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "创建项目失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"创建项目失败: {str(e)}")

class AddExpenseDialog:
    """添加费用记录对话框"""
    def __init__(self, parent, file_manager, calculator):
        self.file_manager = file_manager
        self.calculator = calculator
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加费用记录")
        self.dialog.geometry("500x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_interface()
        
        # 居中显示
        self.center_dialog(parent)
    
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
        
        # 费用名称
        ttk.Label(main_frame, text="费用名称:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=1, column=1, 
                                                                        sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 公式选择
        ttk.Label(main_frame, text="计算公式:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.formula_var = tk.StringVar()
        self.formula_combo = ttk.Combobox(main_frame, textvariable=self.formula_var, state='readonly')
        self.formula_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.formula_combo.bind('<<ComboboxSelected>>', self.on_formula_selected)
        
        # 参数输入框架
        self.param_frame = ttk.Frame(main_frame)
        self.param_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 手动金额输入
        ttk.Label(main_frame, text="或直接输入金额:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.manual_amount_var = tk.StringVar()
        self.manual_amount_entry = ttk.Entry(main_frame, textvariable=self.manual_amount_var, width=20)
        self.manual_amount_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 其他信息
        ttk.Label(main_frame, text="数量 (可选):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.quantity_var, width=20).grid(row=5, column=1, 
                                                                            sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="单价 (可选):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.unit_price_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.unit_price_var, width=20).grid(row=6, column=1, 
                                                                              sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="日期 (YYYY-MM-DD):").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.date_var, width=20).grid(row=7, column=1, 
                                                                        sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="备注 (可选):").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.notes_var, width=30).grid(row=8, column=1, 
                                                                         sticky=tk.W, pady=5, padx=(10, 0))
        
        # 计算结果显示
        self.result_var = tk.StringVar(value="总金额: 0.00")
        ttk.Label(main_frame, textvariable=self.result_var, font=('Arial', 10, 'bold')).grid(
            row=9, column=0, columnspan=2, pady=15)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="计算", command=self.calculate_amount).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=self.save_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 加载公式
        self.load_formulas()
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
    
    def center_dialog(self, parent):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def load_formulas(self):
        """加载公式列表"""
        try:
            formulas = self.file_manager.get_all_formulas()
            formula_list = []
            for formula in formulas:
                formula_name = formula.get('name', '未命名公式')
                if formula.get('is_custom', False):
                    formula_name += " [自定义]"
                formula_list.append(formula_name)
            
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
            formulas = self.file_manager.get_all_formulas()
            formula_data = None
            for formula in formulas:
                formula_name = formula.get('name', '未命名公式')
                if formula.get('is_custom', False):
                    formula_name += " [自定义]"
                
                if formula_name == selected_formula:
                    formula_data = formula
                    break
            
            if formula_data and 'params' in formula_data:
                # 创建参数输入框
                params = formula_data['params']
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
                    # 获取公式表达式
                    formulas = self.file_manager.get_all_formulas()
                    formula_expression = None
                    for formula in formulas:
                        formula_name = formula.get('name', '未命名公式')
                        if formula.get('is_custom', False):
                            formula_name += " [自定义]"
                        
                        if formula_name == selected_formula:
                            formula_expression = formula.get('expression')
                            break
                    
                    if formula_expression:
                        amount = self.calculator.calculate_expense(formula_expression, params)
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
            
            # 如果输入了数量和单价
            quantity_str = self.quantity_var.get().strip()
            unit_price_str = self.unit_price_var.get().strip()
            if quantity_str and unit_price_str:
                try:
                    quantity = float(quantity_str)
                    unit_price = float(unit_price_str)
                    amount = quantity * unit_price
                    self.result_var.set(f"总金额: {amount:.2f}")
                except ValueError:
                    pass
            
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
                # 简单日期验证
                if len(date) == 10 and date[4] == '-' and date[7] == '-':
                    expense_data['date'] = date
                else:
                    messagebox.showwarning("提示", "日期格式错误，已忽略")
            
            # 保存到文件
            expense_id = self.file_manager.add_expense(expense_data)
            if expense_id:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "保存失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

class CustomTypeManagementDialog:
    """自定义类型管理对话框"""
    def __init__(self, parent, file_manager):
        self.file_manager = file_manager
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("自定义费用类型管理")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_interface()
        
        # 居中显示
        self.center_dialog(parent)
        
        # 加载现有类型
        self.load_custom_types()
    
    def create_interface(self):
        """创建对话框界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：类型列表
        list_frame = ttk.LabelFrame(main_frame, text="自定义费用类型列表", padding="10")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 创建树状视图
        columns = ('ID', '名称', '描述')
        self.custom_types_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # 定义列
        column_widths = [50, 100, 200]
        for col, width in zip(columns, column_widths):
            self.custom_types_tree.heading(col, text=col)
            self.custom_types_tree.column(col, width=width, minwidth=50)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.custom_types_tree.yview)
        self.custom_types_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.custom_types_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 右侧：操作区域
        operation_frame = ttk.LabelFrame(main_frame, text="操作", padding="10")
        operation_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 新增类型按钮
        ttk.Button(operation_frame, text="新增类型", 
                  command=self.add_custom_type).pack(fill=tk.X, pady=5)
        ttk.Button(operation_frame, text="编辑类型", 
                  command=self.edit_selected_type).pack(fill=tk.X, pady=5)
        ttk.Button(operation_frame, text="删除类型", 
                  command=self.delete_selected_type).pack(fill=tk.X, pady=5)
        ttk.Button(operation_frame, text="刷新列表", 
                  command=self.load_custom_types).pack(fill=tk.X, pady=5)
        
        ttk.Separator(operation_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Button(operation_frame, text="完成", 
                  command=self.dialog.destroy).pack(fill=tk.X, pady=5)
        
        # 绑定双击事件（编辑类型）
        self.custom_types_tree.bind('<Double-Button-1>', lambda e: self.edit_selected_type())
    
    def center_dialog(self, parent):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def load_custom_types(self):
        """加载自定义类型列表"""
        # 清空现有数据
        for item in self.custom_types_tree.get_children():
            self.custom_types_tree.delete(item)
        
        try:
            custom_types = self.file_manager.get_all_custom_expense_types()
            
            for custom_type in custom_types:
                values = (
                    custom_type.get('id', ''),
                    custom_type.get('name', ''),
                    custom_type.get('description', '')
                )
                self.custom_types_tree.insert('', tk.END, values=values, tags=(custom_type.get('id', ''),))
        
        except Exception as e:
            messagebox.showerror("错误", f"加载自定义类型失败: {str(e)}")
    
    def add_custom_type(self):
        """添加自定义类型"""
        dialog = CustomTypeEditDialog(self.dialog, self.file_manager)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.load_custom_types()
            self.result = True
    
    def edit_selected_type(self):
        """编辑选中的类型"""
        selected_items = self.custom_types_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要编辑的类型")
            return
        
        type_id = self.custom_types_tree.item(selected_items[0])['values'][0]
        
        # 获取类型详情
        custom_types = self.file_manager.get_all_custom_expense_types()
        type_data = None
        for custom_type in custom_types:
            if custom_type.get('id') == type_id:
                type_data = custom_type
                break
        
        if not type_data:
            messagebox.showerror("错误", "找不到选中的类型")
            return
        
        dialog = CustomTypeEditDialog(self.dialog, self.file_manager, type_data)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.load_custom_types()
            self.result = True
    
    def delete_selected_type(self):
        """删除选中的类型"""
        selected_items = self.custom_types_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要删除的类型")
            return
        
        type_id = self.custom_types_tree.item(selected_items[0])['values'][0]
        type_name = self.custom_types_tree.item(selected_items[0])['values'][1]
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除类型 '{type_name}' 吗？\n\n此操作无法撤销！"):
            return
        
        try:
            # TODO: 实现删除自定义类型的功能
            # 这里需要文件管理器支持删除自定义类型
            messagebox.showinfo("提示", "删除功能将在后续版本中实现")
            # self.result = True
        except Exception as e:
            messagebox.showerror("错误", f"删除类型失败: {str(e)}")

class CustomTypeEditDialog:
    """自定义类型编辑对话框"""
    def __init__(self, parent, file_manager, type_data=None):
        self.file_manager = file_manager
        self.type_data = type_data  # 如果为None，则是新增；否则是编辑
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑自定义费用类型" if type_data else "新增自定义费用类型")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_interface()
        
        # 居中显示
        self.center_dialog(parent)
        
        # 如果是编辑模式，填充数据
        if type_data:
            self.load_type_data()
    
    def create_interface(self):
        """创建对话框界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 类型名称
        ttk.Label(main_frame, text="类型名称:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, 
                                                                        sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # 类型描述
        ttk.Label(main_frame, text="类型描述:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(main_frame, textvariable=self.desc_var, width=30)
        desc_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # 费用分类（可选）
        ttk.Label(main_frame, text="关联费用分类:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.category_var = tk.StringVar(value=list(EXPENSE_TYPES.keys())[0])
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                      values=list(EXPENSE_TYPES.keys()), state='readonly')
        category_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_custom_type).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
    
    def center_dialog(self, parent):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def load_type_data(self):
        """加载类型数据到界面"""
        if self.type_data:
            self.name_var.set(self.type_data.get('name', ''))
            self.desc_var.set(self.type_data.get('description', ''))
            self.category_var.set(self.type_data.get('category', list(EXPENSE_TYPES.keys())[0]))
    
    def save_custom_type(self):
        """保存自定义类型"""
        try:
            # 验证必填字段
            name = self.name_var.get().strip()
            if not name:
                messagebox.showwarning("提示", "请输入类型名称")
                return
            
            description = self.desc_var.get().strip()
            category = self.category_var.get()
            
            type_data = {
                'name': name,
                'description': description,
                'category': category
            }
            
            # 保存到文件管理器
            if self.type_data:  # 编辑模式
                # TODO: 实现更新自定义类型的功能
                messagebox.showinfo("提示", "更新功能将在后续版本中实现")
                self.result = False
            else:  # 新增模式
                type_id = self.file_manager.add_custom_expense_type(type_data)
                if type_id:
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("错误", "保存失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

class FormulaManagementDialog:
    """公式管理对话框"""
    def __init__(self, parent, file_manager):
        self.file_manager = file_manager
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("计算公式管理")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_interface()
        
        # 居中显示
        self.center_dialog(parent)
        
        # 加载现有公式
        self.load_formulas()
    
    def create_interface(self):
        """创建对话框界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：公式列表
        list_frame = ttk.LabelFrame(main_frame, text="计算公式列表", padding="10")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 创建树状视图
        columns = ('ID', '名称', '表达式', '参数', '描述')
        self.formulas_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # 定义列
        column_widths = [80, 100, 120, 80, 150]
        for col, width in zip(columns, column_widths):
            self.formulas_tree.heading(col, text=col)
            self.formulas_tree.column(col, width=width, minwidth=50)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.formulas_tree.yview)
        self.formulas_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.formulas_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 右侧：操作区域
        operation_frame = ttk.LabelFrame(main_frame, text="操作", padding="10")
        operation_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 新增公式按钮
        ttk.Button(operation_frame, text="新增公式", 
                  command=self.add_formula).pack(fill=tk.X, pady=5)
        ttk.Button(operation_frame, text="编辑公式", 
                  command=self.edit_selected_formula).pack(fill=tk.X, pady=5)
        ttk.Button(operation_frame, text="删除公式", 
                  command=self.delete_selected_formula).pack(fill=tk.X, pady=5)
        ttk.Button(operation_frame, text="刷新列表", 
                  command=self.load_formulas).pack(fill=tk.X, pady=5)
        
        ttk.Separator(operation_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Button(operation_frame, text="完成", 
                  command=self.dialog.destroy).pack(fill=tk.X, pady=5)
        
        # 绑定双击事件（编辑公式）
        self.formulas_tree.bind('<Double-Button-1>', lambda e: self.edit_selected_formula())
    
    def center_dialog(self, parent):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def load_formulas(self):
        """加载公式列表"""
        # 清空现有数据
        for item in self.formulas_tree.get_children():
            self.formulas_tree.delete(item)
        
        try:
            formulas = self.file_manager.get_all_formulas()
            
            for formula in formulas:
                params_str = ', '.join(formula.get('params', []))
                formula_type = "自定义" if formula.get('is_custom', False) else "预定义"
                
                values = (
                    formula.get('id', ''),
                    f"{formula.get('name', '')} [{formula_type}]",
                    formula.get('expression', ''),
                    params_str,
                    formula.get('description', '')
                )
                self.formulas_tree.insert('', tk.END, values=values, tags=(formula.get('id', ''),))
        
        except Exception as e:
            messagebox.showerror("错误", f"加载公式失败: {str(e)}")
    
    def add_formula(self):
        """添加自定义公式"""
        dialog = FormulaEditDialog(self.dialog, self.file_manager)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.load_formulas()
            self.result = True
    
    def edit_selected_formula(self):
        """编辑选中的公式"""
        selected_items = self.formulas_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要编辑的公式")
            return
        
        formula_id = self.formulas_tree.item(selected_items[0])['values'][0]
        
        # 获取公式详情
        formulas = self.file_manager.get_all_formulas()
        formula_data = None
        for formula in formulas:
            if formula.get('id') == formula_id:
                formula_data = formula
                break
        
        if not formula_data:
            messagebox.showerror("错误", "找不到选中的公式")
            return
        
        # 只能编辑自定义公式
        if not formula_data.get('is_custom', False):
            messagebox.showwarning("提示", "预定义公式不能编辑")
            return
        
        dialog = FormulaEditDialog(self.dialog, self.file_manager, formula_data)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.load_formulas()
            self.result = True
    
    def delete_selected_formula(self):
        """删除选中的公式"""
        selected_items = self.formulas_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要删除的公式")
            return
        
        formula_id = self.formulas_tree.item(selected_items[0])['values'][0]
        formula_name = self.formulas_tree.item(selected_items[0])['values'][1]
        
        # 检查是否为预定义公式
        formulas = self.file_manager.get_all_formulas()
        is_custom = False
        for formula in formulas:
            if formula.get('id') == formula_id:
                is_custom = formula.get('is_custom', False)
                break
        
        if not is_custom:
            messagebox.showwarning("提示", "预定义公式不能删除")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除公式 '{formula_name}' 吗？\n\n此操作无法撤销！"):
            return
        
        try:
            # TODO: 实现删除公式的功能
            messagebox.showinfo("提示", "删除功能将在后续版本中实现")
            # self.result = True
        except Exception as e:
            messagebox.showerror("错误", f"删除公式失败: {str(e)}")

class FormulaEditDialog:
    """公式编辑对话框"""
    def __init__(self, parent, file_manager, formula_data=None):
        self.file_manager = file_manager
        self.formula_data = formula_data  # 如果为None，则是新增；否则是编辑
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑计算公式" if formula_data else "新增计算公式")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_interface()
        
        # 居中显示
        self.center_dialog(parent)
        
        # 如果是编辑模式，填充数据
        if formula_data:
            self.load_formula_data()
    
    def create_interface(self):
        """创建对话框界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 公式名称
        ttk.Label(main_frame, text="公式名称:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, 
                                                                        sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # 表达式
        ttk.Label(main_frame, text="表达式:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.expression_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.expression_var, width=30).grid(row=1, column=1, 
                                                                              sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # 参数列表
        ttk.Label(main_frame, text="参数列表 (用逗号分隔):").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.params_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.params_var, width=30).grid(row=2, column=1, 
                                                                          sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # 公式描述
        ttk.Label(main_frame, text="公式描述:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(main_frame, textvariable=self.desc_var, width=30)
        desc_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # 示例说明
        example_frame = ttk.LabelFrame(main_frame, text="示例说明", padding="10")
        example_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        example_text = """表达式示例:
• 数量×单价: quantity * unit_price
• 工时×时薪: hours * hourly_rate
• 基础费用+附加费用: base_cost + additional_fees
• 带折扣的计算: quantity * price * (1 - discount)
• 使用数学函数: quantity * price * math.sqrt(discount_factor)

参数示例: quantity, unit_price, hours, hourly_rate, discount"""
        
        ttk.Label(example_frame, text=example_text, justify=tk.LEFT).pack(fill=tk.BOTH, expand=True)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="保存", command=self.save_formula).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
    
    def center_dialog(self, parent):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def load_formula_data(self):
        """加载公式数据到界面"""
        if self.formula_data:
            self.name_var.set(self.formula_data.get('name', ''))
            self.expression_var.set(self.formula_data.get('expression', ''))
            self.params_var.set(', '.join(self.formula_data.get('params', [])))
            self.desc_var.set(self.formula_data.get('description', ''))
    
    def save_formula(self):
        """保存公式"""
        try:
            # 验证必填字段
            name = self.name_var.get().strip()
            if not name:
                messagebox.showwarning("提示", "请输入公式名称")
                return
            
            expression = self.expression_var.get().strip()
            if not expression:
                messagebox.showwarning("提示", "请输入表达式")
                return
            
            params_str = self.params_var.get().strip()
            params = [p.strip() for p in params_str.split(',')] if params_str else []
            
            description = self.desc_var.get().strip()
            
            formula_data = {
                'name': name,
                'expression': expression,
                'params': params,
                'description': description
            }
            
            # 保存到文件管理器
            if self.formula_data:  # 编辑模式
                # TODO: 实现更新公式的功能
                messagebox.showinfo("提示", "更新功能将在后续版本中实现")
                self.result = False
            else:  # 新增模式
                formula_id = self.file_manager.add_custom_formula(formula_data)
                if formula_id:
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("错误", "保存失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

def main():
    """主函数"""
    root = tk.Tk()
    app = ProjectExpenseTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
