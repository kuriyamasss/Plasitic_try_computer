#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新组织文件结构脚本
将模块文件移动到modules文件夹，并更新import语句
"""
import os
import shutil
import re
from pathlib import Path

# 需要移动的模块文件列表
MODULE_FILES = [
    'config.py',
    'expense_calculator.py',
    'export_manager.py',
    'file_manager.py'
]

# 主程序文件（不移动）
MAIN_PROGRAM = 'project_gui.py'

# 其他可能包含import的文件
OTHER_FILES = [
    'project_gui.py',
    'gui_main.py',
    'test_gui_updates.py',
    'test_new_system.py',
    'test_system.py',
    'manual_test.py',
    'comprehensive_test.py',
    'final_demo.py'
]

def create_modules_directory():
    """创建modules目录"""
    if not os.path.exists('modules'):
        os.makedirs('modules')
        print("[信息] 创建modules目录")
    else:
        print("[信息] modules目录已存在")

def move_module_files():
    """移动模块文件到modules目录"""
    moved_files = []
    skipped_files = []
    
    for filename in MODULE_FILES:
        source_path = filename
        dest_path = os.path.join('modules', filename)
        
        if os.path.exists(source_path):
            # 检查目标文件是否已存在
            if os.path.exists(dest_path):
                # 备份旧文件
                backup_path = dest_path + '.backup'
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.move(dest_path, backup_path)
                print(f"[信息] 备份现有文件: {dest_path} -> {backup_path}")
            
            # 移动文件
            shutil.move(source_path, dest_path)
            moved_files.append(filename)
            print(f"[信息] 移动文件: {source_path} -> {dest_path}")
        else:
            skipped_files.append(filename)
            print(f"[警告] 文件不存在: {source_path}")
    
    print(f"\n[完成] 移动了 {len(moved_files)} 个文件到modules目录")
    if skipped_files:
        print(f"[警告] 跳过 {len(skipped_files)} 个不存在的文件: {', '.join(skipped_files)}")

def update_import_statements():
    """更新所有文件中的import语句"""
    # 需要更新的import模式
    import_patterns = [
        (r'^from config import', 'from modules.config import'),
        (r'^from expense_calculator import', 'from modules.expense_calculator import'),
        (r'^from export_manager import', 'from modules.export_manager import'),
        (r'^from file_manager import', 'from modules.file_manager import'),
        (r'^import config$', 'import modules.config'),
        (r'^import expense_calculator$', 'import modules.expense_calculator'),
        (r'^import export_manager$', 'import modules.export_manager'),
        (r'^import file_manager$', 'import modules.file_manager'),
    ]
    
    updated_files = []
    
    # 检查并更新所有相关文件
    all_files = OTHER_FILES + [os.path.join('modules', f) for f in MODULE_FILES if os.path.exists(os.path.join('modules', f))]
    
    for filename in all_files:
        if not os.path.exists(filename):
            print(f"[警告] 文件不存在: {filename}")
            continue
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            updated = False
            
            # 应用所有替换模式
            for pattern, replacement in import_patterns:
                # 使用多行模式确保只匹配行首
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    updated = True
                    content = new_content
            
            if updated:
                # 备份原文件
                backup_path = filename + '.backup'
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.copy2(filename, backup_path)
                
                # 写入更新后的内容
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updated_files.append(filename)
                print(f"[信息] 更新文件: {filename}")
        
        except Exception as e:
            print(f"[错误] 处理文件 {filename} 时出错: {str(e)}")
    
    print(f"\n[完成] 更新了 {len(updated_files)} 个文件的import语句")

def check_module_imports():
    """检查modules目录下的文件是否互相正确引用"""
    modules_dir = 'modules'
    if not os.path.exists(modules_dir):
        print("[错误] modules目录不存在")
        return
    
    module_files = [f for f in os.listdir(modules_dir) if f.endswith('.py')]
    
    for module_file in module_files:
        module_path = os.path.join(modules_dir, module_file)
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查modules目录下的文件是否互相正确引用
            for other_module in module_files:
                if other_module == module_file:
                    continue
                
                module_name = other_module.replace('.py', '')
                # 检查是否有类似 "from module_name import" 的语句
                patterns = [
                    rf'^from {module_name} import',
                    rf'^import {module_name}$',
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content, flags=re.MULTILINE):
                        print(f"[警告] {module_file} 需要更新import语句引用 {other_module}")
                        # 更新为相对导入
                        if module_name in ['config', 'expense_calculator', 'export_manager', 'file_manager']:
                            updated = False
                            # 更新 from module_name import
                            from_pattern = rf'^from {module_name} import'
                            new_from = rf'from .{module_name} import'
                            content = re.sub(from_pattern, new_from, content, flags=re.MULTILINE)
                            if content != f.read():  # 重新读取以比较
                                updated = True
                            
                            # 更新 import module_name
                            import_pattern = rf'^import {module_name}$'
                            new_import = f'import .{module_name}'
                            content = re.sub(import_pattern, new_import, content, flags=re.MULTILINE)
                            
                            if updated:
                                with open(module_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                print(f"[信息] 更新 {module_file} 中的import语句")
        
        except Exception as e:
            print(f"[错误] 检查模块 {module_file} 时出错: {str(e)}")

def main():
    """主函数"""
    print("=" * 50)
    print("开始重新组织文件结构")
    print("=" * 50)
    
    # 1. 创建modules目录
    create_modules_directory()
    
    # 2. 移动模块文件
    move_module_files()
    
    # 3. 更新import语句
    update_import_statements()
    
    # 4. 检查modules目录下的文件互相引用
    check_module_imports()
    
    print("\n" + "=" * 50)
    print("重新组织完成")
    print("=" * 50)
    
    # 提供重要提示
    print("\n重要提示:")
    print("1. 所有模块文件已移动到 modules/ 目录")
    print("2. 所有import语句已更新为 'from modules.module_name import'")
    print("3. 原文件已备份为 .backup 文件")
    print("4. 主程序 project_gui.py 仍位于项目根目录")
    print("\n运行前请确保:")
    print("1. Python能够找到modules目录")
    print("2. 所有依赖都已安装 (requirements.txt)")
    print("3. 测试程序是否能正常运行")

if __name__ == '__main__':
    main()