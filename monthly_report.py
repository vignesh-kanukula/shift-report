from openpyxl import load_workbook
import json
import os
# one record = one DAY
# keys come from columns_names(column B), day names from rows (row r6)
# the table is rows 6 to 14, columns B to I
# skip: rows 1-5 (title), column A (empty), column J (Week to Date total)
# empty day means: Actual sales is None

# IN : one tab at time (worksheet)
# out : list of record days, skip empty days and count 

def load_week(ws):   # Pattern: TRANSFORM (wide → long) + FILTER + COUNT
    # in: one worksheet (one week tab) → out: list of day-records (empty days skipped), number of days skipped
    # crop the table (rows 6-14, columns B-I) into a grid
    grid = list(ws.iter_rows(min_row=6, max_row=14, min_col=2, max_col=9, values_only=True))
    # start an empty records list and skipped = 0
    records = []
    skipped = 0
    # loop over every day column (width = len(grid[0]))
    for c in range(1, len(grid[0])):
        # start a new record with the day name from grid[0]
        record = {'day': grid[0][c]}
        # loop over every metric row, store label → value
        for r in range(1, len(grid)):
            record[grid[r][0]] = grid[r][c]
        # if the day's Actual Sales is None → add 1 to skipped, skip to next day
        if record['Actual Sales'] is None:
            skipped += 1
            continue
        # otherwise append the record
        records.append(record)
    # return records and skipped
    return records, skipped


def load_monthly_summary(path):   # Pattern: ACCUMULATE (combine weeks) + TRANSFORM (add week)
    # in: path to the monthly workbook → out: list of all day-records, total days skipped
    # 1. open the workbook (data_only=True, so formulas give numbers)
    wb = load_workbook(path, data_only=True )
    # 2. start an empty all_records list and total_skipped = 0
    all_records = []
    total_skipped = 0
    # 3. loop over every tab name in the workbook
    for name in wb.sheetnames:
        # 4.   get this tab's records and skipped count from load_week
        records, skipped = load_week(wb[name])
        # 5.   stamp each record with the tab name under 'week'
        for record in records:
            record['week'] = name
        # 6.   add this tab's records to all_records (extend)
        all_records.extend(records)
        
        # 7.   add this tab's skipped to total_skipped
        total_skipped += skipped
    # 8. return all_records and total_skipped
    return all_records, total_skipped

def days_over_labour(all_records): # pattern :  FILTER
    # in: list of day-records → out: list of (week, day) where actual labour % > budgeted
    # 1. start an empty list
    over_used = []
     # 2. loop over every day-record
    for record in all_records:
    # 3.   if actual labour % is above budget → add (week, day)
        if record['Actual Labour %'] > record['Budgeted Labour %']:
            over_used.append((record['week'], record['day']))
        # 4. return the list
    return over_used

def monthly_labour_pct(all_records): # pattern : ACCUMULATE  (weighted average)
    # in: list of day-records OUT : monthly labour %(weigthed by sales)
    # 1. start 2 totals at 0: labour € and sales € 
    total_labour = 0
    total_sales = 0
    # 2 loop over day-records 
    for record in all_records:
        sales = record['Actual Sales']
        labour = record['Actual Labour %']
        # 3. after the loop: labour € ÷ sales € × 100
        total_sales += sales
        total_labour += sales * labour
    #return final count
    return round(total_labour/total_sales * 100, 2)

def sales_by_day(records):   # Pattern: TRANSFORM (list of records → dict)
    # in: list of day-records → out: {'W1 Mon': sales, ...}
    # 1. start an empty dict
    sales_day = {}
    # 2. loop over every record
    for record in records:
        # 3.   build the key from week + day
        key = f"{record['week']} {record['day']}"     # → 'W1 Mon'
        sales = record['Actual Sales']
        # 4.   store that day's Actual Sales under the key
        sales_day[key] = sales
     # 5. return the dict
    return sales_day

def worst_key(values):# pattern : WORST SO FAR (LOWEST)
    # in: any {key: number} dict → out: the key with the smallest number
    worst = None
    worst_day_sales = 0
    for day, sales in values.items():
        if worst is None or sales < worst_day_sales:
            worst_day_sales = sales
            worst = day
    return worst

def best_key(values):   # Pattern: BEST SO FAR (highest)
    # in: any {key: number} dict → out: the key with the biggest number
    best = None
    best_value = 0
    for key, value in values.items():
        if value > best_value:
            best_value = value
            best = key
    return best

def simple_labour_pct(records): # pattern : ACCUMULATE
    # IN : list of day records , OUT : daily labour % 
    # 1. add up every day's labour % (no sales involved)
    total_pct = sum(r['Actual Labour %'] for r in records)
     # 2. divide by how many days
    # 3. turn the fraction into a percentage, 2 decimals
    return round(total_pct / len(records) * 100, 2)
 

def build_monthly_summary(records, skipped):   # Pattern: TRANSFORM (calculations → one dict)
    # in: list of day-records + skipped count → out: one dict of headline numbers
    # 1. calculate the pieces once
    sales = sales_by_day(records)
    best = best_key(sales)
    worst = worst_key(sales)
    total_sales = sum(r['Actual Sales'] for r in records)
    total_budget = sum(r['Budgeted Sales'] for r in records)
    # 2. package them into one dict
    summary = {
        'days_loaded': len(records),
        'skipped': skipped,
        'total_sales': total_sales,
        'total_budget': total_budget,
        'vs_budget': total_sales - total_budget,
        'best_day': best,
        'best_day_sales': sales[best],
        'worst_day': worst,
        'worst_day_sales': sales[worst],
        'labour_pct': monthly_labour_pct(records),
        'simple_labour_pct': simple_labour_pct(records),
        'days_over_labour': len(days_over_labour(records)),
    }
    return summary

def save_json(summary, path):      
# in: summary dict + path → out: JSON file at path, returns None              
    with open(path, 'w') as file:
        json.dump(summary, file, indent=2)

def print_monthly_report(summary):
    s = summary
    print(f"SPACE PIZZA - Monthly Report (W1-W5)")
    print(f'Days loaded: {s['days_loaded']} ({s['skipped']} empty days skipped)')
    print(f'Total sales: {s['total_sales']:,.0f} vs budget {s['total_budget']:,.0f} ({s['vs_budget']:+,.0f})')
    print(f'Best day: {s['best_day']} ({s['best_day_sales']:,.0f})')
    print(f'Worst day: {s['worst_day']} ({s['worst_day_sales']:,.0f})')
    print(f'Labour %: {s['labour_pct']} (weighted by sales; simple average {s['simple_labour_pct']})')
    print(f'Days over labour target: {s['days_over_labour']}')

def main():
    os.makedirs('reports', exist_ok=True)
    all_records, skipped = load_monthly_summary('data/monthly_summary.xlsx')
    summary = build_monthly_summary(all_records, skipped)
    save_json(summary, 'reports/monthly_summary.json')
    print_monthly_report(summary)

main()
