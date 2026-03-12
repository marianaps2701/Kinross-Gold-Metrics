# Kinross-Gold-Metrics

This project extracts and analyzes financial and market data for Kinross Gold using Python and the yfinance library. The script collects historical price data, trading volume, and fundamental financial indicators such as revenue, gross profit, net income, EBITDA, and shareholders’ equity. It then computes key financial metrics including returns and profitability margins (gross, operating, EBITDA, and net) and organizes the data into structured datasets (daily, monthly, quarterly, and annual). The final output is exported to an Excel file for further financial analysis and visualization.

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/kinross-gold-financial-metrics.git
```

Install the required libraries:

```bash
pip install pandas yfinance openpyxl
```

---

## Usage

Run the script:

```bash
python scriptDados.py
```

The program will automatically:

- Download financial and market data
- Calculate financial metrics
- Generate an Excel file containing all datasets

---

## Output

The script generates an Excel file containing structured financial data that can be used for:

- Financial analysis
- Valuation models
- Data visualization
- Further data processing

---

## Project Structure

```
kinross-gold-financial-metrics
│
├── scriptDados.py
├── kinross_gold_2020_2025.xlsx
└── README.md
```
