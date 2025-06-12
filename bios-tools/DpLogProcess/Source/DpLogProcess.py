import sys
import os
import subprocess
import shutil
from pathlib import Path
import platform

def run_script(script_path, *args):
    """Run a Python script with arguments and check for errors."""
    try:
        result = subprocess.run(
            [sys.executable, script_path, *args],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {script_path} encountered an issue.\n{e.stderr}")
        sys.exit(e.returncode)

def main():
    # Detect operating system
    os_name = platform.system()
    path_example = "C:\\Logs\\dp_log.log" if os_name == "Windows" else "/logs/dp_log.log"

    # Check if a log file parameter was provided
    if len(sys.argv) != 2:
        print("Error: No log file provided.")
        print(f"Usage: python {sys.argv[0]} LOG_FILE")
        print(f"Example: python {sys.argv[0]} {path_example}")
        sys.exit(1)

    log_file = sys.argv[1]
    # Validate log file extension
    if not log_file.lower().endswith('.log'):
        print("Error: Input file must be a .log file (EDKII Dp.efi log).")
        sys.exit(1)

    # Extract the base name of the log file without the extension
    base_name = Path(log_file).stem
    # Set the output and source folder paths
    output_folder = Path("Output") / base_name
    source_folder = Path("Source")

    # Create the output folder if it does not exist
    output_folder.mkdir(parents=True, exist_ok=True)

    # LogCapture
    print("Running LogCapture...")
    run_script(source_folder / "LogCapture.py", log_file)

    # Move the generated files to the output folder
    for file in ["Major.txt", "General.txt", "Drivers.txt", "PEIMs.txt"]:
        if os.path.exists(file):
            shutil.move(file, output_folder / f"{base_name}_{file}")
        else:
            print(f"Warning: {file} not found, skipping move.")

    print("LogCapture completed successfully.")

    # Process Major, Drivers, PEIMs, and General
    for section in ["Major", "Drivers", "PEIMs", "General"]:
        print(f"Processing {section}...")
        input_file = output_folder / f"{base_name}_{section}.txt"
        output_md = output_folder / f"{base_name}_{section}.md"
        if input_file.exists():
            run_script(source_folder / "ProcessData.py", str(input_file), "--output_md_file", str(output_md))
            print(f"ProcessData {section} completed successfully.")
        else:
            print(f"Error: {input_file} not found, skipping {section} processing.")

    # Combine md files to Excel
    print("Combining Markdown files to Excel...")
    excel_file = output_folder / f"{base_name}.xlsx"
    run_script(
        source_folder / "MdCombineToExcel.py",
        str(excel_file),
        str(output_folder / f"{base_name}_Major.md"), "Major",
        str(output_folder / f"{base_name}_Drivers.md"), "Drivers",
        str(output_folder / f"{base_name}_PEIMs.md"), "PEIMs",
        str(output_folder / f"{base_name}_General.md"), "General"
    )

    # Clean up temporary text files
    for txt_file in output_folder.glob("*.txt"):
        txt_file.unlink()
    print("Combine md files completed successfully.")

    print("Script completed successfully.")

if __name__ == "__main__":
    main()