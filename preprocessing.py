import pandas as pd
import os
from typing import Callable
import numpy as np

# opening data folder
data_path = os.path.join(os.path.dirname(__file__), 'data')

# uncomment and run if product and location data downloaded as TAB file
# product_path = os.path.join(data_path, 'product_hs92.tab')
# country_path = os.path.join(data_path, 'location_country.tab')

# uncomment and run if product and location data downloaded as CSV file
# product_path = os.path.join(data_path, 'product_hs92.csv')
# country_path = os.path.join(data_path, 'location_country.csv')

# read in CSVs for preprocessing
product_codes_df = pd.read_csv(product_path, sep=',')
country_df = pd.read_csv(country_path, sep=',')

def lower_standardize(x: str):
    """
    Lowercases all inputted data.

    Input:
        x - string to lowercase
    Output:
        final_word - lowercased string
    """
    lower = x.lower()
    final_word = lower.replace(" ","_")
    return final_word

# applies lowercase standardization to products in product and country DataFrames
product_codes_df['name_short_en'] = product_codes_df['name_short_en'].apply(lower_standardize)
country_df['name_short_en'] = country_df['name_short_en'].apply(lower_standardize)

# intitalizes dictionaries to translate between product IDs and product codes
productids_to_codes_dict = {}

# intitalizes dictionaries to translate between product codes and product names
productcodes_to_names_dict = {}

# populates dictionary for product IDs and product codes
for i in range(len(product_codes_df['name_short_en'])):
    productids_to_codes_dict[product_codes_df['product_id'][i]] = (product_codes_df['code'][i], product_codes_df['name_short_en'][i])

# populates dictionary for product codes and product names
for i in range(len(product_codes_df['name_short_en'])):
    productcodes_to_names_dict[product_codes_df['code'][i]] = product_codes_df['name_short_en'][i]

# replicates dictionary logic for country IDs and country names
countryid_to_country_dict = {}

for i in range(len(country_df['name_short_en'])):
   countryid_to_country_dict[country_df['country_id'][i]] = country_df['name_short_en'][i]

# replicates dictionary logic for country IDs and country codes
countryid_to_code_dict = {}

for i in range(len(country_df['iso3_code'])):
    countryid_to_code_dict[country_df['country_id'][i]] =  country_df['iso3_code'][i]

def add_productnames_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Adds product names as columns to DataFrame.

    Input:
        dataframe - DataFrame to add product name column
    Output:
        dataframe - DataFrame with product name column
    """
    dataframe['product_code'] = dataframe['product_id'].apply(lambda x: productids_to_codes_dict[x][0])
    dataframe['name_short_en'] = dataframe['product_id'].apply(lambda x: productids_to_codes_dict[x][1])
    return dataframe

def add_countrynames_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Adds country names as columns to DataFrame.

    Input:
        dataframe - DataFrame to add country name column
    Output:
        dataframe - DataFrame with country name column
    """
    dataframe['country'] = dataframe['country_id'].apply(lambda x: countryid_to_country_dict[x])
    dataframe['country_code'] = dataframe['country_id'].apply(lambda x: countryid_to_code_dict[x])
    return dataframe

