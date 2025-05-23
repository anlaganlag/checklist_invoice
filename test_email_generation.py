#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试邮件生成功能
"""

import pandas as pd
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 从streamlit_app导入邮件生成函数
from streamlit_app import generate_email_draft

def test_email_generation():
    """测试邮件生成功能"""
    print("开始测试邮件生成功能...")
    
    # 创建测试数据
    test_data = {
        'ID': ['CI001_1', 'CI002_2', 'CI003_3'],
        'HSN': ['85423900 -> 85423901', '84716000 -> 84716001', ''],
        'BCD': ['10 -> 12', '', '5 -> 8'],
        'SWS': ['', '2 -> 3', '1 -> 2'],
        'IGST': ['18 -> 20', '12 -> 15', ''],
        'Qty': ['100 -> 120', '', ''],
        'Price': ['50.5 -> 55.0', '25.0 -> 30.0', ''],
        'Desc': ['CAMERA -> SECURITY CAMERA', '', '']
    }
    
    # 创建DataFrame
    diff_report_df = pd.DataFrame(test_data)
    
    print("测试数据:")
    print(diff_report_df)
    print("\n" + "="*50 + "\n")
    
    # 生成邮件草稿
    email_content = generate_email_draft(diff_report_df)
    
    if email_content:
        print("邮件草稿生成成功!")
        print("\n生成的邮件内容:")
        print("-" * 50)
        print(email_content)
        print("-" * 50)
        
        # 保存到文件
        with open('test_email_draft.txt', 'w', encoding='utf-8') as f:
            f.write(email_content)
        print("\n邮件草稿已保存到 test_email_draft.txt")
        
    else:
        print("邮件草稿生成失败!")
    
    # 测试空数据
    print("\n测试空数据...")
    empty_df = pd.DataFrame()
    empty_email = generate_email_draft(empty_df)
    
    if empty_email is None:
        print("空数据测试通过 - 正确返回None")
    else:
        print("空数据测试失败 - 应该返回None")

if __name__ == "__main__":
    test_email_generation() 