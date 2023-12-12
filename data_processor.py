from datetime import datetime, timedelta
import calendar

from datetime import datetime, timedelta
import calendar

def process_data(raw_data):
    if not raw_data or 'errors' in raw_data:
        return None

    consumption_data = raw_data['data']['viewer']['homes'][0]['consumption']['nodes']

    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_of_month = now.replace(day=calendar.monthrange(now.year, now.month)[1])

    daily_consumption = {now.replace(day=day).strftime('%Y-%m-%d'): 0 for day in range(1, last_day_of_month.day + 1)}
    daily_cost = daily_consumption.copy()

    for node in consumption_data:
        date = node['from'].split('T')[0]
        if date in daily_consumption:
            consumption = node.get('consumption', 0) or 0  # Bruk 0 hvis None
            cost = node.get('cost', 0) or 0  # Bruk 0 hvis None
            daily_consumption[date] += consumption
            daily_cost[date] += cost

    total_consumption = sum(daily_consumption.values())
    total_cost = sum(daily_cost.values())

    return {
        'dates': list(daily_consumption.keys()),
        'consumption': list(daily_consumption.values()),
        'cost': list(daily_cost.values()),
        'total_consumption': total_consumption,
        'total_cost': total_cost
    }

def process_monthly_data(raw_data):
    if not raw_data or 'errors' in raw_data:
        return None

    # Anta at vi er interessert i den første hjemmeprofilen
    monthly_data = raw_data['data']['viewer']['homes'][0]['consumption']['nodes']
    
    dates = [entry['from'][:7] for entry in monthly_data]  # Få år-måned format
    consumption_values = [entry['consumption'] for entry in monthly_data]
    cost_values = [entry['cost'] for entry in monthly_data]

    return {
        'dates': dates,
        'consumption': consumption_values,
        'cost': cost_values
    }