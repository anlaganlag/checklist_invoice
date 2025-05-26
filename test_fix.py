import pandas as pd
import os
import sys

# 添加当前目录到Python路径
sys.path.append('.')

# 导入修复后的函数
from streamlit_app import process_checklist

def test_process_checklist():
    """测试process_checklist函数的健壮性"""
    
    # 创建一个测试Excel文件，模拟可能的列名变化
    test_data = {
        'Item No': [1, 2, 3],  # 不同的列名格式
        'Part Number': ['PN001', 'PN002', 'PN003'],  # P/N的变体
        'Description': ['Item 1', 'Item 2', 'Item 3'],  # Desc的变体
        'Quantity': [10, 20, 30],  # Qty的变体
        'Unit Price': [100, 200, 300],  # Price的变体
        'HSN Code': [12345, 67890, 11111],  # HSN的变体
        'Basic Customs Duty': [5, 10, 15],  # BCD的变体
        'Social Welfare Surcharge': [1, 2, 3],  # SWS的变体
        'IGST Rate': [18, 18, 18]  # IGST的变体
    }
    
    # 创建测试DataFrame
    df = pd.DataFrame(test_data)
    
    # 添加一些空行（模拟skiprows=3的效果）
    header_rows = pd.DataFrame([[''] * len(df.columns)] * 3, columns=df.columns)
    df_with_headers = pd.concat([header_rows, df], ignore_index=True)
    
    # 保存为测试文件
    test_file = 'test_checklist.xlsx'
    df_with_headers.to_excel(test_file, index=False)
    
    print(f"Created test file: {test_file}")
    print(f"Test data columns: {df.columns.tolist()}")
    
    try:
        # 测试修复后的函数
        result = process_checklist(test_file)
        print(f"Function executed successfully!")
        print(f"Result shape: {result.shape}")
        print(f"Result columns: {result.columns.tolist()}")
        
        if not result.empty:
            print("Sample result data:")
            print(result.head())
        else:
            print("Result is empty - this might be expected for this test data")
            
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"Cleaned up test file: {test_file}")

if __name__ == "__main__":
    test_process_checklist() 