import pandas as pd
import os
import matplotlib.pyplot as plt

filt_data_path =  os.path.join(os.path.dirname(__file__),'data/filt_hs92_country_product_year_2.csv')
filtered_data = pd.read_csv(filt_data_path)

# section1_list = [1,2,3,4,5]
# section2_list = [6,7,8,9,10,11,12,13,14]
# section3_list = [15]
# section4_list = [16,17,18,19,20,21,22,23,24]
# section5_list = [25,26,27]
# section6_list = [28,29,30,31,32,33,34,35,36,37,38]
# section7_list = [39,40]
# section8_list = [41,42,43]
# section9_list = [44,45,46]
# section10_list = [47,48,49]
# section11_list = [50,51,52,53,54,55,56,57,58,59,60,61,62,63]
# section12_list = [64,65,66,67]
# section13_list = [68,69,70]
# section14_list = [71]
# section15_list = [72,73,74,75,76,77,78,79,80,81,82,83]
# section16_list = [84,85]
# section17_list = [86,87,88,89]
# section18_list = [90,91,92]
# section19_list = [93]
# section20_list = [94,95,96]
# section21_list = [97]
# section22_list = [98,99]

# dictionary mapping each HS code to a section name
section_dictionary = {1:"Live Animals; Animal Products (1)", 
                      2:"Live Animals; Animal Products (1)", 
                      3: "Live Animals; Animal Products (1)",
                      4: "Live Animals; Animal Products (1)",
                      5: "Live Animals; Animal Products (1)",
                      6: "Vegetable products (2)",
                      7: "Vegetable products (2)",
                      8: "Vegetable products (2)",
                      9: "Vegetable products (2)",
                      10: "Vegetable products (2)",
                      11: "Vegetable products (2)",
                      12: "Vegetable products (2)",
                      13: "Vegetable products (2)",
                      14: "Vegetable products (2)",
                      15: "Animal or Vegetable Fats (3)",
                      16: "Prepared Foodstuffs (4)",
                      17: "Prepared Foodstuffs (4)", 
                      18: "Prepared Foodstuffs (4)",
                      19: "Prepared Foodstuffs (4)",
                      20: "Prepared Foodstuffs (4)",
                      21: "Prepared Foodstuffs (4)",
                      22: "Prepared Foodstuffs (4)",
                      23: "Prepared Foodstuffs (4)",
                      24: "Prepared Foodstuffs (4)",
                      25: "Mineral Products (5)",
                      26: "Mineral Products (5)",
                      27: "Mineral Products (5)",
                      28: "Products of the Chemical or Allied Industries (6)",
                      29: "Products of the Chemical or Allied Industries (6)",
                      30: "Products of the Chemical or Allied Industries (6)",
                      31: "Products of the Chemical or Allied Industries (6)",
                      32: "Products of the Chemical or Allied Industries (6)",
                      33: "Products of the Chemical or Allied Industries (6)",
                      34: "Products of the Chemical or Allied Industries (6)",
                      35: "Products of the Chemical or Allied Industries (6)",
                      36: "Products of the Chemical or Allied Industries (6)",
                      37: "Products of the Chemical or Allied Industries (6)",
                      38: "Products of the Chemical or Allied Industries (6)",
                      39: "Articles of Plastic and Rubber (7)",
                      40: "Articles of Plastic and Rubber (7)",
                      41: "Raw Hides and Skins (8)",
                      42: "Raw Hides and Skins (8)",
                      43: "Raw Hides and Skins (8)",
                      44: "Articles of Wood (9)",
                      45: "Articles of Wood (9)",
                      46: "Articles of Wood (9)",
                      47: "Pulp of Wood (10)",
                      48: "Pulp of Wood (10)",
                      49: "Pulp of Wood (10)",
                      50: "Articles of Textiles (11)",
                      51: "Articles of Textiles (11)",
                      52: "Articles of Textiles (11)",
                      53: "Articles of Textiles (11)",
                      54: "Articles of Textiles (11)",
                      55: "Articles of Textiles (11)",
                      56: "Articles of Textiles (11)",
                      57: "Articles of Textiles (11)",
                      58: "Articles of Textiles (11)",
                      59: "Articles of Textiles (11)",
                      60: "Articles of Textiles (11)",
                      61: "Articles of Textiles (11)",
                      62: "Articles of Textiles (11)",
                      63: "Articles of Textiles (11)",
                      64: "Footwear, Headgear, Umbrellas, Feathers (12)",
                      65: "Footwear, Headgear, Umbrellas, Feathers (12)",
                      66: "Footwear, Headgear, Umbrellas, Feathers (12)",
                      67: "Footwear, Headgear, Umbrellas, Feathers (12)",
                      68: "Articles of Stone, Ceramics, Glass (13)",
                      69: "Articles of Stone, Ceramics, Glass (13)",
                      70: "Articles of Stone, Ceramics, Glass (13)",
                      71: "Precious or Semi-precious Stones and Metals (14)",
                      72: "Articles of Base Metal (15)",
                      73: "Articles of Base Metal (15)",
                      74: "Articles of Base Metal (15)",
                      75: "Articles of Base Metal (15)",
                      76: "Articles of Base Metal (15)",
                      77: "Articles of Base Metal (15)",
                      78: "Articles of Base Metal (15)",
                      79: "Articles of Base Metal (15)",
                      80: "Articles of Base Metal (15)",
                      81: "Articles of Base Metal (15)",
                      82: "Articles of Base Metal (15)",
                      83: "Articles of Base Metal (15)",
                      84: "Machinery and Mechanical Appliances (16)",
                      85: "Machinery and Mechanical Appliances (16)",
                      86: "Vehicles and Transport Equipment (17)",
                      87: "Vehicles and Transport Equipment (17)",
                      88: "Vehicles and Transport Equipment (17)", 
                      89: "Vehicles and Transport Equipment (17)",
                      90: "Optical Instruments, Clocks, Musical Instruments (18)",
                      91: "Optical Instruments, Clocks, Musical Instruments (18)",
                      92: "Optical Instruments, Clocks, Musical Instruments (18)",
                      93: "Arms and Ammunition (19)",
                      94: "Miscellaneous Manufactured Articles (20)",
                      95: "Miscellaneous Manufactured Articles (20)",
                      96: "Miscellaneous Manufactured Articles (20)",
                      97: "Collectors' Art and Antiques (21)",
                      98: "Special Classification provisions and Temporary Legislation (22)",
                      99: "Special Classification provisions and Temporary Legislation (22)"
}
product_section = []

