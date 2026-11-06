# orders.csv line 13 - price col is missing
# shifts.csv line 6 - driver end col is missing

import csv
from datetime import datetime, date

def safe_float(text):
    try:
        return float(text)
    except ValueError:
        return None

def load_orders(path):
    good_orders = []
    count = 0
    with open(path) as file:
        reader = csv.DictReader(file)
        for row in reader:
            price = safe_float(row.get('price', ''))
            qty = safe_float(row['qty'])
            if price is None or qty is None :
                count += 1
            else:
                row['price'] = price
                row['qty'] = int(row['qty'])
                good_orders.append(row)
        return good_orders, count

# orders, skipped = load_orders('data/orders.csv')
# print(len(orders), skipped)      # expected: 17 1

def parse_time(text):
    return datetime.strptime(text, '%Y-%m-%d %H:%M')

def load_shifts(path):
    good_shifts = []
    flagged = []
    with open(path) as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['end'] == '':
               flagged.append(row['staff_id'])
            else:
               row['start'] = parse_time(row['start'])
               row['end']  = parse_time(row['end'])
               good_shifts.append(row)

        return good_shifts, flagged
    
# shifts, flagged = load_shifts('data/shifts.csv')
# print(len(shifts), flagged)               # expected: 5 ['S5']
# print(shifts[0]['start'].hour)            # expected: 12

def labour_by_hour(shifts): # Pattern : GROUP count
    hours = {}
    for shift in shifts:
        for hour in range(shift['start'].hour,shift['end'].hour):
            if hour in hours:
                hours[hour] += 1
            else:
                hours[hour] = 1
    return hours

shifts, flagged = load_shifts('data/shifts.csv')
labour = labour_by_hour(shifts)
print(labour)
print(sum(labour.values()))