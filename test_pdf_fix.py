#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 PDF 生成修复效果的脚本
"""

import os
import sys
import tempfile
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath('.'))

from app.pdf_generator import generate_pdf
from app.models import ScrapedData

class MockScrapedData:
    """模拟 ScrapedData 对象"""
    def __init__(self, id, title, content, source, url, keyword, created_at):
        self.id = id
        self.title = title
        self.content = content
        self.source = source
        self.url = url
        self.keyword = keyword
        self.created_at = created_at

# 创建测试数据
def create_test_data(count=10):
    """创建模拟测试数据"""
    mock_data = []
    for i in range(count):
        item = MockScrapedData(
            id=i+1,
            title=f"测试标题{i+1} - 包含中文字符的标题",
            content=f"这是测试内容{i+1}，包含中文内容，用于测试PDF生成的中文显示效果。" * 3,
            source=f"来源{i+1}.com",
            url=f"http://example.com/test{i+1}",
            keyword=f"关键词{i+1}",
            created_at=datetime.now()
        )
        mock_data.append(item)
    return mock_data

# 测试 PDF 生成
def test_pdf_generation():
    """测试 PDF 生成功能"""
    print("=" * 50)
    print("开始测试 PDF 生成修复效果")
    print("=" * 50)
    
    # 创建测试数据
    test_data = create_test_data(15)  # 创建15条测试数据
    
    try:
        # 生成 PDF
        report_title = "PDF生成修复测试报告 - 包含中文标题"
        print(f"\n1. 生成PDF报告: {report_title}")
        print(f"   数据条数: {len(test_data)}")
        
        pdf_path = generate_pdf(report_title, test_data)
        
        # 验证 PDF 文件
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"\n2. PDF生成成功!")
            print(f"   文件路径: {pdf_path}")
            print(f"   文件大小: {file_size} 字节")
            
            if file_size > 5000:  # 合理的文件大小阈值
                print("   ✓ 文件大小正常")
            else:
                print("   ⚠ 警告: 文件大小可能过小")
            
            print("\n3. 测试完成!")
            return True
        else:
            print("\n2. PDF生成失败!")
            return False
            
    except Exception as e:
        print(f"\n2. PDF生成错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    
    print("\n" + "=" * 50)
    if success:
        print("PDF生成测试通过!")
    else:
        print("PDF生成测试失败!")
    print("=" * 50)
    sys.exit(0 if success else 1)
