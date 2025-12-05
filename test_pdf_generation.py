#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF生成功能和内容完整性
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定义测试数据类
class TestItem:
    def __init__(self, title, source, url=None, content=None, created_at=None):
        self.title = title
        self.source = source
        self.url = url or f"http://example.com/test/{hash(title) % 1000}"
        self.content = content or f"这是{title}的测试内容，用于生成PDF报告。"
        self.created_at = created_at or datetime.now()

def test_pdf_generation():
    """
    测试PDF生成功能
    """
    try:
        # 创建测试数据
        test_data = [
            TestItem("人工智能在医疗领域的应用", "科技日报", "http://example.com/ai-medical"),
            TestItem("大数据分析在金融行业的实践", "金融时报", "http://example.com/bigdata-finance"),
            TestItem("机器学习算法的最新进展", "计算机学报", "http://example.com/ml-progress"),
            TestItem("深度学习模型优化技术", "人工智能学报", "http://example.com/dl-optimization"),
            TestItem("自然语言处理的未来发展", "语言学报", "http://example.com/nlp-future"),
            TestItem("计算机视觉技术在自动驾驶中的应用", "汽车工程学报", "http://example.com/cv-autopilot"),
            TestItem("区块链技术在供应链管理中的应用", "供应链管理学报", "http://example.com/blockchain-supply"),
            TestItem("云计算技术的发展趋势", "云计算学报", "http://example.com/cloud-trends"),
            TestItem("物联网技术在智能家居中的应用", "物联网学报", "http://example.com/iot-smart-home"),
            TestItem("5G技术对社会的影响", "通信学报", "http://example.com/5g-impact")
        ]
        
        logger.info(f"创建了{len(test_data)}条测试数据")
        
        # 导入PDF生成模块
        try:
            from app.pdf_generator import generate_pdf_with_fpdf
            logger.info("成功导入generate_pdf_with_fpdf模块")
        except ImportError as e:
            logger.error(f"导入PDF生成模块失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试FPDF生成方式
        logger.info("开始测试PDF生成功能...")
        pdf_path = generate_pdf_with_fpdf("测试报告", test_data)
        
        # 验证PDF文件
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            logger.info(f"PDF生成成功！文件路径: {pdf_path}")
            logger.info(f"PDF文件大小: {file_size} 字节")
            
            # 检查文件大小是否合理
            if file_size > 1000:
                logger.info("PDF文件大小合理，内容可能完整")
                return True
            else:
                logger.warning("PDF文件大小过小，内容可能不完整")
                return False
        else:
            logger.error("PDF生成失败，文件不存在")
            return False
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("开始测试PDF生成功能...")
    success = test_pdf_generation()
    
    if success:
        logger.info("PDF生成功能测试成功！")
        sys.exit(0)
    else:
        logger.error("PDF生成功能测试失败！")
        sys.exit(1)