import pandas as pd
import os
import matplotlib.pyplot as plt

#takes in preprocessed data that has been filtered
data_path = os.path.join(os.path.dirname(__file__),'data/filt_hs92_country_product_year_2.csv')
data = pd.read_csv(data_path)

#function to sort the biggest ranking shifts for each product level
def entire_time_period_ranking_shift(rank_column_name: str, start: int, end: int ):
    '''Given a start and end year, this function  calculates the rank shift based on a given ranking system for each country-product pair '''

    grouped = data.groupby(['country','name_short_en'])
    new_data = pd.DataFrame(columns=['country', 'product',f'{start}-{end}_rank_shift'])
    country_code_list = []
    product_code_list = []
    ranking_shift_list = []
    for name, group in grouped:
        country_code_list.append(name[0])
        product_code_list.append(name[1])
        if(len(group[group['year'] == end]) == 1) and (len(group[group['year'] == start]) == 1):
            end_ranking = group[group['year'] == end][rank_column_name].iloc[0]
            beg_ranking = group[group['year'] == start][rank_column_name].iloc[0]
            rank_shift = end_ranking - beg_ranking
        else:
            rank_shift = None
        ranking_shift_list.append(rank_shift)

    new_data['country'] = country_code_list
    new_data['product'] = product_code_list
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
            all_windows_data, window_data, on=['country', 'product'], how='outer'
        ) if not all_windows_data.empty else window_data

    return all_windows_data

rank_metrics = data.columns[17:]


for rank_metric in rank_metrics:
    #Gets the top 200 sector success stories
    overall_time_period = entire_time_period_ranking_shift(rank_metric, 1995,2022)
    twohundred_sector_successes = overall_time_period.sort_values(by='1995-2022_rank_shift', ascending=False).head(200)

    windows_overall = window_time_period_ranking_shift(5, rank_metric)
    detailed_two_hundred = windows_overall.merge(twohundred_sector_successes, on=['country', 'product'], how='inner')
    detailed_two_hundred_sorted = detailed_two_hundred.sort_values('1995-2022_rank_shift', ascending=False)

    #Visualization for ranking shifts per window for the top 20 sucess stories
    os.makedirs('sector_successes_plots', exist_ok=True)

    window_names = ['1995-2000_rank_shift', '2000-2005_rank_shift', '2005-2010_rank_shift', '2010-2015_rank_shift', '2015-2020_rank_shift',
    '2020-2022_rank_shift']

    for index, row in detailed_two_hundred_sorted.head(20).iterrows():
        shifts = [row['1995-2000_rank_shift'], row['2000-2005_rank_shift'], row['2005-2010_rank_shift'], row['2010-2015_rank_shift'], row['2015-2020_rank_shift'], row['2020-2022_rank_shift']]
        plt.figure()
        plt.plot(window_names, shifts, marker='o')
        plt.title(f'{row["country"]}: {row["product"]}')
        plt.grid(True)
        output = os.path.join( rank_metric + '_sector_successes_plots', f'{row["country"]}_{row["product"]}.png')
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




