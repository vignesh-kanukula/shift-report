from openpyxl import load_workbook
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


wb = load_workbook('data/monthly_summary.xlsx', data_only=True)
records, skipped = load_week(wb['W1'])
print(len(records), skipped)    # expect 7 0
records, skipped = load_week(wb['W5'])
print(len(records), skipped)    # expect 3 4

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

all_records, skipped = load_monthly_summary('data/monthly_summary.xlsx')
print(len(all_records), skipped)                          # expect 31 4
print(all_records[0]['week'], all_records[0]['day'])      # expect W1 Mon
print(all_records[-1]['week'], all_records[-1]['day'])    # expect W5 Wed
print(sum(r['Actual Sales'] for r in all_records))        # expect 77696
    
