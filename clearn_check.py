import pandas as pd
import os

def process_excel(file_path):
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
                'Category': None,
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
                
                result_rows.append({
                    'Item#': row['Item#'],
                    'ID': item_id,
                    'P/N': row['P/N'],
                    'Desc': row['Desc'],
                    'Qty': row['Qty'],
                    'Price': row['Price'],
                    'Category': row['Category'],
                    'Item_Name': item_name,
                    'HSN': row['HSN'],
                    'Duty': row['Duty'],
                    'Welfare': row['Welfare'],
                    'IGST': row['IGST'],
                })
    
    # 创建结果DataFrame
    result_df = pd.DataFrame(result_rows)
    
    return result_df

# 使用示例
file_path = 'c.xlsx'
result = process_excel(file_path)

# 保存结果
try:
    # Try to save normally first
    result.to_excel('clean_check.xlsx', index=False)
except PermissionError:
    # If file exists and is locked/open, try to remove it first
    try:
        os.remove('clean_check.xlsx')
    except:
        pass
    # Try saving again after removing
    result.to_excel('clean_check.xlsx', index=False)
except Exception as e:
    print(f"Error saving file: {str(e)}")
    # Try saving with a different filename
    result.to_excel('clean_check_new.xlsx', index=False)