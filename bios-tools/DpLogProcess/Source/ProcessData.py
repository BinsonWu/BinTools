# -*- coding: utf-8 -*-

import sys
import argparse
import re
import pandas as pd
from collections import defaultdict

# Check for Python 3.x
if sys.version_info[0] != 3:
    print("This script requires Python 3.x.")
    sys.exit(1)

def process_peims_data(input_file, output_md_file='output.md'):
    # Read the data
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Clean the data, removing the Index and Token columns
    data = []
    for line in lines:
        # Skip header lines and separators
        if line.startswith('Index') or '----' in line or line.startswith('==['):
            continue
        
        # Use regular expression to extract Instance GUID and Time(us)
        match = re.match(r'\s*\d+:\s+(\S+)\s+\S+\s+(\d+)', line.strip())
        if match:
            instance_guid = match.group(1).strip()
            time_us = int(match.group(2).strip())
            data.append([instance_guid, time_us])
    
    # Merge rows with the same Instance GUID
    merged_data = defaultdict(lambda: [0, 0, []])  # [Total Time, Merge Count, Original Times]
    for instance_guid, time_us in data:
        merged_data[instance_guid][0] += time_us
        merged_data[instance_guid][1] += 1
        merged_data[instance_guid][2].append(time_us)
    
    # Convert the results to a list and sort by Total Time(us)
    sorted_data = sorted(merged_data.items(), key=lambda x: x[1][0], reverse=True)
    
    # Output as Markdown table
    with open(output_md_file, 'w') as file:
        file.write('| Instance GUID | Total Time(us) | Call Count | Time(us) |\n')
        file.write('|---------------|----------------|-------------|----------|\n')
        for instance_guid, (total_time_us, merge_count, times) in sorted_data:
            times_str = ', '.join(map(str, times))
            file.write(f'| {instance_guid} | {total_time_us} | {merge_count} | {times_str} |\n')
    
    print(f'Markdown file saved to: {output_md_file}')

def process_drivers_data(input_file, output_md_file='output.md'):
    # Read the data
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Clean the data, removing unnecessary rows and columns
    data = []
    for line in lines:
        # Skip header lines and separators
        if line.startswith('Index:') or 'Handle' in line or '----' in line:
            continue
        
        # Use regular expression to split Driver Name and Description
        match = re.match(r'\d+:  \[.\S*?\]\s+(.*?)\s{4,}(.*)\s+(\d+)', line.strip())
        if match:
            driver_name = match.group(1).strip()
            description = match.group(2).strip()
            time_us = int(match.group(3).strip())
            data.append([driver_name, description, time_us])
    
    # Merge rows with the same Driver Name and Description
    merged_data = defaultdict(lambda: [0, 0, []])  # [Total Time, Merge Count, Original Times]
    for driver_name, description, time_us in data:
        merged_data[(driver_name, description)][0] += time_us
        merged_data[(driver_name, description)][1] += 1
        merged_data[(driver_name, description)][2].append(time_us)
    
    # Convert the results to a list and sort by Total Time(us)
    sorted_data = sorted(merged_data.items(), key=lambda x: x[1][0], reverse=True)
    
    # Output as Markdown table
    with open(output_md_file, 'w') as file:
        file.write('| Driver Name | Description | Total Time(us) | Call Count | Time(us) |\n')
        file.write('|-------------|-------------|----------------|-------------|----------|\n')
        for (driver_name, description), (total_time_us, merge_count, times) in sorted_data:
            times_str = ', '.join(map(str, times))
            file.write(f'| {driver_name} | {description} | {total_time_us} | {merge_count} | {times_str} |\n')
    
    print(f'Markdown file saved to: {output_md_file}')

