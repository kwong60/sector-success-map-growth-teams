import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

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
    new_df = pd.DataFrame(columns=['country', 'product', 'rank_shifts', 'years', 'rankings'])
    countries = []
    products = []
    years = []
    ranks = []
    rank_shifts = []

    for name, group in df_group:
        countries.append(name[0])
        products.append(name[1])

        years_group = group['year'].tolist()
        years.append(years_group)

        rank_group = group[rank_col].tolist()
        ranks.append(rank_group)

        recent_window = 2022 - recent_len
        recent_df = group[group['year'] >= recent_window]
        nonzero_rdf = recent_df[recent_df[rank_col] != 0]
        recent_growth = float('inf')
        
        if len(nonzero_rdf) > 1:
            recent_growth = (nonzero_rdf.iloc[len(nonzero_rdf) - 1][rank_col] - nonzero_rdf.iloc[0][rank_col]) / (nonzero_rdf.iloc[len(nonzero_rdf) - 1]['year'] - nonzero_rdf.iloc[0]['year'])
            
        early_df = group[group['year'] < recent_window]
        nonzero_edf = early_df[early_df[rank_col] != 0]

        early_growth = []
        early_growth_avg = float('inf')

        if len(nonzero_edf) > 1:
            early_growth_avg = nonzero_edf.iloc[len(nonzero_edf) - 1][rank_col] - nonzero_edf.iloc[0][rank_col]
            i = 0
            curr_yr = 1995

            while curr_yr + window_len < recent_window:
                early_mask = (curr_yr <= nonzero_edf['year']) & (nonzero_edf['year'] < (curr_yr + window_len))
                early_window = nonzero_edf[early_mask]

                if len(early_window) > 1:
                    early_slope = early_window.iloc[len(early_window) - 1][rank_col] - early_window.iloc[0][rank_col]
                    early_growth.append(len(early_window) * early_slope)
                    i += len(early_window)

                curr_yr = curr_yr + window_len

            early_mask = (curr_yr <= nonzero_edf['year']) & (nonzero_edf['year'] < (recent_window))
            early_window = nonzero_edf[early_mask]

            if len(early_window) > 1:
                early_slope = (early_window.iloc[len(early_window) - 1][rank_col] - early_window.iloc[0][rank_col]) / (early_window.iloc[len(early_window) - 1]['year'] - early_window.iloc[0]['year'])
                early_growth.append(len(early_window) * early_slope)
                i += len(early_window)

            if i != 0:
                early_growth_avg = sum(early_growth) / i
            
        rank_shifts.append(recent_growth - early_growth_avg)
    
    new_df['country'] = countries
    new_df['product'] = products
    new_df['rank_shifts'] = rank_shifts
    new_df['years'] = years
    new_df['rankings'] = ranks

    new_df_clean = new_df[~new_df['rank_shifts'].isna() & ~np.isinf(new_df['rank_shifts'])]
    df_sorted = new_df_clean.sort_values(by='rank_shifts', ascending=True)
    df_sorted_top = df_sorted.head(top_rows)

    os.makedirs('emerging_successes_plots', exist_ok=True)

    for index, row in df_sorted_top.iterrows():
        yrs = row['years']
        rkgs = row['rankings']

        plt.figure()
        plt.plot(yrs, rkgs, marker='o')

        plt.xlabel('Year') 
        plt.ylabel('Ranking') 
        plt.title(f'{row["country"]}: {row["product"]}')
        plt.grid(True)

        output = os.path.join('emerging_successes_plots', f'{row["country"]}_{row["product"]}.png')
        plt.tight_layout()
        plt.savefig(output)
        plt.close()

    for index, row in df_sorted_top.iterrows():
        yrs = row['years']
        rkgs = row['rankings']
        plt.plot(yrs, rkgs, marker='o')

    plt.xlabel('Year') 
    plt.ylabel('Ranking') 
    plt.title(f'Top {top_rows} Emerging Sector Successes')
    plt.grid(True)

    output = os.path.join('emerging_successes_plots', f'top_{top_rows}_successes.png')
    plt.tight_layout()
    plt.savefig(output)
    plt.close()

    df_sorted_top.drop(columns=['years', 'rankings'], inplace=True)
    df_sorted_top.to_csv('emerging_successes.csv', index=False)

    plt.figure(figsize=(12, 6))
    plt.axis('off')
    plt.title("Emerging Sector Successes")
    table = plt.table(cellText=df_sorted_top.values, colLabels=df_sorted_top.columns, loc='center')
    plt.savefig('emerging_successes_table.png')

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

# fourth input (non-zero integer): currently 20
# determines number of top growth cases to return

print(emerging_success('rank_avg', 5, 5, 20))
