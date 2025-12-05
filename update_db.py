#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新数据库结构，添加user_id字段到ScrapedData和ReportData表
"""

import os
import sys
from sqlalchemy import text

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入必要的模块
from app import create_app, db
from app.models import User, ScrapedData, ReportData

# 创建应用对象
app = create_app()

with app.app_context():
    try:
        print("开始更新数据库结构...")
        
        # 检查ScrapedData表是否有user_id字段
        print("检查ScrapedData表结构...")
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(scraped_data)")).fetchall()
            has_user_id = any(col[1] == 'user_id' for col in result)
            
            if not has_user_id:
                print("添加ScrapedData.user_id字段...")
                conn.execute(text("ALTER TABLE scraped_data ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1"))
                conn.execute(text("ALTER TABLE scraped_data ADD CONSTRAINT fk_scraped_data_user FOREIGN KEY (user_id) REFERENCES user (id)"))
                conn.commit()
            else:
                print("ScrapedData.user_id字段已存在")
        
        # 检查ReportData表是否有user_id字段
        print("检查ReportData表结构...")
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(report_data)")).fetchall()
            has_user_id = any(col[1] == 'user_id' for col in result)
            
            if not has_user_id:
                print("添加ReportData.user_id字段...")
                conn.execute(text("ALTER TABLE report_data ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1"))
                conn.execute(text("ALTER TABLE report_data ADD CONSTRAINT fk_report_data_user FOREIGN KEY (user_id) REFERENCES user (id)"))
                conn.commit()
            else:
                print("ReportData.user_id字段已存在")
        
        print("数据库结构更新完成！")
        
    except Exception as e:
        print(f"更新数据库时出错: {str(e)}")
        import traceback
        traceback.print_exc()
