"""
文件管理模块 - 替换原有的数据库系统
基于JSON文件的项目数据存储系统
"""
import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import hashlib

from .config import (
    PROJECTS_DIR, 
    PROJECT_FILE_EXTENSION,
    EXPENSE_TYPES,
    PREDEFINED_FORMULAS,
    DEFAULT_PROJECT_TEMPLATE
)

class FileManager:
    """文件管理器 - 管理项目文件的创建、读取、更新、删除"""
    
    def __init__(self):
        """初始化文件管理器"""
        self.projects_dir = PROJECTS_DIR
        self.file_extension = PROJECT_FILE_EXTENSION
        self._ensure_projects_dir()
        self.current_project = None  # 当前打开的项目名称
        self.project_data = None     # 当前项目的完整数据
        
    def _ensure_projects_dir(self):
        """确保项目目录存在"""
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)
            print(f"[CREATE] Project directory: {self.projects_dir}")
    
    def _get_project_path(self, project_name: str) -> str:
        """获取项目文件完整路径"""
        # 清理项目名称，移除非法字符
        safe_name = self._sanitize_filename(project_name)
        return os.path.join(self.projects_dir, f"{safe_name}{self.file_extension}")
    
    def _sanitize_filename(self, filename) -> str:
        """Clean filename, remove illegal characters"""
        # Convert to string to handle integer input
        if not isinstance(filename, str):
            filename = str(filename)
        
        # Remove illegal characters from Windows/Unix filenames
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        # Remove leading/trailing spaces
        filename = filename.strip()
        # If filename is empty, use default name
        if not filename:
            filename = "untitled_project"
        return filename
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """获取所有项目的基本信息列表"""
        projects = []
        
        if not os.path.exists(self.projects_dir):
            return projects
        
        for filename in os.listdir(self.projects_dir):
            if filename.endswith(self.file_extension):
                project_path = os.path.join(self.projects_dir, filename)
                try:
                    with open(project_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 从JSON数据中获取项目名称，而不是从文件名推断
                    project_info = data.get('project_info', {})
                    project_name = project_info.get('name', '')
                    
                    # 如果JSON中没有项目名称，则使用文件名（不含扩展名）
                    if not project_name:
                        project_name = os.path.splitext(filename)[0]
                    
                    projects.append({
                        'name': project_name,
                        'file_name': filename,
                        'path': project_path,
                        'created_date': project_info.get('created_date', 'unknown'),
                        'last_modified': project_info.get('last_modified', 'unknown'),
                        'description': project_info.get('description', ''),
                        'expense_count': len(data.get('expenses', [])),
                        'total_amount': sum(exp.get('total_amount', 0) for exp in data.get('expenses', []))
                    })
                except Exception as e:
                    print(f"[ERROR] Failed to read project file {filename}: {str(e)}")
        
        # 按最后修改时间排序，最新的在前
        projects.sort(key=lambda x: x.get('last_modified', ''), reverse=True)
        return projects
    
    def project_exists(self, project_name: str) -> bool:
        """检查项目是否已存在"""
        project_path = self._get_project_path(project_name)
        return os.path.exists(project_path)
    
    def create_project(self, project_name: str, description: str = "") -> bool:
        """Create new project"""
        try:
            if self.project_exists(project_name):
                raise ValueError(f"Project '{project_name}' already exists")
            
            # 创建项目数据结构
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            project_data = DEFAULT_PROJECT_TEMPLATE.copy()
            project_data['project_info'] = {
                'name': project_name,
                'created_date': now,
                'last_modified': now,
                'description': description
            }
            
            # 添加预定义公式
            for formula_key, formula in PREDEFINED_FORMULAS.items():
                project_data['formulas'].append({
                    'id': formula_key,
                    'name': formula['name'],
                    'expression': formula['expression'],
                    'params': formula['params'],
                    'description': formula['description'],
                    'is_custom': False
                })
            
            # 保存项目文件
            project_path = self._get_project_path(project_name)
            with open(project_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            
            print(f"[SUCCESS] Project created successfully: {project_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to create project: {str(e)}")
            return False
    
    def open_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Open project, load project data into memory"""
        try:
            project_path = self._get_project_path(project_name)
            
            if not os.path.exists(project_path):
                raise FileNotFoundError(f"Project file does not exist: {project_path}")
            
            with open(project_path, 'r', encoding='utf-8') as f:
                self.project_data = json.load(f)
            
            self.current_project = project_name
            
            # 更新最后修改时间
            self._update_last_modified()
            
            print(f"[SUCCESS] Project opened successfully: {project_name}")
            return self.project_data
            
        except Exception as e:
            print(f"[ERROR] Failed to open project: {str(e)}")
            return None
    
    def save_project(self) -> bool:
        """Save current project to file"""
        try:
            if not self.current_project or not self.project_data:
                raise ValueError("No project opened")
            
            project_path = self._get_project_path(self.current_project)
            
            # 更新最后修改时间
            self._update_last_modified()
            
            # 保存到文件
            with open(project_path, 'w', encoding='utf-8') as f:
                json.dump(self.project_data, f, ensure_ascii=False, indent=2)
            
            print(f"[SUCCESS] Project saved successfully: {self.current_project}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save project: {str(e)}")
            return False
    
    def close_project(self):
        """关闭当前项目"""
        if self.current_project:
            self.save_project()
            print(f"[SUCCESS] Project closed: {self.current_project}")
        
        self.current_project = None
        self.project_data = None
    
    def delete_project(self, project_name: str) -> bool:
        """Delete project"""
        try:
            project_path = self._get_project_path(project_name)
            
            if not os.path.exists(project_path):
                raise FileNotFoundError(f"Project file does not exist: {project_path}")
            
            # 如果是当前打开的项目，先关闭
            if self.current_project == project_name:
                self.close_project()
            
            os.remove(project_path)
            print(f"[SUCCESS] Project deleted successfully: {project_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to delete project: {str(e)}")
            return False
    
    def rename_project(self, old_name: str, new_name: str) -> bool:
        """Rename project"""
        try:
            old_path = self._get_project_path(old_name)
            new_path = self._get_project_path(new_name)
            
            if not os.path.exists(old_path):
                raise FileNotFoundError(f"Original project file does not exist: {old_path}")
            
            if os.path.exists(new_path):
                raise ValueError(f"New project name already exists: {new_name}")
            
            # 如果是当前打开的项目，更新项目数据中的名称
            if self.current_project == old_name:
                self.current_project = new_name
                if self.project_data and 'project_info' in self.project_data:
                    self.project_data['project_info']['name'] = new_name
                self.save_project()
            
            os.rename(old_path, new_path)
            print(f"[SUCCESS] Project renamed: {old_name} -> {new_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to rename project: {str(e)}")
            return False
    
    def _update_last_modified(self):
        """更新最后修改时间"""
        if self.project_data and 'project_info' in self.project_data:
            self.project_data['project_info']['last_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # ===== 费用记录管理方法 =====
    
    def add_expense(self, expense_data: Dict[str, Any]) -> Optional[int]:
        """添加费用记录"""
        try:
            if not self.current_project or not self.project_data:
                raise ValueError("没有打开的项目")
            
            # 生成唯一的ID
            expenses = self.project_data.get('expenses', [])
            new_id = max([exp.get('id', 0) for exp in expenses], default=0) + 1
            
            # 创建完整的费用记录
            expense_record = {
                'id': new_id,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            expense_record.update(expense_data)
            
            # 添加到项目数据
            if 'expenses' not in self.project_data:
                self.project_data['expenses'] = []
            
            self.project_data['expenses'].append(expense_record)
            
            # 保存项目
            self.save_project()
            
            print(f"[SUCCESS] Expense added: ID={new_id}")
            return new_id
            
        except Exception as e:
            print(f"[ERROR] Failed to add expense: {str(e)}")
            return None
    
    def get_all_expenses(self) -> List[Dict[str, Any]]:
        """获取所有费用记录"""
        if not self.current_project or not self.project_data:
            return []
        
        return self.project_data.get('expenses', [])
    
    def get_expense_by_id(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取费用记录"""
        expenses = self.get_all_expenses()
        for expense in expenses:
            if expense.get('id') == expense_id:
                return expense
        return None
    
    def update_expense(self, expense_id: int, expense_data: Dict[str, Any]) -> bool:
        """更新费用记录"""
        try:
            expenses = self.project_data.get('expenses', [])
            
            for i, expense in enumerate(expenses):
                if expense.get('id') == expense_id:
                    # 保留原有的创建时间和ID
                    expense_data['id'] = expense_id
                    expense_data['created_at'] = expense.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    
                    # 更新记录
                    self.project_data['expenses'][i] = expense_data
                    
                    # 保存项目
                    self.save_project()
                    
                    print(f"[SUCCESS] Expense updated: ID={expense_id}")
                    return True
            
            raise ValueError(f"找不到费用记录: ID={expense_id}")
            
        except Exception as e:
            print(f"[ERROR] Failed to update expense: {str(e)}")
            return False
    
    def delete_expense(self, expense_id: int) -> bool:
        """删除费用记录"""
        try:
            expenses = self.project_data.get('expenses', [])
            
            for i, expense in enumerate(expenses):
                if expense.get('id') == expense_id:
                    # 删除记录
                    del self.project_data['expenses'][i]
                    
                    # 保存项目
                    self.save_project()
                    
                    print(f"[SUCCESS] Expense deleted: ID={expense_id}")
                    return True
            
            raise ValueError(f"找不到费用记录: ID={expense_id}")
            
        except Exception as e:
            print(f"[ERROR] Failed to delete expense: {str(e)}")
            return False
    
    # ===== 自定义类型管理方法 =====
    
    def add_custom_expense_type(self, type_data: Dict[str, Any]) -> Optional[int]:
        """添加自定义费用类型"""
        try:
            if not self.current_project or not self.project_data:
                raise ValueError("没有打开的项目")
            
            # 生成唯一的ID
            custom_types = self.project_data.get('custom_expense_types', [])
            new_id = max([t.get('id', 0) for t in custom_types], default=0) + 1
            
            # 创建类型记录
            type_record = {
                'id': new_id,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            type_record.update(type_data)
            
            # 添加到项目数据
            if 'custom_expense_types' not in self.project_data:
                self.project_data['custom_expense_types'] = []
            
            self.project_data['custom_expense_types'].append(type_record)
            
            # 保存项目
            self.save_project()
            
            print(f"[SUCCESS] Custom expense type added: ID={new_id}")
            return new_id
            
        except Exception as e:
            print(f"[ERROR] Failed to add custom expense type: {str(e)}")
            return None
    
    def get_all_custom_expense_types(self) -> List[Dict[str, Any]]:
        """获取所有自定义费用类型"""
        if not self.current_project or not self.project_data:
            return []
        
        return self.project_data.get('custom_expense_types', [])
    
    # ===== 公式管理方法 =====
    
    def add_custom_formula(self, formula_data: Dict[str, Any]) -> Optional[int]:
        """添加自定义公式"""
        try:
            if not self.current_project or not self.project_data:
                raise ValueError("没有打开的项目")
            
            # 生成唯一的ID
            formulas = self.project_data.get('formulas', [])
            custom_formulas = [f for f in formulas if f.get('is_custom', False)]
            new_id = max([f.get('id', 0) for f in custom_formulas], default=0) + 1
            
            # 创建公式记录
            formula_record = {
                'id': f"custom_{new_id}",
                'is_custom': True,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            formula_record.update(formula_data)
            
            # 添加到项目数据
            self.project_data['formulas'].append(formula_record)
            
            # 保存项目
            self.save_project()
            
            print(f"[SUCCESS] Custom formula added: ID={formula_record['id']}")
            return formula_record['id']
            
        except Exception as e:
            print(f"[ERROR] Failed to add custom formula: {str(e)}")
            return None
    
    def get_all_formulas(self) -> List[Dict[str, Any]]:
        """获取所有公式（包括预定义和自定义）"""
        if not self.current_project or not self.project_data:
            return []
        
        return self.project_data.get('formulas', [])
    
    def get_formula_by_id(self, formula_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取公式"""
        formulas = self.get_all_formulas()
        for formula in formulas:
            if formula.get('id') == formula_id:
                return formula
        return None
    
    # ===== 统计方法 =====
    
    def get_expense_statistics(self) -> Dict[str, Any]:
        """获取费用统计信息"""
        if not self.current_project or not self.project_data:
            return {}
        
        expenses = self.get_all_expenses()
        
        if not expenses:
            return {
                'overall': {
                    'total_count': 0,
                    'grand_total': 0,
                    'avg_amount': 0
                },
                'by_type': [],
                'by_custom_type': []
            }
        
        # 总体统计
        total_count = len(expenses)
        grand_total = sum(exp.get('total_amount', 0) for exp in expenses)
        avg_amount = grand_total / total_count if total_count > 0 else 0
        
        # 按类型统计
        type_stats = {}
        for expense in expenses:
            expense_type = expense.get('expense_type', 'other')
            type_name = EXPENSE_TYPES.get(expense_type, expense_type)
            
            if type_name not in type_stats:
                type_stats[type_name] = {
                    'count': 0,
                    'total_amount': 0
                }
            
            type_stats[type_name]['count'] += 1
            type_stats[type_name]['total_amount'] += expense.get('total_amount', 0)
        
        # 转换为列表格式
        by_type = []
        for type_name, stats in type_stats.items():
            by_type.append({
                'expense_type': type_name,
                'count': stats['count'],
                'total_amount': stats['total_amount']
            })
        
        # 按自定义类型统计（如果有）
        by_custom_type = []
        custom_types = self.get_all_custom_expense_types()
        if custom_types:
            custom_type_stats = {}
            for expense in expenses:
                custom_type_id = expense.get('custom_type_id')
                if custom_type_id:
                    for custom_type in custom_types:
                        if custom_type.get('id') == custom_type_id:
                            type_name = custom_type.get('name', f"自定义类型{custom_type_id}")
                            
                            if type_name not in custom_type_stats:
                                custom_type_stats[type_name] = {
                                    'count': 0,
                                    'total_amount': 0
                                }
                            
                            custom_type_stats[type_name]['count'] += 1
                            custom_type_stats[type_name]['total_amount'] += expense.get('total_amount', 0)
                            break
            
            for type_name, stats in custom_type_stats.items():
                by_custom_type.append({
                    'type_name': type_name,
                    'count': stats['count'],
                    'total_amount': stats['total_amount']
                })
        
        return {
            'overall': {
                'total_count': total_count,
                'grand_total': grand_total,
                'avg_amount': avg_amount
            },
            'by_type': by_type,
            'by_custom_type': by_custom_type
        }
    
    # ===== 导入导出方法 =====
    
    def import_project(self, source_path: str, overwrite: bool = False) -> bool:
        """导入项目文件"""
        try:
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"源文件不存在: {source_path}")
            
            # 读取源文件
            with open(source_path, 'r', encoding='utf-8') as f:
                source_data = json.load(f)
            
            # 验证项目数据结构
            if 'project_info' not in source_data or 'name' not in source_data['project_info']:
                raise ValueError("无效的项目文件格式")
            
            project_name = source_data['project_info']['name']
            target_path = self._get_project_path(project_name)
            
            # 检查目标文件是否已存在
            if os.path.exists(target_path) and not overwrite:
                raise ValueError(f"项目 '{project_name}' 已存在，请选择覆盖或重命名")
            
            # 保存项目文件
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(source_data, f, ensure_ascii=False, indent=2)
            
            print(f"[SUCCESS] Project imported: {project_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to import project: {str(e)}")
            return False
    
    def export_project(self, project_name: str, target_path: str) -> bool:
        """导出项目文件"""
        try:
            source_path = self._get_project_path(project_name)
            
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"项目文件不存在: {source_path}")
            
            # 复制文件
            shutil.copy2(source_path, target_path)
            
            print(f"[SUCCESS] Project exported: {project_name} -> {target_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to export project: {str(e)}")
            return False

# 全局文件管理器实例
file_manager_instance = None

def get_file_manager():
    """获取文件管理器实例（单例模式）"""
    global file_manager_instance
    if file_manager_instance is None:
        file_manager_instance = FileManager()
    return file_manager_instance