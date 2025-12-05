#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Flask应用程序中的PDF显示功能
"""

from flask import Flask, send_file, render_template_string
import os
import tempfile

app = Flask(__name__)

# 测试HTML模板
PDF_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF测试</title>
</head>
<body>
    <h1>PDF测试页面</h1>
    <p>使用&lt;iframe&gt;标签显示PDF:</p>
    <iframe src="{{ url_for('get_pdf') }}" width="100%" height="600px"></iframe>
    <br>
    <p>使用&lt;embed&gt;标签显示PDF:</p>
    <embed src="{{ url_for('get_pdf') }}" width="100%" height="600px" type="application/pdf">
    <br>
    <p><a href="{{ url_for('get_pdf') }}" target="_blank">直接下载PDF</a></p>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(PDF_TEMPLATE)

@app.route('/pdf')
def get_pdf():
    # 获取最新生成的PDF文件
    pdf_dir = os.path.join(os.path.dirname(__file__), 'app', 'pdfs')
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    if not pdf_files:
        return "没有PDF文件", 404
    
    # 按修改时间排序，获取最新的文件
    latest_pdf = sorted(pdf_files, key=os.path.getmtime, reverse=True)[0]
    print(f"发送PDF文件: {latest_pdf}")
    
    return send_file(latest_pdf, mimetype='application/pdf')

if __name__ == '__main__':
    print("启动测试Flask应用...")
    print("访问地址: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)