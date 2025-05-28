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
import unicodedata
import re
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
        font-size: 2.2rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
        margin-top: 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1rem;
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

    /* 文件上传区域样式优化 */
    .upload-section {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #BBDEFB;
        margin-bottom: 1rem;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .upload-section h3 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        color: #1565C0;
        font-size: 1.2rem;
        font-weight: 600;
    }

    /* 设置区域样式 */
    .settings-section {
        background-color: #F3E5F5;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E1BEE7;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 处理按钮区域样式 */
    .process-section {
        background-color: #E8F5E8;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #C8E6C9;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 帮助区域样式 */
    .help-section {
        background-color: #FFF3E0;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #FFCC02;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 紧凑的列布局 */
    .stColumns {
        gap: 1.5rem !important;
    }

    /* 减少标签页间距 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    /* 优化文件上传器样式 */
    .stFileUploader {
        margin-bottom: 0.5rem;
    }

    /* 优化成功和信息消息样式 */
    .stSuccess, .stInfo {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }

    /* 优化进度条样式 */
    .stProgress {
        margin-bottom: 0.5rem;
    }

    /* 防止按钮点击后页面跳转的样式 */
    .stDownloadButton > button {
        position: relative;
        z-index: 1;
    }

    .stButton > button {
        position: relative;
        z-index: 1;
    }

    /* 保持页面位置的样式 */
    .main .block-container {
        scroll-behavior: smooth;
        padding-top: 1rem;
    }

    /* 改善按钮的视觉反馈 */
    .stDownloadButton > button:hover,
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }

    /* 防止页面重新加载时的闪烁 */
    .stApp {
        transition: none;
    }

    /* 优化侧边栏样式 */
    .css-1d391kg {
        padding-top: 1rem;
    }

    /* 侧边栏文件上传器样式 */
    .css-1d391kg .stFileUploader {
        margin-bottom: 1rem;
    }

    /* 侧边栏按钮样式 */
    .css-1d391kg .stButton > button {
        width: 100%;
        margin-top: 0.5rem;
    }

    /* 侧边栏标题样式 */
    .css-1d391kg h2, .css-1d391kg h3 {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    /* 侧边栏滑块样式 */
    .css-1d391kg .stSlider {
        margin-bottom: 0.5rem;
    }

    /* 减少页面顶部间距 */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* 减少各个组件之间的间距 */
    .element-container {
        margin-bottom: 0.5rem;
    }

    /* 优化标签页容器 */
    .stTabs > div > div > div > div {
        padding-top: 1rem;
    }
</style>

<script>
// 防止按钮点击后页面跳转到顶部
document.addEventListener('DOMContentLoaded', function() {
    // 监听所有按钮点击事件
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            // 记录当前滚动位置
            const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;

            // 延迟恢复滚动位置
            setTimeout(function() {
                window.scrollTo(0, scrollPosition);
            }, 100);
        }
    });
});
</script>
""", unsafe_allow_html=True)

# Create directories if they don't exist
os.makedirs('input', exist_ok=True)
os.makedirs('output', exist_ok=True)

def normalize_filename(filename):
    """
    标准化文件名，解决Mac系统中文编码问题
    """
    if not filename:
        return filename

    try:
        # 1. Unicode标准化 (NFD -> NFC)
        normalized = unicodedata.normalize('NFC', filename)

        # 2. 移除或替换特殊字符
        # 保留中文、英文、数字、点号、下划线、连字符
        safe_chars = re.sub(r'[^\w\u4e00-\u9fff\.\-_()]', '_', normalized)

        # 3. 限制文件名长度
        name, ext = os.path.splitext(safe_chars)
        if len(name) > 100:  # 限制主文件名长度
            name = name[:100]

        result = name + ext
        logging.info(f"Normalized filename: '{filename}' -> '{result}'")
        return result

    except Exception as e:
        logging.error(f"Error normalizing filename '{filename}': {str(e)}")
        # 如果标准化失败，使用安全的英文文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(filename)[1] if filename else '.xlsx'
        fallback_name = f"uploaded_file_{timestamp}{ext}"
        logging.info(f"Using fallback filename: '{fallback_name}'")
        return fallback_name

def safe_save_uploaded_file(uploaded_file, target_path):
    """
    安全保存上传的文件，处理文件名编码问题
    """
    try:
        # 标准化文件名
        safe_filename = normalize_filename(uploaded_file.name)

        # 构建安全的目标路径
        target_dir = os.path.dirname(target_path)
        safe_target_path = os.path.join(target_dir, safe_filename)

        # 保存文件
        with open(safe_target_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        logging.info(f"File saved successfully: {safe_target_path}")
        return safe_target_path, safe_filename

    except Exception as e:
        logging.error(f"Error saving uploaded file: {str(e)}")
        raise e

def create_safe_file_uploader(label, file_type=["xlsx"], key=None, accept_multiple_files=False):
    """
    创建一个安全的文件上传器，处理中文文件名问题
    """
    # 添加文件名建议
    help_text = """
    💡 文件名建议：
    • 避免使用特殊字符和空格
    • 推荐使用英文、数字、下划线
    • 如：invoice_20250127.xlsx
    """

    # 创建文件上传器
    uploaded_files = st.file_uploader(
        label,
        type=file_type,
        key=key,
        accept_multiple_files=accept_multiple_files,
        help=help_text
    )

    return uploaded_files

# Main header
st.markdown("<h1 class='main-header'>Checklist核对系统</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/invoice.png", width=80)
    st.markdown("## Checklist核对系统")
    st.markdown("**版本 1.2**")

    st.markdown("---")

    # 显示当前状态
    st.markdown("### 当前状态")

    # 检查文件上传状态（使用session state）
    duty_uploaded = 'duty_rate_uploaded' in st.session_state and st.session_state.duty_rate_uploaded
    checklist_uploaded = 'checklist_uploaded' in st.session_state and st.session_state.checklist_uploaded
    invoices_uploaded = 'invoices_uploaded' in st.session_state and st.session_state.invoices_uploaded

    # 文件上传状态显示
    if duty_uploaded:
        st.success("✅ 税率文件已上传")
    else:
        st.info("⏳ 等待税率文件")

    if checklist_uploaded:
        st.success("✅ 核对清单已上传")
    else:
        st.info("⏳ 等待核对清单")

    if invoices_uploaded:
        st.success("✅ 发票文件已上传")
    else:
        st.info("⏳ 等待发票文件")

    # 显示整体进度
    total_files = 3
    uploaded_files = sum([duty_uploaded, checklist_uploaded, invoices_uploaded])
    progress = uploaded_files / total_files

    st.markdown("### 📈 上传进度")
    st.progress(progress)
    st.caption(f"已上传 {uploaded_files}/{total_files} 个文件")

    st.markdown("---")

    # 快速导航
    st.markdown("### 🧭 快速导航")
    st.markdown("""
    - 📁 **文件上传与设置** - 上传文件并配置参数
    - 👀 **数据预览** - 查看上传的数据
    - 📊 **处理结果** - 查看处理后的数据
    - 📋 **差异报告** - 查看比对差异
    - 📝 **日志** - 查看处理日志
    """)

    st.markdown("---")
    st.markdown("### ℹ️ 系统信息")
    st.caption("© 2025 Checklist核对系统")
    st.caption("专业的发票核对解决方案")

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["文件上传", "数据预览", "处理结果", "差异报告", "日志"])

def normalize_item_name(item_name):
    """
    标准化Item Name，用于更好的匹配
    """
    if pd.isna(item_name) or item_name == '':
        return ''

    # 转换为字符串并转为大写
    normalized = str(item_name).upper()

    # 移除常见的特殊字符和空格
    normalized = normalized.replace(' ', '').replace('-', '').replace('_', '')
    normalized = normalized.replace(',', '.').replace(';', '.')

    # 移除常见的后缀
    suffixes_to_remove = ['PARTNO', 'PART', 'NO', 'NUM', 'NUMBER']
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]

    return normalized.strip()

def find_best_match(item_name, duty_rates_dict):
    """
    为给定的item_name在duty_rates字典中找到最佳匹配
    """
    if not item_name or pd.isna(item_name):
        return None

    normalized_item = normalize_item_name(item_name)

    # 首先尝试精确匹配
    if item_name in duty_rates_dict:
        return item_name

    # 尝试标准化后的精确匹配
    for duty_item in duty_rates_dict.keys():
        if normalize_item_name(duty_item) == normalized_item:
            return duty_item

    # 尝试部分匹配（包含关系）- 改进版本
    best_match = None
    best_score = 0

    for duty_item in duty_rates_dict.keys():
        normalized_duty = normalize_item_name(duty_item)

        # 计算匹配分数
        score = 0

        # 完全包含关系
        if normalized_item in normalized_duty:
            score = len(normalized_item) / len(normalized_duty)
        elif normalized_duty in normalized_item:
            score = len(normalized_duty) / len(normalized_item)
        else:
            # 计算公共子串长度
            common_length = 0
            min_len = min(len(normalized_item), len(normalized_duty))
            for i in range(min_len):
                if normalized_item[i] == normalized_duty[i]:
                    common_length += 1
                else:
                    break

            # 如果有足够长的公共前缀，也认为是匹配
            if common_length >= 8:  # 至少8个字符的公共前缀
                score = common_length / max(len(normalized_item), len(normalized_duty))

        # 更新最佳匹配
        if score > best_score and score >= 0.7:  # 至少70%的匹配度
            best_score = score
            best_match = duty_item

    return best_match

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

        # Process sheet names for display and ID creation (remove CI- prefix and trim spaces)
        processed_sheet_names = [name.replace('CI-', '').strip() if name.startswith('CI-') else name.strip()
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

            # 动态检测列结构
            # 首先尝试找到表头行
            header_row_idx = None
            for i in range(min(15, len(df))):
                row = df.iloc[i]
                # 检查是否包含典型的表头关键词
                row_str = ' '.join([str(cell).upper() for cell in row if pd.notna(cell)])
                if any(keyword in row_str for keyword in ['QTY', 'QUANTITY', 'PRICE', 'AMOUNT', 'DESC', 'DESCRIPTION']):
                    header_row_idx = i
                    logging.info(f"Found potential header row at index {i}: {row_str}")
                    break
            
            # 根据实际的发票文件结构定义列索引
            # 如果找到表头，尝试动态映射；否则使用默认映射
            if header_row_idx is not None:
                header_row = df.iloc[header_row_idx]
                column_indices = {}
                
                for idx, cell in enumerate(header_row):
                    if pd.notna(cell):
                        cell_str = str(cell).upper().strip()
                        if any(keyword in cell_str for keyword in ['ITEM', 'NO', 'SL']) and 'Item#' not in column_indices:
                            column_indices['Item#'] = idx
                        elif any(keyword in cell_str for keyword in ['MODEL', 'PART']) and 'Model_No' not in column_indices:
                            column_indices['Model_No'] = idx
                        elif ('P/N' in cell_str or 'PN' in cell_str) and 'P/N' not in column_indices:
                            column_indices['P/N'] = idx
                        elif any(keyword in cell_str for keyword in ['DESC', 'DESCRIPTION']) and 'Desc' not in column_indices:
                            column_indices['Desc'] = idx
                        elif any(keyword in cell_str for keyword in ['COUNTRY', 'ORIGIN']) and 'Country' not in column_indices:
                            column_indices['Country'] = idx
                        elif any(keyword in cell_str for keyword in ['QTY', 'QUANTITY']) and 'Qty' not in column_indices:
                            column_indices['Qty'] = idx
                        elif any(keyword in cell_str for keyword in ['PRICE', 'RATE']) and 'Price' not in column_indices:
                            column_indices['Price'] = idx
                        elif any(keyword in cell_str for keyword in ['AMOUNT', 'TOTAL']) and 'Amount' not in column_indices:
                            column_indices['Amount'] = idx
                
                logging.info(f"Dynamic column mapping: {column_indices}")
                
                # 检查是否所有必要的列都被检测到
                required_columns = ['Item#', 'Model_No', 'P/N', 'Desc', 'Qty', 'Price']
                missing_columns = [col for col in required_columns if col not in column_indices]
                
                if missing_columns:
                    logging.warning(f"Dynamic column detection failed, missing columns: {missing_columns}")
                    logging.warning("Using default mapping")
                    column_indices = {
                        'Item#': 0,      # Item number (1, 2, 3...)
                        'Model_No': 1,   # Model number (IPC-K7CP-3H1WE)
                        'P/N': 2,        # Part number (1.2.03.01.0002)
                        'Desc': 3,       # Description
                        'Country': 4,    # Country
                        'Qty': 5,        # Quantity
                        'Price': 6,      # Unit price
                        'Amount': 7,     # Total amount
                    }
                else:
                    # 补充可能缺失的非必要列
                    if 'Country' not in column_indices:
                        column_indices['Country'] = 4  # 默认值
                    if 'Amount' not in column_indices:
                        column_indices['Amount'] = 7   # 默认值
            else:
                logging.warning("No header row found, using default mapping")
                # 使用默认的列索引映射
                column_indices = {
                    'Item#': 0,      # Item number (1, 2, 3...)
                    'Model_No': 1,   # Model number (IPC-K7CP-3H1WE)
                    'P/N': 2,        # Part number (1.2.03.01.0002)
                    'Desc': 3,       # Description
                    'Country': 4,    # Country
                    'Qty': 5,        # Quantity
                    'Price': 6,      # Unit price
                    'Amount': 7,     # Total amount
                }

            logging.info(f"Using column indices for sheet {original_sheet_name}: {column_indices}")
            
            # 查找数据开始的行（在表头行之后，包含数字的行）
            data_start_row = None
            search_start = header_row_idx + 1 if header_row_idx is not None else 0
            
            for row_idx in range(search_start, min(search_start + 20, len(df))):
                # 检查第一列是否为数字（Item#）
                if row_idx < len(df):
                    first_col_val = df.iloc[row_idx, 0]
                    if pd.notna(first_col_val) and str(first_col_val).strip().isdigit():
                        data_start_row = row_idx
                        logging.info(f"Found data starting at row {row_idx} in sheet {original_sheet_name}")
                        break
            
            if data_start_row is None:
                logging.warning(f"No data rows found in sheet {original_sheet_name}")
                continue
            
            # 提取数据行
            data_df = df.iloc[data_start_row:].copy()
            
            # 重置索引
            data_df = data_df.reset_index(drop=True)

            # 创建新的DataFrame
            sheet_df = pd.DataFrame()
            
            # 只处理有数据的行
            valid_rows = []
            for idx, row in data_df.iterrows():
                # 检查第一列是否为有效的Item#
                item_num = row.iloc[0] if len(row) > 0 else None
                if pd.notna(item_num) and str(item_num).strip().isdigit():
                    valid_rows.append(idx)
            
            if not valid_rows:
                logging.warning(f"No valid data rows found in sheet {original_sheet_name}")
                continue
            
            logging.info(f"Found {len(valid_rows)} valid data rows in sheet {original_sheet_name}")
            
            # 最终安全检查：确保所有必要的列索引都存在
            required_keys = ['Item#', 'Model_No', 'P/N', 'Desc', 'Country', 'Qty', 'Price']
            for key in required_keys:
                if key not in column_indices:
                    logging.error(f"Missing required column index: {key}")
                    logging.error(f"Available column indices: {column_indices}")
                    logging.error("Falling back to default mapping")
                    column_indices = {
                        'Item#': 0,      # Item number (1, 2, 3...)
                        'Model_No': 1,   # Model number (IPC-K7CP-3H1WE)
                        'P/N': 2,        # Part number (1.2.03.01.0002)
                        'Desc': 3,       # Description
                        'Country': 4,    # Country
                        'Qty': 5,        # Quantity
                        'Price': 6,      # Unit price
                        'Amount': 7,     # Total amount
                    }
                    break
            
            # 处理每个有效行
            for row_idx in valid_rows:
                row = data_df.iloc[row_idx]
                
                # 安全获取列值
                def safe_get_col(col_idx):
                    if col_idx < len(row):
                        val = row.iloc[col_idx]
                        return val if pd.notna(val) else ''
                    return ''
                
                # 提取各列数据
                item_num = safe_get_col(column_indices['Item#'])
                part_num = safe_get_col(column_indices['P/N'])
                model_no = safe_get_col(column_indices['Model_No'])
                desc = safe_get_col(column_indices['Desc'])
                country = safe_get_col(column_indices['Country'])
                qty = safe_get_col(column_indices['Qty'])
                price = safe_get_col(column_indices['Price'])
                
                # 添加详细的调试信息，特别关注Qty字段
                if row_idx < 3:  # 只记录前3行的调试信息
                    logging.info(f"Row {row_idx} debugging:")
                    logging.info(f"  - Row length: {len(row)}")
                    logging.info(f"  - Qty column index: {column_indices.get('Qty', 'NOT_FOUND')}")
                    if 'Qty' in column_indices and column_indices['Qty'] < len(row):
                        raw_qty = row.iloc[column_indices['Qty']]
                        logging.info(f"  - Raw Qty value: '{raw_qty}' (type: {type(raw_qty)})")
                        logging.info(f"  - Processed Qty: '{qty}'")
                    else:
                        logging.info(f"  - Qty column index out of range or not found")
                    
                    if 'Price' in column_indices and column_indices['Price'] < len(row):
                        raw_price = row.iloc[column_indices['Price']]
                        logging.info(f"  - Raw Price value: '{raw_price}' (type: {type(raw_price)})")
                        logging.info(f"  - Processed Price: '{price}'")
                    else:
                        logging.info(f"  - Price column index out of range or not found")
                
                # 处理描述字段，提取Item_Name
                item_name = ''
                if desc:
                    # 从描述中提取Item_Name（通常是第一个'-'之前的部分）
                    desc_str = str(desc)
                    if '-' in desc_str:
                        item_name = desc_str.split('-')[0].strip()
                    else:
                        item_name = desc_str.strip()
                
                # 清理描述文本
                clean_desc = ''
                if desc:
                    clean_desc = ''.join(char.upper() for char in str(desc) if char.isalnum() or char in '.()').replace('Φ', '').replace('Ω', '').replace('-', '').replace('φ', '')
                
                # 创建ID
                item_id = f"{processed_sheet_name}_{str(item_num).strip()}"
                
                # 添加到结果DataFrame
                row_data = {
                    'Item#': str(item_num).strip(),
                    'ID': item_id,
                    'P/N': str(part_num).strip(),
                    'Desc': clean_desc,
                    'Qty': str(qty).strip(),
                    'Price': str(price).strip(),
                    'Item_Name': item_name,
                    'HSN': '',
                    'BCD': '',
                    'SWS': '',
                    'IGST': ''
                }
                
                sheet_df = pd.concat([sheet_df, pd.DataFrame([row_data])], ignore_index=True)
            
            logging.info(f"Processed {len(sheet_df)} items from sheet {original_sheet_name}")

            # 填充税率信息并收集未匹配的项目
            unique_desc = set()
            new_items_count = 0
            
            for idx, row in sheet_df.iterrows():
                itemName = row['Item_Name']
                if pd.notna(itemName) and itemName != '':
                    # 使用改进的匹配算法
                    matched_duty_item = find_best_match(itemName, duty_rates)

                    if matched_duty_item:
                        rates = duty_rates[matched_duty_item]
                        sheet_df.at[idx, 'HSN'] = str(rates['hsn'])
                        sheet_df.at[idx, 'BCD'] = str(rates['bcd'])
                        sheet_df.at[idx, 'SWS'] = str(rates['sws'])
                        sheet_df.at[idx, 'IGST'] = str(rates['igst'])

                        # 记录匹配信息用于调试
                        if matched_duty_item != itemName:
                            logging.info(f"Fuzzy match found: '{itemName}' -> '{matched_duty_item}'")
                    else:
                        sheet_df.at[idx, 'HSN'] = 'new item'
                        sheet_df.at[idx, 'BCD'] = 'new item'
                        sheet_df.at[idx, 'SWS'] = 'new item'
                        sheet_df.at[idx, 'IGST'] = 'new item'
                        if itemName not in unique_desc:
                            unique_desc.add(itemName)
                            new_items_count += 1
                            logging.info(f"No match found for item: '{itemName}' (normalized: '{normalize_item_name(itemName)}')")
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
        # 确保所有列为字符串类型，解决Arrow序列化问题
        logging.info(f"Converting all columns to string type for invoices DataFrame. Columns: {all_invoices_df.columns.tolist()}")
        for col in all_invoices_df.columns:
            try:
                all_invoices_df[col] = all_invoices_df[col].astype(str)
            except Exception as e:
                logging.error(f"Error converting column '{col}' to string: {str(e)}")
                # 如果转换失败，尝试强制转换
                all_invoices_df[col] = all_invoices_df[col].apply(lambda x: str(x) if x is not None else '')

        # 额外处理：确保没有字符串形式的'nan'或'none'
        for col in all_invoices_df.columns:
            all_invoices_df[col] = all_invoices_df[col].apply(
                lambda x: '' if str(x).lower() in ['nan', 'none'] else str(x)
            )

        logging.info("Completed type conversion for invoices DataFrame")

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

        # 检查必要的列是否存在，如果不存在则尝试找到相似的列名
        required_columns = ['P/N', 'Item#', 'Desc', 'Qty', 'Price', 'HSN', 'BCD', 'SWS', 'IGST']
        column_mapping = {}

        for req_col in required_columns:
            if req_col in df.columns:
                column_mapping[req_col] = req_col
            else:
                # 特殊处理IGST列，可能对应Duty列
                if req_col == 'IGST' and 'Duty' in df.columns:
                    column_mapping[req_col] = 'Duty'
                    logging.info(f"Mapped column '{req_col}' to 'Duty'")
                    continue
                
                # 尝试找到相似的列名（不区分大小写，忽略空格和特殊字符）
                found = False
                for col in df.columns:
                    col_clean = str(col).strip().replace(' ', '').replace('/', '').replace('-', '').upper()
                    req_col_clean = req_col.replace('/', '').replace('-', '').upper()
                    if col_clean == req_col_clean or req_col_clean in col_clean:
                        column_mapping[req_col] = col
                        logging.info(f"Mapped column '{req_col}' to '{col}'")
                        found = True
                        break

                if not found:
                    logging.warning(f"Column '{req_col}' not found in checklist file")
                    column_mapping[req_col] = None

        logging.info(f"Column mapping: {column_mapping}")

        # 初始化新的DataFrame用于存储结果
        result_rows = []
        current_invoice = None
        invoice_count = 0
        item_count = 0

        # 遍历每一行
        for _, row in df.iterrows():  # 使用 _ 表示不使用的索引变量
            # 检查是否是发票行 - 使用安全的列访问
            pn_col = column_mapping.get('P/N')
            if pn_col and pn_col in df.columns:
                pn = str(row[pn_col]) if pd.notna(row[pn_col]) else ''
            else:
                # 如果没有P/N列，尝试在第一列或其他列中查找Invoice信息
                pn = ''
                for col in df.columns:
                    if pd.notna(row[col]) and 'Invoice:' in str(row[col]):
                        pn = str(row[col])
                        break

            if 'Invoice:' in str(pn):
                # 提取发票号并去除所有空格
                invoice_no = pn.split('Invoice:')[1].split('dt.')[0].strip().replace(' ', '')
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
                # 处理常规行 - 使用安全的列访问
                item_col = column_mapping.get('Item#')
                if item_col and item_col in df.columns and pd.notna(row[item_col]) and current_invoice:
                    # Convert Item# to integer before concatenating to remove the decimal and spaces
                    try:
                        item_num = int(float(row[item_col])) if pd.notna(row[item_col]) else 0
                        item_id = f"{current_invoice}_{item_num}"
                    except (ValueError, TypeError):
                        # Remove spaces from item number to ensure clean IDs
                        clean_item = str(row[item_col]).strip().replace(' ', '')
                        item_id = f"{current_invoice}_{clean_item}"

                    # 安全获取Desc列
                    desc_col = column_mapping.get('Desc')
                    if desc_col and desc_col in df.columns and pd.notna(row[desc_col]):
                        item_name = str(row[desc_col]).split('-')[0]
                        # 修改item_name的处理逻辑
                        desc_parts = str(row[desc_col]).split('-PART NO')
                        desc = desc_parts[0]
                        # 只保留字母数字和点号，并转换为大写
                        desc = desc.replace('+OR-', '')
                        desc = desc.replace('DEG', '')
                        desc = desc.replace('-', '')
                        desc = ''.join(char for char in desc if char.isalnum() or char in '.()').upper()
                    else:
                        item_name = ''
                        desc = ''

                    item_count += 1

                    # 创建一个安全的字典，使用映射的列名
                    def safe_get_value(col_name):
                        mapped_col = column_mapping.get(col_name)
                        if mapped_col and mapped_col in df.columns:
                            return row[mapped_col] if pd.notna(row[mapped_col]) else ''
                        return ''

                    item_dict = {
                        'Item#': safe_get_value('Item#'),
                        'ID': item_id,
                        'P/N': safe_get_value('P/N'),
                        'Desc': desc,
                        'Qty': safe_get_value('Qty'),
                        'Price': safe_get_value('Price'),
                        'Item_Name': item_name,
                        'HSN': '',
                        'BCD': '',
                        'SWS': '',
                        'IGST': '',
                    }

                    # 处理HSN列（可能是数字）
                    hsn_value = safe_get_value('HSN')
                    if hsn_value and str(hsn_value).strip().isdigit():
                        item_dict['HSN'] = int(float(hsn_value))
                    else:
                        item_dict['HSN'] = hsn_value

                    # 处理其他数值列
                    for col in ['BCD', 'SWS', 'IGST']:
                        item_dict[col] = safe_get_value(col)

                    # 确保所有值都是字符串类型
                    for key in ['Item#', 'P/N', 'ID', 'Qty', 'Price', 'HSN', 'BCD', 'SWS', 'IGST']:
                        if key in item_dict and item_dict[key] is not None:
                            item_dict[key] = str(item_dict[key])

                    result_rows.append(item_dict)

        # 创建结果DataFrame
        result_df = pd.DataFrame(result_rows)
        logging.info(f"Processed checklist with {invoice_count} invoices and {item_count} items")
        logging.info(f"Final checklist DataFrame shape: {result_df.shape}")

        # 如果没有处理到任何数据，记录详细信息
        if result_df.empty:
            logging.warning("No data was processed from checklist file")
            logging.warning(f"Available columns in file: {df.columns.tolist()}")
            logging.warning(f"Column mapping used: {column_mapping}")
            logging.warning("Please check if the file format matches expected structure")

            # 显示前几行数据以帮助调试
            if not df.empty:
                logging.warning(f"First few rows of data:")
                for i, row in df.head(5).iterrows():
                    logging.warning(f"Row {i}: {row.to_dict()}")
        else:
            logging.info(f"Successfully processed checklist data")
            if not result_df.empty:
                logging.info(f"Sample processed data: {result_df.head(2).to_dict()}")

        # Check for duplicate IDs
        duplicate_ids = result_df['ID'].value_counts()[result_df['ID'].value_counts() > 1]
        if not duplicate_ids.empty:
            logging.warning(f"Found {len(duplicate_ids)} duplicate IDs in processed checklist:")
            logging.warning(duplicate_ids.head(10).to_dict())  # Log first 10 duplicates
            # Remove duplicates
            result_df = result_df.drop_duplicates(subset=['ID'], keep='first')
            logging.info(f"Removed duplicates. New DataFrame shape: {result_df.shape}")

        # 在return前添加类型转换
        # 确保所有列为字符串类型，解决Arrow序列化问题
        for col in result_df.columns:
            result_df[col] = result_df[col].astype(str)

        # 额外处理：确保没有字符串形式的'nan'或'none'
        for col in result_df.columns:
            result_df[col] = result_df[col].apply(
                lambda x: '' if str(x).lower() in ['nan', 'none'] else str(x)
            )

        return result_df
    except Exception as e:
        error_msg = f"处理核对清单失败: {str(e)}"
        logging.error(error_msg)
        logging.exception("Exception details:")

        # 提供更详细的错误信息给用户
        if "KeyError" in str(e):
            missing_col = str(e).split("'")[1] if "'" in str(e) else "未知列"
            detailed_msg = f"核对清单文件缺少必要的列: '{missing_col}'"
            st.error(f"❌ {detailed_msg}")
            st.info("💡 请检查文件格式是否正确，确保包含以下列：Item#, P/N, Desc, Qty, Price, HSN, BCD, SWS, IGST")
        else:
            st.error(f"❌ {error_msg}")
            st.info("💡 请检查文件格式是否为正确的Excel文件(.xlsx)")

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
                    
                    # 添加详细的BCD调试信息
                    if 'BCD' in diff_cols:
                        logging.info(f"BCD difference detected for ID {id1}:")
                        logging.info(f"  - Invoice BCD: '{row1['BCD']}' (type: {type(row1['BCD'])})")
                        logging.info(f"  - Checklist BCD: '{row2['BCD']}' (type: {type(row2['BCD'])})")

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

                                # 特别为BCD字段添加调试信息
                                if col == 'BCD':
                                    logging.info(f"Processing BCD difference for ID {id1}:")
                                    logging.info(f"  - Original values: '{row1[col]}' vs '{row2[col]}'")
                                    logging.info(f"  - Processed values: '{val1}' vs '{val2}'")

                                # 检查是否为空值/NaN值
                                def is_empty_value(val):
                                    return (val.lower() in ['nan', 'none', ''] or
                                           val.strip() == '' or
                                           val == 'nan')

                                val1_is_empty = is_empty_value(val1)
                                val2_is_empty = is_empty_value(val2)

                                # 特别处理：如果值相同，但原始值不同，仍然记录差异
                                # 这解决了BCD字段被意外跳过的问题
                                if val1 == val2 and str(row1[col]) == str(row2[col]):
                                    # 真正相同的值才跳过
                                    if col == 'BCD':
                                        logging.info(f"BCD values are truly equal, skipping: {val1} == {val2}")
                                    continue

                                # 处理显示值：空值显示为 "null"
                                display_val1 = 'null' if val1_is_empty else val1
                                display_val2 = 'null' if val2_is_empty else val2

                                # 添加差异信息（格式：checklist值 -> invoice值）
                                diff_info[f'{col}'] = f'{display_val2} -> {display_val1}'
                                
                                # 特别为BCD字段添加确认信息
                                if col == 'BCD':
                                    logging.info(f"BCD difference added to report: '{display_val2} -> {display_val1}'")
                            else:
                                # 跳过相同值的显示
                                if row1[col] == row2[col]:
                                    continue

                                # 检查是否为空值/NaN值
                                def is_empty_value_general(val):
                                    if pd.isna(val):
                                        return True
                                    val_str = str(val).strip().lower()
                                    return val_str in ['nan', 'none', ''] or val_str == ''

                                val1_is_empty = is_empty_value_general(row1[col])
                                val2_is_empty = is_empty_value_general(row2[col])

                                # 只有当两个值都为空时才跳过
                                if val1_is_empty and val2_is_empty:
                                    continue

                                # 跳过相同值的显示 (例如 nan -> nan)
                                if str(row1[col]).lower() == str(row2[col]).lower():
                                    continue

                                # 处理显示值：空值显示为 "null"
                                display_val1 = 'null' if val1_is_empty else str(row1[col])
                                display_val2 = 'null' if val2_is_empty else str(row2[col])

                                # 添加差异信息（格式：checklist值 -> invoice值）
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

                    # 特别为BCD列添加详细调试信息
                    if col == 'BCD':
                        logging.info(f"BCD column filtering check:")
                        logging.info(f"  - Column exists in diff_df: {col in diff_df.columns}")
                        logging.info(f"  - Has data: {has_data}")
                        if col in diff_df.columns:
                            logging.info(f"  - Column values: {diff_df[col].tolist()}")
                            logging.info(f"  - Non-null values: {[v for v in diff_df[col] if pd.notna(v) and str(v).strip() != '']}")

                    if has_data:
                        non_empty_columns.append(col)
                        logging.info(f"Column '{col}' added to non_empty_columns (has data)")
                    else:
                        logging.info(f"Column '{col}' skipped (no data found)")

            logging.info(f"Non-empty columns: {non_empty_columns}")

            # 严格按照期望的列顺序排序，只包含存在的列
            ordered_columns = []
            for col in expected_columns:
                if col in diff_df.columns and (col == 'ID' or col in non_empty_columns):
                    ordered_columns.append(col)
                    logging.info(f"添加列到最终报告: {col}")
                elif col in expected_columns:
                    # 特别为BCD列添加详细信息
                    if col == 'BCD':
                        logging.info(f"BCD列被跳过的原因:")
                        logging.info(f"  - 在diff_df中存在: {col in diff_df.columns}")
                        logging.info(f"  - 在non_empty_columns中: {col in non_empty_columns}")
                        if col in diff_df.columns:
                            logging.info(f"  - BCD列的所有值: {diff_df[col].tolist()}")
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
                # 提取正确值（格式：checklist值 -> invoice值，我们需要invoice值）
                hsn_correct = str(row['HSN']).split(' -> ')[1] if ' -> ' in str(row['HSN']) else str(row['HSN'])
                if hsn_correct != 'null':  # 只有当正确值不是null时才添加
                    corrections.append(f"HSN {hsn_correct}")

            if 'BCD' in row and pd.notna(row['BCD']) and str(row['BCD']).strip():
                # 提取正确值（格式：checklist值 -> invoice值，我们需要invoice值）
                bcd_correct = str(row['BCD']).split(' -> ')[1] if ' -> ' in str(row['BCD']) else str(row['BCD'])
                if bcd_correct != 'null':  # 只有当正确值不是null时才添加
                    corrections.append(f"BCD is {bcd_correct}")

            if 'SWS' in row and pd.notna(row['SWS']) and str(row['SWS']).strip():
                # 提取正确值（格式：checklist值 -> invoice值，我们需要invoice值）
                sws_correct = str(row['SWS']).split(' -> ')[1] if ' -> ' in str(row['SWS']) else str(row['SWS'])
                if sws_correct != 'null':  # 只有当正确值不是null时才添加
                    corrections.append(f"SWS is {sws_correct}")

            if 'IGST' in row and pd.notna(row['IGST']) and str(row['IGST']).strip():
                # 提取正确值（格式：checklist值 -> invoice值，我们需要invoice值）
                hgst_correct = str(row['IGST']).split(' -> ')[1] if ' -> ' in str(row['IGST']) else str(row['IGST'])
                if hgst_correct != 'null':  # 只有当正确值不是null时才添加
                    corrections.append(f"HGST is {hgst_correct}")

            if 'Qty' in row and pd.notna(row['Qty']) and str(row['Qty']).strip():
                # 提取正确值（格式：checklist值 -> invoice值，我们需要invoice值）
                qty_correct = str(row['Qty']).split(' -> ')[1] if ' -> ' in str(row['Qty']) else str(row['Qty'])
                if qty_correct != 'null':  # 只有当正确值不是null时才添加
                    corrections.append(f"Qty is {qty_correct}")

            if 'Price' in row and pd.notna(row['Price']) and str(row['Price']).strip():
                # 提取正确值（格式：checklist值 -> invoice值，我们需要invoice值）
                price_correct = str(row['Price']).split(' -> ')[1] if ' -> ' in str(row['Price']) else str(row['Price'])
                if price_correct != 'null':  # 只有当正确值不是null时才添加
                    corrections.append(f"Price is {price_correct}")

            if 'Desc' in row and pd.notna(row['Desc']) and str(row['Desc']).strip():
                # 提取正确值（格式：checklist值 -> invoice值，我们需要invoice值）
                desc_correct = str(row['Desc']).split(' -> ')[1] if ' -> ' in str(row['Desc']) else str(row['Desc'])
                if desc_correct != 'null':  # 只有当正确值不是null时才添加
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

def safe_display_dataframe(df, container_width=True):
    """
    安全显示 DataFrame，避免 PyArrow 序列化错误
    """
    try:
        # 创建副本并转换所有列为字符串类型
        display_df = df.copy()
        for col in display_df.columns:
            display_df[col] = display_df[col].astype(str)
        
        # 处理 NaN 值
        display_df = display_df.fillna('')
        
        # 显示 DataFrame
        st.dataframe(display_df, use_container_width=container_width)
        return True
        
    except Exception as display_error:
        # 如果还是有问题，显示基本信息
        st.warning(f"数据显示遇到问题，显示基本信息: {str(display_error)}")
        st.write(f"数据形状: {df.shape}")
        st.write(f"列名: {df.columns.tolist()}")
        
        # 尝试显示前几行的文本版本
        if not df.empty:
            st.write("前5行数据:")
            try:
                st.text(df.head().to_string())
            except Exception as text_error:
                st.error(f"无法显示数据: {str(text_error)}")
        return False

# File Upload Tab
with tab1:
    st.markdown("<h2 class='sub-header'>文件上传与设置</h2>", unsafe_allow_html=True)

    # 创建两行布局：第一行是文件上传，第二行是设置和处理

    # 第一行：文件上传区域
    st.markdown("### 📁 文件上传")
    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

    with col1:
        st.markdown("""
        <div class='upload-section'>
            <h3>税率文件</h3>
        </div>
        """, unsafe_allow_html=True)
        duty_rate_file = st.file_uploader("上传税率文件", type=["xlsx"], key="duty_rate")
        if duty_rate_file is not None:
            try:
                # 使用安全保存函数
                safe_path, safe_name = safe_save_uploaded_file(duty_rate_file, os.path.join("input", "duty_rate.xlsx"))
                st.success(f"✅ 已上传: {safe_name}")
                # 更新session state
                st.session_state.duty_rate_uploaded = True
                st.session_state.duty_rate_path = safe_path
            except Exception as e:
                st.error(f"❌ 上传失败: {str(e)}")
                st.session_state.duty_rate_uploaded = False
        else:
            st.info("📁 请上传税率文件")
            st.session_state.duty_rate_uploaded = False

    with col2:
        st.markdown("""
        <div class='upload-section'>
            <h3>核对清单</h3>
        </div>
        """, unsafe_allow_html=True)
        checklist_file = st.file_uploader("上传核对清单", type=["xlsx"], key="checklist")
        if checklist_file is not None:
            try:
                # 使用安全保存函数
                safe_path, safe_name = safe_save_uploaded_file(checklist_file, os.path.join("input", "processing_checklist.xlsx"))
                st.success(f"✅ 已上传: {safe_name}")
                # 更新session state
                st.session_state.checklist_uploaded = True
                st.session_state.checklist_path = safe_path
            except Exception as e:
                st.error(f"❌ 上传失败: {str(e)}")
                st.session_state.checklist_uploaded = False
        else:
            st.info("📁 请上传核对清单")
            st.session_state.checklist_uploaded = False

    with col3:
        st.markdown("""
        <div class='upload-section'>
            <h3>发票文件</h3>
        </div>
        """, unsafe_allow_html=True)
        invoices_file = st.file_uploader("上传发票文件", type=["xlsx"], key="invoices")
        if invoices_file is not None:
            try:
                # 使用安全保存函数
                safe_path, safe_name = safe_save_uploaded_file(invoices_file, os.path.join("input", "processing_invoices.xlsx"))
                st.success(f"✅ 已上传: {safe_name}")
                # 更新session state
                st.session_state.invoices_uploaded = True
                st.session_state.invoices_path = safe_path
            except Exception as e:
                st.error(f"❌ 上传失败: {str(e)}")
                st.session_state.invoices_uploaded = False
        else:
            st.info("📁 请上传发票文件")
            st.session_state.invoices_uploaded = False

    # 添加分隔线
    st.markdown("---")

    # 第二行：设置和处理区域
    col_settings, col_process, col_help = st.columns([2, 1, 2], gap="large")

    with col_settings:
        st.markdown("""
        <div class='settings-section'>
            <h3>⚙️ 处理设置</h3>
        </div>
        """, unsafe_allow_html=True)
        price_tolerance = st.slider("价格比对误差范围 (%)", min_value=0.1, max_value=5.0, value=1.1, step=0.1)
        st.caption(f"当前设置: 价格差异超过 {price_tolerance}% 将被标记")

    with col_process:
        st.markdown("""
        <div class='process-section'>
            <h3>🚀 开始处理</h3>
        </div>
        """, unsafe_allow_html=True)
        process_button = st.button("开始处理", type="primary", use_container_width=True)

        # 显示处理状态
        if st.session_state.get('duty_rate_uploaded', False) and \
           st.session_state.get('checklist_uploaded', False) and \
           st.session_state.get('invoices_uploaded', False):
            st.success("✅ 所有文件已就绪")
        else:
            st.warning("⚠️ 请先上传所有文件")

    with col_help:
        st.markdown("""
        <div class='help-section'>
            <h3>💡 使用说明</h3>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("查看详细步骤", expanded=False):
            st.markdown("""
            **操作步骤：**
            1. 📄 上传税率文件 (duty_rate.xlsx)
            2. 📋 上传核对清单 (processing_checklist.xlsx)
            3. 🧾 上传发票文件 (processing_invoices*.xlsx)
            4. ⚙️ 调整价格比对误差范围（可选）
            5. 🚀 点击"开始处理"按钮
            6. 📊 在其他标签页查看处理结果

            **注意事项：**
            - 确保文件格式为 .xlsx
            - 文件大小限制为 200MB
            - 处理时间取决于数据量大小
            """)

