import pandas as pd
import sys
import os

def check_python_version():
    """Check if the script is running with Python 3."""
    if sys.version_info[0] < 3:
        print("This script requires Python 3.")
        sys.exit(1)

def clean_column_names(df):
    """Clean DataFrame column names by stripping whitespace."""
    df.columns = df.columns.str.strip()
    return df

def save_as_markdown(df, output_file):
    """Save DataFrame to Markdown file."""
    with open(output_file, 'w') as f:
        f.write(df.to_markdown(index=False))

def compare_major_files(file1, file2, output_file=None):
    # Read the two Markdown files and convert them to DataFrames
    df1 = pd.read_csv(file1, delimiter='|', skipinitialspace=True, engine='python', header=0, skiprows=[1])
    df2 = pd.read_csv(file2, delimiter='|', skipinitialspace=True, engine='python', header=0, skiprows=[1])

    # Remove extra columns that may have been misread
    df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
    df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

    # Clean column names
    df1 = clean_column_names(df1)
    df2 = clean_column_names(df2)

    # Check if the required columns exist
    required_columns = ['Phase', 'Duration (us)']
    for col in required_columns:
        if col not in df1.columns:
            print(f"Column {col} is missing in file1")
        if col not in df2.columns:
            print(f"Column {col} is missing in file2")
    
    # Convert the Duration (us) columns to integer type
    df1['Duration (us)'] = df1['Duration (us)'].astype(int)
    df2['Duration (us)'] = df2['Duration (us)'].astype(int)
    
    # Extract file names without extensions for clearer column names
    file1_name = os.path.splitext(os.path.basename(file1))[0]
    file2_name = os.path.splitext(os.path.basename(file2))[0]
    
    # Merge the two DataFrames on Phase
    df_merged = pd.merge(df1, df2, on='Phase', suffixes=(f'_{file1_name}', f'_{file2_name}'))
    
    # Rename columns for clarity
    df_merged.rename(columns={
        f'Duration (us)_{file1_name}': f'{file1_name} Duration (us)',
        f'Duration (us)_{file2_name}': f'{file2_name} Duration (us)'
    }, inplace=True)
    
    # Calculate the difference and add a Difference(us) column
    df_merged['Difference (us)'] = df_merged[f'{file2_name} Duration (us)'] - df_merged[f'{file1_name} Duration (us)']
    
    # Sort the DataFrame by Difference (us) in descending order
    df_result = df_merged[['Phase', f'{file1_name} Duration (us)', f'{file2_name} Duration (us)', 'Difference (us)']]
    df_result = df_result.sort_values(by='Difference (us)', ascending=False)
    
    # Determine the output file name if not provided
    if output_file is None:
        output_file = f'comparison_Major.md'
    
    # Output the result to a Markdown file
    save_as_markdown(df_result, output_file)
    print(f"Results have been saved to {output_file}")
    
    # Print the result to the console
    print(df_result.to_markdown(index=False))

def compare_peims_files(file1, file2, output_file='comparison_PEIMs.md'):
    # Read the two Markdown files and convert them to DataFrames
    df1 = pd.read_csv(file1, delimiter='|', skipinitialspace=True, engine='python', header=0, skiprows=[1])
    df2 = pd.read_csv(file2, delimiter='|', skipinitialspace=True, engine='python', header=0, skiprows=[1])

    # Remove extra columns that may have been misread
    df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
    df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

    # Clean column names
    df1 = clean_column_names(df1)
    df2 = clean_column_names(df2)

    # Check if the required columns exist
    required_columns = ['Instance GUID', 'Total Time(us)']
    for col in required_columns:
        if col not in df1.columns:
            print(f"Column {col} is missing in file1")
        if col not in df2.columns:
            print(f"Column {col} is missing in file2")
    
    # Convert the Total Time(us) columns to integer type
    df1['Total Time(us)'] = df1['Total Time(us)'].astype(int)
    df2['Total Time(us)'] = df2['Total Time(us)'].astype(int)
    
    # Extract file names without extensions for clearer column names
    file1_name = os.path.splitext(os.path.basename(file1))[0]
    file2_name = os.path.splitext(os.path.basename(file2))[0]
    
    # Merge the two DataFrames on Instance GUID
    df_merged = pd.merge(df1, df2, on='Instance GUID', suffixes=(f'_{file1_name}', f'_{file2_name}'))
    
    # Rename columns for clarity
    df_merged.rename(columns={
        f'Total Time(us)_{file1_name}': f'{file1_name} Total Time(us)',
        f'Total Time(us)_{file2_name}': f'{file2_name} Total Time(us)'
    }, inplace=True)
    
    # Calculate the difference and add a Difference(us) column
    df_merged['Difference(us)'] = df_merged[f'{file2_name} Total Time(us)'] - df_merged[f'{file1_name} Total Time(us)']
    
    # Sort the DataFrame by Difference(us) in descending order
    df_result = df_merged[['Instance GUID', f'{file1_name} Total Time(us)', f'{file2_name} Total Time(us)', 'Difference(us)']]
    df_result = df_result.sort_values(by='Difference(us)', ascending=False)
    
    # Output the result to a Markdown file
    save_as_markdown(df_result, output_file)
    print(f"Results have been saved to {output_file}")
    
    # Print the result to the console
    print(df_result.to_markdown(index=False))

