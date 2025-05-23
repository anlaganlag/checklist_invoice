#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的邮件生成功能测试
"""

import pandas as pd
import logging

# 设置简单的日志
logging.basicConfig(level=logging.INFO)

def generate_email_draft(diff_report_df):
    """
    根据差异报告生成邮件草稿内容
    """
    logging.info("生成邮件草稿开始")
    
    if diff_report_df.empty:
        logging.info("没有差异数据，无需生成邮件草稿")
        return None
    
    try:
        email_body_lines = []
        email_body_lines.append("-------------------------------------------------------")
        email_body_lines.append("Hello ,")
        email_body_lines.append("")
        email_body_lines.append("Please revise the checklist as below:")
        
        # 遍历每一行差异数据
        for _, row in diff_report_df.iterrows():
            invoice_id = row.get('ID', 'Unknown')
            
            # 构建邮件内容行
            corrections = []
            
            # 检查各个字段的差异并构建修正信息
            if 'HSN' in row and pd.notna(row['HSN']) and str(row['HSN']).strip():
                hsn_correct = str(row['HSN']).split(' -> ')[0] if ' -> ' in str(row['HSN']) else str(row['HSN'])
                corrections.append(f"HSN {hsn_correct}")
            
            if 'BCD' in row and pd.notna(row['BCD']) and str(row['BCD']).strip():
                bcd_correct = str(row['BCD']).split(' -> ')[0] if ' -> ' in str(row['BCD']) else str(row['BCD'])
                corrections.append(f"BCD is {bcd_correct}")
            
            if 'SWS' in row and pd.notna(row['SWS']) and str(row['SWS']).strip():
                sws_correct = str(row['SWS']).split(' -> ')[0] if ' -> ' in str(row['SWS']) else str(row['SWS'])
                corrections.append(f"SWS is {sws_correct}")
            
            if 'IGST' in row and pd.notna(row['IGST']) and str(row['IGST']).strip():
                hgst_correct = str(row['IGST']).split(' -> ')[0] if ' -> ' in str(row['IGST']) else str(row['IGST'])
                corrections.append(f"HGST is {hgst_correct}")
            
            if 'Qty' in row and pd.notna(row['Qty']) and str(row['Qty']).strip():
                qty_correct = str(row['Qty']).split(' -> ')[0] if ' -> ' in str(row['Qty']) else str(row['Qty'])
                corrections.append(f"Qty is {qty_correct}")
            
            if 'Price' in row and pd.notna(row['Price']) and str(row['Price']).strip():
                price_correct = str(row['Price']).split(' -> ')[0] if ' -> ' in str(row['Price']) else str(row['Price'])
                corrections.append(f"Price is {price_correct}")
            
            if 'Desc' in row and pd.notna(row['Desc']) and str(row['Desc']).strip():
                desc_correct = str(row['Desc']).split(' -> ')[0] if ' -> ' in str(row['Desc']) else str(row['Desc'])
                corrections.append(f"Description is {desc_correct}")
            
            if corrections:
                email_line = f"Invoice {invoice_id} use {' '.join(corrections)}。"
                email_body_lines.append(email_line)
        
        email_body_lines.append("")
        email_body_lines.append("Thank you!")
        email_body_lines.append("-------------------------------------------------------")
        
        email_content = "\n".join(email_body_lines)
        logging.info(f"邮件草稿生成完成，共{len(diff_report_df)}条差异记录")
        
        return email_content
        
    except Exception as e:
        error_msg = f"生成邮件草稿失败: {str(e)}"
        logging.error(error_msg)
        return None

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