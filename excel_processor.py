import pandas as pd

def create_checking_list():
    try:
        # Get all sheet names
        excel_file = pd.ExcelFile('import_invoice.xlsx')
        sheet_names = excel_file.sheet_names[1:]  # Skip the first sheet
        
        # Initialize an empty DataFrame for the final result
        final_df = pd.DataFrame()
        
        # Process each sheet starting from the second one
        for sheet_name in sheet_names:
            # Read the sheet, skipping the first 12 rows
            df = pd.read_excel('import_invoice.xlsx', sheet_name=sheet_name, skiprows=12)
            
            # Process rows to handle empty rows after numbered data
            processed_rows = []
            skip_mode = False
            
            for idx, row in df.iterrows():
                # Check if row is empty (all values are NaN)
                is_empty = row.isna().all()
                
                # If we find a non-empty row and we're not in skip mode
                if not is_empty and not skip_mode:
                    processed_rows.append(row)
                    # Check if this row starts with a number and next row (if exists) is empty
                    if idx < len(df) - 1:
                        next_row = df.iloc[idx + 1]
                        if next_row.isna().all():
                            skip_mode = True
                elif not is_empty and skip_mode:
                    # If we find a non-empty row while in skip mode, check if it's a new section
                    try:
                        # Try to convert first cell to float to check if it's a number
                        float(str(row.iloc[0]).split('.')[0])
                        skip_mode = False
                        processed_rows.append(row)
                    except (ValueError, IndexError):
                        continue
            
            # Convert processed rows back to DataFrame
            df = pd.DataFrame(processed_rows, columns=df.columns)
            
            # Add sheet name as the first row only if we have data
            if not df.empty:
                # Create a row with empty values except for the first column which contains the sheet name
                sheet_row_data = [""] * len(df.columns)
                sheet_row_data[0] = sheet_name
                sheet_row = pd.DataFrame([sheet_row_data], columns=df.columns)
                df = pd.concat([sheet_row, df], ignore_index=True)
            
            # Print actual columns to help identify them
            print(f"\nColumns in sheet '{sheet_name}':")
            for i, col in enumerate(df.columns):
                print(f"{i}: '{col}'")
            
            # IMPORTANT: Update these indices based on the printed columns
            column_indices = {
                'Item#': 0,  # Replace with actual index of "Item Nos." column
                'P/N': 2,    # Replace with actual index of "P/N" column
                'Desc': 3,   # Replace with actual index of "Description" column
                'Qty': 5,    # Replace with actual index of "Quantity PCS" column
                'Price': 6   # Replace with actual index of "Unit Price USD" column
            }
            
            # Create a new DataFrame with selected columns
            sheet_df = pd.DataFrame()
            for new_name, idx in column_indices.items():
                sheet_df[new_name] = df.iloc[:, idx]
            
            # Append to the final DataFrame
            final_df = pd.concat([final_df, sheet_df], ignore_index=True)
            
        # Rename final_df to new_df to maintain compatibility with existing code
        new_df = final_df
        
        # Save to new Excel file
        new_df.to_excel('checking_list.xlsx', index=False)
        print("\nSuccessfully created checking_list.xlsx")
        return True
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    create_checking_list()