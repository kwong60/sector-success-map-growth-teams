import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

exc_countries_china = ["australia", "austria", "belgium", "canada", "chile", "colombia",
                 "costa_rica", "czechia", "denmark", "estonia", "finland", "france",
                 "germany", "greece", "hungary", "iceland", "ireland", "israel",
                 "italy", "japan", "south_korea", "latvia", "lithuania", "luxembourg",
                 "mexico", "netherlands", "new_zealand", "norway", "poland", 
                 "portugal", "slovakia", "slovenia", "spain", "sweden", "switzerland",
                 "turkiye", "united_kingdom", "united_states_of_america", "us_virgin_islands",
                 "us_minor_outlying_islands", "china", "hong_kong", "macao"]

exc_countries = ["australia", "austria", "belgium", "canada", "chile", "colombia",
                 "costa_rica", "czechia", "denmark", "estonia", "finland", "france",
                 "germany", "greece", "hungary", "iceland", "ireland", "israel",
                 "italy", "japan", "south_korea", "latvia", "lithuania", "luxembourg",
                 "mexico", "netherlands", "new_zealand", "norway", "poland", 
                 "portugal", "slovakia", "slovenia", "spain", "sweden", "switzerland",
                 "turkiye", "united_kingdom", "united_states_of_america", "us_virgin_islands",
                 "us_minor_outlying_islands"]

exc_goods = ["ores_slag_and_ash", "mineral_fuels,_oils_and_waxes", "precious_metals_and_stones",
             "iron_and_steel", "articles_of_iron_or_steel", "copper", "nickel", "aluminum",
             "lead", "zinc", "tin", "other_base_metals", "miscellaneous_articles_of_base_metal"]


# takes in preprocessed data with applied modification filters
data_path = os.path.join(os.path.dirname(__file__),'data/clean_hs92_country_product_year_2.csv')
data = pd.read_csv(data_path)

# takes in preprocessed data without modification filters
data_path2 = os.path.join(os.path.dirname(__file__),'data/filt_hs92_country_product_year_2.csv')
original_data = pd.read_csv(data_path2)

