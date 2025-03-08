import pandas as pd, numpy as np
from datetime import datetime, timedelta

def get_data():
    df = pd.read_excel('Input/Working Sheet Strategy.xlsx', sheet_name='Strategy', skiprows=1).dropna(how='all').iloc[1:]
    holidays = pd.read_excel('Input/Working Sheet Strategy.xlsx', sheet_name='Holidays')['London Holidays']
    weights = pd.DataFrame({"Underlying Component": [f"Underlying{i}" for i in range(1, 7)],
                            "Rebalance Cost": [0.005, 0.0025, 0.001, 0.001, 0.0025, 0.0025],
                            "Weight": [0.1, 0.2, 0.15, 0.05, 0.3, 0.2]})
    return df, holidays, weights

def get_last_8th_business_day(date, holidays):
    days = pd.bdate_range(date.replace(day=1), date.replace(day=28), holidays=holidays)
    return days[7] if len(days) > 8 and date > days[7] else pd.bdate_range((date - timedelta(28)).replace(day=1), date - timedelta(1), holidays=holidays)[7]

def annualized_metric(df, input_date, n, metric):
    input_date, df = pd.to_datetime(input_date), df.rename(columns={'index_value': 'closing_price'})
    start_date = df['Date'].min() if n == 'All' else input_date - pd.DateOffset(years=n)
    df = df.loc[(df['Date'] >= start_date) & (df['Date'] <= input_date)].dropna(subset=['closing_price'])
    return (df['closing_price'].pct_change().std() * np.sqrt(252) if metric == 'risk' else ((df.iloc[-1]['closing_price'] / df.iloc[0]['closing_price']) ** (365.25 / (df.iloc[-1]['Date'] - df.iloc[0]['Date']).days)) - 1) if len(df) > 1 else np.nan

def process_data(df, holidays, weights):
    df['last_8th_business_day'] = df['Date'].apply(lambda x: get_last_8th_business_day(x, holidays))
    df_long = pd.melt(df, id_vars=['Date', 'last_8th_business_day'], value_vars=[col for col in df.columns if col not in ['Date', 'last_8th_business_day']], var_name='stock_name', value_name='closing_price')
    merged = pd.merge(pd.merge(df_long, df_long, left_on=['last_8th_business_day','stock_name'], right_on=['Date','stock_name'], suffixes=('', '_BD8')), weights, left_on='stock_name', right_on='Underlying Component')
    merged['index_value'] = ((merged['closing_price'] / merged['closing_price_BD8']) - 1) * merged['Weight']
    index_values = merged.groupby('Date')['index_value'].sum().reset_index()
    index_values['index_value'] = (index_values['index_value'] + 1) * (1 - (sum(weights['Rebalance Cost']) * len(weights) / 220))
    return index_values.dropna()

def save_output(index_values):
    latest_date = index_values['Date'].max()
    results = pd.DataFrame({'Period': ['1 Year', '2 Years', '5 Years', 'All years'],
                            'Annualized Return': [annualized_metric(index_values, latest_date, i, 'return') for i in [1, 2, 5, 'All']],
                            'Annualized Risk': [annualized_metric(index_values, latest_date, i, 'risk') for i in [1, 2, 5, 'All']]})
    with pd.ExcelWriter('Output/output.xlsx', engine='openpyxl') as writer:
        index_values.to_excel(writer, sheet_name='index_value', index=False)
        results.to_excel(writer, sheet_name='results', index=False)

if __name__ == '__main__':
    df, holidays, weights = get_data()
    save_output(process_data(df, holidays, weights))
	
	
