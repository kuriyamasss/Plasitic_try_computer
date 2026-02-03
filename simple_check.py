import re

def check_methods(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否还有on_project_search_changed方法
    search_patterns = [
        (r'def on_project_search_changed', 'on_project_search_changed method'),
        (r'self\.project_search_var', 'project_search_var reference'),
        (r'search_text', 'search_text variable'),
        (r'搜索', 'Chinese "search" text')
    ]
    
    found = []
    for pattern, desc in search_patterns:
        matches = re.findall(pattern, content)
        if matches:
            found.append((desc, len(matches)))
    
    print(f"Checking {filename}")
    if found:
        print("Found remaining search-related code:")
        for desc, count in found:
            print(f"  {desc}: {count} occurrences")
    else:
        print("No search-related code found.")
    
    # 输出上下文以便确认
    if found:
        print("\nChecking context for 'on_project_search_changed':")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'on_project_search_changed' in line:
                print(f"Line {i+1}: {line.strip()}")

if __name__ == '__main__':
    check_methods('project_gui.py')