def compare_drivers_files(file1, file2, output_file=None):
    # Read the two Markdown files and convert them to DataFrames
    df1 = pd.read_csv(file1, delimiter='|', skipinitialspace=True, engine='python', header=0, skiprows=[1])
    df2 = pd.read_csv(file2, delimiter='|', skipinitialspace=True, engine='python', header=0, skiprows=[1])

    # Remove extra columns that may have been misread
    df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
    df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

    # Clean column names
    df1 = clean_column_names(df1)
    df2 = clean_column_names(df2)

    # Check if the required columns exist
    required_columns = ['Driver Name', 'Description', 'Total Time(us)']
    for col in required_columns:
        if col not in df1.columns:
            print(f"Column {col} is missing in file1")
        if col not in df2.columns:
            print(f"Column {col} is missing in file2")
    
    # Convert the Total Time(us) columns to integer type
    df1['Total Time(us)'] = df1['Total Time(us)'].astype(int)
    df2['Total Time(us)'] = df2['Total Time(us)'].astype(int)
    
    # Extract file names without extensions for clearer column names
    file1_name = os.path.splitext(os.path.basename(file1))[0]
    file2_name = os.path.splitext(os.path.basename(file2))[0]
    
    # Merge the two DataFrames on Driver Name and Description
    df_merged = pd.merge(df1, df2, on=['Driver Name', 'Description'], suffixes=(f'_{file1_name}', f'_{file2_name}'))
    
    # Rename columns for clarity
    df_merged.rename(columns={
        f'Total Time(us)_{file1_name}': f'{file1_name} Total Time(us)',
        f'Total Time(us)_{file2_name}': f'{file2_name} Total Time(us)'
    }, inplace=True)
    
    # Calculate the difference and add a Difference(us) column
    df_merged['Difference(us)'] = df_merged[f'{file2_name} Total Time(us)'] - df_merged[f'{file1_name} Total Time(us)']
    
    # Sort the DataFrame by Difference (us) in descending order
    df_result = df_merged[['Driver Name', 'Description', f'{file1_name} Total Time(us)', f'{file2_name} Total Time(us)', 'Difference(us)']]
    df_result = df_result.sort_values(by='Difference(us)', ascending=False)
    
    # Determine the output file name if not provided
    if output_file is None:
        output_file = f'comparison_Drivers.md'
    
    # Output the result to a Markdown file
    save_as_markdown(df_result, output_file)
    print(f"Results have been saved to {output_file}")
    
    # Print the result to the console
    print(df_result.to_markdown(index=False))


def compare_general_files(file1, file2, output_file=None):
    # Read the two Markdown files and convert them to DataFrames
    df1 = pd.read_csv(file1, delimiter='|', skipinitialspace=True, engine='python', header=0, skiprows=[1])
    df2 = pd.read_csv(file2, delimiter='|', skipinitialspace=True, engine='python', header=0, skiprows=[1])

    # Remove extra columns that may have been misread
    df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
    df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]

    # Clean column names
    df1 = clean_column_names(df1)
    df2 = clean_column_names(df2)

    # Check if the required columns exist
    required_columns = ['Name', 'Description', 'Total Time(us)']
    for col in required_columns:
        if col not in df1.columns:
            print(f"Column {col} is missing in file1")
        if col not in df2.columns:
            print(f"Column {col} is missing in file2")
    
    # Convert the Total Time(us) columns to integer type
    df1['Total Time(us)'] = df1['Total Time(us)'].astype(int)
    df2['Total Time(us)'] = df2['Total Time(us)'].astype(int)
    
    # Extract file names without extensions for clearer column names
    file1_name = os.path.splitext(os.path.basename(file1))[0]
    file2_name = os.path.splitext(os.path.basename(file2))[0]
    
    # Merge the two DataFrames on Name and Description
    df_merged = pd.merge(df1, df2, on=['Name', 'Description'], suffixes=(f'_{file1_name}', f'_{file2_name}'))
    
    # Rename columns for clarity
    df_merged.rename(columns={
        f'Total Time(us)_{file1_name}': f'{file1_name} Total Time(us)',
        f'Total Time(us)_{file2_name}': f'{file2_name} Total Time(us)'
    }, inplace=True)
    
    # Calculate the difference and add a Difference(us) column
    df_merged['Difference(us)'] = df_merged[f'{file2_name} Total Time(us)'] - df_merged[f'{file1_name} Total Time(us)']
    
    # Sort the DataFrame by Difference(us) in descending order
    df_result = df_merged[['Name', 'Description', f'{file1_name} Total Time(us)', f'{file2_name} Total Time(us)', 'Difference(us)']]
    df_result = df_result.sort_values(by='Difference(us)', ascending=False)
    
    # Determine the output file name if not provided
    if output_file is None:
        output_file = f'comparison_General.md'
    
    # Output the result to a Markdown file
    save_as_markdown(df_result, output_file)
    print(f"Results have been saved to {output_file}")
    
    # Print the result to the console
    print(df_result.to_markdown(index=False))

if __name__ == "__main__":
    check_python_version()

    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python script.py <mode> <file1.md> <file2.md> [output_file.md]")
        sys.exit(1)

    mode = sys.argv[1]
    file1 = sys.argv[2]
    file2 = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) == 5 else None

    # Print file names for debugging
    print("Mode:", mode)
    print("File1:", file1)
    print("File2:", file2)
    print("Output File:", output_file if output_file else "Not provided, using default")

    try:
        if mode == "peims":
            compare_peims_files(file1, file2, output_file)
        elif mode == "drivers":
            compare_drivers_files(file1, file2, output_file)
        elif mode == "general":
            compare_general_files(file1, file2, output_file)
        elif mode == "major":
            compare_major_files(file1, file2, output_file)
        else:
            print("Invalid mode. Use 'peims', 'drivers', 'general', or 'major'.")
            sys.exit(1)
    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