def emerging_success(input_data: pd.DataFrame, rank_col: str, window_len: int, recent_len: int, top_rows: int, mod: bool, china: bool):
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
    if not china:
        oecd = [156, 344, 446]
        df_mask = input_data["country_id"].isin(oecd)
        input_data = input_data[~df_mask]

    if mod:
        filtered_data = input_data[(input_data['year'] == 2022) & (input_data[rank_col] < 30)]
        filtered_countries = filtered_data['country'].tolist()
        filtered_products = filtered_data['name_short_en'].tolist()
        clean_data = input_data[(input_data['country'].isin(filtered_countries)) & (input_data['name_short_en'].isin(filtered_products))]
        df_group = clean_data.groupby(['country','name_short_en'])
        
    else:
        # group data by cases (country, product)
        df_group = input_data.groupby(['country','name_short_en'])

    # intialize a new DataFrame to store slope of each sector's shift in rank
    new_df = pd.DataFrame(columns=['country', 'product', 'hs_code', 'rank_shifts', 'years', 'rankings'])
    countries = []
    products = []
    hs_codes = []
    years = []
    ranks = []
    rank_shifts = []

    # iterates through each country-product pair
    for name, group in df_group:
        if china:
            excluded_countries = exc_countries
        else:
            excluded_countries = exc_countries_china

        if (name[0] in excluded_countries) or (name[1] in exc_goods):
            continue

        countries.append(name[0])
        products.append(name[1])
        hs_codes.append(group['product_code'].iloc[0])

        years_group = group['year'].tolist()
        years.append(years_group)

        rank_group = group[rank_col].tolist()
        ranks.append(rank_group)

        # establishes window of "recent years" based on recent_len parameter
        recent_window = 2022 - recent_len
        recent_df = group[group['year'] >= recent_window]

        # filters out zero ranks due to NaN data
        nonzero_rdf = recent_df[recent_df[rank_col] != 0]

        # initialize slope of recent data to infinity (worst case scenario)
        recent_growth = float('inf')
        
        # calculate recent growth as change in ranking across window of "recent
        # years" over change in years
        if len(nonzero_rdf) > 1:
            recent_growth = (nonzero_rdf.iloc[len(nonzero_rdf) - 1][rank_col] - nonzero_rdf.iloc[0][rank_col]) / (nonzero_rdf.iloc[len(nonzero_rdf) - 1]['year'] - nonzero_rdf.iloc[0]['year'])
            
        # establishes window of "earlier years" based on what is not in the
        # window of "recent years"
        early_df = group[group['year'] < recent_window]

        # filters out zero ranks due to NaN data
        nonzero_edf = early_df[early_df[rank_col] != 0]

        # initialize slope of early data to infinity (worst case scenario)
        early_growth = []
        early_growth_avg = float('inf')

        if len(nonzero_edf) > 1:
            # set slope of early data to the change in ranking across window of
            # "earlier years" if there is enough data
            early_growth_avg = nonzero_edf.iloc[len(nonzero_edf) - 1][rank_col] - nonzero_edf.iloc[0][rank_col]

            i = 0
            curr_yr = 1995

            # iterate through earlier years using windows of window_len length
            while curr_yr + window_len < recent_window:
                # filter for years in each window
                early_mask = (curr_yr <= nonzero_edf['year']) & (nonzero_edf['year'] < (curr_yr + window_len))
                early_window = nonzero_edf[early_mask]

                # if there's enough data, find slope of rank shifts across each window
                if len(early_window) > 1:
                    early_slope = (early_window.iloc[len(early_window) - 1][rank_col] - early_window.iloc[0][rank_col]) / (early_window.iloc[len(early_window) - 1]['year'] - early_window.iloc[0]['year'])
                    
                    # append slope to list to later take average
                    early_growth.append(early_slope)

                    # add the data points to total number of data points
                    i += len(early_window)

                # set the current year to the end of the previous window to begin the next window
                curr_yr = curr_yr + window_len

            # repeat while loop logic for last window before "recent years" (window may not be the entire window_len)
            early_mask = (curr_yr <= nonzero_edf['year']) & (nonzero_edf['year'] < (recent_window))
            early_window = nonzero_edf[early_mask]

            # repeat slope calculations on last window
            if len(early_window) > 1:
                early_slope = (early_window.iloc[len(early_window) - 1][rank_col] - early_window.iloc[0][rank_col]) / (early_window.iloc[len(early_window) - 1]['year'] - early_window.iloc[0]['year'])
                early_growth.append(early_slope)
                i += len(early_window)

            if i != 0:
                # sum slopes of each window over the total number of data points (retrieves mean slope of earlier years)
                early_growth_avg = sum(early_growth) / i
        
        # calculate difference between recent slope and earlier slope
        rank_shifts.append(recent_growth - early_growth_avg)
    
    # assign each list to a column in the new DataFrame
    new_df['country'] = countries
    new_df['product'] = products
    new_df['hs_code'] = hs_codes
    new_df['rank_shifts'] = rank_shifts
    new_df['years'] = years
    new_df['rankings'] = ranks

    # ensure DataFrame as no null or infinite slope values
    new_df_clean = new_df[~new_df['rank_shifts'].isna() & ~np.isinf(new_df['rank_shifts'])]

    # sort DataFrameby rank_shifts (more negative slope = greater increase in rank)
    df_sorted = new_df_clean.sort_values(by='rank_shifts', ascending=True)

    # retrieve top emerging success cases using top_rows parameter
    df_sorted_top = df_sorted.head(top_rows)

    if china:
        if mod:
            dir_name = 'china_mod_'
        else:
            dir_name = 'china_'
    else:
        if mod:
            dir_name = 'mod_'
        else:
            dir_name = ''
        
    # make a directory for plot of each emerging success case (plots rankings
    # for each case over time)
    os.makedirs(f'{dir_name}{rank_col}_emerging_successes_plots', exist_ok=True)

    # iterates through each row of sorted DataFrame to plot each case on separate graphs
    for index, row in df_sorted_top.iterrows():
        yrs = row['years']
        rkgs = row['rankings']

        # plots rankings for each case over years
        plt.figure()
        plt.plot(yrs, rkgs, marker='o')

        # labelling
        plt.xlabel('Year') 
        plt.ylabel('Ranking') 
        plt.title(f'{row["country"]}: \n {row["product"]} ({row["hs_code"]})')
        plt.grid(True)

        # save figure to 'emerging_successes_plots' directory
        output = os.path.join(f'{dir_name}{rank_col}_emerging_successes_plots', f'{row["country"]}_{row["product"]}_{row["hs_code"]}.png')

        plt.tight_layout()
        plt.savefig(output)
        plt.close()

    # iterates through each row of sorted DataFrame to plot each case on same graph
    for index, row in df_sorted_top.iterrows():
        yrs = row['years']
        rkgs = row['rankings']

        # plots rankings for each case over years
        plt.plot(yrs, rkgs, marker='o')

    # labelling
    plt.xlabel('Year') 
    plt.ylabel('Ranking') 
    plt.title(f'Top {top_rows} Emerging Sector Successes ({rank_col})')
    plt.grid(True)

    # save figure to 'emerging_successes_plots' directory
    output = os.path.join(f'{dir_name}{rank_col}_emerging_successes_plots', f'{rank_col}_top_{top_rows}_successes.png')
    
    plt.tight_layout()
    plt.savefig(output)
    plt.close()

    # drop "years" and "rankings" columns (no longer necessary after graphing)
    df_sorted_top.drop(columns=['years', 'rankings'], inplace=True)

    os.makedirs(f'{dir_name}emerging_successes_tables', exist_ok=True)

    # saves sorted DataFrame to CSV
    csv_path = os.path.join(f'{dir_name}emerging_successes_tables', f'{rank_col}_emerging_successes.csv')

    df_sorted_top.to_csv(csv_path, index=False)

    # converts and saves sorted DataFrame to table (for interpretability)
    plt.figure(figsize=(12, 6))
    plt.axis('off')
    plt.title(f'Emerging Sector Successes ({rank_col})')
    plt.table(cellText=df_sorted_top.values, colLabels=df_sorted_top.columns, loc='center')

    table_path = os.path.join(f'{dir_name}emerging_successes_tables', f'{rank_col}_emerging_successes_table.png')

    plt.savefig(table_path)
    plt.close()

    return df_sorted_top.head(top_rows)

