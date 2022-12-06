# Malaria_Vaccine-Averted_Burden

This repository contains the data and code used in the manuscript "Malaria Vaccine Impact on Cases, Drug Resistant Cases, and Deaths in Africa: A Modeling Study", which can be accessed at https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4231231. The model projects health burden averted with a vaccine similar to RTS,S administered yearly to one-year-olds in the WHO Africa Region from 2021-2030. 

FOLDERS
1. Code: Python code for analysis and R code for figures 
2. Data: Input data files (Sources in Malaria_Data.py)
3. Results: Generated .csv, .tiff, and .pdf files

WORKFLOW
1. Update OneDrive = "[Main file path]" in all Python and R scripts.

2. Malaria_Data.py reads files from the Data folder and outputs malaria_df.csv, runds Malaria_Imputation.py, and outputs Malaria_Data.csv for analysis.

3. Malaria_Imputation.py reads malaria_df.csv and uses multivariate regression to impute missing values for treatment received rate and treatment failure rates. This script generages Results/Malaria_Imputation.png (Supplementary Figure 1) and malaria_imputed.csv, which is used by Malaria_Data.py.

4. Malaria_PE.py reads Malaria_Data.csv, runs the model to produce point estimates by country-year, and outputs Results/Malaria_PE.csv and Malaria_Country_Parameters.csv (Supplementary Table 4).

5. Malaria_MC.py reads Malaria_Data.csv and Malaria_PE.csv, generates uncertainty intervals using Monte Carlo simulation (1,000 iterations), and outputs results by country-year in Malaria_MC.csv.

6. Malaria_Post.py reads Malaria_MC.csv and generates results by country (Results/Malaria_byCountry.csv and Results/Malaria_byCountry.xlsx) for Table 1, Figures 6-8, and Supplementary Tables 5-9 and generates results by year (Results/Malaria_byYear.csv) for Figures 2-5.

7. Malaria_LineGraphs.R reads Malaria_byYear.csv and outputs Malaria_CasesAvt_byYear.tiff (Figure 2), Malaria_ResCasesAvt_byYear.tiff (Figure 3), Malaria_DeathsAvt_byYear.tiff (Figure 4), Malaria_ResCases_byTFR.tiff (Figure 5), Malaria_CasesAll_byYear.tiff (Supplementary Figure 2), Malaria_ResCasesAll_byYear.tiff (Supplementary Figure 3), and Malaria_DeathsAll_byYear.tiff (Supplementary Figure 4).

8. Malaria_Map_Cases.R reads Malaria_ByCountry.csv and files in "Data/CreateChoroplethPlotFiles" to generate Malaria_Map_Cases.pdf (Figure 6). Similarly, Malaria_Map_ResCases.R ouptus Malaria_ResMap_Cases.pdf (Figure 7), and Malaria_Map_Deaths.R outputs Malaria_Map_Deaths.pdf (Figure 8).

9. Outcomes averted per 1,000 population for each country are generated at the end of each Malaria_Map_[Outcome].R file. 
