import streamlit as st
import pandas as pd
import os
import sys
import warnings
import glob
import logging
import datetime
import urllib.parse
import webbrowser
from io import BytesIO

# Set up logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"streamlit_app_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Log startup information
logging.info("="*50)
logging.info("STREAMLIT APP STARTED")
logging.info(f"Log file: {log_file}")
logging.info(f"Working directory: {os.getcwd()}")
logging.info(f"Python version: {sys.version}")
logging.info("="*50)

# Filter out the warning about print area
warnings.filterwarnings('ignore', message='Print area cannot be set to Defined name')

# Set page configuration
st.set_page_config(
    page_title="Checklist核对系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-message {
        color: #4CAF50;
        font-weight: bold;
    }
    .error-message {
        color: #F44336;
        font-weight: bold;
    }
    .warning-message {
        color: #FF9800;
        font-weight: bold;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Create directories if they don't exist
os.makedirs('input', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Main header
st.markdown("<h1 class='main-header'>Checklist核对系统</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/invoice.png", width=100)
    st.markdown("## 操作面板")

    # File upload section
    st.markdown("### 上传文件")

    # Upload duty_rate file
    duty_rate_file = st.file_uploader("上传税率文件 (duty_rate.xlsx)", type=["xlsx"])

    # Upload checklist file
    checklist_file = st.file_uploader("上传核对清单 (processing_checklist.xlsx)", type=["xlsx"])

    # Upload invoices file
    invoices_file = st.file_uploader("上传发票文件 (processing_invoices*.xlsx)", type=["xlsx"])

    # Add tolerance input for Price comparison
    st.markdown("### 设置")
    price_tolerance = st.slider("价格比对误差范围 (%)", min_value=0.1, max_value=5.0, value=1.1, step=0.1)
    st.caption(f"当前设置: 价格差异超过 {price_tolerance}% 将被标记")

    # Process button
    process_button = st.button("开始处理", type="primary")

    # Help section
    st.markdown("---")
    st.markdown("### 帮助")
    with st.expander("如何使用"):
        st.markdown("""
        1. 上传税率文件 (duty_rate.xlsx)
        2. 上传核对清单 (processing_checklist.xlsx)
        3. 上传发票文件 (processing_invoices*.xlsx)
        4. 调整价格比对误差范围（可选）
        5. 点击"开始处理"按钮
        6. 查看处理结果
        """)

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["文件上传", "数据预览", "处理结果", "差异报告", "日志"])

# Functions from the original scripts
def get_duty_rates(file_path):
    logging.info(f"Reading duty rates from: {file_path}")
    try:
        # Read duty_rate.xlsx
        df = pd.read_excel(file_path)
        logging.info(f"Duty rate file loaded. Shape: {df.shape}")
        logging.info(f"Duty rate columns: {df.columns.tolist()}")

        # Group by Item_Name and aggregate other columns
        logging.info("Grouping duty rates by 'Item Name'")
        grouped_df = df.groupby('Item Name').agg({
            'HSN1': lambda x: ' '.join(str(i) for i in x if pd.notna(i)),  # Concatenate HSN1 with space
            'HSN2': lambda x: ' '.join(str(i) for i in x if pd.notna(i)),  # Add HSN2
            'Final BCD': 'min',
            'Final SWS': 'min',
            'Final IGST': 'min'
        }).reset_index()

        logging.info(f"Grouped duty rates. Shape: {grouped_df.shape}")

        # Convert DataFrame to dictionary
        duty_dict = {}
        for _, row in grouped_df.iterrows():
            # Use HSN2 if HSN1 is empty
            hsn_value = row['HSN1'] if pd.notna(row['HSN1']) and row['HSN1'].strip() != '' else row['HSN2']
            duty_dict[row['Item Name']] = {
                'hsn': hsn_value,
                'bcd': row['Final BCD'],
                'sws': row['Final SWS'],
                'igst': row['Final IGST']
            }

        logging.info(f"Created duty dictionary with {len(duty_dict)} items")
        return duty_dict, df
    except Exception as e:
        error_msg = f"读取税率文件失败: {str(e)}"
        logging.error(error_msg)
        logging.exception("Exception details:")
        st.error(error_msg)
        return {}, None

def process_invoice_file(file_path, duty_rates):
    logging.info(f"Processing invoice file: {file_path}")
    try:
        # Get all sheet names
        excel_file = pd.ExcelFile(file_path)
        all_sheet_names = excel_file.sheet_names
        logging.info(f"All sheet names in invoice file: {all_sheet_names}")

        # Store original sheet names for accessing sheets
        original_sheet_names = excel_file.sheet_names[1:]  # Skip the first sheet
        logging.info(f"Processing sheets (skipping first): {original_sheet_names}")

        # Process sheet names for display and ID creation (remove CI- prefix)
        processed_sheet_names = [name.replace('CI-', '') if name.startswith('CI-') else name
                      for name in original_sheet_names]
        logging.info(f"Processed sheet names: {processed_sheet_names}")

        # Initialize DataFrames for results
        all_invoices_df = pd.DataFrame()
        new_descriptions_df = pd.DataFrame()

        # Process each sheet
        for i, (original_sheet_name, processed_sheet_name) in enumerate(zip(original_sheet_names, processed_sheet_names)):
            logging.info(f"Processing sheet {i+1}/{len(original_sheet_names)}: {original_sheet_name}")
            # Read the sheet
            df = pd.read_excel(file_path, sheet_name=original_sheet_name)
            logging.info(f"Sheet data loaded. Shape: {df.shape}")
            if not df.empty:
                logging.info(f"First few columns: {df.columns[:5].tolist() if len(df.columns) > 5 else df.columns.tolist()}")

            # Create a new DataFrame for this sheet
            sheet_df = pd.DataFrame()

            # Add Item# column first
            sheet_df['Item#'] = df.iloc[:, 0]  # Assuming Item# is always the first column

            # IMPORTANT: Update these indices based on the printed columns
            column_indices = {
                'Item#': 0,
                'P/N': 2,
                'Desc': 3,
                'Qty': 5,
                'Price': 6,
                'Item_Name': 3,
            }
            logging.info(f"Using column indices: {column_indices}")

            # Then add other columns except Item# (since it's already added)
            for new_name, idx in column_indices.items():
                if new_name == 'Item#':
                    continue # Skip Item# as it's already added
                # For Item_Name column, split by '-' and take only the part before it
                if new_name == 'Item_Name':
                    sheet_df[new_name] = df.iloc[:, idx].apply(lambda x: str(x).split('-')[0].strip() if pd.notna(x) and '-' in str(x) else x)
                elif new_name == 'Desc':
                    # Clean the description text to only keep alphanumeric, dots, hyphens and parentheses
                    sheet_df[new_name] = df.iloc[:, idx].apply(lambda x: ''.join(char.upper() for char in str(x) if char.isalnum() or char in '.()').replace('Φ', '').replace('Ω', '').replace('-', '').replace('φ', '') if pd.notna(x) else x)
                else:
                    sheet_df[new_name] = df.iloc[:, idx]

            # Create ID in the first column
            sheet_df.loc[1:,'ID'] = processed_sheet_name + '_' + sheet_df['Item#'].astype(str)
            logging.info(f"Created IDs for sheet {original_sheet_name}")

            # Add duty rate columns after all other columns are set
            sheet_df['HSN'] = ''
            sheet_df['BCD'] = ''
            sheet_df['SWS'] = ''
            sheet_df['IGST'] = ''
            unique_desc = set()

            # Fill duty rate information and collect unmatched items
            new_items_count = 0
            for idx, row in sheet_df.iterrows():
                itemName = row['Item_Name']
                if pd.notna(itemName) and itemName != '':
                    if itemName in duty_rates:
                        rates = duty_rates[itemName]
                        sheet_df.at[idx, 'HSN'] = rates['hsn']
                        sheet_df.at[idx, 'BCD'] = rates['bcd']
                        sheet_df.at[idx, 'SWS'] = rates['sws']
                        sheet_df.at[idx, 'IGST'] = rates['igst']
                    else:
                        sheet_df.at[idx, 'HSN'] = 'new item'
                        sheet_df.at[idx, 'BCD'] = 'new item'
                        sheet_df.at[idx, 'SWS'] = 'new item'
                        sheet_df.at[idx, 'IGST'] = 'new item'
                        if itemName not in unique_desc:
                            unique_desc.add(itemName)
                            new_items_count += 1
                            # Add unmatched items to new_descriptions_df
                            new_descriptions_df = pd.concat([new_descriptions_df, pd.DataFrame({
                                '发票及项号': [str(row['ID'])],
                                'Item Name': [itemName],
                                'Final BCD': [''],
                                'Final SWS': [''],
                                'Final IGST': [''],
                                'HSN1': [''],
                                # 添加兼容旧版本的列，确保为字符串类型
                                'Duty': [''],
                                'Welfare': ['']
                            })], ignore_index=True)

            logging.info(f"Found {new_items_count} new items in sheet {original_sheet_name}")

            # Add this sheet's data to the combined DataFrame
            all_invoices_df = pd.concat([all_invoices_df, sheet_df], ignore_index=True)
            logging.info(f"Added sheet data to combined DataFrame. Current size: {all_invoices_df.shape}")

        logging.info(f"Completed processing invoice file. Final DataFrame shape: {all_invoices_df.shape}")
        logging.info(f"New items found: {len(new_descriptions_df)}")

        # Check for duplicate IDs
        duplicate_ids = all_invoices_df['ID'].value_counts()[all_invoices_df['ID'].value_counts() > 1]
        if not duplicate_ids.empty:
            logging.warning(f"Found {len(duplicate_ids)} duplicate IDs in processed invoices:")
            logging.warning(duplicate_ids.head(10).to_dict())  # Log first 10 duplicates
            # Remove duplicates
            all_invoices_df = all_invoices_df.drop_duplicates(subset=['ID'], keep='first')
            logging.info(f"Removed duplicates. New DataFrame shape: {all_invoices_df.shape}")

        # 在return前添加类型转换
        # 确保特定列为字符串类型，解决Arrow序列化问题
        columns_to_convert = ['Item#', 'P/N', 'ID', 'Qty', 'Price', 'HSN', 'BCD', 'SWS', 'IGST', 'Item_Name']
        for col in columns_to_convert:
            if col in all_invoices_df.columns:
                all_invoices_df[col] = all_invoices_df[col].astype(str)

        # 确保new_descriptions_df中的所有列都是字符串类型，特别是Duty列
        if not new_descriptions_df.empty:
            # 记录列名，帮助调试
            logging.info(f"new_descriptions_df columns: {new_descriptions_df.columns.tolist()}")

            # 除了'Item Name'外，将所有列转换为字符串
            for col in new_descriptions_df.columns:
                if col != 'Item Name':  # 保留Item Name列的原始类型
                    new_descriptions_df[col] = new_descriptions_df[col].astype(str)

            # 特别处理可能存在的Duty和Welfare列（旧名称）
            for col in ['Duty', 'Welfare', 'Final BCD', 'Final SWS', 'Final IGST', 'HSN1']:
                if col in new_descriptions_df.columns:
                    new_descriptions_df[col] = new_descriptions_df[col].astype(str)

        return all_invoices_df, new_descriptions_df
    except Exception as e:
        error_msg = f"处理发票文件失败: {str(e)}"
        logging.error(error_msg)
        logging.exception("Exception details:")
        st.error(error_msg)
        return pd.DataFrame(), pd.DataFrame()

def process_checklist(file_path):
    logging.info(f"Processing checklist file: {file_path}")
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path, skiprows=3)
        logging.info(f"Checklist file loaded. Shape: {df.shape}")
        logging.info(f"Checklist columns: {df.columns.tolist()}")

        # 初始化新的DataFrame用于存储结果
        result_rows = []
        current_invoice = None
        invoice_count = 0
        item_count = 0

        # 遍历每一行
        for _, row in df.iterrows():  # 使用 _ 表示不使用的索引变量
            # 检查是否是发票行
            pn = str(row['P/N'])
            if 'Invoice:' in str(pn):
                # 提取发票号
                invoice_no = pn.split('Invoice:')[1].split('dt.')[0].strip()
                current_invoice = invoice_no
                invoice_count += 1
                logging.info(f"Found invoice #{invoice_count}: {invoice_no}")
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
                    'BCD': None,
                    'SWS': None,
                    'IGST': None
                })
            else:
                # 处理常规行
                if pd.notna(row['Item#']) and current_invoice:
                    # Convert Item# to integer before concatenating to remove the decimal
                    item_id = f"{current_invoice}_{int(row['Item#'])}"
                    item_name = str(row['Desc']).split('-')[0] if pd.notna(row['Desc']) else ''
                    item_count += 1

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

                    # 创建一个安全的字典，检查列是否存在
                    item_dict = {
                        'Item#': row['Item#'],
                        'ID': item_id,
                        'P/N': row.get('P/N', ''),
                        'Desc': desc,
                        'Qty': row.get('Qty', ''),
                        'Price': row.get('Price', ''),
                        'Item_Name': item_name,
                        'HSN': int(row.get('HSN', 0)) if str(row.get('HSN', '')).strip().isdigit() else row.get('HSN', ''),
                        'BCD': row.get('BCD', ''),
                        'SWS': row.get('SWS', ''),
                        'IGST': row.get('IGST', ''),
                    }

                    # 确保所有值都是字符串类型
                    for key in ['Item#', 'P/N', 'ID', 'Qty', 'Price', 'HSN', 'BCD', 'SWS', 'IGST']:
                        if key in item_dict and item_dict[key] is not None:
                            item_dict[key] = str(item_dict[key])

                    result_rows.append(item_dict)

        # 创建结果DataFrame
        result_df = pd.DataFrame(result_rows)
        logging.info(f"Processed checklist with {invoice_count} invoices and {item_count} items")
        logging.info(f"Final checklist DataFrame shape: {result_df.shape}")

        # Check for duplicate IDs
        duplicate_ids = result_df['ID'].value_counts()[result_df['ID'].value_counts() > 1]
        if not duplicate_ids.empty:
            logging.warning(f"Found {len(duplicate_ids)} duplicate IDs in processed checklist:")
            logging.warning(duplicate_ids.head(10).to_dict())  # Log first 10 duplicates
            # Remove duplicates
            result_df = result_df.drop_duplicates(subset=['ID'], keep='first')
            logging.info(f"Removed duplicates. New DataFrame shape: {result_df.shape}")

        # 在return前添加类型转换
        # 确保特定列为字符串类型，解决Arrow序列化问题
        columns_to_convert = ['Item#', 'P/N', 'ID', 'Qty', 'Price', 'HSN', 'BCD', 'SWS', 'IGST']
        for col in columns_to_convert:
            if col in result_df.columns:
                result_df[col] = result_df[col].astype(str)

        return result_df
    except Exception as e:
        error_msg = f"处理核对清单失败: {str(e)}"
        logging.error(error_msg)
        logging.exception("Exception details:")
        st.error(error_msg)
        return pd.DataFrame()

