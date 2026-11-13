from openpyxl import load_workbook
# one record = one DAY
# keys come from columns_names(column B), day names from rows (row r6)
# the table is rows 6 to 14, columns B to I
# skip: rows 1-5 (title), column A (empty), column J (Week to Date total)
# empty day means: Actual sales is None

# wb = load_workbook('data/monthly_summary.xlsx', data_only=True)
# ws = wb['W1']
# grid = list(ws.iter_rows(min_row=6, max_row=14, min_col=2, max_col=9, values_only=True))
# print(grid[0])                     # ('Metric', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
# print(grid[1])                     # ('Actual Sales', 1963, 2020, 2144, 1592, 3987, 3851, 3614)
# print(len(grid), len(grid[0]))     # 9 8

# records = []
# for c in range(1, len(grid[0])):
#     record = {'day': grid[0][c]}
#     for r in range(1, len(grid)):
#         record[grid[r][0]] = grid[r][c]
#     records.append(record)

# print(len(records))     
# print(records[0])       
# print(sum(r['Actual Sales'] for r in records))   # expect 19171

# IN : one tab at time (worksheet)
# out : list of record days, skip empty days and count 

def load_week(ws):   # Pattern: TRANSFORM (wide → long) + FILTER + COUNT
    # in: one worksheet (one week tab) → out: list of day-records (empty days skipped), number of days skipped
    grid = list(ws.iter_rows(min_row=6, max_row=14, min_col=2, max_col=9, values_only=True))
    records = []
    skipped = 0
    for c in range(1,len(grid[0])):
        record = {'day': grid[0][c]}
        for r in range(1, len(grid)):
            record[grid[r][0]] = grid[r][c]
        if record['Actual Sales'] is None :
            skipped += 1
            continue
        records.append(record)
            
    return records, skipped

wb = load_workbook('data/monthly_summary.xlsx', data_only=True)
records,skipped = load_week(wb['W1'])

records, skipped = load_week(wb['W1'])
print(len(records), skipped)    # expect 7 0
records, skipped = load_week(wb['W5'])
print(len(records), skipped)    # expect 3 4
        