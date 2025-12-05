import os
import win32com.client
from datetime import datetime
import time
import logging
import sys
import re
import json
import requests
from collections import Counter
from .data_analyzer import DataAnalyzer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# 使用reportlab库（项目已有的依赖）生成PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 注册系统中文字体
def register_chinese_fonts():
    """注册系统中可用的中文字体"""
    try:
        # 检查系统字体目录
        font_dirs = [
            "C:\\Windows\\Fonts",
            "C:\\Program Files\\Microsoft Office\\root\\vfs\\Fonts",
        ]
        
        # 常用中文字体列表
        chinese_fonts = [
            ("SimHei", "simhei.ttf"),  # 黑体
            ("SimSun", "simsun.ttc"),  # 宋体
            ("MicrosoftYaHei", "msyh.ttf"),  # 微软雅黑
        ]
        
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for font_name, font_file in chinese_fonts:
                    font_path = os.path.join(font_dir, font_file)
                    if os.path.exists(font_path):
                        # 只注册未注册的字体
                        if font_name not in pdfmetrics.getRegisteredFontNames():
                            pdfmetrics.registerFont(TTFont(font_name, font_path))
                            logger.info(f"成功注册中文字体: {font_name} - {font_file}")
                        break
    except Exception as e:
        logger.error(f"注册中文字体失败: {str(e)}")

# 初始化时注册中文字体
register_chinese_fonts()

# API配置信息
API_KEY = "sk-cpgqvljyhmugkkdtobnhurrxcenarmrvygfflwqzexgryjkm"
MODEL_NAME = "Qwen2.5-7B-Instruct"
API_URL = "https://api.siliconflow.cn/v1"  # 移除末尾的斜杠

