import pandas as pd
import os
import matplotlib.pyplot as plt

filt_data_path =  os.path.join(os.path.dirname(__file__),'data/filt_hs92_country_product_year_2.csv')
filtered_data = pd.read_csv(filt_data_path)

section1_list = [1,2,3,4,5]
section2_list = [6,7,8,9,10,11,12,13,14]
section3_list = [15]
section4_list = [16,17,18,19,20,21,22,23,24]
section5_list = [25,26,27]
section6_list = [28,29,30,31,32,33,34,35,36,37,38]
section7_list = [39,40]
section8_list = [41,42,43]
section9_list = [44,45,46]
section10_list = [47,48,49]
section11_list = [50,51,52,53,54,55,56,57,58,59,60,61,62,63]
section12_list = [64,65,66,67]
section13_list = [68,69,70]
section14_list = [71]
section15_list = [72,73,74,75,76,77,78,79,80,81,82,83]
section16_list = [84,85]
section17_list = [86,87,88,89]
section18_list = [90,91,92]
section19_list = [93]
section20_list = [94,95,96]
section21_list = [97]
section22_list = [98,99]

section_dictionary = {1:"Live Animals; Animal Products", 
                      2:"Live Animals; Animal Products", 
                      3: "Live Animals; Animal Products",
                      4: "Live Animals; Animal Products",
                      5: "Live Animals; Animal Products",
                      6: "Vegetable products",
                      7: "Vegetable products",
                      8: "Vegetable products",
                      9: "Vegetable products",
                      10: "Vegetable products",
                      11: "Vegetable products",
                      12: "Vegetable products",
                      13: "Vegetable products",
                      14: "Vegetable products",
                      15: "Animal or Vegetable Fats",
                      16: "Prepared Foodstuffs",
                      17: "Prepared Foodstuffs", 
                      18: "Prepared Foodstuffs",
                      19: "Prepared Foodstuffs",
                      20: "Prepared Foodstuffs",
                      21: "Prepared Foodstuffs",
                      22: "Prepared Foodstuffs",
                      23: "Prepared Foodstuffs",
                      24: "Prepared Foodstuffs",
                      25: "Mineral Products",
                      26: "Mineral Products",
                      27: "Mineral Products",
                      28: "Products of the Chemical or Allied Industries",
                      29: "Products of the Chemical or Allied Industries",
                      30: "Products of the Chemical or Allied Industries",
                      31: "Products of the Chemical or Allied Industries",
                      32: "Products of the Chemical or Allied Industries",
                      33: "Products of the Chemical or Allied Industries",
                      34: "Products of the Chemical or Allied Industries",
                      35: "Products of the Chemical or Allied Industries",
                      36: "Products of the Chemical or Allied Industries",
                      37: "Products of the Chemical or Allied Industries",
                      38: "Products of the Chemical or Allied Industries",
                      39: "Articles of Plastic and Rubber",
                      40: "Articles of Plastic and Rubber",
                      41: "Raw Hides and Skins",
                      42: "Raw Hides and Skins",
                      43: "Raw Hides and Skins",
                      44: "Articles of Wood",
                      45: "Articles of Wood",
                      46: "Articles of Wood",
                      47: "Pulp of Wood",
                      48: "Pulp of Wood",
                      49: "Pulp of Wood",
                      50: "Articles of Textiles",
                      51: "Articles of Textiles",
                      52: "Articles of Textiles",
                      53: "Articles of Textiles",
                      54: "Articles of Textiles",
                      55: "Articles of Textiles",
                      56: "Articles of Textiles",
                      57: "Articles of Textiles",
                      58: "Articles of Textiles",
                      59: "Articles of Textiles",
                      60: "Articles of Textiles",
                      61: "Articles of Textiles",
                      62: "Articles of Textiles",
                      63: "Articles of Textiles",
                      64: "Footwear, Headgear, Umbrellas, Feathers",
                      65: "Footwear, Headgear, Umbrellas, Feathers",
                      66: "Footwear, Headgear, Umbrellas, Feathers",
                      67: "Footwear, Headgear, Umbrellas, Feathers",
                      68: "Articles of Stone, Ceramics, Glass",
                      69: "Articles of Stone, Ceramics, Glass",
                      70: "Articles of Stone, Ceramics, Glass",
                      71: "Precious or Semi-precious Stones and Metals",
                      72: "Articles of Base Metal",
                      73: "Articles of Base Metal",
                      74: "Articles of Base Metal",
                      75: "Articles of Base Metal",
                      76: "Articles of Base Metal",
                      77: "Articles of Base Metal",
                      78: "Articles of Base Metal",
                      79: "Articles of Base Metal",
                      80: "Articles of Base Metal",
                      81: "Articles of Base Metal",
                      82: "Articles of Base Metal",
                      83: "Articles of Base Metal",
                      84: "Machinery and Mechanical Appliances",
                      85: "Machinery and Mechanical Appliances",
                      86: "Vehicles and Transport Equipment",
                      87: "Vehicles and Transport Equipment",
                      88: "Vehicles and Transport Equipment", 
                      89: "Vehicles and Transport Equipment",
                      90: "Optical Instruments, Clocks, Musical Instruments",
                      91: "Optical Instruments, Clocks, Musical Instruments",
                      92: "Optical Instruments, Clocks, Musical Instruments",
                      93: "Arms and Ammunition",
                      94: "Miscellaneous Manufactured Articles",
                      95: "Miscellaneous Manufactured Articles",
                      96: "Miscellaneous Manufactured Articles",
                      97: "Collectors' Art and Antiques",
                      98: "Special Classification provisions and Temporary Legislation",
                      99: "Special Classification provisions and Temporary Legislation"
}
product_section = []

for index, row in filtered_data.iterrows():
    product_section.append(section_dictionary[int(row['product_code'])])

filtered_data.drop('name_short_en', axis=1)
filtered_data["name_short_en"] = product_section


grouped = filtered_data[['country_id','name_short_en', "year",'global_market_share','eci', "export_per_capita", "rca"]] \
    .groupby(["country_id", "name_short_en", "year"]) \
    .sum() \
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

