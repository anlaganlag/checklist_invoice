#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入修复后的函数
from streamlit_app import get_duty_rates, process_invoice_file, process_checklist, compare_excels

def test_processing():
    """测试修复后的处理流程"""
    
    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("🧪 开始测试修复后的处理流程...")
    print("="*60)
    
    try:
        # 1. 测试税率文件处理
        print("📊 步骤1: 处理税率文件...")
        duty_rate_path = "input/duty_rate.xlsx"
        if not os.path.exists(duty_rate_path):
            print(f"❌ 税率文件不存在: {duty_rate_path}")
            return False
            
        duty_rates, duty_df = get_duty_rates(duty_rate_path)
        print(f"✅ 税率文件处理成功，包含 {len(duty_rates)} 个项目")
        
        # 2. 测试发票文件处理
        print("\n📋 步骤2: 处理发票文件...")
        invoice_files = ["input/processing_invoices23.xlsx", "input/processing_invoices33.xlsx"]
        
        for invoice_path in invoice_files:
            if os.path.exists(invoice_path):
                print(f"处理发票文件: {invoice_path}")
                processed_invoices, new_items = process_invoice_file(invoice_path, duty_rates)
                
                if not processed_invoices.empty:
                    print(f"✅ 发票文件处理成功:")
                    print(f"   - 处理了 {len(processed_invoices)} 行数据")
                    print(f"   - 发现 {len(new_items)} 个新项目")
                    print(f"   - 列名: {processed_invoices.columns.tolist()}")
                    
                    # 显示前几行数据
                    if len(processed_invoices) > 0:
                        print("   - 前3行数据:")
                        for i, row in processed_invoices.head(3).iterrows():
                            print(f"     行{i}: ID={row.get('ID', 'N/A')}, P/N={row.get('P/N', 'N/A')}, Item_Name={row.get('Item_Name', 'N/A')}")
                    
                    # 使用这个文件进行后续测试
                    test_invoice_path = invoice_path
                    test_processed_invoices = processed_invoices
                    test_new_items = new_items
                    break
                else:
                    print(f"⚠️ 发票文件 {invoice_path} 处理后为空")
            else:
                print(f"⚠️ 发票文件不存在: {invoice_path}")
        
        # 3. 测试核对清单处理
        print("\n📝 步骤3: 处理核对清单...")
        checklist_path = "input/processing_checklist.xlsx"
        if not os.path.exists(checklist_path):
            print(f"❌ 核对清单文件不存在: {checklist_path}")
            return False
            
        processed_checklist = process_checklist(checklist_path)
        if not processed_checklist.empty:
            print(f"✅ 核对清单处理成功:")
            print(f"   - 处理了 {len(processed_checklist)} 行数据")
            print(f"   - 列名: {processed_checklist.columns.tolist()}")
            
            # 显示前几行数据
            if len(processed_checklist) > 0:
                print("   - 前3行数据:")
                for i, row in processed_checklist.head(3).iterrows():
                    print(f"     行{i}: ID={row.get('ID', 'N/A')}, P/N={row.get('P/N', 'N/A')}, Item_Name={row.get('Item_Name', 'N/A')}")
        else:
            print("❌ 核对清单处理后为空")
            return False
        
        # 4. 测试比较功能
        print("\n🔍 步骤4: 比较发票和核对清单...")
        if 'test_processed_invoices' in locals() and not test_processed_invoices.empty:
            diff_report = compare_excels(test_processed_invoices, processed_checklist, 1.1)
            
            if not diff_report.empty:
                print(f"✅ 比较完成，发现 {len(diff_report)} 个差异:")
                print(f"   - 差异报告列名: {diff_report.columns.tolist()}")
                
                # 显示前几个差异
                if len(diff_report) > 0:
                    print("   - 前3个差异:")
                    for i, row in diff_report.head(3).iterrows():
                        print(f"     差异{i}: ID={row.get('ID', 'N/A')}")
                        for col in diff_report.columns:
                            if col != 'ID' and pd.notna(row[col]) and str(row[col]).strip():
                                print(f"       {col}: {row[col]}")
            else:
                print("✅ 比较完成，没有发现差异")
        else:
            print("⚠️ 跳过比较步骤，因为发票数据为空")
        
        print("\n🎉 所有测试步骤完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_processing()
    if success:
        print("\n✅ 测试成功！修复已生效。")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！需要进一步调试。")
        sys.exit(1) 