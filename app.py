import streamlit as st
import pandas as pd
import os
import sys
import warnings
import glob
import logging
import datetime
from io import BytesIO

# Set up logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"streamlit_app_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum detail
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Log startup information
logging.info("="*50)
logging.info("STREAMLIT APP STARTED")
logging.info(f"Log file: {log_file}")
logging.info(f"Working directory: {os.getcwd()}")
logging.info(f"Python version: {sys.version}")
logging.info(f"Command line arguments: {sys.argv}")
logging.info(f"Platform: {sys.platform}")
logging.info("="*50)

# Log environment variables that might affect execution
env_vars = {
    'PYTHONPATH': os.environ.get('PYTHONPATH', 'Not set'),
    'PATH': os.environ.get('PATH', 'Not set')[:100] + '...',  # Truncate for readability
}
logging.info(f"Environment variables: {env_vars}")

# Filter out the warning about print area
warnings.filterwarnings('ignore', message='Print area cannot be set to Defined name')

# Set page configuration
st.set_page_config(
    page_title="发票核对系统",
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
st.markdown("<h1 class='main-header'>发票核对系统</h1>", unsafe_allow_html=True)

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
        4. 点击"开始处理"按钮
        5. 查看处理结果
        """)

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["文件上传", "数据预览", "处理结果", "差异报告"])

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
            sheet_df['Duty'] = ''
            sheet_df['Welfare'] = ''
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
                        sheet_df.at[idx, 'Duty'] = rates['bcd']
                        sheet_df.at[idx, 'Welfare'] = rates['sws']
                        sheet_df.at[idx, 'IGST'] = rates['igst']
                    else:
                        sheet_df.at[idx, 'HSN'] = 'new item'
                        sheet_df.at[idx, 'Duty'] = 'new item'
                        sheet_df.at[idx, 'Welfare'] = 'new item'
                        sheet_df.at[idx, 'IGST'] = 'new item'
                        if itemName not in unique_desc:
                            unique_desc.add(itemName)
                            new_items_count += 1
                            # Add unmatched items to new_descriptions_df
                            new_descriptions_df = pd.concat([new_descriptions_df, pd.DataFrame({
                                '发票及项号': [row['ID']],
                                'Item Name': [itemName],
                                'Final BCD': [''],
                                'Final SWS': [''],
                                'Final IGST': [''],
                                'HSN1': [''],
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
        for index, row in df.iterrows():
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
        logging.info(f"Processed checklist with {invoice_count} invoices and {item_count} items")
        logging.info(f"Final checklist DataFrame shape: {result_df.shape}")

        # Check for duplicate IDs
        duplicate_ids = result_df['ID'].value_counts()[result_df['ID'].value_counts() > 1]
        if not duplicate_ids.empty:
            logging.warning(f"Found {len(duplicate_ids)} duplicate IDs in processed checklist:")
            logging.warning(duplicate_ids.head(10).to_dict())  # Log first 10 duplicates

        return result_df
    except Exception as e:
        error_msg = f"处理核对清单失败: {str(e)}"
        logging.error(error_msg)
        logging.exception("Exception details:")
        st.error(error_msg)
        return pd.DataFrame()

def compare_excels(df1, df2, price_tolerance_pct=0.5):
    logging.info("="*60)
    logging.info(f"STARTING COMPARISON with price tolerance: {price_tolerance_pct}%")
    logging.info(f"DataFrame 1 (invoices) shape: {df1.shape}")
    logging.info(f"DataFrame 2 (checklist) shape: {df2.shape}")
    logging.info("="*60)

    try:
        # Log column information
        logging.info(f"DataFrame 1 columns: {df1.columns.tolist()}")
        logging.info(f"DataFrame 2 columns: {df2.columns.tolist()}")

        # Check for null IDs
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
            df1_before = df1.shape[0]
            df1 = df1.drop_duplicates(subset=['ID'], keep='first')
            df1_after = df1.shape[0]
            logging.info(f"Removed {df1_before - df1_after} duplicates from DataFrame 1. New shape: {df1.shape}")

        if not duplicate_ids_df2.empty:
            logging.warning(f"Found {len(duplicate_ids_df2)} duplicate IDs in DataFrame 2 (checklist)")
            logging.warning(f"First 5 duplicates: {duplicate_ids_df2.head().to_dict()}")
            # Remove duplicates from df2, keeping the first occurrence
            df2_before = df2.shape[0]
            df2 = df2.drop_duplicates(subset=['ID'], keep='first')
            df2_after = df2.shape[0]
            logging.info(f"Removed {df2_before - df2_after} duplicates from DataFrame 2. New shape: {df2.shape}")

        # 确保两个 DataFrame 的列名顺序一致
        logging.info(f"Aligning columns between DataFrames")
        df2 = df2[df1.columns]
        logging.info(f"Columns aligned successfully")

        # 用于存储差异信息
        diff_data = []
        # Keep track of processed IDs to avoid duplicates
        processed_ids = set()
        match_count = 0
        diff_count = 0
        no_match_count = 0

        # Log a sample of IDs from each DataFrame for debugging
        sample_ids_df1 = df1['ID'].dropna().sample(min(5, len(df1))).tolist() if not df1.empty else []
        sample_ids_df2 = df2['ID'].dropna().sample(min(5, len(df2))).tolist() if not df2.empty else []
        logging.info(f"Sample IDs from DataFrame 1: {sample_ids_df1}")
        logging.info(f"Sample IDs from DataFrame 2: {sample_ids_df2}")

        # Create a set of all IDs in df2 for faster lookup
        df2_ids = set(df2['ID'].dropna())
        logging.info(f"Total unique IDs in DataFrame 2: {len(df2_ids)}")

        # Log the total number of rows to process
        total_rows = len(df1)
        logging.info(f"Starting to process {total_rows} rows from DataFrame 1")

        for index, row1 in df1.iterrows():
            # Log progress every 100 rows
            if index % 100 == 0:
                logging.debug(f"Processing row {index}/{total_rows}")

            id1 = row1['ID']
            # Skip if this ID has already been processed or is None
            if id1 is None or pd.isna(id1) or id1 in processed_ids:
                logging.debug(f"Skipping ID {id1} (None, NaN, or already processed)")
                continue

            # Add this ID to the processed set
            processed_ids.add(id1)

            # Check if ID exists in df2
            if id1 in df2_ids:
                # 查找 df2 中对应 ID 的行
                matching_row = df2[df2['ID'] == id1]
                if not matching_row.empty:
                    match_count += 1
                    row2 = matching_row.iloc[0]
                    diff_cols = []

                    # Log every 100th comparison for debugging
                    if match_count % 100 == 0:
                        logging.debug(f"Processing comparison #{match_count}, ID: {id1}")

                    for col in df1.columns[1:]:  # 跳过ID列
                        # 跳过Item_Name列的比对
                        if col == 'Item_Name':
                            continue

                        # 对Price列使用用户设置的误差范围
                        if col == 'Price':
                            if pd.notna(row1[col]) and pd.notna(row2[col]):
                                # Convert to float to ensure proper comparison
                                val1 = float(row1[col])
                                val2 = float(row2[col])
                                tolerance = val1 * (price_tolerance_pct / 100)  # 转换为小数

                                if abs(val1 - val2) > tolerance:
                                    diff_cols.append(col)
                                    # 创建price_diff格式
                                    price_diff = f"{val2} -> {val1}"
                                    # Log price differences for debugging
                                    logging.debug(f"Price difference for ID {id1}: {val2} -> {val1}, Tolerance: {tolerance}")
                        # 其他列使用精确比对
                        elif row1[col] != row2[col]:
                            diff_cols.append(col)
                            # Log differences for debugging
                            logging.debug(f"Difference in column {col} for ID {id1}: {row2[col]} -> {row1[col]}")

                    if diff_cols:
                        diff_count += 1
                        diff_info = {'ID': id1}
                        for col in diff_cols:
                            if col == 'Price':
                                diff_info['price_diff'] = price_diff
                            else:
                                diff_info[f'{col}_file1'] = row1[col]
                                diff_info[f'{col}_file2'] = row2[col]
                        diff_data.append(diff_info)

                        # Log every 10th difference for debugging
                        if diff_count % 10 == 0:
                            logging.info(f"Found {diff_count} differences so far")
                else:
                    no_match_count += 1
                    logging.warning(f"ID {id1} found in df2_ids set but not in df2 DataFrame - this should not happen")
            else:
                no_match_count += 1
                if no_match_count <= 10:  # Only log the first 10 to avoid flooding the log
                    logging.debug(f"No matching ID found in DataFrame 2 for ID: {id1}")

        logging.info(f"Comparison complete. Processed {len(processed_ids)} unique IDs")
        logging.info(f"Found {match_count} matching IDs between files")
        logging.info(f"Found {diff_count} differences")
        logging.info(f"Found {no_match_count} IDs in DataFrame 1 with no match in DataFrame 2")

        if diff_data:
            diff_df = pd.DataFrame(diff_data)
            # 重新排列列，确保price_diff在前面
            if 'price_diff' in diff_df.columns:
                cols = ['ID', 'price_diff'] + [col for col in diff_df.columns if col not in ['ID', 'price_diff']]
                diff_df = diff_df[cols]
            logging.info(f"Created difference DataFrame with shape: {diff_df.shape}")

            # Log a sample of differences for debugging
            if not diff_df.empty:
                sample_size = min(5, len(diff_df))
                sample_diff = diff_df.sample(sample_size)
                logging.info(f"Sample of {sample_size} differences:")
                for _, row in sample_diff.iterrows():
                    logging.info(f"  ID: {row['ID']}, Differences: {', '.join([col for col in row.index if col != 'ID' and not pd.isna(row[col])])}")

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
    logging.info("="*80)
    logging.info("PROCESS BUTTON CLICKED - STARTING NEW PROCESSING RUN")
    logging.info("="*80)

    # Log system information
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Working directory: {os.getcwd()}")
    logging.info(f"Platform: {sys.platform}")

    # Log file existence and sizes
    input_dir = "input"
    output_dir = "output"
    logging.info(f"Input directory exists: {os.path.exists(input_dir)}")
    logging.info(f"Output directory exists: {os.path.exists(output_dir)}")

    if os.path.exists(input_dir):
        input_files = os.listdir(input_dir)
        logging.info(f"Files in input directory: {input_files}")
        for file in input_files:
            file_path = os.path.join(input_dir, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                logging.info(f"Input file: {file}, Size: {file_size} bytes")

    if os.path.exists(output_dir):
        output_files = os.listdir(output_dir)
        logging.info(f"Files in output directory: {output_files}")
        for file in output_files:
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                logging.info(f"Output file: {file}, Size: {file_size} bytes")

    # Check for required files
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
        # Log uploaded file information
        logging.info(f"Duty rate file: {duty_rate_file.name}, Size: {len(duty_rate_file.getvalue())} bytes")
        logging.info(f"Checklist file: {checklist_file.name}, Size: {len(checklist_file.getvalue())} bytes")
        logging.info(f"Invoices file: {invoices_file.name}, Size: {len(invoices_file.getvalue())} bytes")

        logging.info("Starting data processing workflow")
        with st.spinner("正在处理数据..."):
            try:
                # Log input file paths
                duty_rate_path = os.path.join("input", "duty_rate.xlsx")
                invoices_path = os.path.join("input", "processing_invoices.xlsx")
                checklist_path = os.path.join("input", "processing_checklist.xlsx")

                logging.info(f"Input files: duty_rate={duty_rate_path}, invoices={invoices_path}, checklist={checklist_path}")

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
                # Get the price tolerance from the slider (default is 0.5%)
                price_tolerance = 0.5  # Default value
                try:
                    # Try to access the price_tolerance variable from the Streamlit app
                    if 'price_tolerance' in globals():
                        price_tolerance = globals()['price_tolerance']
                        logging.info(f"Using price tolerance from slider: {price_tolerance}%")
                    else:
                        logging.info(f"Using default price tolerance: {price_tolerance}%")
                except Exception as e:
                    logging.warning(f"Error accessing price tolerance: {str(e)}, using default: {price_tolerance}%")

                diff_report = compare_excels(processed_invoices, processed_checklist, price_tolerance)

                # Save the processed files
                logging.info("Step 5: Saving output files")
                processed_invoices_path = os.path.join("output", "processed_invoices.xlsx")
                processed_checklist_path = os.path.join("output", "processed_checklist.xlsx")
                processed_report_path = os.path.join("output", "processed_report.xlsx")

                try:
                    processed_invoices.to_excel(processed_invoices_path, index=False)
                    logging.info(f"Saved processed invoices to {processed_invoices_path}")

                    processed_checklist.to_excel(processed_checklist_path, index=False)
                    logging.info(f"Saved processed checklist to {processed_checklist_path}")

                    # Save the diff report if it's not empty
                    if not diff_report.empty:
                        diff_report.to_excel(processed_report_path, index=False)
                        logging.info(f"Saved diff report to {processed_report_path}")
                    else:
                        logging.info("No differences found, skipping diff report creation")
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

                            # Add new descriptions to a new sheet with required columns
                            required_columns = ['发票及项号', 'Item Name', 'Final BCD', 'Final SWS', 'Final IGST', 'HSN1']
                            new_items[required_columns].to_excel(writer, sheet_name='newDutyRate', index=False)
                        logging.info(f"Saved new items to {new_items_path}")
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
            if not diff_report_df.empty:
                st.dataframe(diff_report_df, use_container_width=True)

                # Download button
                with open(diff_report_path, "rb") as file:
                    st.download_button(
                        label="下载差异报告",
                        data=file,
                        file_name="processed_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.success("没有发现差异")
        except Exception as e:
            st.error(f"无法加载差异报告: {str(e)}")
    else:
        st.info("请先处理数据")

# Footer
st.markdown("---")
st.markdown("© 2023 发票核对系统 | 版本 1.1")

# Check if this script is being run directly (not through Streamlit)
if __name__ == "__main__":
    logging.info("="*50)
    logging.info("APP RUNNING IN DIRECT MODE (NOT THROUGH STREAMLIT)")
    logging.info("="*50)

    # Check if command line arguments were provided
    if len(sys.argv) > 1:
        logging.info(f"Command line arguments detected: {sys.argv[1:]}")

        # If arguments are provided, use them directly
        if len(sys.argv) >= 7:
            invoices_file = sys.argv[1]
            checklist_file = sys.argv[2]
            duty_rate_file = sys.argv[3]
            output_invoices = sys.argv[4]
            output_checklist = sys.argv[5]
            output_report = sys.argv[6]

            logging.info(f"Using provided arguments:")
            logging.info(f"  Invoices file: {invoices_file}")
            logging.info(f"  Checklist file: {checklist_file}")
            logging.info(f"  Duty rate file: {duty_rate_file}")
            logging.info(f"  Output invoices: {output_invoices}")
            logging.info(f"  Output checklist: {output_checklist}")
            logging.info(f"  Output report: {output_report}")

            try:
                # Process duty rates
                logging.info("Step 1: Processing duty rates")
                duty_rates, duty_df = get_duty_rates(duty_rate_file)

                # Process invoices
                logging.info("Step 2: Processing invoices")
                processed_invoices, new_items = process_invoice_file(invoices_file, duty_rates)

                # Process checklist
                logging.info("Step 3: Processing checklist")
                processed_checklist = process_checklist(checklist_file)

                # Compare the processed files
                logging.info("Step 4: Comparing processed files")
                # Use a default price tolerance of 1.1% when run from command line
                price_tolerance = 1.1
                if len(sys.argv) > 7:
                    try:
                        price_tolerance = float(sys.argv[7])
                        logging.info(f"Using provided price tolerance: {price_tolerance}%")
                    except:
                        logging.warning(f"Invalid price tolerance provided: {sys.argv[7]}, using default: {price_tolerance}%")
                else:
                    logging.info(f"Using default price tolerance: {price_tolerance}%")

                diff_report = compare_excels(processed_invoices, processed_checklist, price_tolerance)

                # Save the processed files
                processed_invoices.to_excel(output_invoices, index=False)
                logging.info(f"Saved processed invoices to {output_invoices}")

                processed_checklist.to_excel(output_checklist, index=False)
                logging.info(f"Saved processed checklist to {output_checklist}")

                # Save the diff report if it's not empty
                if not diff_report.empty:
                    diff_report.to_excel(output_report, index=False)
                    logging.info(f"Saved diff report to {output_report}")
                else:
                    logging.info("No differences found, skipping diff report creation")

                logging.info("Processing completed successfully")
                print("处理完成！")
            except Exception as e:
                error_msg = f"处理数据时发生错误: {str(e)}"
                logging.error(error_msg)
                logging.exception("Exception details:")
                print(error_msg)
                sys.exit(1)
        else:
            logging.error(f"Insufficient arguments provided. Expected at least 6, got {len(sys.argv)-1}")
            print("Usage: python app.py <invoices_file> <checklist_file> <duty_rate_file> <output_invoices> <output_checklist> <output_report> [price_tolerance]")
            sys.exit(1)
    else:
        logging.warning("No command line arguments provided when running directly")
        print("This script is designed to be run through Streamlit or with command line arguments.")
        print("Usage: python app.py <invoices_file> <checklist_file> <duty_rate_file> <output_invoices> <output_checklist> <output_report> [price_tolerance]")
        print("Or: streamlit run app.py")
        sys.exit(1)
