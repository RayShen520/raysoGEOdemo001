#!/bin/bash

# 解决 Git pull 冲突的脚本

echo "解决 Git pull 冲突..."

cd ~/raysoGEOdemo001

# 方法1：保存本地修改（推荐）
echo "保存本地修改..."
git stash

# 拉取最新代码
echo "拉取最新代码..."
git pull

# 恢复本地修改（如果需要）
echo "恢复本地修改..."
git stash pop

echo "✓ 完成！"

