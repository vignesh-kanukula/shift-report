# orders.csv line 13 - price col is missing
# shifts.csv line 6 - driver end col is missing

import csv

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


orders, skipped = load_orders('data/orders.csv')
print(len(orders), skipped)      # expected: 17 1
