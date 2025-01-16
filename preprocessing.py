import pandas as pd
import os
from typing import Callable
import numpy as np

data_path = os.path.join(os.path.dirname(__file__), 'data')

# run if product and location data downloaded as TAB file
#product_path = os.path.join(data_path, 'product_hs92.tab')
#country_path = os.path.join(data_path, 'location_country.tab')

# run if product and location data downloaded as CSV file
product_path = os.path.join(data_path, 'product_hs92.csv')
country_path = os.path.join(data_path, 'location_country.csv')

product_codes_df = pd.read_csv(product_path, sep=',')
country_df = pd.read_csv(country_path, sep=',')

def lower_standardize(x: str):
    lower = x.lower()
    final_word = lower.replace(" ","_")
    return final_word

product_codes_df['name_short_en'] = product_codes_df['name_short_en'].apply(lower_standardize)
country_df['name_short_en'] = country_df['name_short_en'].apply(lower_standardize)

productids_to_codes_dict = {}

productcodes_to_names_dict = {}

for i in range(len(product_codes_df['name_short_en'])):
    productids_to_codes_dict[product_codes_df['product_id'][i]] = (product_codes_df['code'][i], product_codes_df['name_short_en'][i])

for i in range(len(product_codes_df['name_short_en'])):
    productcodes_to_names_dict[product_codes_df['code'][i]] = product_codes_df['name_short_en'][i]

countryid_to_country_dict = {}

for i in range(len(country_df['name_short_en'])):
   countryid_to_country_dict[country_df['country_id'][i]] = country_df['name_short_en'][i]

countryid_to_code_dict = {}

for i in range(len(country_df['iso3_code'])):
    countryid_to_code_dict[country_df['country_id'][i]] =  country_df['iso3_code'][i]



# def filter_each_file(filter_function:  Callable[[pd.DataFrame], pd.DataFrame]) -> None:
#     for file in os.listdir(data_path):
#         # extracts name and extension of each file
#         base_name = os.path.basename(file)
#         name, ext = os.path.splitext(base_name)
#         print(f"{file} being filtered by {filter_function.__name__}")

#         if ext.lower() == '.csv':
#             file_path = os.path.join(data_path, file)
#             try:
#                 df = pd.read_csv(file_path)
#                 filtered_df = filter_function(df)
#                 filtered_df.to_csv(file_path, index=False)

#             except Exception as e:
#                 print(f"Error processing file {file_path}: {e}")


def add_productnames_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe['product_code'] = dataframe['product_id'].apply(lambda x: productids_to_codes_dict[x][0])
    dataframe['name_short_en'] = dataframe['product_id'].apply(lambda x: productids_to_codes_dict[x][1])
    return dataframe

def add_countrynames_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe['country'] = dataframe['country_id'].apply(lambda x: countryid_to_country_dict[x])
    dataframe['country_code'] = dataframe['country_id'].apply(lambda x: countryid_to_code_dict[x])
    return dataframe

def remove_missing_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    df_cleaned = dataframe.dropna(subset=["country_id", "product_id", "year", "export_value", "product_code", "name_short_en"])
    return df_cleaned


#def filter_outliers(dataframe: pd.DataFrame) -> pd.DataFrame:
    #df_filtered= dataframe[(dataframe["eci"] <= 2.5) & (dataframe["eci"] >= -2.5) & (dataframe["coi"] >= -1.5) & (dataframe["coi"] <= 3.5)]
    #return df_filtered

# United Nations Country M49 Codes for excluded countries
oecd = [36, 40, 56, 124, 152, 170, 188, 203, 208, 233, 246, 250, 276, 300, 348,
        352, 372, 376, 380, 392, 410, 428, 440, 442, 484, 528, 554, 578, 616,
        620, 703, 705, 724, 752, 756, 792, 826, 581, 840, 850, 156, 344, 446]

# HS Codes for excluded goods
goods = [26, 27, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 83]

#Applying the exclusion criteria function
def exclude(df: pd.DataFrame, path: str, name: str):
    """
    Excludes Western/OECD countries and natural resource-based sectors based on
    exclusion criteria.
    
    Input:
        path - path to CSV
        name - name of CSV file
    """

    # filters excluded countries and goods
    df_mask = df["country_id"].isin(oecd) | df["product_id"].astype(str).apply(lambda x: any(x.startswith(str(good)) for good in goods))
    df_filtered = df[~df_mask]

    # saves filtered CSV to data folder
    directory = os.path.dirname(path)
    csv_path = os.path.join(directory, "filt_" + name + ".csv")
    df_filtered.to_csv(csv_path, index=False)