# 配置请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def generate_pdf_with_api(title, data_items):
    """
    使用API生成PDF文件
    """
    try:
        # 确保pdf目录存在
        pdf_dir = os.path.join(os.path.dirname(__file__), 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"report_{timestamp}_api.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        # 初始化数据分析器并执行分析
        analyzer = DataAnalyzer()
        analysis_result = analyzer.perform_full_analysis(data_items)
        
        # 准备数据为JSON格式
        report_data = {
            "title": title,
            "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data_count": analysis_result['cleaned_count'],
            "analysis_result": analysis_result
        }
        
        # 调用API生成PDF
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个PDF生成助手，请根据提供的数据生成格式化的报告内容。"
                },
                {
                    "role": "user",
                    "content": f"请根据以下数据生成一份HTML格式的PDF报告:\n{json.dumps(report_data, ensure_ascii=False)}"
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        print("正在调用API生成PDF...")
        try:
            response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=payload, timeout=30)
        except requests.exceptions.ConnectionError:
            print("无法连接到API服务器，将使用备用方案...")
            return generate_pdf_fallback(title, data_items)
        
        if response.status_code == 200:
            try:
                result = response.json()
                html_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # 保存HTML内容到临时文件
                html_path = pdf_path.replace('.pdf', '.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"API生成的HTML内容已保存: {html_path}")
                print(f"PDF生成成功！文件路径: {pdf_path}")
                return pdf_path
            except Exception as e:
                print(f"处理API响应时出错: {str(e)}")
                return generate_pdf_fallback(title, data_items)
        else:
            print(f"API调用失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            # 记录API错误信息到文件
            error_log_path = pdf_path.replace('.pdf', '_api_error.log')
            with open(error_log_path, 'w', encoding='utf-8') as f:
                f.write(f"状态码: {response.status_code}\n")
                f.write(f"错误信息: {response.text}\n")
            print(f"API错误日志已保存: {error_log_path}")
            # 失败时使用备用方案
            return generate_pdf_fallback(title, data_items)
            
    except Exception as e:
        print(f"使用API生成PDF时出错: {str(e)}")
        # 失败时使用备用方案
        return generate_pdf_fallback(title, data_items)

def generate_pdf(title, data_items):
    """
    PDF生成主函数，优先使用reportlab库方式，然后是API方式，最后是WPS方式
    """
    try:
        # 首先尝试使用纯Python的reportlab库方式
        print("尝试使用reportlab库方式生成PDF...")
        result = generate_pdf_with_fpdf(title, data_items)
        
        # 检查是否成功（返回路径以'.pdf'结尾表示PDF生成成功）
        if result and result.endswith('.pdf') and os.path.exists(result) and os.path.getsize(result) > 1000:
            print(f"reportlab库方式生成PDF成功，返回文件路径: {result}")
            return result
        
        # fpdf方式失败，尝试使用API方式
        print("fpdf方式失败，尝试使用API方式生成PDF...")
        result = generate_pdf_with_api(title, data_items)
        
        # 检查是否成功（返回路径中包含'_api.pdf'表示API生成成功）
        if '_api.pdf' in result:
            return result
        
        # API方式失败，回退到WPS方式
        print("API方式失败，回退到WPS方式生成PDF...")
        
        # 确保pdf目录存在
        pdf_dir = os.path.join(os.path.dirname(__file__), 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        docx_filename = f"report_{timestamp}.docx"
        pdf_filename = f"report_{timestamp}.pdf"
        docx_path = os.path.join(pdf_dir, docx_filename)
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        # 创建临时Word文档（先创建HTML内容，再通过WPS保存为PDF）
        # 这样可以确保内容格式正确
        
        # 初始化数据分析器并执行分析
        analyzer = DataAnalyzer()
        analysis_result = analyzer.perform_full_analysis(data_items)
        
        # 使用清洗后的数据
        cleaned_data = data_items[:analysis_result['cleaned_count']]
        
        # 尝试启动WPS
        print("正在启动WPS...")
        wps_app = win32com.client.Dispatch("KWps.Application")
        wps_app.Visible = False
        wps_app.Caption = "PDF生成服务"
        
        # 创建新文档
        doc = wps_app.Documents.Add()
        
        # 开始编辑文档
        selection = wps_app.Selection
        
        # 设置文档属性，确保正确编码
        doc.Content.Font.Name = "微软雅黑"
        doc.Content.Font.Size = 12
        doc.Content.Font.NameFarEast = "微软雅黑"
        
        # 添加标题
        selection.Font.Size = 24
        selection.Font.Bold = True
        selection.Font.Name = "微软雅黑"
        selection.Font.NameFarEast = "微软雅黑"
        selection.ParagraphFormat.Alignment = 1  # 居中对齐
        selection.TypeText(title)
        selection.TypeParagraph()
        
        # 添加生成时间
        selection.Font.Size = 12
        selection.Font.Bold = False
        selection.ParagraphFormat.Alignment = 2  # 右对齐
        generate_time = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        selection.TypeText(generate_time)
        selection.TypeParagraph()
        selection.TypeParagraph()
        
        # 添加数据列表标题
        selection.Font.Size = 18
        selection.Font.Bold = True
        selection.ParagraphFormat.Alignment = 0  # 左对齐
        selection.TypeText("数据详情")
        selection.TypeParagraph()
        selection.TypeParagraph()
        
        # 创建表格
        num_rows = len(data_items) + 1  # 表头 + 数据行
        num_cols = 4  # 序号、标题、来源、时间
        
        # 插入表格
        table = doc.Tables.Add(selection.Range, num_rows, num_cols)
        
        # 设置表头
        table.Cell(1, 1).Range.Text = "序号"
        table.Cell(1, 2).Range.Text = "标题"
        table.Cell(1, 3).Range.Text = "来源"
        table.Cell(1, 4).Range.Text = "时间"
        
        # 设置表头格式
        for i in range(1, num_cols + 1):
            table.Cell(1, i).Range.Font.Bold = True
            table.Cell(1, i).Shading.BackgroundPatternColor = 12632256  # 灰色背景
            table.Cell(1, i).Range.ParagraphFormat.Alignment = 1  # 居中对齐
        
        # 填充数据
        for i, item in enumerate(data_items, 2):  # 从第二行开始（第一行是表头）
            # 限制标题长度
            short_title = item.title[:60] + '...' if len(item.title) > 60 else item.title
            
            table.Cell(i, 1).Range.Text = str(i - 1)
            table.Cell(i, 2).Range.Text = short_title
            table.Cell(i, 3).Range.Text = item.source
            table.Cell(i, 4).Range.Text = item.created_at.strftime('%Y-%m-%d')
            
            # 设置单元格格式
            table.Cell(i, 1).Range.ParagraphFormat.Alignment = 1  # 居中对齐
            table.Cell(i, 4).Range.ParagraphFormat.Alignment = 1  # 居中对齐
        
        # 自动调整表格列宽
        table.AutoFitBehavior(1)  # wdAutoFitContent
        
        # 添加数据分析部分 - 优化版
        selection.EndKey(6)  # 移到文档末尾
        selection.TypeParagraph()
        selection.TypeParagraph()
        
        # 添加数据分析标题
        selection.Font.Size = 18
        selection.Font.Bold = True
        selection.ParagraphFormat.Alignment = 0  # 左对齐
        selection.TypeText("数据分析报告")
        selection.TypeParagraph()
        selection.TypeParagraph()
        
        # 使用优化后的格式化报告结构
        if 'formatted_report' in analysis_result and analysis_result['formatted_report']:
            # 如果有格式化的报告结构，使用它
            for section in analysis_result['formatted_report'].get('sections', []):
                # 添加章节标题
                selection.Font.Size = 14
                selection.Font.Bold = True
                selection.TypeText(section.get('title', ''))
                selection.TypeParagraph()
                
                # 添加章节内容
                selection.Font.Size = 12
                selection.Font.Bold = False
                
                # 处理多行内容
                content_lines = section.get('content', '').strip().split('\n')
                for line in content_lines:
                    if line.strip():
                        selection.TypeText(line.strip() + '\n')
                
                selection.TypeParagraph()
        else:
            # 兼容原有报告格式
            # 1. 数据质量与处理
            selection.Font.Size = 14
            selection.Font.Bold = True
            selection.TypeText("1. 数据质量与处理")
            selection.TypeParagraph()
            
            selection.Font.Size = 12
            selection.Font.Bold = False
            selection.ParagraphFormat.Alignment = 0  # 左对齐
            
            # 优先使用pdf_content中的质量摘要
            if 'pdf_content' in analysis_result and 'quality_summary' in analysis_result['pdf_content']:
                selection.TypeText(analysis_result['pdf_content']['quality_summary'] + '\n')
            else:
                selection.TypeText(f"原始数据量: {analysis_result['raw_count']} 条\n")
                selection.TypeText(f"清洗后数据量: {analysis_result['cleaned_count']} 条\n")
                
                # 计算清理比例
                if analysis_result['raw_count'] > 0:
                    cleaned_ratio = (analysis_result['cleaned_count'] / analysis_result['raw_count']) * 100
                    duplicate_ratio = 100 - cleaned_ratio
                    if duplicate_ratio > 0:
                        selection.TypeText(f"去重比例: {duplicate_ratio:.1f}%\n")
            
            selection.TypeParagraph()
            
            # 2. 关键词分析
            selection.Font.Size = 14
            selection.Font.Bold = True
            selection.TypeText("2. 关键词分析")
            selection.TypeParagraph()
            
            selection.Font.Size = 12
            selection.Font.Bold = False
            
            # 优先使用pdf_content中的关键词高亮
            if 'pdf_content' in analysis_result and 'keyword_highlights' in analysis_result['pdf_content']:
                selection.TypeText(analysis_result['pdf_content']['keyword_highlights'] + '\n')
            elif 'keywords' in analysis_result and analysis_result['keywords']:
                # 安全地处理关键词数据
                keywords = analysis_result['keywords']
                selection.TypeText("高频关键词:\n")
                
                try:
                    # 处理不同类型的关键词数据结构
                    if isinstance(keywords, list):
                        # 如果是列表，确保取前10个且是可迭代的键值对
                        display_keywords = keywords[:10]
                        for i, item in enumerate(display_keywords, 1):
                            if isinstance(item, (list, tuple)) and len(item) >= 2:
                                selection.TypeText(f"{i:2d}. {item[0]:<10} (出现{item[1]}次)\n")
                            else:
                                selection.TypeText(f"{i:2d}. {str(item):<10}\n")
                    elif isinstance(keywords, dict):
                        # 如果是字典，取前10个键值对
                        display_keywords = list(keywords.items())[:10]
                        for i, (word, count) in enumerate(display_keywords, 1):
                            selection.TypeText(f"{i:2d}. {word:<10} (出现{count}次)\n")
                    else:
                        selection.TypeText(f"关键词数据类型: {type(keywords).__name__}\n")
                except Exception as e:
                    selection.TypeText(f"关键词数据处理异常: {str(e)}\n")
            else:
                selection.TypeText("未能提取到有效关键词\n")
            
            selection.TypeParagraph()
            
            # 3. 时间分布分析
            selection.Font.Size = 14
            selection.Font.Bold = True
            selection.TypeText("3. 时间分布分析")
            selection.TypeParagraph()
            
            selection.Font.Size = 12
            selection.Font.Bold = False
            
            if analysis_result['time_distribution']:
                selection.TypeText("最近7天数据分布:\n")
                for date, count in analysis_result['time_distribution']:
                    selection.TypeText(f"  {date}: {count} 条\n")
            else:
                selection.TypeText("无时间分布数据\n")
            
            selection.TypeParagraph()
            
            # 4. 来源分布分析
            selection.Font.Size = 14
            selection.Font.Bold = True
            selection.TypeText("4. 来源分布分析")
            selection.TypeParagraph()
            
            selection.Font.Size = 12
            selection.Font.Bold = False
            
            if analysis_result['source_distribution']:
                selection.TypeText("数据来源分布:\n")
                for source_info in analysis_result['source_distribution']:
                    selection.TypeText(f"  {source_info['source']}: {source_info['count']} 条 ({source_info['percentage']}%)\n")
            else:
                selection.TypeText("无来源分布数据\n")
            
            selection.TypeParagraph()
            
            # 5. 文本特征分析
            selection.Font.Size = 14
            selection.Font.Bold = True
            selection.TypeText("5. 文本特征分析")
            selection.TypeParagraph()
            
            selection.Font.Size = 12
            selection.Font.Bold = False
            
            # 标题统计
            if analysis_result['text_length_stats']['title_stats']:
                title_stats = analysis_result['text_length_stats']['title_stats']
                selection.TypeText("标题特征:\n")
                selection.TypeText(f"  最短: {title_stats['min']} 字符\n")
                selection.TypeText(f"  最长: {title_stats['max']} 字符\n")
                selection.TypeText(f"  平均: {title_stats['avg']} 字符\n")
            
            # 内容统计
            if analysis_result['text_length_stats']['content_stats']:
                content_stats = analysis_result['text_length_stats']['content_stats']
                selection.TypeText("内容特征:\n")
                selection.TypeText(f"  最短: {content_stats['min']} 字符\n")
                selection.TypeText(f"  最长: {content_stats['max']} 字符\n")
                selection.TypeText(f"  平均: {content_stats['avg']} 字符\n")
            
            selection.TypeParagraph()
            
            # 6. 核心内容摘要
            selection.Font.Size = 14
            selection.Font.Bold = True
            selection.TypeText("6. 核心内容摘要")
            selection.TypeParagraph()
            
            selection.Font.Size = 12
            selection.Font.Bold = False
            
            # 优先使用pdf_content中的内容摘要
            if 'pdf_content' in analysis_result and 'content_summary' in analysis_result['pdf_content']:
                summary_lines = analysis_result['pdf_content']['content_summary'].strip().split('\n')
                for line in summary_lines:
                    if line.strip():
                        selection.TypeText(line.strip() + '\n')
            elif analysis_result['key_summaries']:
                selection.TypeText("重要内容概要:\n")
                for i, item in enumerate(analysis_result['key_summaries'], 1):
                    selection.TypeText(f"{i}. {item.title}\n")
                    content = getattr(item, 'content', '')
                    if content:
                        # 只显示前100个字符
                        summary_text = content[:100] + '...' if len(content) > 100 else content
                        selection.TypeText(f"   {summary_text}\n\n")
            else:
                selection.TypeText("无核心内容摘要\n")
            
            selection.TypeParagraph()
            
            # 7. 分析洞察与建议
            selection.Font.Size = 14
            selection.Font.Bold = True
            selection.TypeText("7. 分析洞察与建议")
            selection.TypeParagraph()
            
            selection.Font.Size = 12
            selection.Font.Bold = False
            
            # 优先使用pdf_content中的洞察
            if 'pdf_content' in analysis_result and 'main_insights' in analysis_result['pdf_content']:
                insight_lines = analysis_result['pdf_content']['main_insights'].strip().split('\n')
                for line in insight_lines:
                    if line.strip():
                        selection.TypeText(line.strip() + '\n')
            elif 'insights' in analysis_result and analysis_result['insights']:
                # 安全地处理insights数据
                insights = analysis_result['insights']
                if isinstance(insights, list):
                    for insight in insights:
                        # 检查insight是否为字典类型
                        if isinstance(insight, dict) and 'title' in insight and 'content' in insight:
                            selection.TypeText(f"● {insight['title']}:\n")
                            selection.TypeText(f"  {insight['content']}\n\n")
                        else:
                            # 处理非字典类型的insight
                            selection.TypeText(f"● {str(insight)}\n")
                else:
                    selection.TypeText(f"分析洞察数据类型: {type(insights).__name__}\n")
            else:
                selection.TypeText("无分析洞察\n")
            
            selection.TypeParagraph()
        
        # 移动到表格后
        selection.EndKey(6)  # wdStory
        selection.TypeParagraph()
        selection.TypeParagraph()
        
        # 添加统计信息
        selection.Font.Size = 12
        selection.Font.Bold = False
        selection.ParagraphFormat.Alignment = 2  # 右对齐
        stats_text = f"共 {analysis_result['cleaned_count']} 条有效记录"
        selection.TypeText(stats_text)
        
        try:
            # 保存为PDF（使用WPS的方式）
            print(f"正在将文档转换为PDF: {pdf_path}")
            # 尝试直接另存为PDF，确保包含字体信息
            # 先保存为Word文档确保格式正确
            temp_docx_path = pdf_path.replace('.pdf', '_temp.docx')
            doc.SaveAs2(temp_docx_path, FileFormat=16)  # 16 = wdFormatXMLDocument
            
            # 然后另存为PDF，使用完整的参数设置
            # 使用更兼容的方式导出PDF
            doc.ExportAsFixedFormat(pdf_path, ExportFormat=17, 
                                   OptimizeFor=0,  # wdExportOptimizeForPrint
                                   IncludeDocProps=True,
                                   BitmapMissingFonts=True,
                                   UseISO19005_1=False)  # 不使用严格PDF
            
            # 验证PDF文件是否成功创建且有内容
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:  # 确保文件大小合理
                print(f"PDF文件创建成功，大小: {os.path.getsize(pdf_path)} 字节")
            else:
                print(f"警告: PDF文件可能不完整，大小: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0} 字节")
                
            # 关闭文档（不保存）
            doc.Close(False)
            
            # 退出WPS
            wps_app.Quit()
            
            print(f"PDF生成成功！文件路径: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"PDF保存过程中出错: {str(e)}")
            # 确保资源正确释放
            try:
                doc.Close(False)
            except:
                pass
            try:
                wps_app.Quit()
            except:
                pass
            # 返回备用方案
            return generate_pdf_fallback(title, data_items)
        
    except Exception as e:
        print(f"使用WPS生成PDF时出错: {str(e)}")
        # 如果WPS方式失败，使用备用方案
        return generate_pdf_fallback(title, data_items)

def generate_pdf_with_fpdf(title, data_items):
    """
    使用reportlab库（项目已有的依赖）生成PDF文件
    """
    try:
        # 确保pdf目录存在
        pdf_dir = os.path.join(os.path.dirname(__file__), 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"report_{timestamp}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        print(f"准备生成PDF文件: {pdf_path}")
        
        # 初始化数据分析器并执行数据清洗和分析
        from .data_analyzer import DataAnalyzer
        analyzer = DataAnalyzer()
        
        # 使用清洗后的数据
        cleaned_items = analyzer.clean_data(data_items)
        print(f"使用清洗后的数据生成PDF，清洗前: {len(data_items)} 条，清洗后: {len(cleaned_items)} 条")
        
        # 创建PDF文档
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=inch, bottomMargin=inch, leftMargin=inch, rightMargin=inch)
        story = []
        
        # 获取样式表
        styles = getSampleStyleSheet()
        
        # 获取可用的中文字体，优先使用已注册的中文字体
        available_fonts = pdfmetrics.getRegisteredFontNames()
        chinese_font_name = 'SimHei'  # 优先使用黑体
        
        # 如果首选字体不可用，尝试其他字体
        if chinese_font_name not in available_fonts:
            backup_fonts = ['SimSun', 'MicrosoftYaHei', 'Helvetica']
            for font in backup_fonts:
                if font in available_fonts:
                    chinese_font_name = font
                    break
        
        logger.info(f"Using font: {chinese_font_name}")
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontName=chinese_font_name,
            fontSize=20,
            textColor=colors.HexColor('#333333'),
            spaceAfter=0.5*inch
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading1'],
            fontName=chinese_font_name,
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=0.3*inch
        )
        heading2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontName=chinese_font_name,
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=0.2*inch
        )
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName=chinese_font_name,
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            leading=14
        )
        small_style = ParagraphStyle(
            'Small',
            parent=styles['Normal'],
            fontName=chinese_font_name,
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            leading=10
        )
        
        # 直接使用原始标题，不移除中文
        
        # 添加标题
        story.append(Paragraph("Data Analysis Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 添加报告标题
        report_title = title[:50] + "..." if len(title) > 50 else title
        story.append(Paragraph(report_title, subtitle_style))
        
        # 添加时间戳
        time_text = f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(time_text, small_style))
        story.append(Spacer(1, 0.5*inch))
        
        # 添加基本统计信息
        story.append(Paragraph("1. Data Overview", heading2_style))
        
        # 基本计数统计
        total_items = len(data_items)
        unique_items = len(cleaned_items)
        
        story.append(Paragraph(f"Total Items: {total_items}", normal_style))
        story.append(Paragraph(f"Unique Items: {unique_items}", normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # 添加数据详情部分
        story.append(Paragraph("2. Data Details", heading2_style))
        story.append(Spacer(1, 0.2*inch))
        
        # 准备表格数据
        table_data = [['No.', 'Title', 'Source', 'URL']]
        for index, item in enumerate(cleaned_items[:10], 1):  # 最多显示10条数据
            # 直接使用原始标题，不移除中文
            title_text = item.title[:50] + "..." if len(item.title) > 50 else item.title
            
            # 直接使用原始来源
            item_source = item.source
            
            # 直接使用原始URL
            url_text = item.url[:60] + "..." if len(item.url) > 60 else item.url
            
            table_data.append([str(index), title_text, item_source, url_text])
        
        # 创建表格
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), chinese_font_name),  # 使用与其他文本相同的中文字体
            ('FONTNAME', (0, 1), (-1, -1), chinese_font_name),  # 确保所有表格内容都使用相同字体
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f9f9f9')])
        ]))
        
        # 设置列宽
        table._argW = [0.5*inch, 3.0*inch, 1.0*inch, 2.5*inch]
        
        # 添加表格到故事中
        story.append(table)
        story.append(Spacer(1, 0.5*inch))
        
        # 添加报告生成信息
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", small_style))
        story.append(Paragraph("INTELLIGENT DATA ANALYSIS SYSTEM", small_style))
        
        # 构建PDF
        print("正在构建PDF文件...")
        doc.build(story)
        
        # 验证PDF文件
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"PDF文件已保存，路径: {pdf_path}，大小: {file_size} 字节")
            return pdf_path
        else:
            print("错误：PDF文件未创建")
            return generate_pdf_fallback(title, data_items)
            
    except Exception as e:
        print(f"PDF生成错误: {str(e)}")
        import traceback
        traceback.print_exc()
        # 出错时返回备用方案
        return generate_pdf_fallback(title, data_items)


