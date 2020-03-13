import json
from decimal import Decimal

import httpx
import pandas as pd
from django.db.models import Sum, Count, Avg, Max, Min

from tracker.models import UserSelectedFund


def get_nav(data):
    code = data['fund__scheme_code']
    response = httpx.get(f'https://api.mfapi.in/mf/{code}')
    r_json = response.json()
    return Decimal(r_json.get('data')[0]['nav'])


def get_current_value(data):
    result = data['total_units'] * data['current_nav']
    return round(result, 2)


def calculate_cagr(data):
    result = float(data['current_value'] / data['amount_invested']) ** (1 / (data['completed_duration'] / 12)) - 1
    print(result)
    return round(result, 2)


query = UserSelectedFund.objects.all().annotate(amount_invested=Sum('transaction__amount'),
                                                completed_duration=Count('transaction'),
                                                total_units=Sum('transaction__units'),
                                                average_nav=Avg('transaction__nav'),
                                                max_nav=Max('transaction__nav'),
                                                min_nav=Min('transaction__nav'))
df = pd.DataFrame(
    query.values('fund__name', 'fund__scheme_code', 'amount', 'duration', 'completed_duration', 'mode', 'active',
                 'amount_invested',
                 'total_units', 'average_nav', 'max_nav', 'min_nav'))
# df['average_nav'] = df.apply(get_nav, axis=1)
df['current_nav'] = df.apply(get_nav, axis=1)
df['current_value'] = df.apply(get_current_value, axis=1)
df['gain/loss'] = df['current_value'] - df['amount_invested']
df['cagr'] = df.apply(calculate_cagr, axis=1)
# df.columns = ['Fund', 'Code', 'Amount', 'Duration', 'Mode', 'Active', 'Invested', 'Completed', 'Units', 'NAV-Average',
#               'NAV-Current', 'NAV-Max', 'NAV-Min', 'Current', 'Gain/Loss', 'CAGR']
df = df.sort_values(by='cagr', ascending=False)
# df.to_csv('export.csv')
d = df.to_json(orient='records')
print(d)
