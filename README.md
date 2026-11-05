# Shift & Sales Report Tool

## The problem
SPACE PIZZA  has seen sales fall while labour costs rise. Shift and store managers need to know which hours are over- or under-staffed, and why orders get cancelled. This tool reads a day’s orders and staff shifts and produces an hourly report to support those decisions.

## What it answers
1. Total sales + number of orders completed in a day
2. Sales per hour and  busiest hour of the day
3. Labour vs sales per hour 
4. Orders cancellations/ refunds  + reasons
5. Best and worst sellers 

## Input
- `data/orders.csv` – `order_id, time, item, qty, price, status, channel, cancel_reason`
- `data/shifts.csv` – `staff_id, role, start, end`

## Output
- Printed report
- `reports/hourly.csv` – sales, orders, labour hours and sales per labour hour, per hour
- `reports/summary.json` – the day's headline numbers

## Status
v1 in progress