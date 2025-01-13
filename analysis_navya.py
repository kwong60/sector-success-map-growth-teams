import pandas as pd
import preprocessing
import os


#function to sort the biggest ranking shifts for each product level
def entire_time_period_ranking_shift(rank_column_name: str):
    data_path = os.path.join(os.path.dirname(__file__),'data/filt_hs92_country_product_year_2.csv')
    data = pd.read_csv(data_path)
    grouped = data.groupby(['country_code','product_code'])
    new_data = pd.DataFrame(columns=['country_code', 'product_code', 'total_rank_shift'])
    country_code_list = []
    product_code_list = []
    ranking_shift_list = []
    for name, group in grouped:
        country_code_list.append(name[0])
        product_code_list.append(name[1])
        if(len(group[group['year'] == 2022]) == 1) and (len(group[group['year'] == 1995]) == 1):
            end_ranking = group[group['year'] == 2022][rank_column_name].iloc[0]
            beg_ranking = group[group['year'] == 1995][rank_column_name].iloc[0]
            rank_shift = end_ranking - beg_ranking
        else:
            rank_shift = None
        ranking_shift_list.append(rank_shift)

    new_data['country_code'] = country_code_list
    new_data['product_code'] = product_code_list
    new_data['total_rank_shift'] = ranking_shift_list
    new_grouped = new_data.groupby('product_code')
    sorted_data_list = []
    for name, group in new_data.groupby('product_code'):
    # Drop rows with NaN values in 'total_rank_shift' before sorting
        group = group.dropna(subset=['total_rank_shift'])
        sorted_group = group.sort_values(by='total_rank_shift', ascending=False)
        sorted_data_list.append(sorted_group)
    return sorted_data_list

print(entire_time_period_ranking_shift('rank_avg'))
