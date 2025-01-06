import pandas as pd
import os

# United Nations Country M49 Codes for excluded countries
oecd = [36, 40, 56, 124, 152, 170, 188, 203, 208, 233, 246, 250, 276, 300, 348,
        352, 372, 376, 380, 392, 410, 428, 440, 442, 484, 528, 554, 578, 616,
        620, 703, 705, 724, 752, 756, 792, 826, 581, 840, 850, 156, 344, 446]

# HS Codes for excluded goods
goods = [26, 27, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 83]

def exclude(path: str, name: str):
    """
    Excludes Western/OECD countries and natural resource-based sectors based on
    exclusion criteria.
    
    Input:
        path - path to CSV
        name - name of CSV file
    """
    # reads CSV as pandas dataframe
    df = pd.read_csv(path)

    # filters excluded countries and goods
    # considers both countries and partner countries if applicable
    df_cols = df.columns.to_list()

    if "country_id" in df_cols and "partner_country_id" in df_cols:
        df_mask = df["country_id"].isin(oecd) | df["partner_country_id"].isin(oecd) | \
            df["product_id"].astype(str).apply(lambda x: any(x.startswith(str(good)) for good in goods))
        
    else:
        df_mask = df["country_id"].isin(oecd) | df["product_id"].astype(str).apply(lambda x: any(x.startswith(str(good)) for good in goods))

    df_filtered = df[~df_mask]

    # saves filtered CSV to data folder
    directory = os.path.dirname(path)
    csv_path = os.path.join(directory, "filt_" + name + ".csv")
    df_filtered.to_csv(csv_path, index=False)

# extracts path of data folder 
# assumes CSV files are in folder titled "data", in same folder as preprocessing.py)
data_path = os.path.join(os.path.dirname(__file__), 'data')

for file in os.listdir(data_path):
    # extracts name and extension of each file
    base_name = os.path.basename(file)
    name, ext = os.path.splitext(base_name)

    # checks file type of each file in "data" folder
    if ext.lower() == '.csv':
        # extracts path name of given file and inputs into pandas conversion function
        file_path = os.path.join(data_path, file)
        exclude(file_path, name)