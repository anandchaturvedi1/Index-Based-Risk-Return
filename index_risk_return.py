# This script calculates the annualized risk and return based on the specified index computation methodology and provided data.

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging


def get_data():
	# Input Data
	df_raw = pd.read_excel('Input/Working Sheet Strategy.xlsx', sheet_name='Strategy', skiprows=1)	
	holiday = pd.read_excel('Input/Working Sheet Strategy.xlsx', sheet_name='Holidays')
	df = df1.dropna(how='all').iloc[1:]
	holidays = holiday['London Holidays']
	# Underlying cost & weight data
	underlying_cost_weight_df  = pd.DataFrame({
		"Underlying Component": ["Underlying1", "Underlying2", "Underlying3", "Underlying4", "Underlying5", "Underlying6"],
		"Rebalance Cost": [0.005, 0.0025, 0.001, 0.001, 0.0025, 0.0025],
		"Weight": [0.1, 0.2, 0.15, 0.05, 0.3, 0.2]
	})
	return df, holiday, underlying_cost_weight_df


def get_last_8th_business_day(date: datetime) -> datetime:
    """
    Returns the 8th-to-last business day of the month for a given date.

    Args:
        date (datetime): The reference date to determine the last 8th business day of its month.

    Returns:
        datetime: The 8th-to-last business day of the month for the given date.

    Raises:
        ValueError: If there are fewer than 8 business days in the month of the given date.
    """
    today = date
    # Define the 8th business day of the current month
    current_month_start = today.replace(day=1)
    holidays = ['2023-12-27', '2024-07-04']
    business_days_current_month = pd.bdate_range(start=current_month_start, end=today.replace(day=28), holidays=holidays, freq='C')    
    if len(business_days_current_month) > 8 and today > business_days_current_month[7]:
        # If today is past the 8th business day of the current month, return the 8th business day of the current month
        bd8_date = business_days_current_month[7]
    else:
        # Compute the 8th business day of the previous month
        previous_month_end = current_month_start - timedelta(days=1)
        previous_month_start = previous_month_end.replace(day=1)
        business_days_previous_month = pd.bdate_range(start=previous_month_start, end=previous_month_end, holidays=holidays, freq='C')
        
        if len(business_days_previous_month) >= 8:
            bd8_date = business_days_previous_month[7]
        else:
            raise ValueError("Not enough business days in the previous month to compute the 8th business day.")

    return bd8_date


def calculate_annualized_return(df, input_date, n):
    input_date = pd.to_datetime(input_date)
    df = df.rename(columns={'index_value': 'closing_price'})    
    if n=='All':
      date_n_years_ago=df['Date'].min()
    else: 
      date_n_years_ago = input_date - pd.DateOffset(years=n)    
    # Find the closest date in the DataFrame that is <= date_n_years_ago
    closest_date = df.loc[df['Date'] <= date_n_years_ago, 'Date'].max()    
    if pd.isnull(closest_date):
        # raise ValueError("No data available for a date n years prior to the input date.")
        return np.nan
    # Get closing prices for the input_date and the closest_date
    price_input_date = df.loc[df['Date'] == input_date, 'closing_price']
    price_closest_date = df.loc[df['Date'] == closest_date, 'closing_price']    
    if price_input_date.empty or price_closest_date.empty:        
        return np.nan    
    price_input_date = price_input_date.values[0]
    price_closest_date = price_closest_date.values[0]    
    # Calculate the number of days between the two dates
    days_between = (input_date - closest_date).days    
    if days_between == 0:        
        return np.nan    
    # Calculate the return
    index_return = ( (price_input_date / price_closest_date) * (365.25 / days_between) )- 1     
    return index_return


def calculate_annualized_risk(df, input_date, n):    
	# Calculate Annualized Risk
    # Convert input_date to datetime
    input_date = pd.to_datetime(input_date)
    df = df.rename(columns={'index_value': 'closing_price'})   
    # Define the date 3 years before the input date
    if n=='All':
      date_n_years_ago=df['Date'].min()
    else: 
      date_n_years_ago = input_date - pd.DateOffset(years=n)    
    # Filter the DataFrame for the dates between three_years_ago and input_date
    df_filtered = df.loc[(df['Date'] >= date_n_years_ago) & (df['Date'] <= input_date) , ]    
    # Drop rows with missing closing prices
    df_filtered = df_filtered.dropna(subset=['closing_price'])    
    if len(df_filtered) < 2:
        raise ValueError("Not enough data to compute returns.")    
    # Calculate daily returns
    df_filtered['daily_return'] = df_filtered['closing_price'].pct_change()    
    # Drop NaN values resulting from pct_change calculation
    df_filtered['daily_return'].replace([np.inf, -np.inf], np.nan, inplace=True)
    df_filtered = df_filtered.dropna(subset=['daily_return'])    
    # Calculate the standard deviation of daily returns
    daily_std_dev = df_filtered['daily_return'].std()        
    # Annualize the standard deviation
    annualized_std_dev = daily_std_dev * np.sqrt(252)  # Assuming 252 trading days in a year    
    return annualized_std_dev


