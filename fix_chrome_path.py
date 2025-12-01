#!/usr/bin/env python3
"""
修复 main.py，添加 Chrome 路径自动查找功能
"""

import re
import sys

def fix_main_py(file_path):
    """在 main.py 中添加 Chrome 路径查找代码"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经包含修复
    if 'chrome_binary_paths' in content:
        print("代码已经包含修复，无需修改")
        return True
    
    # 查找插入位置
    pattern = r"(chrome_options\.add_experimental_option\('useAutomationExtension', False\)\s*\n\s*)\n\s*# 尝试使用 webdriver-manager"
    
    replacement = r'''\1
        # 查找 Chrome 的实际安装位置
        chrome_binary_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/chrome",
            "/usr/bin/chromium"
        ]
        
        chrome_binary = None
        for path in chrome_binary_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                chrome_binary = path
                break
        
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
            print(f"找到 Chrome: {chrome_binary}")
        else:
            # 尝试使用 which 命令查找
            import shutil
            chrome_binary = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium-browser")
            if chrome_binary:
                chrome_options.binary_location = chrome_binary
                print(f"找到 Chrome: {chrome_binary}")
            else:
                print("警告: 未找到 Chrome，尝试使用默认路径...")
        
        # 尝试使用 webdriver-manager'''
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        print("错误: 无法找到插入位置，请手动修改")
        return False
    
    # 备份原文件
    backup_path = file_path + '.bak'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"已备份原文件到: {backup_path}")
    
    # 写入修复后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ 已成功修复 {file_path}")
    return True

if __name__ == '__main__':
    file_path = 'main.py'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    if fix_main_py(file_path):
        print("\n修复完成！现在可以运行程序了：")
        print("  python3 main.py")
    else:
        print("\n修复失败，请手动修改代码")

