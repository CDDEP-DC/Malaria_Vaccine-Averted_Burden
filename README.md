# Malaria_Vaccine-Averted_Burden

This repository contains the data and code used in the paper "Malaria Vaccine Impact on Cases, Resistant Cases, and Deaths: A Modeling Study", which can be accessed at https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4231231. The model projects health burden averted with a vaccine similar to RTS,S administered yearly to infants in the WHO Africa Region from 2021-2030. 

WORKFLOW:

Malaria_Data.py reads files from the Data folder and outputs Malaria_Data.csv for analysis and Malaria_Country_Parameters.csv for Supplementary Table 2.

Malaria_PE.py reads Malaria_Data.csv, runs the model to produce point estimates by country-year, and outputs Malaria_PE.csv.

Malaria_MC.py reads Malaria_Data.csv and Malaria_PE.csv, generates uncertainty intervals using Monte Carlo simulation (1,000 iterations), and outputs results by country-year in Malaria_MC.csv.

Malaria_Post.py reads Malaria_MC.csv and generates results by country (Malaria_byCountry.csv and Malaria_byCountry.xlsx) for Table 1, Figures 6-8, and Supplementary Tables 4-8 and generates results by year (Malaria_byYear.csv) for Figures 2-5.

Malaria_LineGraphs.R reads Malaria_byYear.csv and outputs Malaria_Cases_byYear.tiff (Figure 2), Malaria_ResCases_byYear.tiff (Figure 3), Malaria_Deaths_byYear.tiff (Figure 4), and Malaria_ResCases_byTFR.tiff (Figure 5).

Malaria_Map_Cases.R reads Malaria_ByCountry.csv, pop.csv, and afr_g2014_2013_0.shp and outputs Malaria_Map_Cases.pdf (Figure 6). Similarly, Malaria_Map_ResCases.R ouptus Malaria_ResMap_Cases.pdf (Figure 7), and Malaria_Map_Deaths.R outputs Malaria_Map_Deaths.pdf (Figure 8).

Outcomes averted per capita for each country are generated at the end of each Malaria_Map_[Outcome].R file. 
