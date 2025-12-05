#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本，用于调试PDF生成功能
"""

import os
import sys
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 定义测试数据类
class TestItem:
    def __init__(self, title, source, url=None, content=None, created_at=None):
        self.title = title
        self.source = source
        self.url = url or f"http://example.com/test/{hash(title) % 1000}"
        self.content = content or f"这是{title}的测试内容，用于生成PDF报告。"
        self.created_at = created_at or datetime.now()

def test_pdf_simple():
    """
    简单测试PDF生成功能
    """
    print("=== 开始简单测试PDF生成功能 ===")
    
    try:
        # 创建测试数据
        test_data = [
            TestItem("人工智能在医疗领域的应用", "科技日报", "http://example.com/ai-medical"),
            TestItem("大数据分析在金融行业的实践", "金融时报", "http://example.com/bigdata-finance")
        ]
        
        print(f"创建了{len(test_data)}条测试数据")
        
        # 尝试导入PDF生成模块
        print("正在导入PDF生成模块...")
        try:
            from app.pdf_generator import generate_pdf_with_fpdf
            print("成功导入generate_pdf_with_fpdf模块")
        except ImportError as e:
            print(f"导入PDF生成模块失败: {str(e)}")
            traceback.print_exc()
            return False
        
        # 尝试导入DataAnalyzer模块
        print("正在导入DataAnalyzer模块...")
        try:
            from app.data_analyzer import DataAnalyzer
            print("成功导入DataAnalyzer模块")
        except ImportError as e:
            print(f"导入DataAnalyzer模块失败: {str(e)}")
            traceback.print_exc()
            return False
        
        # 测试数据清洗功能
        print("正在测试数据清洗功能...")
        try:
            analyzer = DataAnalyzer()
            cleaned_data = analyzer.clean_data(test_data)
            print(f"数据清洗成功！清洗前: {len(test_data)} 条，清洗后: {len(cleaned_data)} 条")
        except Exception as e:
            print(f"数据清洗失败: {str(e)}")
            traceback.print_exc()
            return False
        
        # 测试FPDF生成功能
        print("正在测试FPDF生成功能...")
        try:
            pdf_path = generate_pdf_with_fpdf("测试报告", test_data)
            print(f"PDF生成完成，返回路径: {pdf_path}")
            
            # 验证PDF文件
            if pdf_path and os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✓ PDF文件存在，路径: {pdf_path}")
                print(f"✓ PDF文件大小: {file_size} 字节")
                return True
            else:
                print(f"✗ PDF文件不存在")
                return False
                
        except Exception as e:
            print(f"PDF生成失败: {str(e)}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_simple()
    if success:
        print("\n=== 测试成功！===\n")
        sys.exit(0)
    else:
        print("\n=== 测试失败！===\n")
        sys.exit(1)