# Data Preview Tab
with tab2:
    st.markdown("<h2 class='sub-header'>数据预览</h2>", unsafe_allow_html=True)

    preview_tabs = st.tabs(["税率数据", "核对清单", "发票数据"])

    with preview_tabs[0]:
        if duty_rate_file is not None:
            try:
                duty_df = pd.read_excel(duty_rate_file)
                safe_display_dataframe(duty_df)
            except Exception as e:
                st.error(f"无法预览税率文件: {str(e)}")
        else:
            st.info("请先上传税率文件")

    with preview_tabs[1]:
        if checklist_file is not None:
            try:
                checklist_df = pd.read_excel(checklist_file, skiprows=3)
                safe_display_dataframe(checklist_df)
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
                    safe_display_dataframe(invoices_df)
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
                # 使用session state中保存的实际文件路径
                duty_rate_path = st.session_state.get('duty_rate_path', os.path.join("input", "duty_rate.xlsx"))
                invoices_path = st.session_state.get('invoices_path', os.path.join("input", "processing_invoices.xlsx"))
                checklist_path = st.session_state.get('checklist_path', os.path.join("input", "processing_checklist.xlsx"))

                logging.info(f"Input files: duty_rate={duty_rate_path}, invoices={invoices_path}, checklist={checklist_path}")
                logging.info(f"Price tolerance: {price_tolerance}%")
                
                # 验证文件是否存在
                if not os.path.exists(duty_rate_path):
                    raise FileNotFoundError(f"税率文件不存在: {duty_rate_path}")
                if not os.path.exists(invoices_path):
                    raise FileNotFoundError(f"发票文件不存在: {invoices_path}")
                if not os.path.exists(checklist_path):
                    raise FileNotFoundError(f"核对清单文件不存在: {checklist_path}")

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
                        logging.info("No differences found, creating empty diff report")
                        # 即使没有差异，也创建一个空的报告文件
                        empty_diff_df = pd.DataFrame({'消息': ['没有发现差异']})
                        empty_diff_df.to_excel(processed_report_path, index=False)

                        # 仍然显示下载按钮，让用户可以下载空报告
                        st.session_state.show_download_button = True
                        st.session_state.show_email_button = False

                        # 创建空的下载缓冲区
                        report_buffer = BytesIO()
                        empty_diff_df.to_excel(report_buffer, index=False)
                        report_buffer.seek(0)
                        st.session_state.auto_download_report = report_buffer
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
                            # 检查duty_df是否为None
                            if duty_df is not None:
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
                            else:
                                logging.warning("duty_df is None, skipping CCTV sheet creation")

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
                safe_display_dataframe(processed_invoices_df)

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
                safe_display_dataframe(processed_checklist_df)

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
                        safe_display_dataframe(new_items_df)

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
                safe_display_dataframe(diff_report_df)

                col1, col2 = st.columns(2)

                with col1:
                    # 修改下载按钮，添加use_container_width=True来防止跳转
                    with open(diff_report_path, "rb") as file:
                        st.download_button(
                            label="📥 下载差异报告",
                            data=file,
                            file_name="processed_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            help="下载差异比对报告文件"
                        )

                with col2:
                    # 改进邮件草稿按钮，使用更好的状态管理
                    # 初始化邮件生成状态
                    if 'email_button_clicked' not in st.session_state:
                        st.session_state.email_button_clicked = False

                    if st.button("📧 生成通知邮件草稿", type="secondary", key="generate_email_button", use_container_width=True):
                        # 设置按钮点击状态
                        st.session_state.email_button_clicked = True

                        email_content = generate_email_draft(diff_report_df)
                        if email_content:
                            # 显示邮件内容预览
                            st.session_state.email_draft_content = email_content

                            # 使用容器来显示状态消息，避免页面跳转
                            success_container = st.container()
                            with success_container:
                                st.success("✅ 邮件草稿已生成！")

                            # 尝试打开邮件客户端
                            if open_email_client(email_content):
                                info_container = st.container()
                                with info_container:
                                    st.info("📧 已尝试打开默认邮件客户端")
                            else:
                                warning_container = st.container()
                                with warning_container:
                                    st.warning("⚠️ 无法打开邮件客户端，请查看下方邮件内容")
                        else:
                            error_container = st.container()
                            with error_container:
                                st.error("❌ 生成邮件草稿失败")

                    # 如果按钮被点击过，显示重置选项
                    if st.session_state.email_button_clicked:
                        if st.button("🔄 重置", key="reset_email_button", help="重置邮件生成状态"):
                            st.session_state.email_button_clicked = False
                            if 'email_draft_content' in st.session_state:
                                del st.session_state.email_draft_content
                            st.rerun()

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
if 'show_download_button' in st.session_state and st.session_state.show_download_button:
    if 'auto_download_report' in st.session_state:
        st.success("处理完成！比对报告已准备好下载")

        col1, col2 = st.columns(2)

        with col1:
            # 使用session state来管理下载状态，避免页面跳转
            # 初始化下载状态
            if 'download_clicked' not in st.session_state:
                st.session_state.download_clicked = False

            # 创建下载按钮
            download_button = st.download_button(
                label="📥 点击下载比对报告",
                data=st.session_state.auto_download_report,
                file_name="比对报告.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="auto_download_report_button",
                use_container_width=True,
                help="点击下载差异比对报告文件"
            )

            # 如果下载按钮被点击，显示反馈
            if download_button:
                st.session_state.download_clicked = True
                success_container = st.container()
                with success_container:
                    st.success("✅ 报告下载已开始")
                    st.info(" 文件将保存到您的默认下载文件夹")

        with col2:
            # 使用session state来管理邮件生成状态，避免页面跳转
            if 'show_email_button' in st.session_state and st.session_state.show_email_button:
                # 检查是否已经生成过邮件草稿
                if 'email_generated' not in st.session_state:
                    st.session_state.email_generated = False

                # 使用不同的按钮文本来反映状态
                button_label = "🔄 重新生成邮件草稿" if st.session_state.email_generated else "📧 生成通知邮件草稿"

                if st.button(button_label, type="secondary", key="auto_generate_email_button", use_container_width=True, help="生成并打开邮件客户端"):
                    if 'email_draft_content' in st.session_state:
                        # 标记邮件已生成
                        st.session_state.email_generated = True

                        # 使用容器来显示状态消息，避免页面跳转
                        success_container = st.container()
                        with success_container:
                            st.success("✅ 邮件草稿已准备就绪")

                        # 尝试打开邮件客户端
                        if open_email_client(st.session_state.email_draft_content):
                            info_container = st.container()
                            with info_container:
                                st.info("📧 已打开默认邮件客户端")
                        else:
                            warning_container = st.container()
                            with warning_container:
                                st.warning("⚠️ 无法打开邮件客户端，请查看下方邮件内容")
                    else:
                        error_container = st.container()
                        with error_container:
                            st.error("❌ 邮件草稿内容不可用，请重新处理数据")

# 显示自动生成的邮件草稿预览 - 使用session state控制显示
if 'email_draft_content' in st.session_state and st.session_state.email_draft_content:
    st.markdown("### 📧 邮件草稿已自动生成")
    with st.expander("查看邮件内容", expanded=False):
        st.text_area(
            "邮件内容",
            st.session_state.email_draft_content,
            height=200,
            help="您可以复制此内容到邮件客户端",
            key="auto_email_preview",
            disabled=True  # 设置为只读，避免意外修改
        )

st.markdown("© 2025 Checklist核对系统 | 版本 1.2")