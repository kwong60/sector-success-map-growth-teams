
import pandas as pd
import os
import matplotlib.pyplot as plt



#takes in preprocessed data that has been filtered
original_data_path = os.path.join(os.path.dirname(__file__),'2_digit_data/filt_hs92_country_product_year_2.csv')
original_data = pd.read_csv(original_data_path)


# adding the eci filter
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
original_data = original_data[original_data['country_id'].isin(new_eci_countryids)]

clean_data_file_path = os.path.join('2_digit_data', "clean_hs92_country_product_year_2.csv")
original_data.to_csv(clean_data_file_path, index=False)