def remove_missing_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Removes missing NaN values from DataFrame.

    Input:
        dataframe - DataFrame to remove NaN values
    Output:
        dataframe - DataFrame with removed NaN values
    """
    df_cleaned = dataframe.dropna(subset=["country_id", "product_id", "year", "export_value", "product_code", "name_short_en"])
    return df_cleaned

# United Nations Country M49 Codes for excluded countries
oecd = [36, 40, 56, 124, 152, 170, 188, 203, 208, 233, 246, 250, 276, 300, 348,
        352, 372, 376, 380, 392, 410, 428, 440, 442, 484, 528, 554, 578, 616,
        620, 703, 705, 724, 752, 756, 792, 826, 581, 840, 850, 156, 344, 446]

# HS Codes for excluded goods
goods = [26, 27, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 83]

# applies exclusion criteria function
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

    return df_filtered


# calculating one criteria for ranking: export per capita
def export_per_capita(dataframe: pd.DataFrame) -> pd.DataFrame:
    ''' Function to calculate export per capita uses population data. This makes the export values of each country 
    more comparable as it adjusts for larger export values due to population size,
    
    Input:
        dataframe - DataFrame to calculate export per capita
    Output:
        dataframe - DataFrame with calculated export per capita
    '''

    # load population data
    population_path = os.path.join(os.path.dirname(__file__), 'data/API_SP.POP.TOTL_DS2_en_csv_v2_900.csv')
    population_df = pd.read_csv(population_path)
    
    # convert "Country Name" to lowercase in both dataframes
    population_df["Country Name"] = population_df["Country Name"].apply(lower_standardize)
    
    # convert population columns to numeric
    population_df.iloc[:, 4:] = population_df.iloc[:, 4:].apply(pd.to_numeric, errors="coerce")
    
    # initialize a new column for export_per_capita
    export_per_capita_values = []
    
    for _, row in dataframe.iterrows():
        # get population for the specific country and year
        year = str(row["year"])  # ensure year is string to match population_df columns
        population = population_df.loc[
            (population_df["Country Code"] == row["country_code"]), year
        ] # directly access the single value
        
        if population.empty:
            print(f"Warning: No population data found for {row['country']} in year {year}")
            export_per_capita = None
        else:
            population_value = population.values[0]
            # calculate export_per_capita
            if not pd.isna(population_value):  # ensure population value is valid
                export_per_capita = row["export_value"] / int(population_value)
            else:
                export_per_capita = None  # handle missing population data
        export_per_capita_values.append(export_per_capita)
    
    # add the new column to the DataFrame
    dataframe["export_per_capita"] = export_per_capita_values
    return dataframe

def calculate_rca(dataframe: pd.DataFrame) -> pd.DataFrame:
    '''Calculates the relative comparative advantage each country has for a 
    product in relation to the total percentage of world exports the product export is responsible for.
     
    Input:
        dataframe - DataFrame to calculate RCA on
    Output:
        dataframe - DataFrame with calculated RCA 
    '''

    # calculates export values per country per year
    export_value_sum_per_country = dataframe.groupby(['country_code', 'year']).sum()['export_value']

    # calculates export values per product per year
    export_value_sum_per_product = dataframe.groupby(['product_code', 'year']).sum()['export_value']

    # calculates total export value across year
    total_exports_by_year = dataframe.groupby('year').sum()['export_value']

    rca_values = []

    # iterates through each row of DataFrame
    for _, row in dataframe.iterrows():
        # RCA calculation
        country_code = row['country_code']
        product_code = row['product_code']
        year = row['year']
        country_export_ratio = row['export_value'] / export_value_sum_per_country[country_code][year]
        world_export_ratio = export_value_sum_per_product[product_code][year]/total_exports_by_year[year]
        rca = country_export_ratio / world_export_ratio
        rca_values.append(rca)
    
    dataframe['rca'] = rca_values
    return dataframe

def ranking(dataframe: pd.DataFrame) -> pd.DataFrame:
    '''Calculates rankings based on three different metrics (export per capita,
    RCA, and global market share.)
     
    Input:
        dataframe - DataFrame to calculate rankings on
    Output:
        dataframe - DataFrame with calculated rankings 
    '''
    # groups DataFrame by product and year
    groups_by_product = dataframe.groupby(['product_code','year'])
    updated_groups = []

    for name, group in groups_by_product:
        # ranks by export per capita
        group['rank_per_capita'] = group['export_per_capita'].rank(ascending=True, method='min')

        # ranks by RCA
        group['rank_rca'] = group['rca'].rank(ascending=True, method='min')

        # ranks by global market share
        group['rank_market_share'] = group['global_market_share'].rank(ascending=True, method='min')

        # ranks by average of above three rankings
        group['rank_avg'] = group[['rank_per_capita', 'rank_rca', 'rank_market_share']].mean(axis=1)

        # appends all rankings to updated group
        updated_groups.append(group)
    
    # concatenates updated group to resulting DataFrame
    result_dataframe = pd.concat(updated_groups)

    return result_dataframe
    
for file in os.listdir(data_path):
    # extracts name and extension of each file
    base_name = os.path.basename(file)
    name, ext = os.path.splitext(base_name)

    # checks file type of each file in "data" folder
    if ext.lower() == '.csv' and name != "location_country" and name != "product_hs92": ###
        # extracts path name of given file and reads to dataframe
        file_path = os.path.join(data_path, file)
        df = pd.read_csv(file_path)

        # applies all functions to add new columns
        product_df = add_productnames_columns(df)
        country_name_df = add_countrynames_columns(product_df)
        missing_df = remove_missing_values(country_name_df)
        exp_per_capita_df = export_per_capita(missing_df)
        exclude_df = exclude(missing_df, file_path, name)
        rca_df = calculate_rca(exclude_df)
        rank_df = ranking(rca_df)

        # saves filtered CSV to data folder
        directory = os.path.dirname(file_path)
        csv_path = os.path.join(directory, "filt_" + name + ".csv")
        rank_df.to_csv(csv_path,index=False)
