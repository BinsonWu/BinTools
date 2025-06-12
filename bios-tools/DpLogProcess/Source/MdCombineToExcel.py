import pandas as pd
import sys
import os

def adjust_column_width(writer, sheet_name):
    workbook = writer.book
    worksheet = workbook[sheet_name]

    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter  # Get the column name

        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass

        adjusted_width = max_length + 2
        worksheet.column_dimensions[column_letter].width = adjusted_width

def read_md_to_df(file_path):
    try:
        # Read the Markdown file
        df = pd.read_csv(file_path, delimiter='|', skipinitialspace=True)
        # Remove any completely empty rows and reset the index
        df = df.dropna(how='all').reset_index(drop=True)
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        # Remove columns with names starting with 'Unnamed:'
        df = df.loc[:, ~df.columns.str.contains('^Unnamed:')]
        # Filter out rows that contain the substring '--'
        df = df[~df.apply(lambda row: row.astype(str).str.contains('--').any(), axis=1)]
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return pd.DataFrame()

def merge_md_files(file_sheet_pairs, output_file='merged_file.xlsx'):
    # Create a new Excel file and write each file to a different sheet
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for file, sheet_name in file_sheet_pairs:
            df = read_md_to_df(file)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            adjust_column_width(writer, sheet_name)

    print(f"Markdown files have been merged into '{output_file}'")

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) < 4 or (len(sys.argv) - 2) % 2 != 0:
        print("Usage: python merge_md.py <output_file> <file1> <sheet_name1> [<file2> <sheet_name2> ...]")
    else:
        # Get the output file name and the file-sheet pairs from command line arguments
        output_file = sys.argv[1]
        file_sheet_pairs = [(sys.argv[i], sys.argv[i + 1]) for i in range(2, len(sys.argv) - 1, 2)]
        
        # Merge the Markdown files
        merge_md_files(file_sheet_pairs, output_file)
