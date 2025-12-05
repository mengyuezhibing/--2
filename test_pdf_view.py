#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF生成和显示功能
"""

import os
import sys
import tempfile
from app.pdf_generator import generate_pdf_with_fpdf, generate_pdf_fallback
from datetime import datetime

# 模拟数据项
class MockDataItem:
    def __init__(self, id, title, content, source, url):
        self.id = id
        self.title = title
        self.content = content
        self.source = source
        self.url = url

# 创建测试数据
print("创建测试数据...")
test_data = [
    MockDataItem(1, "测试标题1", "这是测试内容1", "来源1", "http://example.com/1"),
    MockDataItem(2, "测试标题2", "这是测试内容2", "来源2", "http://example.com/2"),
    MockDataItem(3, "测试标题3", "这是测试内容3", "来源3", "http://example.com/3"),
]

# 测试generate_pdf_with_fpdf函数
print("\n=== 测试 generate_pdf_with_fpdf 函数 ===")
title = "测试报告"
try:
    pdf_path = generate_pdf_with_fpdf(title, test_data)
    if os.path.exists(pdf_path):
        print(f"✅ PDF生成成功: {pdf_path}")
        print(f"   文件大小: {os.path.getsize(pdf_path)} 字节")
    else:
        print(f"❌ PDF文件未生成")
except Exception as e:
    print(f"❌ 生成PDF时出错: {str(e)}")

# 测试generate_pdf_fallback函数
print("\n=== 测试 generate_pdf_fallback 函数 ===")
try:
    fallback_path = generate_pdf_fallback(title, test_data)
    if os.path.exists(fallback_path):
        print(f"✅ 备用PDF生成成功: {fallback_path}")
        print(f"   文件大小: {os.path.getsize(fallback_path)} 字节")
    else:
        print(f"❌ 备用PDF文件未生成")
except Exception as e:
    print(f"❌ 生成备用PDF时出错: {str(e)}")

print("\n=== 测试完成 ===")