def process_general_data(input_file, output_md_file='output.md'):
    # Read the data
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Clean the data, removing the Index column
    data = []
    for line in lines:
        # Skip header lines and separators
        if line.startswith('Index') or '----' in line:
            continue
        
        # Use regular expression to extract Name, Description, and Time(us)
        match = re.match(r'\s*\d+:\s*(.*?)\s{4,}(.*?)\s+(\d+)', line.strip())
        if match:
            name = match.group(1).strip()
            description = match.group(2).strip()
            time_us = int(match.group(3).strip())
            data.append([name, description, time_us])
    
    # Merge rows with the same Name and Description
    merged_data = defaultdict(lambda: [0, 0, []])  # [Total Time, Merge Count, Original Times]
    for name, description, time_us in data:
        merged_data[(name, description)][0] += time_us
        merged_data[(name, description)][1] += 1
        merged_data[(name, description)][2].append(time_us)
    
    # Convert the results to a list and sort by Total Time(us)
    sorted_data = sorted(merged_data.items(), key=lambda x: x[1][0], reverse=True)
    
    # Output as Markdown table
    with open(output_md_file, 'w') as file:
        file.write('| Name | Description | Total Time(us) | Call Count | Time(us) |\n')
        file.write('|------|-------------|----------------|-------------|----------|\n')
        for (name, description), (total_time_us, merge_count, times) in sorted_data:
            times_str = ', '.join(map(str, times))
            file.write(f'| {name} | {description} | {total_time_us} | {merge_count} | {times_str} |\n')
    
    print(f'Markdown file saved to: {output_md_file}')

def process_major_data(input_file, output_md_file='output.md'):
    # Read the data
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    # Define a dictionary to store the durations
    durations = {
        'Reset End': None,
        'SEC Phase Duration': None,
        'PEI Phase Duration': None,
        'DXE Phase Duration': None,
        'BDS Phase Duration': None,
        'Total Duration': None
    }
    
    # Regular expressions to match values
    value_pattern = re.compile(r'(\d+)\s*\(?(us|ms)?\)?')
    
    # Parse the durations from the lines
    for line in lines:
        line = line.strip()
        match = value_pattern.search(line)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            
            if 'Reset End' in line:
                durations['Reset End'] = value
            elif 'SEC Phase Duration' in line:
                durations['SEC Phase Duration'] = value
            elif 'PEI Phase Duration' in line:
                durations['PEI Phase Duration'] = value * 1000 if unit == 'ms' else value
            elif 'DXE Phase Duration' in line:
                durations['DXE Phase Duration'] = value * 1000 if unit == 'ms' else value
            elif 'BDS Phase Duration' in line:
                durations['BDS Phase Duration'] = value * 1000 if unit == 'ms' else value
            elif 'Total       Duration' in line:
                durations['Total Duration'] = value * 1000 if unit == 'ms' else value

    # Convert the results to a list
    data = [
        ['Reset End', durations['Reset End']],
        ['SEC Phase Duration', durations['SEC Phase Duration']],
        ['PEI Phase Duration', durations['PEI Phase Duration']],
        ['DXE Phase Duration', durations['DXE Phase Duration']],
        ['BDS Phase Duration', durations['BDS Phase Duration']],
        ['Total Duration', durations['Total Duration']]
    ]
    
    # Output as Markdown table
    with open(output_md_file, 'w') as file:
        file.write('| Phase | Duration (us) |\n')
        file.write('|-------|---------------|\n')
        for phase, duration in data:
            file.write(f'| {phase} | {duration} |\n')
    
    print(f'Markdown file saved to: {output_md_file}')

def determine_and_process_file(input_file, output_md_file='output.md'):
    with open(input_file, 'r') as file:
        first_line = file.readline().strip()
    
    # Check for PEIMs format
    if "Instance GUID" in first_line:
        process_peims_data(input_file, output_md_file)
    # Check for Drivers format
    elif "Driver Name" in first_line:
        process_drivers_data(input_file, output_md_file)
    elif "Name" in first_line:
        process_general_data(input_file, output_md_file)
    elif "Reset End" in first_line:
        process_major_data(input_file, output_md_file)
    else:
        print("The input file format is not recognized.")
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process data from a TXT file and output to a Markdown file.')
    parser.add_argument('input_file', type=str, help='Input TXT file with data')
    parser.add_argument('--output_md_file', type=str, default='output.md', help='Output Markdown file (default: output.md)')
    
    args = parser.parse_args()
    determine_and_process_file(args.input_file, args.output_md_file)
