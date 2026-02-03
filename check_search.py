#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查是否还有搜索相关的代码残留
"""
import re
import sys

def check_search_code(filename):
    """检查文件中是否还有搜索相关代码"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 搜索关键词
    search_keywords = [
        'on_project_search_changed',
        'project_search_var',
        'search_text',
        'search box',
        '搜索'
    ]
    
    found_items = []
    
    for keyword in search_keywords:
        pattern = re.compile(keyword, re.IGNORECASE)
        matches = pattern.finditer(content)
        
        for match in matches:
            # 获取上下文
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].replace('\n', ' ').strip()
            
            found_items.append({
                'keyword': keyword,
                'position': match.start(),
                'context': context
            })
    
    # 打印结果
    print(f"检查文件: {filename}")
    print(f"找到 {len(found_items)} 个可能的搜索相关项目")
    print("=" * 80)
    
    if found_items:
        for i, item in enumerate(found_items, 1):
            print(f"{i}. 关键词: '{item['keyword']}'")
            print(f"   位置: {item['position']}")
            print(f"   上下文: ...{item['context']}...")
            print()
    
    return found_items

def main():
    """主函数"""
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = ['project_gui.py']
    
    all_found = []
    
    for file in files:
        try:
            found = check_search_code(file)
            all_found.extend(found)
            print("\n" + "=" * 80 + "\n")
        except Exception as e:
            print(f"检查文件 {file} 时出错: {str(e)}")
    
    # 总结
    if all_found:
        print("⚠️  警告: 发现搜索相关代码残留，需要清理")
        print("建议清理以下内容:")
        for item in all_found:
            print(f"  - 移除 '{item['keyword']}' 相关代码")
    else:
        print("✅ 检查完成: 未发现明显的搜索相关代码残留")

if __name__ == "__main__":
    main()