import sys
import os
import subprocess
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
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {script_path} failed with exit code {e.returncode}.\n{e.stderr}")
        raise  # Re-raise the exception to stop execution

def main():
    # Detect operating system
    os_name = platform.system()
    path_example = "C:\\Logs\\dp_log1.log C:\\Logs\\dp_log2.log" if os_name == "Windows" else "/logs/dp_log1.log /logs/dp_log2.log"

    # Usage instructions
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} LOG_FILE_1 LOG_FILE_2")
        print("\nLOG_FILE_1 - Path to the first EDKII Dp.efi log file.")
        print("LOG_FILE_2 - Path to the second EDKII Dp.efi log file.")
        print(f"\nExample: python {sys.argv[0]} {path_example}")
        sys.exit(1)

    log_file_1 = sys.argv[1]
    log_file_2 = sys.argv[2]

    # Validate log file extensions
    for log_file in [log_file_1, log_file_2]:
        if not log_file.lower().endswith('.log'):
            print(f"Error: {log_file} must be a .log file (EDKII Dp.efi log).")
            sys.exit(1)

    # Extract the base names of the log files without extensions
    base_name_1 = Path(log_file_1).stem
    base_name_2 = Path(log_file_2).stem

    # Set the output and source folder paths
    output_folder = Path("Output")
    output_folder_1 = output_folder / base_name_1
    output_folder_2 = output_folder / base_name_2
    source_folder = Path("Source")

    # Create output folders if they do not exist
    output_folder_1.mkdir(parents=True, exist_ok=True)
    output_folder_2.mkdir(parents=True, exist_ok=True)

    # Process LOG_FILE_1
    print(f"------ Processing {log_file_1} ------")
    run_script(source_folder / "DpLogProcess.py", log_file_1)
    print(f"Processing {log_file_1} completed successfully.")

    # Process LOG_FILE_2
    print(f"------ Processing {log_file_2} ------")
    run_script(source_folder / "DpLogProcess.py", log_file_2)
    print(f"Processing {log_file_2} completed successfully.")

    # Compare Major, Drivers, PEIMs, and General
    for section, mode in [("Major", "major"), ("Drivers", "drivers"), ("PEIMs", "peims"), ("General", "general")]:
        print(f"------ Comparing {section} ------")
        file1 = output_folder_1 / f"{base_name_1}_{section}.md"
        file2 = output_folder_2 / f"{base_name_2}_{section}.md"
        output_md = output_folder / f"{base_name_1}_{base_name_2}_{section}.md"
        try:
            run_script(source_folder / "CompareTime.py", mode, str(file1), str(file2), str(output_md))
            print(f"Comparing {section} completed successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to compare {section}. Check the input Markdown files and try again.")
            sys.exit(1)

    # Combine all md files to Excel
    print("------ Combine All ------")
    excel_file = output_folder / f"{base_name_1}_{base_name_2}.xlsx"
    run_script(
        source_folder / "MdCombineToExcel.py",
        str(excel_file),
        str(output_folder / f"{base_name_1}_{base_name_2}_Major.md"), "Major",
        str(output_folder / f"{base_name_1}_{base_name_2}_Drivers.md"), "Drivers",
        str(output_folder / f"{base_name_1}_{base_name_2}_PEIMs.md"), "PEIMs",
        str(output_folder / f"{base_name_1}_{base_name_2}_General.md"), "General"
    )

    # Clean up temporary Markdown files
    for md_file in [
        output_folder / f"{base_name_1}_{base_name_2}_Major.md",
        output_folder / f"{base_name_1}_{base_name_2}_Drivers.md",
        output_folder / f"{base_name_1}_{base_name_2}_PEIMs.md",
        output_folder / f"{base_name_1}_{base_name_2}_General.md"
    ]:
        if md_file.exists():
            md_file.unlink()
    print("Combine md files completed successfully.")

    print("Script completed successfully.")

if __name__ == "__main__":
    main()