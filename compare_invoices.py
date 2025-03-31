import pandas as pd

def compare_invoices(invoice_path, check_path, output_path):
    # Read the two files into dataframes
    df1 = pd.read_excel(invoice_path)
    df2 = pd.read_excel(check_path)
    
    # Define the keys for comparison
    key_columns = ['invoice_number', 'item_number']
    
    # Define the order of comparison columns
    comparison_order = ['P/N', 'Qty', 'Price', 'Desc', 'Category', 'HSN', 'Duty', 'Welfare', 'IGST']
    
    # Merge the dataframes on invoice_number and item_number
    merged_df = df1.merge(
        df2,
        on=key_columns,
        how='outer',
        suffixes=('_invoice', '_check'),
        indicator=True
    )
    
    # Find differences
    differences = []
    
    # Compare each row
    for _, row in merged_df.iterrows():
        if row['_merge'] == 'both':  # Record exists in both files
            diff_details = []
            
            for col in comparison_order:
                if col in df1.columns:  # Only check if column exists
                    col1 = f"{col}_invoice"
                    col2 = f"{col}_check"
                    
                    # Compare values and handle NaN cases
                    if pd.isna(row[col1]) and pd.isna(row[col2]):
                        continue
                    elif row[col1] != row[col2]:
                        diff_details.append(f"{col}: {row[col2]} -> {row[col1]}")
            
            if diff_details:  # If any differences found
                differences.append({
                    'invoice_number': row['invoice_number'],
                    'item_number': row['item_number'],
                    'differences': '; '.join(diff_details)
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
    invoice_path = "checking_list.xlsx"
    check_path = "clean_check.xlsx"
    output_path = "invoice_differences.xlsx"
    
    compare_invoices(invoice_path, check_path, output_path) 