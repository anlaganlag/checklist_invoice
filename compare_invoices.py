import pandas as pd

def compare_invoices(file1_path, file2_path, output_path):
    # Read the two files into dataframes
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)
    
    # Define the keys for comparison
    key_columns = ['invoice_number', 'item_number']
    
    # Merge the dataframes on invoice_number and item_number
    merged_df = df1.merge(
        df2,
        on=key_columns,
        how='outer',
        suffixes=('_file1', '_file2'),
        indicator=True
    )
    
    # Find differences
    differences = []
    
    # Get all columns except the key columns
    value_columns = [col for col in df1.columns if col not in key_columns]
    
    # Compare each row
    for _, row in merged_df.iterrows():
        if row['_merge'] == 'both':  # Record exists in both files
            for col in value_columns:
                col1 = f"{col}_file1"
                col2 = f"{col}_file2"
                
                # Compare values and handle NaN cases
                if pd.isna(row[col1]) and pd.isna(row[col2]):
                    continue
                elif row[col1] != row[col2]:
                    differences.append({
                        'invoice_number': row['invoice_number'],
                        'item_number': row['item_number'],
                        'column': col,
                        'file1_value': row[col1],
                        'file2_value': row[col2]
                    })
    
    # Create difference report
    if differences:
        diff_df = pd.DataFrame(differences)
        diff_df.to_excel(output_path, index=False)
        print(f"Differences found and saved to {output_path}")
    else:
        print("No differences found for matching invoice numbers and item numbers")

# Example usage
if __name__ == "__main__":
    file1_path = "invoice_file1.xlsx"
    file2_path = "invoice_file2.xlsx"
    output_path = "invoice_differences.xlsx"
    
    compare_invoices(file1_path, file2_path, output_path) 