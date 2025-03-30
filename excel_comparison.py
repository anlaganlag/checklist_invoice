import pandas as pd
import sys
import os


def compare_excels(file1, file2, output_file):
    try:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        # 确保两个 DataFrame 的列名顺序一致
        df2 = df2[df1.columns]

        # 用于存储差异信息
        diff_data = []

        for index, row1 in df1.iterrows():
            id1 = row1['id']
            # 查找 df2 中对应 id 的行
            matching_row = df2[df2['id'] == id1]
            if not matching_row.empty:
                row2 = matching_row.iloc[0]
                diff_cols = []
                for col in df1.columns[1:]:
                    if row1[col] != row2[col]:
                        diff_cols.append(col)
                if diff_cols:
                    diff_info = {'id': id1}
                    for col in diff_cols:
                        diff_info[f'{col}_file1'] = row1[col]
                        diff_info[f'{col}_file2'] = row2[col]
                    diff_data.append(diff_info)

        if diff_data:
            diff_df = pd.DataFrame(diff_data)
            diff_df.to_excel(output_file, index=False)
            print(f"差异已保存到 {output_file}")
        else:
            print("两个 Excel 文件内容一致。")

    except FileNotFoundError:
        print("错误: 文件未找到!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else 'differences.xlsx'
    else:
        file1 = 'file1.xlsx'
        file2 = 'file2.xlsx'
        output_file = 'differences.xlsx'
    
    # Print current working directory and file paths for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for files:\n  {file1}\n  {file2}")
    
    compare_excels(file1, file2, output_file)
    