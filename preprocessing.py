import pandas as pd
import os
from typing import Callable
import numpy as np

data_path = os.path.join(os.path.dirname(__file__), 'data')

# run if product and location data downloaded as TAB file
# product_path = os.path.join(data_path, 'product_hs92.tab')
# country_path = os.path.join(data_path, 'location_country.tab')

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
    dataframe['code'] = dataframe['product_id'].apply(lambda x: productids_to_codes_dict[x][0])
    dataframe['name_short_en'] = dataframe['product_id'].apply(lambda x: productids_to_codes_dict[x][1])
    return dataframe

def add_countrynames_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe['country'] = dataframe['country_id'].apply(lambda x: countryid_to_country_dict[x])
    return dataframe

def remove_missing_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    df_cleaned = dataframe.dropna(subset=["country_id", "product_id", "year", "export_value", "code", "name_short_en", "eci"])
    return df_cleaned

def filter_outliers(dataframe: pd.DataFrame) -> pd.DataFrame:
    df_filtered= dataframe[(dataframe["eci"] <= 2.5) & (dataframe["eci"] >= -2.5) & (dataframe["coi"] >= -1.5) & (dataframe["coi"] <= 3.5)]
    return df_filtered

# United Nations Country M49 Codes for excluded countries
oecd = [36, 40, 56, 124, 152, 170, 188, 203, 208, 233, 246, 250, 276, 300, 348,
        352, 372, 376, 380, 392, 410, 428, 440, 442, 484, 528, 554, 578, 616,
        620, 703, 705, 724, 752, 756, 792, 826, 581, 840, 850, 156, 344, 446]

# HS Codes for excluded goods
goods = [26, 27, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 83]

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

def main():

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
            outlier_df = filter_outliers(missing_df)
            exclude(outlier_df, file_path, name)

if __name__ == "__main__":
    main()