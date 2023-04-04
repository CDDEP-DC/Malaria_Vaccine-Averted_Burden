# Malaria_Vaccine-Averted_Burden

This repository contains the data and code used in the manuscript "Malaria Vaccine Impact on Cases, Drug Resistant Cases, and Deaths in Africa: A Modeling Study", which can be accessed at https://doi.org/10.21203/rs.3.rs-2362054/v1. The model projects health burden averted with a vaccine similar to RTS,S administered yearly to one-year-olds in the WHO Africa Region from 2021-2030. 

FOLDERS
1. Code: Python code for analysis and R code for figures 
2. Data: Input data files (Sources in Malaria_Data.py)
3. Results: Generated .csv, .tiff, and .pdf files

WORKFLOW
1. Update OneDrive = "[Main file path]" in all Python and R scripts.

2. Malaria_Data.py reads files from the Data folder and outputs Data/malaria_df.csv, runs Malaria_Imputation.py, and outputs Results/Malaria_Data.csv and Pop1_byCountry.csv for analysis.

3. Malaria_Imputation.py reads Data/malaria_df.csv and uses multivariate regression to impute missing values for treatment received rate and treatment failure rates (Supplementary Table 3). This script generages Results/Malaria_Imputation.png (Supplementary Figure 1) and Data/malaria_imputed.csv, which is used by Malaria_Data.py.

4. Malaria_PE.py reads Results/Malaria_Data.csv, runs the model to produce point estimates by country-year, and outputs Results/Malaria_PE.csv and Results/Malaria_Country_Parameters.csv (Supplementary Tables 4 and 5).

5. Malaria_MC.py reads Results/Malaria_Data.csv and Results/Malaria_PE.csv, generates uncertainty intervals using Monte Carlo simulation (1,000 iterations), and outputs results by country-year in Results/Malaria_MC.csv.

6. Malaria_Post.py reads Results/Malaria_MC.csv and outputs Results/Malaria_byCountry.csv, Results/Malaria_byCountry_per1000.csv (Supplementary Tables 6-10), Results/Malaria_Total_per1000.csv, and Results/Malaria_byYear.csv'.

7. Malaria_LineGraphs.R reads Resutls/Malaria_byYear.csv and outputs Malaria_CasesAvt_byYear.tiff (Figure 2), Malaria_ResCasesAvt_byYear.tiff (Figure 3), Malaria_DeathsAvt_byYear.tiff (Figure 4), Malaria_ResCases_byTFR.tiff (Figure 5), Malaria_CasesAll_byYear.tiff (Supplementary Figure 2), Malaria_ResCasesAll_byYear.tiff (Supplementary Figure 3), and Malaria_DeathsAll_byYear.tiff (Supplementary Figure 4) in the Results folder.

8. Malaria_Map_Cases.R reads Results/Malaria_ByCountry.csv and files in "Data/CreateChoroplethPlotFiles" to generate Malaria_Map_Cases.pdf (Supplementary Table 5). Similarly, Malaria_Map_ResCases.R ouptus Malaria_ResMap_Cases.pdf (Supplementary Table 6), and Malaria_Map_Deaths.R outputs Malaria_Map_Deaths.pdf (Supplementary Table 7) in the Results folder.