# first input (string):
# changes the ranking metric that determines success
# must be one of: 'rank_per_capita', 'rank_rca', 'rank_market_share', 'rank_avg'

# second input (non-zero integer): currently 10
# changes the length of time series windows (in years) to calculate relative changes of rank in earlier years
# average of these relative changes is used as the control to determine recent sector success

# third_input (non-zero integer): currently 5
# changes the length of time series windows (in years) to calculate relative change of rank in recent years

# fourth input (non-zero integer): currently 20
# determines number of top growth cases to return

#If we want data with the modification filters use this, or else if not comment it out: 
print(emerging_success(original_data, 'rank_avg', 10, 5, 20, False, False))
print(emerging_success(original_data,'rank_per_capita', 10, 5, 20, False, False))
print(emerging_success(original_data, 'rank_rca', 10, 5, 20, False, False))
print(emerging_success(original_data, 'rank_market_share', 10, 5, 20, False, False))

#Otherwise if we want the original data without modifications, uncomment this:
print(emerging_success(data, 'rank_avg', 10, 5, 20, True, False))
print(emerging_success(data,'rank_per_capita', 10, 5, 20, True, False))
print(emerging_success(data, 'rank_rca', 10, 5, 20, True, False))
print(emerging_success(data, 'rank_market_share', 10, 5, 20, True, False))

print(emerging_success(original_data, 'rank_avg', 10, 5, 20, False, True))
print(emerging_success(original_data,'rank_per_capita', 10, 5, 20, False, True))
print(emerging_success(original_data, 'rank_rca', 10, 5, 20, False, True))
print(emerging_success(original_data, 'rank_market_share', 10, 5, 20, False, True))

print(emerging_success(data, 'rank_avg', 10, 5, 20, True, True))
print(emerging_success(data,'rank_per_capita', 10, 5, 20, True, True))
print(emerging_success(data, 'rank_rca', 10, 5, 20, True, True))
print(emerging_success(data, 'rank_market_share', 10, 5, 20, True, True))