# calculating one criteria for ranking: export per capita
def export_per_capita(dataframe: pd.DataFrame) -> pd.DataFrame:
    ''' Function to calculate export per capita uses population data. This makes the export values of each country 
    more comparable as it adjusts for larger export values due to population size'''
    # Load population data
    population_path = os.path.join(os.path.dirname(__file__), 'data/API_SP.POP.TOTL_DS2_en_csv_v2_900.csv')
    population_df = pd.read_csv(population_path)
    
    # Convert "Country Name" to lowercase in both dataframes
    population_df["Country Name"] = population_df["Country Name"].apply(lower_standardize)
    
    # Convert population columns to numeric
    population_df.iloc[:, 4:] = population_df.iloc[:, 4:].apply(pd.to_numeric, errors="coerce")
    
    # Initialize a new column for export_per_capita
    export_per_capita_values = []
    
    for _, row in dataframe.iterrows():
        # Get population for the specific country and year
        year = str(row["year"])  # Ensure year is string to match population_df columns
        population = population_df.loc[
            (population_df["Country Code"] == row["country_code"]), year
        ] # Directly access the single value
        
        if population.empty:
            print(f"Warning: No population data found for {row['country']} in year {year}")
            export_per_capita = None
        else:
            population_value = population.values[0]
            # Calculate export_per_capita
            if not pd.isna(population_value):  # Ensure population value is valid
                export_per_capita = row["export_value"] / int(population_value)
            else:
                export_per_capita = None  # Handle missing population data
        export_per_capita_values.append(export_per_capita)
    
    # Add the new column to the DataFrame
    dataframe["export_per_capita"] = export_per_capita_values
    return dataframe
    

#Filtering all the datasets at different product levels for preprocessing. But the main dataset to 
#focus on is the hs92_country_product_year_2.csv which has products at the 2-digit-level
''''

    productlevel2datapath = os.path.join(os.path.dirname(__file__), 'data/hs92_country_product_year_2.csv')
    base_name = os.path.basename(productlevel2datapath)
    name, ext = os.path.splitext(base_name)
    df2 = pd.read_csv(productlevel2datapath)
    product_df2 = add_productnames_columns(df2)
    country_name_df2 = add_countrynames_columns(product_df2)
    missing_df2 = remove_missing_values(country_name_df2)
    export_capita_df2 = export_per_capita(missing_df2)
    exclude(export_capita_df2, productlevel2datapath, name)
    '''
    
'''
    for file in os.listdir(data_path):
        # extracts name and extension of each file
        base_name = os.path.basename(file)
        name, ext = os.path.splitext(base_name)

        # checks file type of each file in "data" folder
        if ext.lower() == '.csv' and name != "location_country" and name != "product_hs92":
            # extracts path name of given file and reads to dataframe
            file_path = os.path.join(data_path, file)
            df = pd.read_csv(file_path)

            product_df = add_productnames_columns(df)
            country_name_df = add_countrynames_columns(product_df)
            missing_df = remove_missing_values(country_name_df)
            #outlier_df = filter_outliers(missing_df)
            exclude(missing_df, file_path, name)
    
    '''

#Calculating another criteria for ranking: rca
def calculate_rca(dataframe: pd.DataFrame) -> pd.DataFrame:
    '''Calculates the relative comparative advantage each country has for a product in relation to the total percentage of world exports the product export is responsible for '''
    export_value_sum_per_country = dataframe.groupby(['country_code', 'year']).sum()['export_value']
    export_value_sum_per_product = dataframe.groupby(['product_code', 'year']).sum()['export_value']
    total_exports_by_year = dataframe.groupby('year').sum()['export_value']
    rca_values = []

    for _, row in dataframe.iterrows():
        country_code = row['country_code']
        product_code = row['product_code']
        year = row['year']
        country_export_ratio = row['export_value']/export_value_sum_per_country[country_code][year]
        world_export_ratio = export_value_sum_per_product[product_code][year]/total_exports_by_year[year]
        rca = country_export_ratio/world_export_ratio
        rca_values.append(rca)
    
    dataframe['rca'] = rca_values
    return dataframe

def ranking(dataframe: pd.DataFrame) -> pd.DataFrame:
    groups_by_product = dataframe.groupby(['product_code','year'])
    updated_groups = []
    for name, group in groups_by_product:
        group['rank_per_capita'] = group['export_per_capita'].rank(ascending=True, method='min')
        group['rank_rca'] = group['rca'].rank(ascending=True, method='min')
        group['rank_market_share'] = group['global_market_share'].rank(ascending=True, method='min')
        group['rank_avg'] = group[['rank_per_capita', 'rank_rca', 'rank_market_share']].mean(axis=1)
        updated_groups.append(group)
    
    result_dataframe = pd.concat(updated_groups)
    return result_dataframe





def main():

    #focusing on product level 2:
    new_path = os.path.join(os.path.dirname(__file__),'data/filt_hs92_country_product_year_2.csv')
    '''

    #add rca column:
    final_data = pd.read_csv(new_path)
    edited_data = calculate_rca(final_data)
    edited_data.to_csv(new_path, index=False)
    '''
    ranking_data = pd.read_csv(new_path)
    result_data = ranking(ranking_data)
    del result_data['rank']
    result_data.to_csv(new_path,index=False)
    

    



   

    




if __name__ == "__main__":
    main()