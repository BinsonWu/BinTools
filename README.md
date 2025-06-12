# My Tools

This repository contains tools I've written for:

- 🧾 Investment analysis
- 🖥️ BIOS and firmware utilities

## Structure
```
investment-tools/
├── stock-analyzer/
└── portfolio-tracker/

bios-tools/
├── bios-config-extractor/
└── firmware-checker/
```

## Naming Conventions

To keep this repository organized and consistent, the following naming rules are used:

| Scope               | Convention           | Example                   |
|---------------------|----------------------|---------------------------|
| Repository name     | kebab-case           | `my-tools`, `edk2-utils` |
| Folder name         | PascalCase or snake_case | `BiosTools/`, `investment_tools/` |
| File name (scripts) | snake_case (Python), PascalCase (EDK II-style tools) | `extract_fv.py`, `PatchDxe.py` |
| Class name          | PascalCase           | `class FirmwarePatcher:` |
| CLI command name    | kebab-case           | `extract-fv`, `bios-dump-parser` |

**Notes:**
- For BIOS/EDK II tools, PascalCase is preferred for file names and folder names to match community conventions.
- For general-purpose or Python tools, snake_case is acceptable for files and folders.

### Bitcoin Buy Signal Generator
- **Location**: `investment-tools/bitcoin-buy-signal`
- **Description**: A Python script that generates Bitcoin buy signals based on technical indicators (EMA, RSI, halving cycles) and calculates the return rate. Outputs include an Excel file with buy signals and a plot of price and RSI.
- **Details**: See [investment-tools/bitcoin-buy-signal/README.md](investment-tools/bitcoin-buy-signal/README.md)
