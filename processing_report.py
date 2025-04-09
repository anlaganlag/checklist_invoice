import pandas as pd
import sys
import os


def compare_excels(file1, file2, output_file):
    try:
        # 指定所有列都按字符串类型读取
        df1 = pd.read_excel(file1, dtype=str)
        df2 = pd.read_excel(file2, dtype=str)
        
        # 将Price列转换为float类型，因为它需要进行数值计算
        df1['Price'] = pd.to_numeric(df1['Price'], errors='coerce')
        df2['Price'] = pd.to_numeric(df2['Price'], errors='coerce')

        # Print detailed information about the columns
        print("\nFile 1 columns:")
        print(df1.columns.tolist())
        print("\nFile 2 columns:")
        print(df2.columns.tolist())
        
        # Check if 'ID' column exists
        if 'ID' not in df1.columns or 'ID' not in df2.columns:
            print("\nWarning: 'ID' column not found!")
            print("Available columns in file 1:", df1.columns.tolist())
            print("Available columns in file 2:", df2.columns.tolist())
            return

        # 确保两个 DataFrame 的列名顺序一致
        df2 = df2[df1.columns]

        # 用于存储差异信息
        diff_data = []

        for index, row1 in df1.iterrows():
            id1 = row1['ID']
            # 查找 df2 中对应 ID 的行
            matching_row = df2[df2['ID'] == id1]
            if not matching_row.empty:
                row2 = matching_row.iloc[0]
                diff_cols = []
                for col in df1.columns[1:]:  # 跳过ID列
                    # 跳过Item_Name列的比对
                    if col == 'Item_Name':
                        continue
                    
                    # 对Price列使用1.1%的误差范围
                    if col == 'Price':
                        tolerance = row1[col] * 0.011  # 1.1%的误差
                        if abs(row1[col] - row2[col]) > tolerance:
                            diff_cols.append(col)
                    # 其他列使用精确比对
                    elif row1[col] != row2[col]:
                        diff_cols.append(col)
                        
                if diff_cols:
                    diff_info = {'ID': id1}
                    for col in diff_cols:
                        diff_info[f'{col}'] = f'{row2[col]} -> {row1[col]}'
                    diff_data.append(diff_info)

        if diff_data:
            diff_df = pd.DataFrame(diff_data)
            
            # 替换列名：Duty -> BCD, Welfare -> SWS
            column_mapping = {}
            for col in diff_df.columns:
                if col == 'Duty':
                    column_mapping[col] = 'BCD'
                elif col == 'Welfare':
                    column_mapping[col] = 'SWS'
                else:
                    column_mapping[col] = col
            
            # 重命名列
            diff_df = diff_df.rename(columns=column_mapping)
            
            # Create Excel writer with xlsxwriter engine
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                diff_df.to_excel(writer, index=False, sheet_name="checkList和进口发票比对")
                # Get the xlsxwriter workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets["checkList和进口发票比对"]
                # Set a fixed width of 20 for all columns
                for i, col in enumerate(diff_df.columns):
                    worksheet.set_column(i, i, 24)
            print(f"差异已保存到 {output_file}")
        else:
            print("两个 Excel 文件内容一致。")

    except FileNotFoundError as e:
        print(f"\n❌ 文件未找到: {str(e)}")
        print(f"错误发生在 compare_excels 函数的第 {e.__traceback__.tb_lineno} 行")
    except Exception as e:
        print(f"\n❌ 发生未知错误: {str(e)}")
        print(f"错误发生在 compare_excels 函数的第 {e.__traceback__.tb_lineno} 行")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 5:  # 参数数量增加到6个
        input_files = {
            'invoices': sys.argv[1],
            'checklist': sys.argv[2],
            'duty_rate': sys.argv[3],  # 新增税率文件参数
            'output_invoices': sys.argv[4],
            'output_checklist': sys.argv[5],
            'output_report': sys.argv[6] if len(sys.argv) > 6 else 'output/processed_report.xlsx'
        }
    else:
        # 使用默认输入输出路径
        input_files = {
            'invoices': 'input/processing_invoices.xlsx',
            'checklist': 'input/processing_checklist.xlsx',
            'duty_rate': 'input/duty_rate.xlsx',
            'output_invoices': 'output/processed_invoices.xlsx',
            'output_checklist': 'output/processed_checklist.xlsx',
            'output_report': 'output/processed_report.xlsx'
        }
    
    # 创建输出目录
    os.makedirs('output', exist_ok=True)
    
    # 调用处理流程（需要与其他处理脚本整合）
    compare_excels(input_files['output_invoices'], 
                 input_files['output_checklist'],
                 input_files['output_report'])
    
    try:
        # Update path for opening file
        output_path = os.path.abspath(input_files['output_report'])
        if os.path.exists(output_path):
            if sys.platform.startswith('win'):
                os.startfile(output_path)
            else:
                print(f"\n文件已生成：{output_path}")
                print("注意：非Windows系统不支持自动打开文件")
    except Exception as e:
        print(f"\n❌ 打开结果文件失败: {str(e)}")
        print(f"错误发生在第 {e.__traceback__.tb_lineno} 行")
    finally:
        print("\n处理完成！")
        input("按回车键退出程序...")  # 无论是否出错都等待用户确认后退出
    