def compare_excels(df1, df2, price_tolerance_pct=1.1):
    logging.info("Starting comparison between processed invoices and checklist")
    logging.info(f"Using price tolerance: {price_tolerance_pct}%")
    logging.info(f"DataFrame 1 (invoices) shape: {df1.shape}")
    logging.info(f"DataFrame 2 (checklist) shape: {df2.shape}")

    # 记录两个DataFrame的列名，帮助调试
    logging.info(f"DataFrame 1 columns: {df1.columns.tolist()}")
    logging.info(f"DataFrame 2 columns: {df2.columns.tolist()}")

    try:
        # 检查ID列是否存在
        if 'ID' not in df1.columns:
            error_msg = "'ID' column not found in DataFrame 1"
            logging.error(error_msg)
            st.error(error_msg)
            return pd.DataFrame()

        if 'ID' not in df2.columns:
            error_msg = "'ID' column not found in DataFrame 2"
            logging.error(error_msg)
            st.error(error_msg)
            return pd.DataFrame()

        # 检查为null的IDs
        null_ids_df1 = df1['ID'].isna().sum()
        null_ids_df2 = df2['ID'].isna().sum()
        if null_ids_df1 > 0:
            logging.warning(f"Found {null_ids_df1} null IDs in DataFrame 1 (invoices)")
        if null_ids_df2 > 0:
            logging.warning(f"Found {null_ids_df2} null IDs in DataFrame 2 (checklist)")

        # Check for duplicate IDs before comparison
        duplicate_ids_df1 = df1['ID'].value_counts()[df1['ID'].value_counts() > 1]
        duplicate_ids_df2 = df2['ID'].value_counts()[df2['ID'].value_counts() > 1]

        if not duplicate_ids_df1.empty:
            logging.warning(f"Found {len(duplicate_ids_df1)} duplicate IDs in DataFrame 1 (invoices)")
            logging.warning(f"First 5 duplicates: {duplicate_ids_df1.head().to_dict()}")
            # Remove duplicates from df1, keeping the first occurrence
            df1 = df1.drop_duplicates(subset=['ID'], keep='first')
            logging.info(f"Removed duplicates from DataFrame 1. New shape: {df1.shape}")

        if not duplicate_ids_df2.empty:
            logging.warning(f"Found {len(duplicate_ids_df2)} duplicate IDs in DataFrame 2 (checklist)")
            logging.warning(f"First 5 duplicates: {duplicate_ids_df2.head().to_dict()}")
            # Remove duplicates from df2, keeping the first occurrence
            df2 = df2.drop_duplicates(subset=['ID'], keep='first')
            logging.info(f"Removed duplicates from DataFrame 2. New shape: {df2.shape}")

        # 确保两个 DataFrame 的列名顺序一致
        # 首先检查两个 DataFrame 的列是否一致
        common_columns = list(set(df1.columns) & set(df2.columns))
        logging.info(f"Common columns between DataFrames: {common_columns}")

        # 只使用两个 DataFrame 中都存在的列进行比较
        df1 = df1[common_columns]
        df2 = df2[common_columns]
        logging.info(f"Aligned columns between DataFrames")

        # 用于存储差异信息
        diff_data = []
        # Keep track of processed IDs to avoid duplicates
        processed_ids = set()
        match_count = 0
        diff_count = 0

        for _, row1 in df1.iterrows():
            id1 = row1['ID']
            # Skip if this ID has already been processed or is None
            if id1 is None or pd.isna(id1) or id1 in processed_ids:
                continue

            # Add this ID to the processed set
            processed_ids.add(id1)

            # 查找 df2 中对应 ID 的行
            matching_row = df2[df2['ID'] == id1]
            if not matching_row.empty:
                match_count += 1
                row2 = matching_row.iloc[0]
                diff_cols = []
                for col in df1.columns[1:]:  # 跳过ID列
                    # 跳过Item_Name列和Item#列的比对
                    if col == 'Item_Name' or col == 'Item#':
                        continue

                    # 对Price列使用用户设置的误差范围
                    if col == 'Price':
                        if pd.notna(row1[col]) and pd.notna(row2[col]):
                            try:
                                # 首先尝试将值转换为float类型
                                price1 = float(row1[col]) if isinstance(row1[col], str) else row1[col]
                                price2 = float(row2[col]) if isinstance(row2[col], str) else row2[col]

                                # 计算容差
                                tolerance = price1 * (price_tolerance_pct / 100)  # 转换为小数
                                if abs(price1 - price2) > tolerance:
                                    diff_cols.append(col)
                            except (ValueError, TypeError):
                                # 如果转换失败，记录错误并跳过比较
                                logging.warning(f"无法比较价格: {row1[col]} vs {row2[col]}，跳过此比较")
                                # 保险起见，标记为有差异
                                diff_cols.append(col)
                    # 对HSN列特殊处理，忽略浮点数和整数的差异（如85423900.0和85423900）
                    elif col == 'HSN':
                        if pd.notna(row1[col]) and pd.notna(row2[col]):
                            # 将两个值转换为字符串并去除小数点后的零
                            val1 = str(row1[col]).rstrip('0').rstrip('.') if '.' in str(row1[col]) else str(row1[col])
                            val2 = str(row2[col]).rstrip('0').rstrip('.') if '.' in str(row2[col]) else str(row2[col])

                            # 记录HSN值的比较
                            if val1 != val2:
                                logging.info(f"HSN difference found: {row1[col]} vs {row2[col]} (normalized: {val1} vs {val2})")
                                diff_cols.append(col)
                            else:
                                logging.debug(f"HSN values considered equal: {row1[col]} vs {row2[col]} (normalized: {val1} vs {val2})")
                    # 其他列使用精确比对
                    elif row1[col] != row2[col]:
                        diff_cols.append(col)

                if diff_cols:
                    diff_count += 1
                    # 只创建包含ID和有差异列的信息
                    diff_info = {'ID': id1}

                    # 记录差异列
                    logging.info(f"ID {id1} 的差异列: {diff_cols}")

                    # 按照期望的列顺序处理差异列
                    expected_columns = ['ID', 'P/N', 'Desc', 'HSN', 'BCD', 'SWS', 'IGST', 'Qty', 'Price']

                    # 首先处理ID列
                    diff_info['ID'] = id1

                    # 然后按照期望的顺序处理其他列
                    for col in expected_columns:
                        if col != 'ID' and col in diff_cols:
                            # 对数字列特殊处理显示格式，去除小数点后的零
                            if col in ['HSN', 'BCD', 'SWS', 'IGST', 'Qty', 'Price']:
                                # 处理数值，去除小数点后的零
                                val1 = str(row1[col]).rstrip('0').rstrip('.') if '.' in str(row1[col]) else str(row1[col])
                                val2 = str(row2[col]).rstrip('0').rstrip('.') if '.' in str(row2[col]) else str(row2[col])

                                # 跳过相同值的显示 (例如 10 -> 10)
                                if val1 == val2:
                                    continue

                                # 跳过NaN值或空值 - 更严格的检查
                                if (val1.lower() == 'nan' or val2.lower() == 'nan' or
                                    val1 == '' or val2 == '' or
                                    val1.lower() == 'none' or val2.lower() == 'none' or
                                    val1.strip() == '' or val2.strip() == ''):
                                    continue

                                # 跳过相同值的显示 (例如 nan -> nan)
                                if val1.lower() == val2.lower():
                                    continue

                                # 确保不是"nan -> 值"或"值 -> nan"的情况
                                display_val1 = '' if val1.lower() in ['nan', 'none', ''] else val1
                                display_val2 = '' if val2.lower() in ['nan', 'none', ''] else val2

                                # 只有当两个值都不是空/nan时才添加
                                if display_val1 and display_val2:
                                    diff_info[f'{col}'] = f'{display_val2} -> {display_val1}'
                            else:
                                # 跳过相同值的显示
                                if row1[col] == row2[col]:
                                    continue

                                # 跳过NaN值或空值 - 更严格的检查
                                if pd.isna(row1[col]) or pd.isna(row2[col]) or str(row1[col]).strip() == '' or str(row2[col]).strip() == '':
                                    continue

                                # 将值转换为字符串并检查是否为'nan'或'none'
                                val1 = str(row1[col]).lower()
                                val2 = str(row2[col]).lower()
                                if (val1 == 'nan' or val2 == 'nan' or
                                    val1 == 'none' or val2 == 'none' or
                                    val1.strip() == '' or val2.strip() == ''):
                                    continue

                                # 跳过相同值的显示 (例如 nan -> nan)
                                if val1 == val2:
                                    continue

                                # 确保不是"nan -> 值"或"值 -> nan"的情况
                                display_val1 = '' if val1 in ['nan', 'none', ''] else str(row1[col])
                                display_val2 = '' if val2 in ['nan', 'none', ''] else str(row2[col])

                                # 只有当两个值都不是空/nan时才添加
                                if display_val1 and display_val2:
                                    diff_info[f'{col}'] = f'{display_val2} -> {display_val1}'

                    # 只有当diff_info中有除了ID以外的其他列时才添加到diff_data
                    if len(diff_info) > 1:
                        diff_data.append(diff_info)

        logging.info(f"Comparison complete. Found {match_count} matching IDs between files")
        logging.info(f"Found {diff_count} differences")

        if diff_data:
            diff_df = pd.DataFrame(diff_data)

            # 列名已经是 BCD 和 SWS，不需要再进行映射

            # 定义期望的列顺序 (按照指定顺序)
            expected_columns = ['ID', 'P/N', 'Desc', 'HSN', 'BCD', 'SWS', 'IGST', 'Qty', 'Price']

            # 只保留实际有数据的列
            non_empty_columns = ['ID']  # ID列始终保留

            # 检查每一列是否有非空/非nan数据
            for col in diff_df.columns:
                if col != 'ID':  # 跳过ID列，因为已经包含
                    # 检查列是否包含任何非空值
                    has_data = False
                    for val in diff_df[col]:
                        if pd.notna(val) and str(val).strip() != '' and str(val).lower() != 'nan' and str(val).lower() != 'none':
                            has_data = True
                            break

                    if has_data:
                        non_empty_columns.append(col)

            # 严格按照期望的列顺序排序，只包含存在的列
            ordered_columns = []
            for col in expected_columns:
                if col in diff_df.columns and (col == 'ID' or col in non_empty_columns):
                    ordered_columns.append(col)
                    logging.info(f"添加列到最终报告: {col}")
                elif col in expected_columns:
                    logging.info(f"列 {col} 不存在或为空，跳过")

            # 不再添加其他列，确保严格按照指定顺序
            logging.info(f"最终列顺序: {ordered_columns}")

            # 应用新的列顺序
            diff_df = diff_df[ordered_columns]

            logging.info(f"Created difference DataFrame with shape: {diff_df.shape}")
            logging.info(f"Columns in final report: {diff_df.columns.tolist()}")

            # 添加类型转换，解决Arrow序列化问题
            for col in diff_df.columns:
                # 所有列都转为字符串，包括之前排除的Item Name
                diff_df[col] = diff_df[col].astype(str)

            # 额外处理：确保没有字符串形式的'nan'或'none'
            for col in diff_df.columns:
                diff_df[col] = diff_df[col].apply(
                    lambda x: '' if x.lower() in ['nan', 'none'] else x
                )

            # 特别处理可能存在的Duty和Welfare列（旧名称）
            for old_col in ['Duty', 'Welfare']:
                if old_col in diff_df.columns:
                    diff_df[old_col] = diff_df[old_col].astype(str)
                    logging.info(f"转换了差异报告中的旧列名 {old_col} 为字符串类型")

            return diff_df
        else:
            logging.info("No differences found between files")
            return pd.DataFrame()

    except Exception as e:
        error_msg = f"比较文件失败: {str(e)}"
        logging.error(error_msg)
        logging.exception("Exception details:")
        st.error(error_msg)
        return pd.DataFrame()

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
        logging.exception("Exception details:")
        return None

