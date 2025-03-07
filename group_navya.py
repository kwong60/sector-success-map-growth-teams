import pandas as pd
import os
import matplotlib.pyplot as plt

#takes in preprocessed data with applied modification filters
data_path = os.path.join(os.path.dirname(__file__),'data/clean_grouped_hs92_country_product_year_2.csv')
data = pd.read_csv(data_path)

#if we are not applying the filters and just running modifications then use:
data_path2 = os.path.join(os.path.dirname(__file__),'data/grouped_hs92_country_product_year_2.csv')
original_data = pd.read_csv(data_path2)

# if we are excluding china in addition to the existing countries for exclusion criteria:
exc_countries_china = ["australia", "austria", "belgium", "canada", "chile", "colombia",
                 "costa_rica", "czechia", "denmark", "estonia", "finland", "france",
                 "germany", "greece", "hungary", "iceland", "ireland", "israel",
                 "italy", "japan", "south_korea", "latvia", "lithuania", "luxembourg",
                 "mexico", "netherlands", "new_zealand", "norway", "poland", 
                 "portugal", "slovakia", "slovenia", "spain", "sweden", "switzerland",
                 "turkiye", "united_kingdom", "united_states_of_america", "us_virgin_islands",
                 "us_minor_outlying_islands", "china", "hong_kong", "macao"]


#if we are not excluding china:
exc_countries = ["australia", "austria", "belgium", "canada", "chile", "colombia",
                 "costa_rica", "czechia", "denmark", "estonia", "finland", "france",
                 "germany", "greece", "hungary", "iceland", "ireland", "israel",
                 "italy", "japan", "south_korea", "latvia", "lithuania", "luxembourg",
                 "mexico", "netherlands", "new_zealand", "norway", "poland", 
                 "portugal", "slovakia", "slovenia", "spain", "sweden", "switzerland",
                 "turkiye", "united_kingdom", "united_states_of_america", "us_virgin_islands",
                 "us_minor_outlying_islands"]

#excluded goods for exclusion criteria
exc_goods = ["ores_slag_and_ash", "mineral_fuels,_oils_and_waxes", "precious_metals_and_stones",
             "iron_and_steel", "articles_of_iron_or_steel", "copper", "nickel", "aluminum",
             "lead", "zinc", "tin", "other_base_metals", "miscellaneous_articles_of_base_metal"]

#function to sort the biggest ranking shifts for each product level
def entire_time_period_ranking_shift(input_data: pd.DataFrame, rank_column_name: str, start: int, end: int, modification: bool, china: bool):
    '''Given a start and end year, this function  calculates the rank shift based on a given ranking system for each country-product pair '''

    #if china boolean is false, we are excluding china
    if not china:
        oecd = [156,344,446]
        df_mask = input_data['country_id'].isin(oecd)
        input_data = input_data[~df_mask]

    #if modification is true then we want to filter for the top countries whose ranking is at most 30 as of 2022 - the final year:
    if modification:
        filtered_data = input_data[(input_data['year'] == 2022) & (input_data[rank_column_name] < 30)]
        filtered_countries = filtered_data['country'].tolist()
        filtered_products = filtered_data['name_short_en'].tolist()
        clean_data = input_data[(input_data['country'].isin(filtered_countries)) & (input_data['name_short_en'].isin(filtered_products))]
        grouped = clean_data.groupby(['country','name_short_en'])


    #if modification is false, we are using the original data without running the filters in modification.py or any additional filters: 
    else:    
        grouped = input_data.groupby(['country','name_short_en'])


    #new dataframe to populate after the ranking shift calculation for sector successes is done:
    new_data = pd.DataFrame(columns=['country', 'name_short_en','1995_export_value', '2022_export_value', f'{start}-{end}_rank_shift'])
    country_list = []
    product_code_list = []
    beginning_export_values_list = []
    final_export_values_list = []
    hs_code_list =[]
    ranking_shift_list = []

    #in each country, product group we are calculating the rank shift overall usually when start=1995, end=2022
    for name, group in grouped:
        #if china is to be excluded or not: 
        if china:
            excluded_countries = exc_countries
        else:
            excluded_countries = exc_countries_china
            

        if (name[0] in excluded_countries) or (name[1] in exc_goods):
            continue

        country_list.append(name[0])
        product_code_list.append(name[1])
        #hs_code_list.append(group['product_code'].iloc[0])
        beginning_export_values_list.append(group['1995_export_value'].iloc[0])
        final_export_values_list.append(group['2022_export_value'].iloc[0])
        
        #each country, product for a particular year should only appear once for the ranking shift calculation to work: 
        if(len(group[group['year'] == end]) == 1) and (len(group[group['year'] == start]) == 1):
            end_ranking = group[group['year'] == end][rank_column_name].iloc[0]
            beg_ranking = group[group['year'] == start][rank_column_name].iloc[0]
            rank_shift = end_ranking - beg_ranking
        else:
            end_ranking = None
            rank_shift = None
        ranking_shift_list.append(rank_shift)

    #populate the series for the dataframe
    new_data['country'] = country_list
    new_data['name_short_en'] = product_code_list
    #new_data['hs_code'] = hs_code_list
    new_data['1995_export_value'] = beginning_export_values_list
    new_data['2022_export_value'] = final_export_values_list
    new_data[f'{start}-{end}_rank_shift'] = ranking_shift_list

    #drop the ranking shifts that are None out of the dataframe as they would interfere with the sorting logic:
    new_data = new_data.dropna(subset=[f'{start}-{end}_rank_shift'])
    
    return new_data



