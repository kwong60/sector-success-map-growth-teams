# Growth Teams: Sector Success Map Data Analysis

To replicate the analysis at a 2-digit product level, no download, conversion, preprocessing, or modification is necessary as the cleaned dataset has already been pushed to GitHub.

Skip to the [Sector Success Analysis section](#sector-success-analysis) or [Emerging Sector Success Analysis section](#emerging-sector-success-analysis) of the README depending on which analysis you would like to replicate.

If you would like to replicate the analysis at a different product level or are having issues pulling the cleaned dataset at the 2-digit level, you may want to download, convert, preprocess, and modify the data from the beginning as follows.


## Downloading the Data

After downloading all files from the [dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/T4CHWJ),
unzip the download and move all files to the folder titled "data". 

If you could not pull the data folder from GitHub, create a new folder titled "data" instead and move the downloaded data there.


## Converting the Data
The dataset is DTA-formatted (STATA-compatible) and should be converted to CSVs (Comma-Separated Values). Run data_conversion.py. If you are given a FileNotFound error, ensure the "data" folder is located in the same folder as data_conversion.py. This process can take up to 30-45 minutes. 

When the file is done running, check the "data" folder to ensure each DTA file has a corresponding CSV file.


## Preprocessing the Data
To clean the data, run preprocessing.py.

This file standardizes capitalization, translates country and product
codes to their English names, removes missing values, and excludes certain countries and products from the
dataset as delineated in the exclusion criteria. Please note that China, Hong Kong, and Macao are not excluded during this step to offer variations in the analysis; they may be excluded later on if the user chooses. 

This file will also calculate the RCA (Revealed Comparative Advantage), exports per capita, and four different rankings based on various criteria (RCA, exports per capita, global market share, and average of all three).

This make take up to an hour to run. You can check the progress of the preprocessing by opening the "data" folder. Once a file is processed, it will appear as "filt_" followed by the original name of the CSV.


## Modifying the Data
To apply modifications, run modifications.py after preprocessing and before running any of the analyses. 

To add additional filters to make the selection of the sector successes more narrow, we took into account ECI rankings as well as the ranking of a (country, product) pair at the end of the time period (2022). After preprocessing, we applied these filters to the data saved in data/filt_hs92_country_product_year_2.csv. 

We downloaded ECI rankings for countries which we have already saved as rankings.tab in the references folder for future use. We calculated the ECI rank shifts for each country from 1995 to 2022 and sorted according to the biggest rank shifts. We took the top 50 rank shifts and derived the countries that had these shifts. In our data, we filtered for these countries so that we could only focus on those countries for analysis and thus made the criteria for success stories more specific. 

Modified data is then saved in data/clean_filt_hs92_country_product_year_2.csv.

We also applied an additional filter (seen in analysis_navya.py and analysis_kara.py) to only look at countries that had a ranking (according to whichever rank_metric we were looking at -- ex: rank_avg, rank_rca, etc) of 30 or less in 2022. This narrowed our criteria for what constituted a success further.


## Sector Success Analysis
To replicate the 500 sector successes analysis, run analysis_navya.py. The program finds the 500 top sector success stories ( countries and product) and also within each success story looks at which window of time was the success at its peak. The file also creates plots of this change over time (over windows of time) for each top 20 country within the 500 sector successes. 

Each success story was determined by calculating the rank shifts in each of the 4 rank metrics (rank_avg, rank_rca, rank_export_per_capita, rank_market_share) between 1995 and 2022. Then the 500 country product pairs with the biggest success stories were selected. We did this separately for each rank metric so that we could compare the results and determine which metric was the best method for measuring a success story. 

Also, we created several variations of the results so that we could compare how different factors affected the results. We created the tables and plots for the success stories for the data with modifications and the data without any of the modified filters. We also varied whether china, macao and hong kong were excluded in the criteria or not to see if it affected the success stories determined. We noticed that even when we included china, with or without the modifctaions filters, mainland china did not feature as a success story, but macao did. So after 1995, it doesn't look like china improved greatly in its ranking for any of the metrics for any of the products. 


## Emerging Sector Success Analysis
To replicate the emerging sector successes analysis, run analysis_kara.py. This program will produce a plot of rankings over time for each emerging success case identified (each titled "{country}\_{product}.png") as well as a single plot with all of these cases overlaid (titled "top\_{number of cases}\_successes.png"). This file will also produce a new CSV with each success case's country, product, and shift in rank (slope) as well as an interpretable table PNG of this CSV.

This process is then replicated across various combinations of filters. One such filter is known as "modifications", in which a country must be in the top 30 ranked countries in 2022 (according to an inputted rank metric) as well as the top 50 countries based on ECI rank shifts between 1995 and 2022. Another such filter is whether or not the user would like to include China in the analysis.

At the bottom of this file, there are function calls to the analysis and plotting function (emerging_success()) demonstarting each combination of these filters as well as no filters at all. Comment out unwanted function calls accordingly. To change the parameters in this analysis (ranking metric, length of early versus recent years (where growth in recent years denotes emerging success), number of success cases displayed, use of general "modifications", and inclusion of China), alter the inputs in the function accordingly. The meaning and order of each input is noted directly above the function call in a comment.

## Grouped Analyses
Both the sector successes and emerging successes analyses were repeated using a grouping method, where the analysis was completed under
country-section pairs instead of country-product pairs. A full dictionary mapping product HS codes to each of these larger sections can be found
in grouped.py.

To replicate the grouped analysis, first run grouped.py on the CSV you would like to group. A CSV of the same name preceded by "grouped_" should appear in your data folder.

If you want to apply the above modifications to this grouped data, ensure the file path in modifications.py points to the grouped data you just created and run modifications.py. A CSV of the same name preceded by "clean_" should appear in your data folder.

If you are performing the grouped analysis at a 2-digit level, you may skip the above parts as the grouped data at a 2-digit level has already been pushed.

To run the sector successes analysis, run group_navya.py, ensuring the file paths at the top of group_navya.py point to the correct grouped data and the correct modified group data. They are currently set to the grouped data at a 2-digit level.

To run the emerging successes analysis, run group_kara.py, ensuring the file paths at the top of group_kara.py point to the correct grouped data and the correct modified group data. They are currently set to the grouped data at a 2-digit level.

## Results
Our results for these analyses are stored under the sector_successes and emerging_successes folders. Grouped analyses are stored in folders
of the same name, preceded by "grouped_". 

Within all folders, there are four subfolders denoting the various combinations of filters applied (no_mod_no_china = no filters, mod = general modifications applied, china = china included, and mod_china = general modifications applied + china included).

Within those subfolders are five smaller folders, four of which each denote the ranking metric used to perform the analysis (exports per capita, RCA, global market share, and average of all three). In each of these four folders are 20 plots representing the top 20 cases. In the emerging successes analyses specifically, you will also find one more plot with all 20 of those plots superimposed.

There is also a fifth folder containing the CSVs and tables of the top 20 cases of all of these analyses and are labelled accordingly based on rank metric.

Please note that repeating the analysis will cause conflicts with directory and folder names. To avoid this, after running an analysis once, make sure to rename the results folders/move them elsewhere before running the analysis again.


## Notes about References

Please note that certain datasets were used in this analysis regardless of the product digit level. These datasets (e.g. population, ECI ranking, United Nations M49 country codes, and product HS codes) are located in the "references" folder to avoid path conflicts.

The United Nations M49 codes and the product HS codes were downloaded from the [Classifications Data](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/3BAL1O) from the Harvard Growth Lab.

The population dataset was downloaded from the [World Bank](https://data.worldbank.org/indicator/SP.POP.TOTL?name_desc=false). Please note that this dataset does not initially include Taiwan. For the purposes of this analysis, Taiwan was manually included using population data from [macrotrends.net](https://www.macrotrends.net/global-metrics/countries/TWN/taiwan/population).

The ECI ranking data was taken from the rankings.tab in the [Harvard dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/XTAQMC).
