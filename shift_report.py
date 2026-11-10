# orders.csv line 13 - price col is missing
# shifts.csv line 6 - driver end col is missing

import csv
from datetime import datetime
import os 
import json


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

def parse_time(text):
    return datetime.strptime(text, '%Y-%m-%d %H:%M')

def load_shifts(path):
    good_shifts = []
    flagged = []
    with open(path) as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not row['start'] or not row['end'] :
               flagged.append(row['staff_id'])
            else:
               row['start'] = parse_time(row['start'])
               row['end']  = parse_time(row['end'])
               good_shifts.append(row)

        return good_shifts, flagged
    
def labour_by_hour(shifts): # Pattern : GROUP count
    hours = {}
    for shift in shifts:
        for hour in range(shift['start'].hour,shift['end'].hour):
            if hour in hours:
                hours[hour] += 1
            else:
                hours[hour] = 1
    return hours

def sales_by_hour(orders): # Pattern : GROUP BY
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

def sales_per_labour_hour(sales, labour): # Pattern : TRANSFORM + LOOKUP
    result = {}
    for hour, staff in labour.items():
        hour_sales = sales.get(hour, 0)
        result[hour] = round(hour_sales/staff,2)
    return result

def count_completed(orders):        # Pattern: FILTER + COUNT
    count = 0
    for order in orders:
        if order['status'] == 'completed':
            count += 1
    return count

def best_and_worst_hour(splh): # Pattern : BEST SO FAR
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

def busiest_hour(sales): # Pattern: BEST SO FAR (highest)
    busy = None
    busy_value = 0
    for hour, value in sales.items():
        if value > busy_value:
            busy_value = value
            busy = hour
    return busy


def lost_orders(orders): # pattern : FILTER
    lost = []
    for order in orders:
        if order['status'] in ('cancelled', 'refunded'):
            lost.append(order)
    return lost

def lost_by_hour(lost): # pattern : GROUP count
    counts = {}
    for order in lost:
        hour  = order['time'].hour
        if hour in counts:
            counts[hour] += 1
        else:
            counts[hour] = 1
    return counts

def lost_by_reason(lost): # pattern : GROUP count
    reasons = {}
    for order in lost:
        reason = order['cancel_reason']
        if reason in reasons:
            reasons[reason] += 1
        else:
            reasons[reason] = 1
    return reasons

def by_count(pair):
    return pair[1]

def units_by_item(orders): # GROUP total
    units = {}
    for order in orders:
        if order['status'] == 'completed':  
            item = order['item']
            qty = order['qty']
            if item in units:
                units[item] += qty
            else:
                units[item] = qty
    return units

def save_hourly_csv(sales, labour, splh, path): # Pattern : TRANSFORM + LOOKUP
    with open(path, 'w' , newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['hour', 'sales', 'staff', 'sales_per_labour_hour'])
        writer.writeheader()

        for hour, value in splh.items():
            staff = labour[hour]
            hour_sales = sales.get(hour, 0.0)
            writer.writerow({
                'hour': hour,
                'sales': round(hour_sales,2),
                'staff': staff,
                'sales_per_labour_hour': value
            })

def shift_hours(start_text, end_text):   # Pattern: TRANSFORM

    if not end_text :
        return None
    
    start = parse_time(start_text)
    end = parse_time(end_text)
    hours = (end - start).total_seconds() / 3600
    return round(hours, 2)


def build_summary(sales, labour, completed, peak, best, worst, lost, reasons, ranked):
 # in: values already calculated in print_report → out: one dict of headline numbers

    best_name, best_qty = ranked[0]
    worst_name, worst_qty = ranked[-1]
    summary = {
        'report_date': '2026-11-05',
        'completed_orders': completed,
        'total_sales' :  round(sum(sales.values()),2),
        'busiest_hour': peak,
        'busiest_hour_sales': sales[peak] ,
        'labour_hours': sum(labour.values()),
        'best_splh_hour':best,
        'worst_splh_hour': worst,
        'lost_orders': len(lost),
        'lost_value': round(sum(o['qty'] * o['price'] for o in lost), 2),
        'lost_by_reason' : reasons,
        'best_seller' : {'name': best_name, 'qty': best_qty},
        'worst_seller' : {'name' : worst_name, 'qty' : worst_qty},
        
    }
    return summary
    
    
def save_json(summary, path):      
# in: summary dict + path → out: JSON file at path, returns None              
    with open(path, 'w') as file:
        json.dump(summary, file, indent=2)


def print_report(orders, shifts, skipped, flagged):

    sales = sales_by_hour(orders)
    labour = labour_by_hour(shifts)
    splh = sales_per_labour_hour(sales, labour)
    best, worst = best_and_worst_hour(splh)
    lost = lost_orders(orders)
    units = units_by_item(orders)
    ranked = sorted(units.items(), key=by_count, reverse=True)
    completed = count_completed(orders)
    peak = busiest_hour(sales)
    
    print('SPACE PIZZA - Shift Report - 2026-11-05')
    print(f'Orders loaded: {len(orders)} ({skipped} skipped: missing price)')
    print(f"Shifts loaded: {len(shifts)} (flagged, no clock-out: {', '.join(flagged)})")
    print()
    print(f'Total sales: {sum(sales.values()):.2f} from {completed} completed orders')
    print(f'Busiest hour: {peak}:00 ({sales[peak]:.2f})')
    print(f'Labour hours: {sum(labour.values())}')
    print(f'Best hour (sales per labour hour): {best}:00 ({splh[best]:.2f})')
    print(f'Worst hour (sales per labour hour): {worst}:00 ({splh[worst]:.2f})')
    print()
    print(f"Lost orders: {len(lost)} ({(sum(o['qty'] * o['price'] for o in lost)):.2f})")
    print('  By reason:')
    reasons = lost_by_reason(lost)
    for reason, count in reasons.items():
        print(f'    {reason}: {count}')
    print()
    best_name, best_qty = ranked[0]
    worst_name, worst_qty = ranked[-1]
    print(f'Best seller: {best_name} ({best_qty})')
    print(f'Worst seller: {worst_name} ({worst_qty})')
    
    save_hourly_csv(sales, labour, splh, 'reports/hourly.csv')
    summary = build_summary(sales, labour, completed, peak, best, worst, lost, reasons, ranked)
    save_json(summary, 'reports/summary.json')

    
os.makedirs('reports', exist_ok=True)       
shifts, flagged = load_shifts('data/shifts.csv')
orders, skipped = load_orders('data/orders.csv')
print_report(orders,shifts,skipped,flagged)
