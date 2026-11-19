# SPACE PIZZA – Shift & Labour Reports

**Problem:** 
In a busy pizza store, it's hard to find out where labour is over used or where under used -- hourly numbers are written by hand and monthly numbers sit in an awkward Excel layout 

**What it does:** 
Python tools that turn orders, shifts and excel sheets into three reports -- a daily shift report, an hourly target vs actual report, and a monthly labour report -- saved as CSV and JSON.

**The data:** 
The data used for this project is made up data, but modelled on real store layouts: a hand-written houlry sheet and five-tab monthly workbook with days as columns.

## Reports

### 1. Daily shift report (`shift_report.py`)
In: `data/orders.csv` + `data/shifts.csv` → Out: printed report, `reports/hourly.csv`, `reports/summary.json`
Handles messy rows: missing price (skipped and counted), missing clock-out (flagged).

### 2. Hourly targets (`labour_report.py`) — in progress
In: `data/hourly_sheet.xlsx` → Out: pizzas actual vs target for each hour.
Hours with missing data are listed separately instead of being silently dropped.

### 3. Monthly labour report (`monthly_report.py`)
In: `data/monthly_summary.xlsx` (5 tabs, days as columns) → Out: printed report + `reports/monthly_summary.json`
Reshapes the wide weekly tabs into 31 daily records. Labour % is weighted by sales: a simple average says 22.52%, but quiet days count as much as busy ones — weighted, the true figure is 22.37%.

## How to run
From inside the `shift_report` folder:
```
pip install openpyxl
python shift_report.py
python labour_report.py
python monthly_report.py
```

## Next steps
- Pilot on real data (with a manager's approval)
- Add SQL