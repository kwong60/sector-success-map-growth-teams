import pandas as pd
import os
import matplotlib.pyplot as plt

#takes in preprocessed data that has been filtered
data_path = os.path.join(os.path.dirname(__file__),'data/filt_hs92_country_product_year_2.csv')
data = pd.read_csv(data_path)

eci_ranking = pd.read_csv('data/rankings.tab', sep='\t')
directory = os.path.dirname('data/rankings.tab')
eci_groups = eci_ranking.groupby('country_id')
new_eci_ranking = pd.DataFrame(columns=['country_id', 'eci_ranking_shift'])
eci_countries = []
eci_ranking_shifts = []
for name,group in eci_groups:
    eci_countries.append(name)
    if(len(group[group['year'] == 2022]) == 1) and (len(group[group['year'] == 1995]) == 1):
        final_eci = group[group['year'] == 2022]['hs_eci_rank'].iloc[0]
        beg_eci = group[group['year'] == 1995]['hs_eci_rank'].iloc[0]
        eci_rank_shift = final_eci - beg_eci
    else:
        eci_rank_shift = None
    eci_ranking_shifts.append(eci_rank_shift)
new_eci_ranking['country_id'] = eci_countries
new_eci_ranking['eci_ranking_shift'] = eci_ranking_shifts
new_eci_ranking = new_eci_ranking.dropna(subset=['eci_ranking_shift'])
new_eci_file = os.path.join(directory, 'eci_rank_shifts.csv')
new_eci_ranking = new_eci_ranking.sort_values(by='eci_ranking_shift', ascending=False)
new_eci_ranking.to_csv(new_eci_file,index=False)
top50countries = new_eci_ranking.head(50)
new_eci_countryids = top50countries['country_id'].tolist()
data = data[data['country_id'].isin(new_eci_countryids)]


exc_countries = ["australia", "austria", "belgium", "canada", "chile", "colombia",
                 "costa_rica", "czechia", "denmark", "estonia", "finland", "france",
                 "germany", "greece", "hungary", "iceland", "ireland", "israel",
                 "italy", "japan", "south_korea", "latvia", "lithuania", "luxembourg",
                 "mexico", "netherlands", "new_zealand", "norway", "poland", 
                 "portugal", "slovakia", "slovenia", "spain", "sweden", "switzerland",
                 "turkiye", "united_kingdom", "united_states_of_america", "us_virgin_islands",
                 "us_minor_outlying_islands", "china", "hong_kong", "macao"]

exc_goods = ["ores_slag_and_ash", "mineral_fuels_oils_and_waxes", "precious_metals_and_stones",
             "iron_and_steel", "articles_of_iron_or_steel", "copper", "nickel", "aluminum",
             "lead", "zinc", "tin", "other_base_metals", "miscellaneous_articles_of_base_metal"]


#function to sort the biggest ranking shifts for each product level
def entire_time_period_ranking_shift(rank_column_name: str, start: int, end: int ):
    '''Given a start and end year, this function  calculates the rank shift based on a given ranking system for each country-product pair '''
    filtered_data = data[(data['year'] == 2022) & (data[rank_column_name] < 30)]
    filtered_countries = filtered_data['country'].tolist()
    filtered_products = filtered_data['name_short_en'].tolist()
    clean_data = data[(data['country'].isin(filtered_countries)) & (data['name_short_en'].isin(filtered_products))]

    grouped = clean_data.groupby(['country','name_short_en'])
    new_data = pd.DataFrame(columns=['country', 'product', 'hs_code' , f'{start}-{end}_rank_shift'])
    country_code_list = []
    product_code_list = []
    hs_code_list =[]
    ranking_shift_list = []
    
    for name, group in grouped:
        if (name[0] in exc_countries) or (name[1] in exc_goods):
            continue

        country_code_list.append(name[0])
        product_code_list.append(name[1])
        hs_code_list.append(group['product_code'].iloc[0])
        if(len(group[group['year'] == end]) == 1) and (len(group[group['year'] == start]) == 1):
            end_ranking = group[group['year'] == end][rank_column_name].iloc[0]
            beg_ranking = group[group['year'] == start][rank_column_name].iloc[0]
            rank_shift = end_ranking - beg_ranking
        else:
            end_ranking = None
            rank_shift = None
        ranking_shift_list.append(rank_shift)

    new_data['country'] = country_code_list
    new_data['product'] = product_code_list
    new_data['hs_code'] = hs_code_list
    new_data[f'{start}-{end}_rank_shift'] = ranking_shift_list
    new_data = new_data.dropna(subset=[f'{start}-{end}_rank_shift'])
    
    return new_data



