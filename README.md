# Growth Teams: Sector Success Map Data Analysis

To replicate the analysis at a 2-digit product level, no download, conversion, or preprocessing is necessary as the cleaned dataset has already been pushed to GitHub.

Skip to the [Sector Success Analysis section](#sector-success-analysis) or [Emerging Sector Success Analysis section](#emerging-sector-success-analysis) of the README depending on which analysis you would like to replicate.

If you would like to replicate the analysis at a different product level or are having issues pulling the cleaned dataset at the 2-digit level, you may want to download, convert, and preprocess the data from the beginning as follows.

## Downloading the Data

After downloading all files from the [dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/T4CHWJ),
unzip the download and move all files to the folder titled "data". 

## Converting the Data
The dataset is DTA-formatted (STATA-compatible) and should be converted to CSVs (Comma-Separated Values). Run data_conversion.py. If you are given a FileNotFound error, ensure the "data" folder is located in the same folder as data_conversion.py. This process can take up to 30-45 minutes. 

When the file is done running, check the "data" folder to ensure each DTA file has a corresponding CSV file.

## Preprocessing the Data
To clean the data, run preprocessing.py. This file standardizes capitalization, translates country and product
codes to their English names, removes missing values, and excludes certain countries and products from the
dataset as delineated in the exclusion criteria. Please note that China, Hong Kong, and Macao are not excluded during this step to offer variations in the analysis; they may be excluded later on if the user chooses. 

This file will also calculate the RCA (Revealed Comparative Advantage), exports per capita, and four different rankings based on various criteria (RCA, exports per capita, global market share, and average of all three).

This make take up to an hour to run. You can check the progress of the preprocessing by opening the "data" folder. Once a file is processed, it will appear as "filt_" followed by the original name of the CSV.

## Modifying the Data
To apply modifications, run modifications.py after doing preprocessing and before running any of the analyses. 

To add additional filters to make the selection of the sector successes more narrow, we took into eci_rankings as well as the ranking of a country, product pair at the end of the time period -- 2022. After preprocessing, we applied these filters to the data saved in data/filt_hs92_country_product_year_2.csv. We then downloaded eci rankings for countries which we saved as rankings.tab in the references folder. We calculated the eci rank shifts for each country from 1995 to 2022 and sorted according to the biggest rank shifts. We took the top 50 rank shifts and derived the countries that had these shifts. In our data, we only filtered for these countries so that we could only focus on those countries for analysis and this made the criteria for success stories more specific. 

We also applied an additional filter (seen in analysis_navya.py) to only look at countries that had a ranking (according to whichever rank_metric we were looking at -- ex: rank_avg, rank_rca, etc) of 30 or less in 2022. This narrowed our criteria for what constituted a success further.


## Sector Success Analysis
To replicate the 500 sector successes analysis, run analysis_navya.py. The program finds the 500 top sector success stories ( countries and product) and also within each success story looks at which window of time was the success at its peak. The file also creates plots of this change over time (over windows of time) for each top 20 country within the 500 sector successes. 

Each success story was determined by calculating the rank shifts in each of the 4 rank metrics (rank_avg, rank_rca, rank_export_per_capita, rank_market_share) between 1995 and 2022. Then the 500 country product pairs with the biggest success stories were selected. We did this separately for each rank metric so that we could compare the results and determine which metric was the best method for measuring a success story. 

Also, we created several variations of the results so that we could compare how different factors affected the results. We created the tables and plots for the success stories for the data with modifications and the data without any of the modified filters. We also varied whether china, macao and hong kong were excluded in the criteria or not to see if it affected the success stories determined. We noticed that even when we included china, with or without the modifctaions filters, mainland china did not feature as a success story, but macao did. So after 1995, it doesn't look like china improved greatly in its ranking for any of the metrics for any of the products. 



## Emerging Sector Success Analysis
To replicate the emerging sector successes analysis, run analysis_kara.py. This program will produce a plot of rankings over time for each emerging success case identified (each titled "{country}\_{product}.png") as well as a single plot with all of these cases overlaid (titled "top\_{number of cases}\_successes.png"). This file will also produce a new CSV with each success case's country, product, and shift in rank (slope) as well as an interpretable table PNG of this CSV.

This process is then replicated across various combinations of filters. One such filter is known as "modifications", in which a country must be in the top 30 ranked countries in 2022 (according to an inputted rank metric) as well as the top 50 countries based on ECI rank shifts between 1995 and 2022. Another such filter is whether or not the user would like to include China in the analysis.

At the bottom of this file, there are function calls to the analysis and plotting function (emerging_success()) demonstarting each combination of these filters as well as no filters at all. Comment out unwanted function calls accordingly. To change the parameters in this analysis (ranking metric, length of early versus recent years (where growth in recent years denotes emerging success), number of success cases displayed, use of general "modifications", and inclusion of China), alter the inputs in the function accordingly. The meaning and order of each input is noted directly above the function call in a comment.

## Results
Our results for these analyses are stored under the sector_successes and emerging_successes folders. 

Within both folders, there are four subfolders denoting the various combinations of filters applied (no_mod_no_china = no filters, mod = general modifications applied, china = china included, and mod_china = general modifications applied + china included).

Within those subfolders are five smaller folders, four of which each denote the ranking metric used to perform the analysis (exports per capita, RCA, global market share, and average of all three). In each of these four folders are 20 plots representing the top 20 cases. In the emerging successes analyses specifically, you will also find one more plot with all 20 of those plots overlaid.

There is also a fifth folder containing the CSVs and tables of the top 20 cases of all of these analyses and are labelled accordingly based on rank metric.

Please note that repeating the analysis will cause conflicts with directory and folder names. To avoid this, after running an analysis once, make sure to rename the results folders/save them elsewhere before running the analysis again.
