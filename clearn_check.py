import pandas as pd

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
                'Original_Row': pn,
                'id': None,
                'P/N': None,
                'Desc': None,
                'Qty': None,
                'Price': None,
                'Category': None,
                'Item_Name': None,
                'Duty': None,
                'Welfare': None,
                'IGST': None
            })
        else:
            # 处理常规行
            if pd.notna(row['Item#']) and current_invoice:
                item_id = f"{current_invoice}_{row['Item#']}"
                item_name = str(row['Desc']).split('-')[0] if pd.notna(row['Desc']) else ''
                
                result_rows.append({
                    'Original_Row': None,
                    'id': item_id,
                    'P/N': row['P/N'],
                    'Desc': row['Desc'],
                    'Qty': row['Qty'],
                    'Price': row['Price'],
                    'Category': row['Category'],
                    'Item_Name': item_name,
                    'Duty': row['Duty'],
                    'Welfare': row['Welfare'],
                    'IGST': row['IGST']
                })
    
    # 创建结果DataFrame
    result_df = pd.DataFrame(result_rows)
    
    # 处理发票行的显示
    result_df['Original_Row'] = result_df['Original_Row'].fillna('')
    
    return result_df

# 使用示例
file_path = 'c.xlsx'
result = process_excel(file_path)

# 保存结果
result.to_excel('clean_check.xlsx', index=False)