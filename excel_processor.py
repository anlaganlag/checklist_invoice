import pandas as pd
import warnings
import os

# Filter out the warning about print area
warnings.filterwarnings('ignore', message='Print area cannot be set to Defined name')


def get_duty_rates():
    try:
        # Read dutyRate.xlsx
        df = pd.read_excel('dutyRate.xlsx')
        
        # Group by Item_Name and aggregate other columns
        grouped_df = df.groupby('Item Name').agg({
            'HSN1': lambda x: ' '.join(str(i) for i in x if pd.notna(i)),  # Concatenate HSN1 with space
            'HSN2': lambda x: ' '.join(str(i) for i in x if pd.notna(i)),  # Add HSN2
            'Final BCD': 'min',
            'Final SWS': 'min',
            'Final IGST': 'min'
        }).reset_index()
        
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
        
        return duty_dict
    except Exception as e:
        print(f"Error reading dutyRate.xlsx: {str(e)}")
        return {}

def create_checking_list():
    try:
        duty_rates = get_duty_rates()
        print(duty_rates)

        # Get all sheet names
        excel_file = pd.ExcelFile('import_invoice.xlsx')
        # Print all available sheet names
        print("Available sheets:", excel_file.sheet_names)
        
        # Store original sheet names for accessing sheets
        original_sheet_names = excel_file.sheet_names[1:]  # Skip the first sheet
        
        # Process sheet names for display and ID creation (remove CI- prefix)
        processed_sheet_names = [name.replace('CI-', '') if name.startswith('CI-') else name 
                      for name in original_sheet_names]
        
        # Print processed sheet names
        print("Processed sheet names:", processed_sheet_names)
        
        # Initialize an empty DataFrame for the final result
        final_df = pd.DataFrame()
        current_sheet_cnt = 0
        sheet_cnt = len(original_sheet_names)
        
        # Process each sheet starting from the second one
        for i, original_sheet_name in enumerate(original_sheet_names):
            print(f"Attempting to access sheet: {original_sheet_name}")
            current_sheet_cnt += 1
            
            # Use processed name for ID creation
            processed_sheet_name = processed_sheet_names[i]
            
            # Read the sheet using original name, skipping the first 12 rows
            df = pd.read_excel('import_invoice.xlsx', sheet_name=original_sheet_name, skiprows=12)
            
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
            

            if not df.empty:
                # Create a row with empty values except for the first column which contains the sheet name
                sheet_row_data = [""] * len(df.columns)
                sheet_row_data[0] = f'{processed_sheet_name} Invoice {current_sheet_cnt}/{sheet_cnt}'
                sheet_row = pd.DataFrame([sheet_row_data], columns=df.columns)
                df = pd.concat([sheet_row, df], ignore_index=True)
            
            # Print actual columns to help identify them
            print(f"\nColumns in sheet '{processed_sheet_name}':")
            for i, col in enumerate(df.columns):
                print(f"{i}: '{col}'")
            
            # IMPORTANT: Update these indices based on the printed columns
            column_indices = {
                'Item#': 0, 
                'P/N': 2,  
                'Desc': 3, 
                'Qty': 5,    # Replace with actual index of "Quantity PCS" column
                'Price': 6,    # Replace with actual index of "Description" column
  # Replace with actual index of "P/N" column
                'Category': 1,  # Replace with actual index of "Model Number" column
 # Replace with actual index of "Unit Price USD" column
                'Item_Name':3,
            }
            
            # Create a new DataFrame with selected columns
            sheet_df = pd.DataFrame()
            
            # Add Item# as the first column
            sheet_df['Item#'] = df.iloc[:, column_indices['Item#']]
            
            # Then create the ID column as the second column
            sheet_df['ID'] = ''  # Initialize empty ID column

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
            sheet_df.loc[1:,'ID'] = processed_sheet_name+ '_' + sheet_df['Item#'].astype(str)                        # Add duty rate columns after all other columns are set
            
            # Add duty rate columns after all other columns are set

            sheet_df['HSN'] = ''
            sheet_df['Duty'] = ''
            sheet_df['Welfare'] = ''
            sheet_df['IGST'] = ''

            # Fill duty rate information for rows with Item_Name
            for idx, row in sheet_df.iterrows():
                if pd.notna(row['Item_Name']) and row['Item_Name'] in duty_rates:
                    rates = duty_rates[row['Item_Name']]
                    sheet_df.at[idx, 'HSN'] = rates['hsn']
                    sheet_df.at[idx, 'Duty'] = rates['bcd']
                    sheet_df.at[idx, 'Welfare'] = rates['sws']
                    sheet_df.at[idx, 'IGST'] = rates['igst']
            



            
            # Append to the final DataFrame
            final_df = pd.concat([final_df, sheet_df], ignore_index=True)
            
        # Rename final_df to new_df to maintain compatibility with existing code
        new_df = final_df
        import os

        # Save to new Excel file
        try:
            new_df.to_excel('checking_list.xlsx', index=False)
            # Try a simpler approach using os.startfile instead of COM automation
            os.startfile('checking_list.xlsx')
            print("\nSuccessfully created checking_list.xlsx")
        except PermissionError:
            print("Error: The file is currently open. Please close it and try again.")
            return False
        except Exception as e:
            print(f"Error opening the file: {str(e)}")
            return False
        return True
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    create_checking_list()