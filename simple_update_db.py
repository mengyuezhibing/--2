#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的数据库更新脚本，添加user_id字段到ScrapedData表
"""

import sqlite3
import os

# 获取数据库路径
db_path = os.path.join('app', 'data', 'app.db')
print(f"使用数据库: {db_path}")

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("开始更新数据库结构...")
    
    # 检查ScrapedData表是否有user_id字段
    cursor.execute("PRAGMA table_info(scraped_data)")
    columns = cursor.fetchall()
    has_user_id = any(col[1] == 'user_id' for col in columns)
    
    if not has_user_id:
        print("添加ScrapedData.user_id字段...")
        cursor.execute("ALTER TABLE scraped_data ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")
        cursor.execute("ALTER TABLE scraped_data ADD CONSTRAINT fk_scraped_data_user FOREIGN KEY (user_id) REFERENCES user (id)")
        conn.commit()
        print("ScrapedData.user_id字段添加成功")
    else:
        print("ScrapedData.user_id字段已存在")
    
    # 检查ReportData表是否有user_id字段
    cursor.execute("PRAGMA table_info(report_data)")
    columns = cursor.fetchall()
    has_user_id = any(col[1] == 'user_id' for col in columns)
    
    if not has_user_id:
        print("添加ReportData.user_id字段...")
        cursor.execute("ALTER TABLE report_data ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1")
        cursor.execute("ALTER TABLE report_data ADD CONSTRAINT fk_report_data_user FOREIGN KEY (user_id) REFERENCES user (id)")
        conn.commit()
        print("ReportData.user_id字段添加成功")
    else:
        print("ReportData.user_id字段已存在")
    
    print("数据库结构更新完成！")
    
except Exception as e:
    print(f"更新数据库时出错: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    # 关闭数据库连接
    conn.close()
