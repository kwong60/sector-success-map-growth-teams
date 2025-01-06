import pandas as pd
import os
from typing import Callable
import numpy as np

data_path = os.path.join(os.path.dirname(__file__), 'data')
product_path = os.path.join(data_path, 'product_hs92.tab')
product_codes_df = pd.read_csv(product_path, sep='\t')

def lower_standardize(x: str):
    lower = x.lower()
    final_word = lower.replace(" ","_")
    return final_word

product_codes_df['name_short_en'] = product_codes_df['name_short_en'].apply(lower_standardize)

productids_to_codes_dict = {}

productcodes_to_names_dict = {}

for i in range(len(product_codes_df['name_short_en'])):
    productids_to_codes_dict[product_codes_df['product_id'][i]] = (product_codes_df['code'][i], product_codes_df['name_short_en'][i])

for i in range(len(product_codes_df['name_short_en'])):
    productcodes_to_names_dict[product_codes_df['code'][i]] = product_codes_df['name_short_en'][i]




def filter_each_file(filter_function:  Callable[[pd.DataFrame], pd.DataFrame]) -> None:
    for file in os.listdir(data_path):
        # extracts name and extension of each file
        base_name = os.path.basename(file)
        name, ext = os.path.splitext(base_name)
        print(f"{file} being filtered by {filter_function.__name__}")

        if ext.lower() == '.csv':
            file_path = os.path.join(data_path, file)
            try:
                df = pd.read_csv(file_path)
                filtered_df = filter_function(df)
                filtered_df.to_csv(file_path, index=False)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")


def add_productnames_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe['code'] = dataframe['product_id'].apply(lambda x: productids_to_codes_dict[x][0])
    dataframe['name_short_en'] = dataframe['product_id'].apply(lambda x: productids_to_codes_dict[x][1])
    return dataframe


def remove_missing_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    df_cleaned = dataframe.dropna(subset=["country_id", "product_id", "year", "export_value", "code", "name_short_en", "eci"])
    return df_cleaned



def filter_outliers(dataframe: pd.DataFrame) -> pd.DataFrame:
    df_filtered= dataframe[(dataframe["eci"] <= 2.5) & (dataframe["eci"] >= -2.5) & (dataframe["coi"] >= -1.5) & (dataframe["coi"] <= 3.5)]
    return df_filtered




def main():
    print ("nothing to filter")
    
    


if __name__ == "__main__":
    main()

