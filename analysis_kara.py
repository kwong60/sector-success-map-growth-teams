import pandas as pd
import numpy as np
import os

def emerging_success(rank_col: str, window_len: int, recent_len: int, top_rows: int):
    """
    Identifies emerging sector successes that have the potential to enter the
    top growth cases.
    
    Input:
        rank_col - name of desired ranking metric
        window_len - length of time series windows (in years) to calculate 
                    relative changes of earlier growth
        recent_len - length of time series window (in years) to calculate 
                    relative change of recent growth
        top_rows - number of emerging sector successes to return
    """
    # extract data from 2-digit level product data
    data_path = os.path.join(os.path.dirname(__file__),'data/filt_hs92_country_product_year_2.csv')
    df = pd.read_csv(data_path)

    # group data by country 
    df_group = df.groupby(['country_code','name_short_en'])
    new_df = pd.DataFrame(columns=['country', 'product', 'rank_shift_slope'])
    countries = []
    products = []
    rankings = []
    for name, group in df_group:
        countries.append(name[0])
        products.append(name[1])

        recent_window = 2022 - recent_len
        recent_df = group[group['year'] >= recent_window]
        
        if len(recent_df) > 1:
            recent_growth = recent_df.iloc[len(recent_df) - 1][rank_col] - recent_df.iloc[0][rank_col]
        else:
            recent_growth = float('-inf')

        early_df = group[group['year'] < recent_window]

        early_growth = []
        early_growth_avg = float('-inf')

        if len(early_df) > 1:
            early_growth_avg = early_df.iloc[len(early_df) - 1][rank_col] - early_df.iloc[0][rank_col]
            i = 0
            curr_yr = 1995

            while curr_yr + window_len < recent_window:
                early_mask = (curr_yr <= early_df['year']) & (early_df['year'] < (curr_yr + window_len))
                early_window = early_df[early_mask]

                if len(early_window) > 1:
                    early_slope = early_window.iloc[len(early_window) - 1][rank_col] - early_window.iloc[0][rank_col]
                    early_growth.append(len(early_window) * early_slope)
                    i += len(early_window)

                curr_yr = curr_yr + window_len

            early_mask = (curr_yr <= early_df['year']) & (early_df['year'] < (recent_window))
            early_window = early_df[early_mask]

            if len(early_window) > 1:
                early_slope = early_window.iloc[len(early_window) - 1][rank_col] - early_window.iloc[0][rank_col]
                early_growth.append(len(early_window) * early_slope)
                i += len(early_window)

            if i != 0:
                early_growth_avg = sum(early_growth) / i
            
        rankings.append(recent_growth - early_growth_avg)
    
    new_df['country'] = countries
    new_df['product'] = products
    new_df['rank_shift_slope'] = rankings

    new_df_clean = new_df[~new_df['rank_shift_slope'].isna() & ~np.isinf(new_df['rank_shift_slope'])]
    df_sorted = new_df_clean.sort_values(by='rank_shift_slope', ascending=False)
    return df_sorted.head(top_rows)

# first input (string): currently 'rank_avg'
# changes the ranking metric that determines success
# must be one of: 'rank_per_capita', 'rank_rca', 'rank_market_share', 'rank_avg'

# second input (non-zero integer): currently 5
# changes the length of time series windows (in years) to calculate relative 
# changes of rank in earlier years
# average of these relative changes is used as the control to determine recent sector success

# third_input (non-zero integer): currently 10
# changes the length of time series windows (in years) to calculate relative 
# change of rank in recent years

# fourth input (non-zero integer): currently 50
# determines number of top growth cases to return

print(emerging_success('rank_avg', 5, 10, 50))