def open_email_client(email_content, subject="Checklist Revision Required"):
    """
    打开默认邮件客户端并填充邮件内容
    """
    try:
        # URL编码邮件内容
        encoded_subject = urllib.parse.quote(subject)
        encoded_body = urllib.parse.quote(email_content)
        
        # 构建mailto链接
        mailto_url = f"mailto:?subject={encoded_subject}&body={encoded_body}"
        
        # 打开邮件客户端
        webbrowser.open(mailto_url)
        logging.info("已打开默认邮件客户端")
        return True
        
    except Exception as e:
        error_msg = f"打开邮件客户端失败: {str(e)}"
        logging.error(error_msg)
        logging.exception("Exception details:")
        return False

# File Upload Tab
with tab1:
    st.markdown("<h2 class='sub-header'>文件上传</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown("### 税率文件")
        if duty_rate_file is not None:
            st.success(f"已上传: {duty_rate_file.name}")
            # Save the uploaded file
            with open(os.path.join("input", "duty_rate.xlsx"), "wb") as f:
                f.write(duty_rate_file.getbuffer())
        else:
            st.warning("请上传税率文件")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown("### 核对清单")
        if checklist_file is not None:
            st.success(f"已上传: {checklist_file.name}")
            # Save the uploaded file
            with open(os.path.join("input", "processing_checklist.xlsx"), "wb") as f:
                f.write(checklist_file.getbuffer())
        else:
            st.warning("请上传核对清单")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown("### 发票文件")
        if invoices_file is not None:
            st.success(f"已上传: {invoices_file.name}")
            # Save the uploaded file
            with open(os.path.join("input", "processing_invoices.xlsx"), "wb") as f:
                f.write(invoices_file.getbuffer())
        else:
            st.warning("请上传发票文件")
        st.markdown("</div>", unsafe_allow_html=True)

# Data Preview Tab
with tab2:
    st.markdown("<h2 class='sub-header'>数据预览</h2>", unsafe_allow_html=True)

    preview_tabs = st.tabs(["税率数据", "核对清单", "发票数据"])

    with preview_tabs[0]:
        if duty_rate_file is not None:
            try:
                duty_df = pd.read_excel(duty_rate_file)
                st.dataframe(duty_df, use_container_width=True)
            except Exception as e:
                st.error(f"无法预览税率文件: {str(e)}")
        else:
            st.info("请先上传税率文件")

    with preview_tabs[1]:
        if checklist_file is not None:
            try:
                checklist_df = pd.read_excel(checklist_file, skiprows=3)
                st.dataframe(checklist_df, use_container_width=True)
            except Exception as e:
                st.error(f"无法预览核对清单: {str(e)}")
        else:
            st.info("请先上传核对清单")

    with preview_tabs[2]:
        if invoices_file is not None:
            try:
                excel_file = pd.ExcelFile(invoices_file)
                sheet_names = excel_file.sheet_names[1:]  # Skip the first sheet

                if sheet_names:
                    selected_sheet = st.selectbox("选择发票工作表", sheet_names)
                    invoices_df = pd.read_excel(invoices_file, sheet_name=selected_sheet)
                    st.dataframe(invoices_df, use_container_width=True)
                else:
                    st.warning("发票文件中没有找到工作表")
            except Exception as e:
                st.error(f"无法预览发票文件: {str(e)}")
        else:
            st.info("请先上传发票文件")

# Process data when button is clicked
if process_button:
    logging.info("Process button clicked")
    if duty_rate_file is None or checklist_file is None or invoices_file is None:
        missing_files = []
        if duty_rate_file is None:
            missing_files.append("税率文件")
        if checklist_file is None:
            missing_files.append("核对清单")
        if invoices_file is None:
            missing_files.append("发票文件")
        error_msg = f"请先上传所有必要的文件: {', '.join(missing_files)}"
        logging.error(error_msg)
        st.error(error_msg)
    else:
        logging.info("Starting data processing workflow")
        with st.spinner("正在处理数据..."):
            try:
                # Log input file paths
                duty_rate_path = os.path.join("input", "duty_rate.xlsx")
                invoices_path = os.path.join("input", "processing_invoices.xlsx")
                checklist_path = os.path.join("input", "processing_checklist.xlsx")

                logging.info(f"Input files: duty_rate={duty_rate_path}, invoices={invoices_path}, checklist={checklist_path}")
                logging.info(f"Price tolerance: {price_tolerance}%")

                # Process duty rates
                logging.info("Step 1: Processing duty rates")
                duty_rates, duty_df = get_duty_rates(duty_rate_path)

                # Process invoices
                logging.info("Step 2: Processing invoices")
                processed_invoices, new_items = process_invoice_file(invoices_path, duty_rates)

                # Process checklist
                logging.info("Step 3: Processing checklist")
                processed_checklist = process_checklist(checklist_path)

                # Compare the processed files
                logging.info("Step 4: Comparing processed files")
                diff_report = compare_excels(processed_invoices, processed_checklist, price_tolerance)

                # Save the processed files
                logging.info("Step 5: Saving output files")
                processed_invoices_path = os.path.join("output", "processed_invoices.xlsx")
                processed_checklist_path = os.path.join("output", "processed_checklist.xlsx")
                processed_report_path = os.path.join("output", "processed_report.xlsx")

                try:
                    # Save the diff report if it's not empty
                    if not diff_report.empty:
                        # 在导出前确保没有NaN值
                        export_diff_report = diff_report.copy()

                        # 将所有NaN值替换为空字符串
                        export_diff_report = export_diff_report.fillna('')

                        # 额外处理：确保没有字符串形式的'nan'或'none'
                        for col in export_diff_report.columns:
                            export_diff_report[col] = export_diff_report[col].apply(
                                lambda x: '' if isinstance(x, str) and x.lower() in ['nan', 'none'] else x
                            )

                        # 使用xlsxwriter引擎保存，以便设置列宽
                        with pd.ExcelWriter(processed_report_path, engine='xlsxwriter') as writer:
                            export_diff_report.to_excel(writer, index=False, sheet_name='差异报告')

                            # 获取工作表
                            worksheet = writer.sheets['差异报告']

                            # 设置列宽 - 除了DESC字段外的所有列都宽一倍
                            for i, col in enumerate(export_diff_report.columns):
                                worksheet.set_column(i, i, 22)

                        logging.info(f"Saved diff report to {processed_report_path} with custom column widths")

                        # 创建用于自动下载的BytesIO对象
                        report_buffer = BytesIO()
                        with pd.ExcelWriter(report_buffer, engine='xlsxwriter') as writer:
                            # 使用已经处理过NaN的export_diff_report
                            export_diff_report.to_excel(writer, index=False, sheet_name='差异报告')

                            # 获取工作表
                            worksheet = writer.sheets['差异报告']

                            # 设置列宽 - 除了DESC字段外的所有列都宽一倍
                            for i, col in enumerate(export_diff_report.columns):
                                worksheet.set_column(i, i, 22)

                        report_buffer.seek(0)

                        # 设置会话状态变量，用于自动下载
                        st.session_state.auto_download_report = report_buffer
                        st.session_state.show_download_button = True
                        
                        # 生成邮件草稿
                        logging.info("Step 6: Generating email draft")
                        email_content = generate_email_draft(diff_report)
                        if email_content:
                            st.session_state.email_draft_content = email_content
                            st.session_state.show_email_button = True
                            logging.info("邮件草稿生成成功")
                        else:
                            st.session_state.show_email_button = False
                    else:
                        logging.info("No differences found, skipping diff report creation")
                        st.session_state.show_download_button = False
                        st.session_state.show_email_button = False
                except Exception as e:
                    logging.error(f"Error saving output files: {str(e)}")
                    logging.exception("Exception details:")
                    st.error(f"保存输出文件时出错: {str(e)}")

                # Save new items if any
                if not new_items.empty:
                    logging.info(f"Found {len(new_items)} new items, saving to added_new_items.xlsx")
                    # Create a new Excel file with the original data
                    new_items_path = os.path.join("output", "added_new_items.xlsx")
                    try:
                        with pd.ExcelWriter(new_items_path, engine='xlsxwriter') as writer:
                            duty_df.to_excel(writer, index=False, sheet_name='CCTV')

                            # 获取CCTV工作表并设置列宽
                            worksheet_cctv = writer.sheets['CCTV']
                            for i, col in enumerate(duty_df.columns):
                                # 计算列的宽度
                                max_len = max(
                                    duty_df[col].astype(str).map(len).max(),  # 最长内容
                                    len(str(col))  # 列名长度
                                ) + 2  # 添加一些额外空间

                                # 除了描述类列外的所有列都宽一倍
                                if col != 'Item Name' and 'Desc' not in col:
                                    max_len = max_len * 1.2

                                # 设置列宽
                                worksheet_cctv.set_column(i, i, max_len)

                            # Add new descriptions to a new sheet with required columns
                            required_columns = ['发票及项号', 'Item Name', 'Final BCD', 'Final SWS', 'Final IGST', 'HSN1']
                            new_items[required_columns].to_excel(writer, sheet_name='newDutyRate', index=False)

                            # 获取newDutyRate工作表并设置列宽
                            worksheet_new = writer.sheets['newDutyRate']
                            for i, col in enumerate(required_columns):
                                # 计算列的宽度
                                max_len = max(
                                    new_items[col].astype(str).map(len).max(),  # 最长内容
                                    len(str(col))  # 列名长度
                                ) + 2  # 添加一些额外空间

                                # 除了描述类列外的所有列都宽一倍
                                if col != 'Item Name':
                                    max_len = max_len * 1.2

                                # 设置列宽
                                worksheet_new.set_column(i, i, max_len)

                        logging.info(f"Saved new items to {new_items_path} with custom column widths")
                    except Exception as e:
                        logging.error(f"Error saving new items: {str(e)}")
                        logging.exception("Exception details:")
                        st.error(f"保存新项目时出错: {str(e)}")

                logging.info("Data processing completed successfully")
                st.success("数据处理完成！")
            except Exception as e:
                error_msg = f"处理数据时发生错误: {str(e)}"
                logging.error(error_msg)
                logging.exception("Exception details:")
                st.error(error_msg)

# Results Tab
with tab3:
    st.markdown("<h2 class='sub-header'>处理结果</h2>", unsafe_allow_html=True)

    results_tabs = st.tabs(["处理后的发票", "处理后的核对清单", "新增税率项"])

    with results_tabs[0]:
        processed_invoices_path = os.path.join("output", "processed_invoices.xlsx")
        if os.path.exists(processed_invoices_path):
            try:
                processed_invoices_df = pd.read_excel(processed_invoices_path)

                # 添加类型转换，解决Arrow序列化问题
                columns_to_convert = ['Item#', 'P/N', 'ID', 'Qty', 'Price', 'HSN', 'BCD', 'SWS', 'IGST', 'Item_Name']
                for col in columns_to_convert:
                    if col in processed_invoices_df.columns:
                        processed_invoices_df[col] = processed_invoices_df[col].astype(str)

                # 特别处理可能存在的Duty和Welfare列（旧名称）
                for old_col in ['Duty', 'Welfare']:
                    if old_col in processed_invoices_df.columns:
                        processed_invoices_df[old_col] = processed_invoices_df[old_col].astype(str)
                        logging.info(f"转换了处理后发票中的旧列名 {old_col} 为字符串类型")

                st.dataframe(processed_invoices_df, use_container_width=True)

                # Download button
                with open(processed_invoices_path, "rb") as file:
                    st.download_button(
                        label="下载处理后的发票",
                        data=file,
                        file_name="processed_invoices.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"无法加载处理后的发票: {str(e)}")
        else:
            st.info("请先处理数据")

    with results_tabs[1]:
        processed_checklist_path = os.path.join("output", "processed_checklist.xlsx")
        if os.path.exists(processed_checklist_path):
            try:
                processed_checklist_df = pd.read_excel(processed_checklist_path)

                # 添加类型转换，解决Arrow序列化问题
                columns_to_convert = ['Item#', 'P/N', 'ID', 'Qty', 'Price', 'HSN', 'BCD', 'SWS', 'IGST', 'Item_Name']
                for col in columns_to_convert:
                    if col in processed_checklist_df.columns:
                        processed_checklist_df[col] = processed_checklist_df[col].astype(str)

                # 特别处理可能存在的Duty和Welfare列（旧名称）
                for old_col in ['Duty', 'Welfare']:
                    if old_col in processed_checklist_df.columns:
                        processed_checklist_df[old_col] = processed_checklist_df[old_col].astype(str)
                        logging.info(f"转换了处理后核对清单中的旧列名 {old_col} 为字符串类型")

                st.dataframe(processed_checklist_df, use_container_width=True)

                # Download button
                with open(processed_checklist_path, "rb") as file:
                    st.download_button(
                        label="下载处理后的核对清单",
                        data=file,
                        file_name="processed_checklist.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"无法加载处理后的核对清单: {str(e)}")
        else:
            st.info("请先处理数据")

    with results_tabs[2]:
        new_items_path = os.path.join("output", "added_new_items.xlsx")
        if os.path.exists(new_items_path):
            try:
                excel_file = pd.ExcelFile(new_items_path)
                sheet_names = excel_file.sheet_names

                if 'newDutyRate' in sheet_names:
                    new_items_df = pd.read_excel(new_items_path, sheet_name='newDutyRate')
                    if not new_items_df.empty:
                        # 添加类型转换 - 包括Item Name也转为字符串
                        for col in new_items_df.columns:
                            # 所有列都转为字符串，不再特殊处理Item Name
                            new_items_df[col] = new_items_df[col].astype(str)

                        # 特别处理可能存在的Duty和Welfare列（旧名称）
                        for old_col, new_col in [('Duty', 'BCD'), ('Welfare', 'SWS')]:
                            if old_col in new_items_df.columns:
                                new_items_df[old_col] = new_items_df[old_col].astype(str)
                                logging.info(f"转换了旧列名 {old_col} 为字符串类型")

                        st.dataframe(new_items_df, use_container_width=True)

                        # Download button
                        with open(new_items_path, "rb") as file:
                            st.download_button(
                                label="下载新增税率项",
                                data=file,
                                file_name="added_new_items.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.info("没有发现新增税率项")
                else:
                    st.info("没有发现新增税率项")
            except Exception as e:
                st.error(f"无法加载新增税率项: {str(e)}")
        else:
            st.info("没有发现新增税率项或请先处理数据")

# Diff Report Tab
with tab4:
    st.markdown("<h2 class='sub-header'>差异报告</h2>", unsafe_allow_html=True)

    diff_report_path = os.path.join("output", "processed_report.xlsx")
    if os.path.exists(diff_report_path):
        try:
            diff_report_df = pd.read_excel(diff_report_path)

            # 添加类型转换，解决Arrow序列化问题
            for col in diff_report_df.columns:
                # 所有列都转为字符串
                diff_report_df[col] = diff_report_df[col].astype(str)

            # 额外处理：确保没有字符串形式的'nan'或'none'
            for col in diff_report_df.columns:
                diff_report_df[col] = diff_report_df[col].apply(
                    lambda x: '' if isinstance(x, str) and x.lower() in ['nan', 'none'] else x
                )

            if not diff_report_df.empty:
                st.dataframe(diff_report_df, use_container_width=True)

                col1, col2 = st.columns(2)
                
                with col1:
                    # Download button
                    with open(diff_report_path, "rb") as file:
                        st.download_button(
                            label="下载差异报告",
                            data=file,
                            file_name="processed_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                with col2:
                    # 生成邮件草稿按钮
                    if st.button("生成通知邮件草稿", type="secondary", key="generate_email_button"):
                        email_content = generate_email_draft(diff_report_df)
                        if email_content:
                            # 显示邮件内容预览
                            st.session_state.email_draft_content = email_content
                            st.success("邮件草稿已生成！")
                            
                            # 尝试打开邮件客户端
                            if open_email_client(email_content):
                                st.info("已尝试打开默认邮件客户端")
                            else:
                                st.warning("无法打开邮件客户端，请手动复制下方内容")
                        else:
                            st.error("生成邮件草稿失败")
                
                # 显示邮件内容预览
                if 'email_draft_content' in st.session_state:
                    st.markdown("### 邮件草稿预览")
                    st.text_area(
                        "邮件内容",
                        st.session_state.email_draft_content,
                        height=300,
                        help="您可以复制此内容到邮件客户端",
                        key="diff_email_preview"
                    )
            else:
                st.success("没有发现差异")
        except Exception as e:
            st.error(f"无法加载差异报告: {str(e)}")
    else:
        st.info("请先处理数据")

# Logs Tab
with tab5:
    st.markdown("<h2 class='sub-header'>处理日志</h2>", unsafe_allow_html=True)

    # List all log files
    log_files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], reverse=True)

    if log_files:
        selected_log = st.selectbox("选择日志文件", log_files)
        log_path = os.path.join(log_dir, selected_log)

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()

            # Add filter options
            filter_options = st.multiselect(
                "筛选日志级别",
                ["INFO", "WARNING", "ERROR"],
                default=["WARNING", "ERROR"]
            )

            # Filter log content
            filtered_lines = []
            for line in log_content.split('\n'):
                if any(level in line for level in filter_options):
                    filtered_lines.append(line)

            if filtered_lines:
                st.text_area("日志内容", '\n'.join(filtered_lines), height=400)
            else:
                st.info("没有符合筛选条件的日志")

            # Download button for log file
            with open(log_path, "rb") as file:
                st.download_button(
                    label="下载完整日志文件",
                    data=file,
                    file_name=selected_log,
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"无法读取日志文件: {str(e)}")
    else:
        st.info("没有找到日志文件")

# Footer
st.markdown("---")

# 自动下载比对报告
if process_button and 'show_download_button' in st.session_state and st.session_state.show_download_button:
    if 'auto_download_report' in st.session_state:
        st.success("处理完成！比对报告已准备好下载")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="点击下载比对报告",
                data=st.session_state.auto_download_report,
                file_name="比对报告.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="auto_download_report_button"
            )
        
        with col2:
            # 自动生成邮件草稿按钮
            if 'show_email_button' in st.session_state and st.session_state.show_email_button:
                if st.button("生成通知邮件草稿", type="secondary", key="auto_generate_email_button"):
                    if 'email_draft_content' in st.session_state:
                        # 尝试打开邮件客户端
                        if open_email_client(st.session_state.email_draft_content):
                            st.info("已尝试打开默认邮件客户端")
                        else:
                            st.warning("无法打开邮件客户端，请前往'差异报告'标签页查看邮件内容")
                    else:
                        st.error("邮件草稿内容不可用")

# 显示自动生成的邮件草稿预览
if process_button and 'email_draft_content' in st.session_state:
    st.markdown("### 📧 邮件草稿已自动生成")
    with st.expander("查看邮件内容", expanded=False):
        st.text_area(
            "邮件内容",
            st.session_state.email_draft_content,
            height=200,
            help="您可以复制此内容到邮件客户端",
            key="auto_email_preview"
        )

st.markdown("© 2025 Checklist核对系统 | 版本 1.2")