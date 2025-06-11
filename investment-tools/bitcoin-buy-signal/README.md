# Bitcoin Buy Signal Generator

This project, part of the `BinTools` repository, generates buy signals for Bitcoin (BTC) based on technical indicators and market conditions. It calculates the return rate by comparing today's price to the average buy price and visualizes the results. The script is written in Python and uses `yfinance` to fetch BTC-USD historical price data.

## Features

- **Buy Signal Generation**: Identifies buy points based on five conditions:
  - Proximity to Bitcoin halving (~500 days before, ±30 days).
  - Recent death cross (100-day EMA crossing below 200-day EMA within 10 days).
  - Price in the rainbow chart bottom (below 80% of 200-day EMA).
  - Date in Q2 (April-June).
  - RSI below 30 (oversold).
- **Return Rate Calculation**: Computes the return rate as `(today's price - average buy price) / average buy price * 100`.
- **Outputs**:
  - Excel file (`output/bitcoin_buy_signals.xlsx`) with buy signals and investment summary.
  - Plot (`output/bitcoin_plot.png`) showing BTC price, EMAs, buy signals, and RSI.
- **Automatic Halving Dates**: Generates approximate halving dates every ~1,460 days starting from 2012-11-28.

## Prerequisites

- Python 3.7+
- Internet connection for fetching data via `yfinance`
- Required Python packages (listed in `requirements.txt`)

## Installation

1. Navigate to the project directory in the `BinTools` repository:

   ```bash
   cd investment-tools/bitcoin-buy-signal
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:

   ```bash
   python src/bitcoin_buy_signal_custom.py
   ```

2. The script will:

   - Fetch BTC-USD data from 2018-01-01 to today (2025-06-11).
   - Generate buy signals (requiring at least 2 conditions).
   - Calculate the return rate based on 306 buy signals (as of 2025-06-11, today's price: $105,793.65).
   - Save results to `output/bitcoin_buy_signals.xlsx` and `output/bitcoin_plot.png`.

3. Check the console for:

   - Generated halving dates.
   - Today’s buy point status (e.g., “Is today (2025-06-11) a buy point? Yes/No”).
   - Investment summary (e.g., Total Buy Points: 306, Average Buy Price, Today’s Price, Return Rate).

## Output Files

- **output/bitcoin_buy_signals.xlsx**:
  - **Buy_Signals Sheet**: Table with 306 buy signals (Date, Close, EMA_100, EMA_200, RSI).
  - **Investment Summary**: Total Buy Points, Average Buy Price, Today’s Price, Total Return Rate.
- **output/bitcoin_plot.png**:
  - Top: BTC price with 100-day and 200-day EMAs, marked buy signals.
  - Bottom: RSI with oversold threshold (30).

## Customization

Edit `src/bitcoin_buy_signal_custom.py` to modify:

- `start_date`: Change to `'2020-01-01'` for a shorter dataset.
- `min_conditions`: Set to `3` for stricter buy signals.
- `threshold`: Adjust to `0.9` in `is_in_rainbow_bottom` for a different rainbow chart threshold.
- `rsi`: Change `< 30` to `< 25` for stronger oversold signals.
- Output paths: Modify `excel_file` or `plot_file`.

## Notes

- **Return Rate**: Assumes equal investment per buy point, held until today. Ignores fees, taxes, or sales.
- **Halving Dates**: Approximated (1,460 days). Actual dates (e.g., 2024-04-20) may differ.
- **Data**: Uses `yfinance`, which may lack data for today. If so, try setting `end_date` to yesterday.
- **Risk**: For educational purposes only. Consider macroeconomic factors before trading.
- **Backtesting**: Validate signals historically before use.

## Dependencies

See `requirements.txt`:

```
yfinance
pandas
matplotlib
numpy
openpyxl
```

## License

MIT License (see root `BinTools` repository for details).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request in the `BinTools` repository.

## Contact

For questions, open an issue on GitHub or contact the repository owner.