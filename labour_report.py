from openpyxl import load_workbook    # top of file, with the other imports
# ... copy load_sheet in, with its comments ...

def load_sheet(path):   # Pattern: TRANSFORM (rows → dicts) + ACCUMULATE
    # in: path to an .xlsx (first row = header) → out: list of dicts, one per data row
    # 1. open the workbook and take the active sheet
    wb = load_workbook(path)
    ws = wb.active
    # 2. read all rows into a list
    rows = list(ws.iter_rows(values_only=True))
    # 3. first row = header (the keys)
          # 3. first row = header (the keys), cleaned of stray spaces
    header = [name.strip() for name in rows[0]]
    # 4. start an empty result list
    result = []
    # 5. loop over every row after the header
    for row in rows[1:]:
        # 6. pair header with the row → dict, append to result
        result.append(dict(zip(header, row)))
    # 7. return result
    return result

hourly = load_sheet('data/hourly_sheet.xlsx')
print(len(hourly))      # expect 12
print(hourly[0]['hour'])        # check: 9 keys, all spelled right, no None key
print(hourly[3])        # 14:00 → expect pizzas_actual None, driver_actual_hours None

def pizzas_target_vs_actual(hourly):   # Pattern: FILTER + TRANSFORM
    # in: hourly rows (list of dicts) → out: {hour: actual - target} for complete hours, list of hours with missing data
    # 1. start an empty dict (diffs) and an empty list (missing)
    diffs = {}
    missing = []
    # 2. loop over each row in hourly
    for row in hourly:
        hour = row['hour']
        target = row['pizzas_target']
        actual = row['pizzas_actual']
    # 3.if pizzas_actual or pizzas_target is empty → add the hour to missing, skip to next row
        if target is None or  actual is None:
            missing.append(hour)
            continue
        # 4.   otherwise work out actual - target
        diffs[hour] = actual - target
        # 5.   store it in diffs under that hour
        # 6. return diffs and missing
    return diffs, missing        

diffs, missing = pizzas_target_vs_actual(hourly)
print(len(diffs))      # expect 11
print(diffs[11], diffs[13])   # expect 2 -6
print(missing)         # expect [14]