for index, row in filtered_data.iterrows():
    product_section.append(section_dictionary[int(row['product_code'])])

filtered_data.drop('name_short_en', axis=1)
filtered_data["name_short_en"] = product_section

grouped = filtered_data[['country', 'country_id','name_short_en', "year",'global_market_share','eci', "export_per_capita", "rca"]] \
    .groupby(["country", "country_id", "name_short_en", "year"]) \
    .sum()\
    .reset_index()  # Ensure groupby columns are included in CSV

def ranking(dataframe: pd.DataFrame) -> pd.DataFrame:
    '''Calculates rankings based on three different metrics (export per capita,
    RCA, and global market share.)
     
    Input:
        dataframe - DataFrame to calculate rankings on
    Output:
        dataframe - DataFrame with calculated rankings 
    '''
    # groups DataFrame by product and year
    groups_by_product = dataframe.groupby(['name_short_en','year'])
    updated_groups = []

    for name, group in groups_by_product:
        # ranks by export per capita
        group['rank_per_capita'] = group['export_per_capita'].rank(ascending=False, method='min')

        # ranks by RCA
        group['rank_rca'] = group['rca'].rank(ascending=False, method='min')

        # ranks by global market share
        group['rank_market_share'] = group['global_market_share'].rank(ascending=False, method='min')

        # ranks by average of above three rankings
        group['rank_avg'] = group[['rank_per_capita', 'rank_rca', 'rank_market_share']].mean(axis=1)

        # appends all rankings to updated group
        updated_groups.append(group)
    
    # concatenates updated group to resulting DataFrame
    result_dataframe = pd.concat(updated_groups)

    return result_dataframe

new_grouped = ranking(grouped)

new_grouped_file_path = os.path.join('data', "grouped_hs92_country_product_year_2.csv")
new_grouped.to_csv(new_grouped_file_path, index=False)