def data_processing(df, holiday, underlying_cost_weight_df):
	# Get last 8th business_day
	df['last_8th_business_day'] = df['Date'].apply(lambda x: get_last_8th_business_day(x))
	value_vars = [col for col in df.columns if col not in ['Date', 'last_8th_business_day']]
	df_long = pd.melt(df,
					   id_vars=['Date', 'last_8th_business_day'],
					   value_vars=value_vars,
					   var_name='stock_name',
					   value_name='closing_price')
	# Merge df_long with itself to get the closing prices of the last 8th business day
	merged_df = pd.merge(df_long, df_long, how='left', left_on=['last_8th_business_day','stock_name'], right_on=['Date','stock_name'], suffixes=('', '_BD8Prices'))
	# Merge the stock price comparison DataFrame with underlying cost weight DataFrame
	merged_df2 = pd.merge(merged_df, underlying_cost_weight_df, how='left', left_on='stock_name', right_on='Underlying Component')
	# Compute Index returns
	merged_df2['index_value'] = ((merged_df2['closing_price'] / merged_df2['closing_price_BD8Prices']) - 1) * merged_df2['Weight']
	# Group by 'Date' to compute index value by date
	index_value_by_date = merged_df2.groupby('Date')['index_value'].sum(min_count=1).reset_index()
	index_value_by_date['index_value'] = (index_value_by_date['index_value'] + 1)* (1 - (sum(underlying_cost_weight_data['Rebalance Cost']) * len(underlying_cost_weight_df) / 220))
	index_value_by_date.replace([np.inf, -np.inf], np.nan, inplace=True)
	index_value_by_date = index_value_by_date.dropna()
	index_value_by_date['last_8th_business_day'] = index_value_by_date['Date'].apply(lambda x: get_last_8th_business_day(x))
	#Apply the final bit in index computation where index values are based on index's past values
	df1 = index_value_by_date.copy(deep=True)
	df1['index_value_final']=np.nan
	index_vals = [np.nan]
	for idx, row in df1.iterrows():
		# Get the price on the last_BD8 date
		if row['Date']==pd.to_datetime('2021-01-12'):
		   print( row['Date'])
		   df1.loc[df1['Date'] == row['Date'], 'index_value_final'] = 100
		   continue
		else:        
			last_BD8_price = df1.loc[df1['Date'] == row['last_8th_business_day'], 'index_value_final'].values		
		# Check if the price for last_BD8 is found
		if len(last_BD8_price) > 0:
			last_BD8_price = last_BD8_price[0]
			# Calculate the index value
			index_val = row['index_value'] * last_BD8_price
		else:
			# Handle cases where last_BD8 price is not found
			index_val = None		
		# Append the index value to the list
		df1.loc[df1['Date'] == row['Date'], 'index_value_final'] = index_val
		index_vals.append(index_val)
	index_value_by_date['index_value'] = index_vals
	return index_value_by_date


def save_output(index_value_by_date):
	latest_date = index_value_by_date['Date'].max()
	# Calculate annualized returns for different periods
	return_1yr = calculate_annualized_return(index_value_by_date, latest_date, 1)
	return_2yr = calculate_annualized_return(index_value_by_date, latest_date, 2)
	return_5yr = calculate_annualized_return(index_value_by_date, latest_date, 5)
	return_all_yrs = calculate_annualized_return(index_value_by_date, latest_date, 'All')
	# Returns results
	results1 = pd.DataFrame({
		'Period': ['1 Year', '2 Years', '5 Years', 'All years'],
		'Annualized Return': [return_1yr, return_2yr, return_5yr, return_all_yrs]
	})
	# Calculate annualized risk for different periods
	risk_1yr = calculate_annualized_risk(index_value_by_date, latest_date, 1)
	risk_2yr = calculate_annualized_risk(index_value_by_date, latest_date, 2)
	risk_5yr = calculate_annualized_risk(index_value_by_date, latest_date, 5)
	risk_all_yrs = calculate_annualized_risk(index_value_by_date, latest_date, 'All')
	# Risk results
	results2 = pd.DataFrame({
		'Period': ['1 Year', '2 Years', '5 Years', 'All years'],
		'Annualized Risk': [risk_1yr, risk_2yr, risk_5yr, risk_all_yrs]
	})
	# Export reconcilation data
	with pd.ExcelWriter('Ouput/output.xlsx', engine='openpyxl') as writer:
		df1.to_excel(writer, sheet_name='intermittent_df', index=False)
		index_value_by_date.to_excel(writer, sheet_name='index_value', index=False)
		results1.to_excel(writer, sheet_name='results1', index=False)
		results2.to_excel(writer, sheet_name='results2', index=False)


if __name__ == 'main':
	try:
		logging.info("Get Input Data")
		df, holiday, underlying_cost_weight_df = get_data()
		logging.info("Process Index Data")
		index_value_by_date = data_processing(df, holiday, underlying_cost_weight_df)
		logging.info("Get Final")
		save_output(index_value_by_date)
	except Exception as e:
		logging.error(f"Index computation couldn't be completed, Error: {e}", exc_info=True)
	
	
