#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础测试脚本 - 只测试模块导入
"""

import os
import sys

print("=== 基础模块导入测试 ===")

# 打印当前工作目录
print(f"当前工作目录: {os.getcwd()}")

# 打印Python路径
print("Python路径:")
for path in sys.path:
    print(f"  {path}")

# 检查app目录是否存在
app_path = os.path.join(os.getcwd(), "app")
print(f"\napp目录存在: {os.path.exists(app_path)}")

# 检查pdf_generator模块是否存在
pdf_generator_path = os.path.join(app_path, "pdf_generator.py")
print(f"pdf_generator.py存在: {os.path.exists(pdf_generator_path)}")

# 检查data_analyzer模块是否存在
data_analyzer_path = os.path.join(app_path, "data_analyzer.py")
print(f"data_analyzer.py存在: {os.path.exists(data_analyzer_path)}")

# 尝试添加当前目录到Python路径
sys.path.insert(0, os.getcwd())
print("\n已将当前目录添加到Python路径")

# 尝试导入模块
print("\n尝试导入模块:")
try:
    import app
    print("✓ 成功导入app模块")
except ImportError as e:
    print(f"✗ 导入app模块失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from app import pdf_generator
    print("✓ 成功导入app.pdf_generator模块")
except ImportError as e:
    print(f"✗ 导入app.pdf_generator模块失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from app import data_analyzer
    print("✓ 成功导入app.data_analyzer模块")
except ImportError as e:
    print(f"✗ 导入app.data_analyzer模块失败: {e}")
    import traceback
    traceback.print_exc()

# 尝试导入具体函数
try:
    from app.pdf_generator import generate_pdf_with_fpdf
    print("✓ 成功导入generate_pdf_with_fpdf函数")
except ImportError as e:
    print(f"✗ 导入generate_pdf_with_fpdf函数失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.data_analyzer import DataAnalyzer
    print("✓ 成功导入DataAnalyzer类")
except ImportError as e:
    print(f"✗ 导入DataAnalyzer类失败: {e}")
    import traceback
    traceback.print_exc()