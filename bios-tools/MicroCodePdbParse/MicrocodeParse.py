import struct
import sys
import os
from collections import namedtuple

# Define the structures according to the given format

CPUMicrocodeDate = namedtuple('CPUMicrocodeDate', ['Year', 'Day', 'Month'])
CPUMicrocodeProcessorSignature = namedtuple('CPUMicrocodeProcessorSignature', ['Stepping', 'Model', 'Family', 'Type', 'Reserved1', 'ExtendedModel', 'ExtendedFamily', 'Reserved2'])
CPUMicrocodeHeader = namedtuple('CPUMicrocodeHeader', ['HeaderVersion', 'UpdateRevision', 'Date', 'ProcessorSignature', 'Checksum', 'LoaderRevision', 'ProcessorFlags', 'DataSize', 'TotalSize', 'Reserved'])

def check_python_version():
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required.")
        sys.exit(1)

def format_size(size_in_bytes):
    if size_in_bytes >= 1024 * 1024:
        return "{:d} MB".format(size_in_bytes // (1024 * 1024))
    elif size_in_bytes >= 1024:
        return "{:d} KB".format(size_in_bytes // 1024)
    else:
        return "{:d} B".format(size_in_bytes)

# Function to parse the PDB file
def parse_pdb_file(file_path):
    with open(file_path, 'rb') as file:
        # Read the binary data
        data = file.read()
        
        # Unpack the header
        header_format = '<I I I I I I I I I I I I 12s'
        unpacked_data = struct.unpack_from(header_format, data)
        
        # Parse the Date field
        date = CPUMicrocodeDate(
            Year=(unpacked_data[2]) & 0xFFFF,
            Day=(unpacked_data[2] >> 16) & 0xFF,
            Month=(unpacked_data[2] >> 24) & 0xFF
        )
        
        # Parse the ProcessorSignature field
        processor_signature = CPUMicrocodeProcessorSignature(
            Stepping=unpacked_data[3] & 0xF,
            Model=(unpacked_data[3] >> 4) & 0xF,
            Family=(unpacked_data[3] >> 8) & 0xF,
            Type=(unpacked_data[3] >> 12) & 0x3,
            Reserved1=(unpacked_data[3] >> 14) & 0x3,
            ExtendedModel=(unpacked_data[3] >> 16) & 0xF,
            ExtendedFamily=(unpacked_data[3] >> 20) & 0xFF,
            Reserved2=(unpacked_data[3] >> 28) & 0xF
        )
        
        # Create the CPUMicrocodeHeader
        header = CPUMicrocodeHeader(
            HeaderVersion=unpacked_data[0],
            UpdateRevision=unpacked_data[1],
            Date=date,
            ProcessorSignature=processor_signature,
            Checksum=unpacked_data[4],
            LoaderRevision=unpacked_data[5],
            ProcessorFlags=unpacked_data[6],
            DataSize=unpacked_data[7],
            TotalSize=unpacked_data[8],
            Reserved=unpacked_data[9]
        )
        
        return header

def print_microcode_header(header):
    print("CPUMicrocodeHeader:")
    print("HeaderVersion      = 0x{:08X}".format(header.HeaderVersion))
    print("UpdateRevision     = 0x{:08X}".format(header.UpdateRevision))
    
    print("CPUMicrocodeDate:")
    print("  Date             = {:04X}/{:02X}/{:02X}".format(header.Date.Year, header.Date.Day, header.Date.Month))
    
    print("ProcessorSignature:")
    print("  Stepping         = 0x{:01X}".format(header.ProcessorSignature.Stepping))
    print("  Model            = 0x{:01X}".format(header.ProcessorSignature.Model))
    print("  Family           = 0x{:01X}".format(header.ProcessorSignature.Family))
    print("  Type             = 0x{:01X}".format(header.ProcessorSignature.Type))
    print("  ExtendedModel    = 0x{:01X}".format(header.ProcessorSignature.ExtendedModel))
    print("  ExtendedFamily   = 0x{:02X}".format(header.ProcessorSignature.ExtendedFamily))
    
    print("Checksum           = 0x{:08X}".format(header.Checksum))
    print("LoaderRevision     = 0x{:08X}".format(header.LoaderRevision))
    print("ProcessorFlags     = 0x{:08X}".format(header.ProcessorFlags))
    print("DataSize           = 0x{:08X} ({})".format(header.DataSize, format_size(header.DataSize)))
    print("TotalSize          = 0x{:08X} ({})".format(header.TotalSize, format_size(header.TotalSize)))

def process_pdb_file(file_path):
    microcode_header = parse_pdb_file(file_path)
    print_microcode_header(microcode_header)

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and file_path.lower().endswith('.pdb'):
            print(f"\nProcessing {file_path}...")
            process_pdb_file(file_path)
        else:
            print(f"Skipping {file_path}, not a PDB file.")

if __name__ == "__main__":
    check_python_version()
    
    if len(sys.argv) != 2:
        print("Usage: python MicrocodeParse.py <absolute_path_to_pdb_file_or_folder>")
        sys.exit(1)
    
    path = sys.argv[1]
    if os.path.isfile(path) and path.lower().endswith('.pdb'):
        process_pdb_file(path)
    elif os.path.isdir(path):
        process_folder(path)
    else:
        print("Error: The specified path is neither a PDB file nor a folder.")
        sys.exit(1)
