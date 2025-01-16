# Growth Teams: Sector Success Map Data Analysis

## Downloading the Data

After downloading all files from the [dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/T4CHWJ),
unzip the download and move all files to a new folder titled "data". Move the 
"data" folder inside the cloned repository.

You also want to download 'location_country.tab' and 'product_hs92.tab' from the [Classifications Data](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/3BAL1O). Move these files into the "data" folder you just created.

## Converting the Data
The dataset is DTA-formatted (STATA-compatible) and should be converted to CSVs (Comma-Separated Values). Run data_conversion.py. If you are given a FileNotFound error, ensure the "data" folder is located in the same folder as data_conversion.py. This process can take up to 30-45 minutes. 

When the file is done running, check the "data" folder to ensure each DTA file has a corresponding CSV file.

## Preprocessing the Data
To clean the data, run preprocessing.py. This file standardizes capitalization, translates country and product
codes to their English names, removes missing values, and excludes certain countries and products from the
dataset as delineated in the exclusion criteria. This file will also calculate the RCA (Revealed Comparative Advantage),
exports per capita, and four different rankings based on various criteria (RCA, exports prt capita, market share, and 
average of all three).

Note that preprocessing.py is currently set to process only hs92_country_product_year_2.csv to focus on products at the 2-digit level. To process the other datasets (1-digit, 4-digit, and 6-digit levels), uncomment the for loop to iterate through every file. This make take up to an hour to run.

You can check the progress of the preprocessing by opening the "data" folder. Once a file is processed, it will appear as "filt_" followed by the original name of the CSV.