#Function to look at the big ranking shifts and drops for smaller windows with the 200 success stories
def window_time_period_ranking_shift(time_window: int, rank_column_name: str):
    '''Calculates small rank shifts given a window size for all windows between 1995-20005
    '''

    windows = []
    current_time = 1995
    while current_time < 2022:
        window_end = min(current_time + time_window, 2022)
        windows.append((current_time, window_end))
        current_time += time_window
    
    all_windows_data = pd.DataFrame()
    for start, end in windows:
        window_data = entire_time_period_ranking_shift(rank_column_name, start, end)
        all_windows_data = pd.merge(
            all_windows_data, window_data, on=['country', 'product', 'hs_code'], how='outer'
        ) if not all_windows_data.empty else window_data

    return all_windows_data

rank_metrics = data.columns[17:]

'''function to filter by extra criteria
def final_ranking_criterion_filter(successStories: pd.DataFrame, rank_column_name: str):
    success_countries = successStories['country'].tolist()
    success_products = successStories['product'].tolist()
    filtered_data = data[(data['country'].isin(success_countries)) & (data['name_short_en'].isin(success_products))]
    top_country_criterion_data = filtered_data[(filtered_data['year'] == 2022) & (filtered_data[rank_column_name] < 30)]
    top_criterion_countries = top_country_criterion_data['country'].tolist()
    top_criterion_products = top_country_criterion_data['name_short_en'].tolist()
    applyfilter_success_stories = successStories[(successStories['country'].isin(top_criterion_countries)) & (successStories['product'].isin(top_criterion_products))]
    return applyfilter_success_stories
'''


for rank_metric in rank_metrics:
    #Gets the top 200 sector success stories
    overall_time_period = entire_time_period_ranking_shift(rank_metric, 1995,2022)
    twohundred_sector_successes = overall_time_period.sort_values(by='1995-2022_rank_shift', ascending=False).head(200)

    windows_overall = window_time_period_ranking_shift(5, rank_metric)
    detailed_two_hundred = windows_overall.merge(twohundred_sector_successes, on=['country', 'product', 'hs_code'], how='inner')
    detailed_two_hundred_sorted = detailed_two_hundred.sort_values('1995-2022_rank_shift', ascending=False)

    #Visualization for ranking shifts per window for the top 20 sucess stories
    os.makedirs('sector_successes_plots', exist_ok=True)

    

    for index, row in twohundred_sector_successes.head(20).iterrows():
        ranks = data[(data['country'] == row['country']) & (data['name_short_en'] == row['product'])]
        year_ranks = ranks.sort_values(by='year', ascending=True)
        rank_data = year_ranks[rank_metric].tolist()
        window_names = year_ranks['year'].tolist()
        plt.figure()
        plt.plot(window_names, rank_data, marker='o')
        plt.title(f'{row["country"]}: {row["product"]} ({row["hs_code"]})')
        plt.grid(True)
        output = os.path.join( rank_metric + '_sector_successes_plots', f'{row["country"]}_{row["product"]}_{row["hs_code"]}.png')
        plt.tight_layout()
        plt.savefig(output)
        plt.close()

    # converts and saves sorted DataFrame to table (for interpretability)
    plt.figure(figsize=(12, 6))
    plt.axis('off')
    plt.title("Top 20 Sector successes")
    table = plt.table(cellText=twohundred_sector_successes.head(20).values, colLabels=twohundred_sector_successes.columns, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(6)
    table.auto_set_column_width(col=list(range(len(twohundred_sector_successes.columns))))
    table_path = os.path.join('200sectorsuccesses', rank_metric + '_top20sectorsuccesstable.png')
    plt.savefig(table_path)

    csv_file_path1 = os.path.join('200sectorsuccesses', rank_metric + '_detailed_rank_shifts')
    csv_file_path2 = os.path.join('200sectorsuccesses', rank_metric + '_overall_rank_shifts')
    detailed_two_hundred_sorted.to_csv(csv_file_path1,index=False)
    twohundred_sector_successes.to_csv(csv_file_path2,index=False)




