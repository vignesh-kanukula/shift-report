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
                row['time'] = parse_time(row['time'])
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

def sales_by_hour(orders):
    total_sales = {}
    for order in orders:
        if order['status'] == 'completed':
            hour = order['time'].hour
            amount = order['qty'] * order['price']
            if hour in total_sales:
                total_sales[hour] += amount
            else:
                total_sales[hour] = amount
    return total_sales

orders, skipped = load_orders('data/orders.csv')
sales = sales_by_hour(orders)
print(sales)                   # {12: 40.0, 13: 5.0, 17: 68.0, 18: 67.0, 19: 38.0, 20: 13.0, 21: 28.0}
print(sum(sales.values()))     # 259.0

def sales_per_labour_hour(sales, labour):
    result = {}
    for hour, staff in labour.items():
        hour_sales = sales.get(hour, 0)
        result[hour] = round(hour_sales/staff,2)
    return result
        
splh = sales_per_labour_hour(sales,labour)
print(splh)

def best_and_worst_hour(splh):
    best = None
    worst = None
    best_value = 0
    worst_value = None
    for hour, value in splh.items():
        if value > best_value:
            best_value = value
            best = hour
        if worst_value is None or value < worst_value:
            worst_value = value
            worst = hour
    return best,worst

best, worst = best_and_worst_hour(splh)
print(best, worst)            # expected: 17 14

def lost_orders(orders):
    lost = []
    for order in orders:
        if order['status'] in ('cancelled', 'refunded'):
            lost.append(order)
    return lost
lost = lost_orders(orders)
print(len(lost))

def lost_by_hour(lost):
    counts = {}
    for order in lost:
        hour  = order['time'].hour
        if hour in counts:
            counts[hour] += 1
        else:
            counts[hour] = 1
    return counts
print(lost_by_hour(lost))

def lost_by_reason(lost):
    reasons = {}
    for order in lost:
        reason = order['cancel_reason']
        if reason in reasons:
            reasons[reason] += 1
        else:
            reasons[reason] = 1

    return reasons

print(lost_by_reason(lost))
print(sum(o['qty'] * o['price'] for o in lost))   # lost value: 66.0