def generate_pdf_fallback(title, data_items):
    """
    备用PDF生成方案，当其他方式不可用时使用
    即使使用简单方式，也确保生成PDF文件
    """
    # 确保pdf目录存在
    pdf_dir = os.path.join(os.path.dirname(__file__), 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # 生成唯一的PDF文件名 - 确保始终使用.pdf扩展名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"report_{timestamp}_fallback.pdf"  # 明确使用.pdf扩展名
    file_path = os.path.join(pdf_dir, filename)
    print(f"备用方案生成中，将创建PDF文件: {file_path}")
    
    # 初始化数据分析器并执行分析
    analyzer = DataAnalyzer()
    analysis_result = analyzer.perform_full_analysis(data_items)
    
    # 生成备用PDF文件，但避免复杂的PDF结构
    # 直接使用简单的PDF文件结构，使用ASCII编码避免中文乱码
    try:
        # 计算内容长度
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content_length = 1000  # 预估长度
        
        pdf_content = b'%PDF-1.4\n'
        pdf_content += b'1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n'
        pdf_content += b'2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n'
        pdf_content += b'3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n'
        pdf_content += f'4 0 obj<< /Length {content_length} >>stream\n'.encode()
        
        # 使用纯ASCII文本避免中文乱码
        pdf_content += b'BT /F1 12 Tf 100 700 Td (DATA ANALYSIS REPORT) Tj ET\n'
        pdf_content += b'BT /F1 10 Tf 100 680 Td (FALLBACK VERSION) Tj ET\n'
        pdf_content += f'BT /F1 10 Tf 100 660 Td (Generated: {timestamp}) Tj ET\n'.encode()
        pdf_content += f'BT /F1 10 Tf 100 640 Td (Total Items: {len(data_items)}) Tj ET\n'.encode()
        
        # 添加基本数据摘要
        y_position = 620
        for i, item in enumerate(data_items[:5]):  # 最多显示5条
            if y_position < 100:  # 避免超出页面
                break
            
            # 只显示英文/数字信息避免乱码
            pdf_content += f'BT /F1 8 Tf 100 {y_position} Td (Item {i+1}: {item.title[:30].encode("ascii", "ignore").decode()}) Tj ET\n'.encode()
            pdf_content += f'BT /F1 8 Tf 120 {y_position-15} Td (Source: {item.source[:20].encode("ascii", "ignore").decode()}) Tj ET\n'.encode()
            y_position -= 40
        
        pdf_content += b'endstream\nendobj\n'
        pdf_content += b'5 0 obj<< /Type /Font /Subtype /Type1 /Name /F1 /BaseFont /Helvetica >>endobj\n'
        
        # 计算实际的xref位置
        xref_pos = len(pdf_content)
        
        pdf_content += b'xref\n'
        pdf_content += b'0 6\n'
        pdf_content += b'0000000000 65535 f \n'
        pdf_content += b'0000000009 00000 n \n'
        pdf_content += b'0000000052 00000 n \n'
        pdf_content += b'0000000099 00000 n \n'
        pdf_content += b'0000000220 00000 n \n'
        pdf_content += b'0000000337 00000 n \n'
        pdf_content += b'trailer<< /Root 1 0 R /Size 6 >>\n'
        pdf_content += f'startxref\n{xref_pos}\n%%EOF\n'.encode()
    except Exception as e:
        # 极端情况下生成最基本的PDF
        pdf_content = b'%PDF-1.4\n'
        pdf_content += b'1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n'
        pdf_content += b'2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n'
        pdf_content += b'3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n'
        pdf_content += b'4 0 obj<< /Length 100 >>stream\n'
        pdf_content += b'BT /F1 12 Tf 100 700 Td (ANALYSIS REPORT) Tj ET\n'
        pdf_content += b'BT /F1 10 Tf 100 680 Td (BASIC VERSION) Tj ET\n'
        pdf_content += b'endstream\nendobj\n'
        pdf_content += b'5 0 obj<< /Type /Font /Subtype /Type1 /Name /F1 /BaseFont /Helvetica >>endobj\n'
        pdf_content += b'xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000099 00000 n \n0000000220 00000 n \n0000000337 00000 n \ntrailer<< /Root 1 0 R /Size 6 >>\nstartxref\n400\n%%EOF\n'
    
    # 写入二进制内容
    with open(file_path, 'wb') as f:
        f.write(pdf_content)
    
    print(f"备用方案已生成PDF文件: {file_path}")
    return file_path
