# -*- coding: utf-8 -*-

import sys
import re
import argparse

def check_python_version():
    # Ensure the script is running with Python 3
    if sys.version_info[0] < 3:
        raise RuntimeError("This script requires Python 3.x")

def extract_sections(log_file_path):
    # Try reading the file with UTF-8 encoding, fall back to UTF-16 if there's a decode error
    try:
        with open(log_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        try:
            with open(log_file_path, 'r', encoding='utf-16') as file:
                content = file.read()
        except Exception as e:
            print(f"Error: Failed to read {log_file_path}. Ensure it is a valid EDKII Dp.efi log file in UTF-8 or UTF-16 encoding.\n{e}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to open {log_file_path}. Ensure the file exists and is accessible.\n{e}")
        sys.exit(1)

    # Define the section titles and their corresponding regular expressions
    sections = {
        "Major": r'==\[ Major Phases \]========(.*?)(?==\[|$)',
        "Drivers": r'==\[ Drivers by Handle \]========(.*?)(?==\[|$)',
        "PEIMs": r'==\[ PEIMs \]========(.*?)(?==\[|$)',
        "General": r'==\[ General \]========(.*?)(?==\[|$)'
    }

    # Check if any sections were found
    sections_found = False
    # Extract each section and write it to a corresponding .txt file
    for section, pattern in sections.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            sections_found = True
            section_content = match.group(1).strip()
            with open(f"{section}.txt", 'w', encoding='utf-8') as file:
                file.write(section_content)
        else:
            print(f"Warning: No content found for section '{section}' in {log_file_path}. Ensure the log contains '==[{section} ]========'.")

    if not sections_found:
        print(f"Error: No valid EDKII Dp.efi sections found in {log_file_path}. Expected sections: Major Phases, Drivers, PEIMs, General.")
        sys.exit(1)

if __name__ == "__main__":
    check_python_version()
    
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="Extract sections from an EDKII Dp.efi log file into separate .txt files.")
    parser.add_argument('log_file', type=str, help='Path to the EDKII Dp.efi .log file to process')
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Extract sections from the specified .log file
    extract_sections(args.log_file)