#Function to look at the big ranking shifts and drops for smaller windows within the 500 success stories
def window_time_period_ranking_shift(input_data: pd.DataFrame, time_window: int, rank_column_name: str, modification: bool, china: bool):
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
        window_data = entire_time_period_ranking_shift(input_data, rank_column_name, start, end, modification,china)
        window_data = window_data.drop(columns=["1995_export_value", "2022_export_value"])
        all_windows_data = pd.merge(
            all_windows_data, window_data, on=['country', 'name_short_en'], how='outer'
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

def generate_outputs_plots(input_data: pd.DataFrame, rank_metric: str, modification: bool, china: bool):
    
    
    #If we want data with the modification filters use this:
    if modification:
        
        if china:
            directory_name = "group_mod_with_china_"
        else:
            directory_name = "group_mod_no_china_"
    
    #else: use the original_data:
    else:
        
        if china:
            directory_name = "group_china_"
        else:
            directory_name = "group_"

    overall_time_period = entire_time_period_ranking_shift(input_data, rank_metric, 1995,2022,modification,china)
    windows_overall = window_time_period_ranking_shift(input_data, 5, rank_metric,modification,china)
    #Gets the top 500 sector success stories
    fivehundred_sector_successes = overall_time_period.sort_values(by='1995-2022_rank_shift', ascending=True).head(1000)

    #gets the detailed rank shifts for each window of 5 years within the 500 sector successes:
    detailed_five_hundred = windows_overall.merge(fivehundred_sector_successes, on=['country', 'name_short_en'], how='inner')
    detailed_five_hundred_sorted = detailed_five_hundred.sort_values('1995-2022_rank_shift', ascending=True)

    #create a folder for the plots: 
    os.makedirs(f'{directory_name}{rank_metric}_sector_successes_plots', exist_ok=True)

    #to plot the top 50 sector successes for the rank metric to visualize the data and top stories:
    for index, row in fivehundred_sector_successes.head(20).iterrows():
        ranks = input_data[(input_data['country'] == row['country']) & (input_data['name_short_en'] == row['name_short_en'])]
        year_ranks = ranks.sort_values(by='year', ascending=True)
        rank_data = year_ranks[rank_metric].tolist()
        window_names = year_ranks['year'].tolist()
        plt.figure()
        plt.plot(window_names, rank_data, marker='o')
        plt.title(f'{row["country"]}: {row["name_short_en"]}')
        plt.grid(True)
        #output = os.path.join( 'mod_' + rank_metric + '_sector_successes_plots', f'{row["country"]}_{row["product"]}_{row["hs_code"]}.png')
        output = os.path.join( directory_name + rank_metric + '_sector_successes_plots', f'{row["country"]}_{row["name_short_en"]}')
        plt.tight_layout()
        plt.savefig(output)
        plt.close()


    #Create the folder
    os.makedirs(f'{directory_name}500sectorsuccesses_tables', exist_ok=True)
    

    # converts and saves sorted DataFrame to table (for interpretability)
    plt.figure(figsize=(12, 6))
    plt.axis('off')
    plt.title("Top 20 Sector successes")
    table = plt.table(cellText=fivehundred_sector_successes.head(20).values, colLabels=fivehundred_sector_successes.columns, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(6)
    table.auto_set_column_width(col=list(range(len(fivehundred_sector_successes.columns))))
    table_path = os.path.join(f'{directory_name}500sectorsuccesses_tables', rank_metric + '_top20sectorsuccesstable')
    plt.savefig(table_path)


    csv_file_path1 = os.path.join(f'{directory_name}500sectorsuccesses_tables', rank_metric + '_detailed_rank_shifts')
    csv_file_path2 = os.path.join(f'{directory_name}500sectorsuccesses_tables', rank_metric + '_overall_rank_shifts')
    
    detailed_five_hundred_sorted.to_csv(csv_file_path1,index=False)
    fivehundred_sector_successes.to_csv(csv_file_path2,index=False)



#Function calls:

#Without modifications and without China:
generate_outputs_plots(original_data,"rank_avg", False,False)
generate_outputs_plots(original_data,"rank_market_share",False,False)
generate_outputs_plots(original_data,"rank_per_capita", False,False)
generate_outputs_plots(original_data,"rank_rca", False,False)

#With modifications but without China:
generate_outputs_plots(data,"rank_avg", True,False)
generate_outputs_plots(data,"rank_market_share",True,False)
generate_outputs_plots(data,"rank_per_capita", True,False)
generate_outputs_plots(data,"rank_rca", True, False)

#Without modifications but with China:
generate_outputs_plots(original_data,"rank_avg", False,True)
generate_outputs_plots(original_data,"rank_market_share",False,True)
generate_outputs_plots(original_data,"rank_per_capita", False,True)
generate_outputs_plots(original_data,"rank_rca", False,True)

#With modifications and with China
generate_outputs_plots(data,"rank_avg", True,True)
generate_outputs_plots(data, "rank_market_share",True,True)
generate_outputs_plots(data,"rank_per_capita",True,True)
generate_outputs_plots(data,"rank_rca", True,True)



