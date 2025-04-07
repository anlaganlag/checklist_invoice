import pandas as pd
import os
import sys

def process_excel(file_path):
    try:
        print("开始清理checkList文件")
        # 读取Excel文件
        df = pd.read_excel(file_path,skiprows=3)
        
        # Print column names to see what we actually have
        print("Available columns:", df.columns.tolist())
        # 初始化新的DataFrame用于存储结果
        result_rows = []
        current_invoice = None
        
        # 遍历每一行
        for index, row in df.iterrows():
            # 检查是否是发票行
            pn = str(row['P/N'])
            if 'Invoice:' in str(pn):
                # 提取发票号
                invoice_no = pn.split('Invoice:')[1].split('dt.')[0].strip()
                current_invoice = invoice_no
                # 保存发票行
                result_rows.append({
                    'Item#': pn,
                    'ID': None,
                    'P/N': None,
                    'Desc': None,
                    'Qty': None,
                    'Price': None,
                    'Item_Name': None,
                    'HSN': None,
                    'Duty': None,
                    'Welfare': None,
                    'IGST': None
                })
            else:
                # 处理常规行
                if pd.notna(row['Item#']) and current_invoice:
                    # Convert Item# to integer before concatenating to remove the decimal
                    item_id = f"{current_invoice}_{int(row['Item#'])}"
                    item_name = str(row['Desc']).split('-')[0] if pd.notna(row['Desc']) else ''

                    # 修改item_name的处理逻辑
                    desc = ''
                    if pd.notna(row['Desc']):
                        # 分割字符串，取"-PART NO"之前的部分
                        desc_parts = str(row['Desc']).split('-PART NO')
                        desc = desc_parts[0]
                        # 只保留字母数字和点号，并转换为大写
                        desc = desc.replace('+OR-', '')
                        desc = desc.replace('DEG', '')
                        desc = desc.replace('-', '')
                        desc = ''.join(char for char in desc if char.isalnum() or char in '.()').upper()
                    
                    result_rows.append({
                        'Item#': row['Item#'],
                        'ID': item_id,
                        'P/N': row['P/N'],
                        'Desc': desc,
                        'Qty': row['Qty'],
                        'Price': row['Price'],
                        'Item_Name': item_name,
                        'HSN': int(row['HSN']) if str(row['HSN']).strip().isdigit() else row['HSN'],
                        'Duty': row['Duty'],
                        'Welfare': row['Welfare'],
                        'IGST': row['IGST'],
                    })
        
        # 创建结果DataFrame
        result_df = pd.DataFrame(result_rows)
        
        return result_df

    except Exception as e:
        print(f"\n❌ 处理文件时发生错误: {str(e)}")
        print(f"错误发生在 process_excel 函数的第 {e.__traceback__.tb_lineno} 行")
        raise

# 使用示例
file_path = 'input/processing_checklist.xlsx'
try:
    result = process_excel(file_path)
except Exception as e:
    print(f"\n❌ 主流程执行失败: {str(e)}")
    print(f"错误发生在第 {e.__traceback__.tb_lineno} 行")
    sys.exit(1)

# 保存结果
try:
    os.makedirs('output', exist_ok=True)  # Add directory creation
    # Update path to output directory
    result.to_excel('output/processed_checklist.xlsx', index=False)
    print("处理完成，结果已保存到 output/processed_checklist.xlsx")
except PermissionError:
    try:
        # Update path for removal
        os.remove('output/processed_checklist.xlsx')
    except:
        pass
    # Update path for retry
    result.to_excel('output/processed_checklist.xlsx', index=False)
except Exception as e:
    # Update path in error handler
    result.to_excel('output/processed_checklist.xlsx', index=False)