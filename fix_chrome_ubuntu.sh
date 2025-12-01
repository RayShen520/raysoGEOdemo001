#!/bin/bash

# 自动修复 Chrome 路径问题

cd ~/raysoGEOdemo001

# 备份文件
cp main.py main.py.backup

# 使用 Python 自动修复
python3 << 'PYTHON_FIX'
import re
import os

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并替换
pattern = r'(if chrome_binary:\s+)(chrome_options\.binary_location = chrome_binary)'

replacement = r'''\1if os.path.islink(chrome_binary):
            chrome_binary = os.path.realpath(chrome_binary)
        \2'''

new_content = re.sub(pattern, replacement, content)

if new_content != content:
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✓ 修复成功！")
else:
    # 如果上面的模式不匹配，尝试另一种模式
    pattern2 = r'(if chrome_binary:\s+chrome_options\.binary_location = chrome_binary)'
    replacement2 = r'''if chrome_binary:
        if os.path.islink(chrome_binary):
            chrome_binary = os.path.realpath(chrome_binary)
        chrome_options.binary_location = chrome_binary'''
    
    new_content = re.sub(pattern2, replacement2, content)
    
    if new_content != content:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✓ 修复成功！")
    else:
        print("检查代码结构...")
        # 更宽松的匹配
        if 'if chrome_binary:' in content and 'chrome_options.binary_location' in content:
            # 手动插入
            lines = content.split('\n')
            new_lines = []
            skip_next = False
            for i, line in enumerate(lines):
                if skip_next:
                    skip_next = False
                    continue
                if 'if chrome_binary:' in line and i+1 < len(lines) and 'chrome_options.binary_location' in lines[i+1]:
                    new_lines.append(line)
                    new_lines.append('        if os.path.islink(chrome_binary):')
                    new_lines.append('            chrome_binary = os.path.realpath(chrome_binary)')
                    skip_next = True
                    continue
                new_lines.append(line)
            
            if len(new_lines) > len(lines):
                with open('main.py', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                print("✓ 修复成功！")
            else:
                print("✗ 无法自动修复，需要手动修改")
        else:
            print("✗ 找不到需要修复的代码")
PYTHON_FIX

echo ""
echo "修复完成！现在可以运行："
echo "  python3 main.py"

