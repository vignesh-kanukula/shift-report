from openpyxl import load_workbook  
import json  
import os 
def load_sheet(path):   # Pattern: TRANSFORM (rows → dicts) + ACCUMULATE
    # in: path to an .xlsx (first row = header) → out: list of dicts, one per data row
    # 1. open the workbook and take the active sheet
    wb = load_workbook(path)
    ws = wb.active
    # 2. read all rows into a list
    rows = list(ws.iter_rows(values_only=True))
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

# PREDICT: len(pizza_diffs) = 11, pizza_missing = [14]
# PREDICT: len(delivery_diffs) = 12, delivery_missing = []
def target_vs_actual(hourly, target_key, actual_key):   # Pattern: FILTER + TRANSFORM
    # in: any target/ actual pair of columuns → out: {hour: actual - target} for complete hours, list of hours with missing data
    # 1. start an empty dict (diffs) and an empty list (missing)
    diffs = {}
    missing = []
    # 2. loop over each row in hourly
    for row in hourly:
        hour = row['hour']
        target = row[target_key]
        actual = row[actual_key]
        # if target or actual is empty → add the hour to missing, skip
        if target is None or  actual is None:
            missing.append(hour)
            continue
        # 4.   otherwise work out actual - target
        # 5.   store it in diffs under that hour

        diffs[hour] = actual - target
    # 6. return diffs and missing
    return diffs, missing    


def count_on_target(diffs): # pattern : FILTER + COUNT
    return len([d for d in diffs.values() if d >= 0])

def off_roster(diffs):
    return [f"{h}:00 ({d:+d})" for h, d in diffs.items() if d != 0]

def worst_key(values):   # Pattern: BEST SO FAR (lowest)
    # in: any {key: number} dict → out: the key with the smallest number
    worst = None
    worst_value = 0
    for key, value in values.items():
        if worst is None or value < worst_value:
            worst_value = value
            worst = key
    return worst

def build_summary(hourly):   # Pattern: TRANSFORM (calculations → one dict)
    # in: list of hourly rows → out: one dict of every number the report needs
    # 1. calculate the pieces once
    pizza_diffs, pizza_missing = target_vs_actual(hourly, 'pizzas_target', 'pizzas_actual')
    delivery_diffs, delivery_missing = target_vs_actual(hourly, 'delivery_target', 'delivery_actual')
    instore_diffs, instore_missing = target_vs_actual(hourly, 'instore_rostered', 'instore_actual_hours')
    driver_diffs, driver_missing = target_vs_actual(hourly, 'driver_rostered', 'driver_actual_hours')  
    worst_pizza = worst_key(pizza_diffs)
    worst_delivery = worst_key(delivery_diffs)
    

    summary = {
        'pizzas_on_target': count_on_target(pizza_diffs),
        'pizza_hours': len(pizza_diffs),
        'pizza_missing': pizza_missing,
        'worst_pizza_hour': worst_pizza,
        'worst_pizza_diff': pizza_diffs[worst_pizza],
        'deliveries_on_target': count_on_target(delivery_diffs),
        'delivery_hours':len(delivery_diffs),
        'delivery_missing': delivery_missing,
        'worst_delivery_hour': worst_delivery,
        'worst_delivery_diff': delivery_diffs[worst_delivery],
        'instore_off_roster': off_roster(instore_diffs),
        'instore_missing': instore_missing,
        'drivers_off_roster': off_roster(driver_diffs),
        'driver_missing': driver_missing,
        'pizza_diffs': pizza_diffs,
        'delivery_diffs': delivery_diffs,
    }
    return summary    

def save_json(summary, path):      
# in: summary dict + path → out: JSON file at path, returns None              
    with open(path, 'w') as file:
        json.dump(summary, file, indent=2)


def print_report(summary):
    s = summary
    print(f'SPACE PIZZA - Hourly Targets (11:00-22:00)')
    print(f'Pizzas on/above target: {s['pizzas_on_target']} of {s['pizza_hours']} hours (missing: {', '.join(f"{h}:00" for h in s['pizza_missing'])})')
    print(f'Deliveries on/above target: {s['deliveries_on_target']} of {s['delivery_hours']} hours')
    print(f'Worst pizza hour: {s['worst_pizza_hour']}:00 ({s['worst_pizza_diff']})')
    print(f'Worst delivery hour: {s['worst_delivery_hour']}:00 ({s['worst_delivery_diff']})')
    print(f'Instore off roster: {', '.join(s['instore_off_roster'])}')
    print(f'Drivers off roster: {', '.join(s['drivers_off_roster'])} (missing: {', '.join(f'{h}:00' for h in s['driver_missing'])})')

def main():
    os.makedirs('reports', exist_ok=True)
    hourly = load_sheet('data/hourly_sheet.xlsx')
    summary = build_summary(hourly)
    save_json(summary, 'reports/labour_summary.json')
    print_report(summary)

main()