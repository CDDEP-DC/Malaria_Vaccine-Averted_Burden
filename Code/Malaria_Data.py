# Malaria Vaccine-Averted Burden
# Data processing
# Created by Alisa Hamilton

import pandas as pd
OneDrive = "/Users/alisahamilton/Library/CloudStorage/OneDrive-CenterforDiseaseDynamics,Economics&Policy/HIV Malaria Vaccine/2. Code/"

# Malaria prevalence
#malaria_url = "https://apps.who.int/gho/data/view.main.MALARIAINCIDENCEv?lang=en"
malaria = pd.read_csv(OneDrive + "Data/GHO Estimated Number of Malaria Cases.csv")
malaria = malaria.rename(columns={'Country':'country', 'Estimated number of malaria cases 2020':'malaria_prev_str'})
malaria = malaria.loc[(malaria['malaria_prev_str'] != 'No malaria')]
malaria['malaria_prev'] = malaria['malaria_prev_str'].str.split('[').str[0].str.replace(" ","").astype(float)
malaria['malaria_prev_min'] = malaria['malaria_prev_str'].str.split('[').str[1]
malaria['malaria_prev_min'] = malaria['malaria_prev_min'].str.split('-').str[0].str.replace(" ","").astype(float)
malaria['malaria_prev_max'] = malaria['malaria_prev_str'].str.split('-').str[1].str.replace(" ","").str.replace("]","").astype(float)
malaria = malaria.fillna(0).drop(columns=['malaria_prev_str'])
#for countries with estimate but no min or max. replace min and max with estimate -20% and +20%, respectively
malaria.loc[malaria['malaria_prev_min'] == 0, 'malaria_prev_min'] = malaria['malaria_prev'] * .8
malaria.loc[malaria['malaria_prev_max'] == 0, 'malaria_prev_max'] = malaria['malaria_prev'] * 1.2
# Côte D'Ivoire has has an error on the GHO website "7 571 801 [7 571 801 - 4 087 000]"
malaria.loc[malaria['country'] == "Côte d'Ivoire", 'malaria_prev_min'] = 4087000
malaria.loc[malaria['country'] == "Côte d'Ivoire", 'malaria_prev_max'] = 8000000

# Malaria incidence GHO
# malaria = malaria.iloc[1:]
# malaria['malaria_prev'] = malaria['malaria_prev'].str.split().str[0].astype(float)
# malaria['malaria_inc_rate'] = malaria['malaria_new_per1000'] / 1000
# malaria = malaria.drop(columns=['malaria_new_per1000'])
# malaria.loc[malaria['malaria_inc_rate'] > 0, 'malaria_endemic'] = 1

# IHME Malaria Prevalence (number) by Age group
#https://vizhub.healthdata.org/gbd-results/
ihme = pd.read_csv(OneDrive + "Data/IHME-MalariaPrevalence_Number_byAge.csv")
ihme = ihme[['location','age', 'val','upper','lower']]
ihme.rename(columns={'location':'country'}, inplace=True)
#ihme.loc[ihme['age'] == '<1 year', 'age'] = "0-4 years"
#ihme.loc[ihme['age'] == '1-4 years', 'age'] = "1-4 years"
#ihme = ihme.groupby(['location', 'age'])['val'].sum().reset_index()
#ihme = ihme.loc[(ihme['age'] == 'All ages') | (ihme['age'] == '1-4 years') | (ihme['age'] == '5-9 years')]
ihme_val = ihme.pivot(index='country', columns='age', values='val').reset_index()
ihme_val.rename(columns={'1-4 years':'1_4est'}, inplace=True)
ihme_val.rename(columns={'5-9 years':'5_9est'}, inplace=True)
ihme_val.rename(columns={'All ages':'Allages_est'}, inplace=True)

ihme_min = ihme.pivot(index='country', columns='age', values='lower').reset_index()
ihme_min.rename(columns={'1-4 years':'1_4min'}, inplace=True)
ihme_min.rename(columns={'5-9 years':'5_9min'}, inplace=True)
ihme_min.rename(columns={'All ages':'Allages_min'}, inplace=True)

ihme_max = ihme.pivot(index='country', columns='age', values='upper').reset_index()
ihme_max.rename(columns={'1-4 years':'1_4max'}, inplace=True)
ihme_max.rename(columns={'5-9 years':'5_9max'}, inplace=True)
ihme_max.rename(columns={'All ages':'Allages_max'}, inplace=True)

ihme_val['1_4prop_est'] = ihme_val['1_4est'] / ihme_val['Allages_est']
ihme_val['5_9prop_est'] = ihme_val['5_9est'] / ihme_val['Allages_est']
ihme_val = ihme_val[['country', '1_4prop_est', '5_9prop_est']]
# ihme_min['1_4prop_min'] = ihme_min['1-4 years'] / ihme_min['All ages']
# ihme_min['5_9prop_min'] = ihme_min['5-9 years'] / ihme_min['All ages']
# ihme_min = ihme_min[['country', '1_4prop_min', '5_9prop_min']]
# ihme_max['1_4prop_max'] = ihme_max['1-4 years'] / ihme_max['All ages']
# ihme_max['5_9prop_max'] = ihme_max['5-9 years'] / ihme_max['All ages']
# ihme_max = ihme_max[['country', '1_4prop_max', '5_9prop_max']]
# ihme = ihme_val.merge(ihme_min, how='left', on='country')
# ihme = ihme.merge(ihme_max, how='left', on='country')
malaria = malaria.merge(ihme_val, how='left', on='country')

# WHO regions
regions = pd.read_csv(OneDrive + "Data/HIV_Incidence.csv")
regions = regions.groupby(['ParentLocation', 'Location'])['Period'].max().reset_index().drop(columns=['Period'])
regions.rename(columns={'ParentLocation':'WHO_region', 'Location':'country'}, inplace=True)
regions = regions.replace("Côte d’Ivoire","Côte d'Ivoire")
malaria = malaria.merge(regions, how='left', on='country')
malaria.loc[(malaria['country'] == 'Sao Tome and Principe'), 'WHO_region'] = 'Africa'
malaria.loc[(malaria['country'] == 'Iraq'), 'WHO_region'] = 'Eastern Mediterranean'
malaria.loc[(malaria['country'] == 'Solomon Islands') | (malaria['country'] == 'Vanuatu'), 'WHO_region'] = 'Western Pacific'

# Malaria at risk rates
atrisk = pd.read_excel(OneDrive + 'Data/Malaria_endemic_at_risk_proportions.xlsx')
atrisk = atrisk.replace("Cote d'Ivoire", "Côte d'Ivoire")
atrisk['pop_total'] = atrisk['pop_total'].str.replace(" ","").astype(float)
atrisk['pop_atrisk'] = atrisk['pop_atrisk'].str.replace(" ","").astype(float)
atrisk['at_risk'] = atrisk['pop_atrisk'] / atrisk['pop_total']
malaria = pd.merge(malaria,atrisk, how='outer', on='country')
# French Guiana input manually. 212 cases in 2019. Incidence rate = 212 / 290,832
# 212 cases - https://www.statista.com/statistics/998391/number-reported-malaria-cases-french-guiana/
# 290,832 total pop - https://www.worldometers.info/world-population/french-guiana-population/
malaria.loc[malaria['country'] == 'French Guiana', 'malaria_prev'] = 212 #/ 290832

# #treatment failure rates for Afican countries
# tfr = pd.read_excel(OneDrive + "data/MTM_THERAPEUTIC_EFFICACY_STUDY_20220224.xlsx", sheet_name="Data")
# tfr = tfr.loc[tfr['PLASMODIUM_SPECIES'] == "P. falciparum"]
# tfr = tfr.loc[tfr['TREATMENT_FAILURE_PP'] != "  NA"]
# tfr['TREATMENT_FAILURE_PP'] = tfr['TREATMENT_FAILURE_PP'].astype(float) * 0.01
# tfr = tfr.loc[tfr['SAMPLE_SIZE'] >= 30]
# iso2 = pd.read_stata(OneDrive + "Data/iso2codes.dta")
# tfr = tfr.merge(iso2, how='left', on='ISO2')
# tfr = tfr.drop(tfr[(tfr['TREATMENT_FAILURE_PP'] > 0.1) & (tfr['DRUG_NAME'] == "DRUG_AL")].index)
# tfr = tfr.groupby('country')['TREATMENT_FAILURE_PP'].mean().reset_index()
# tfr = tfr.replace("Cote d'Ivoire", "Côte d'Ivoire")
# tfr.rename(columns={"TREATMENT_FAILURE_PP": "tfr_malaria"}, inplace = True)
# malaria = malaria.merge(tfr, how='left', on='country').sort_values(by='country').reset_index()

# Map countries with missing TFRs based on climate, under5 mortality, and GDP
# World Bank GDP per capita - https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=ZG
gdp = pd.read_excel(OneDrive + '/Data/AfricaGDPperCapita_byCountry.xls')
gdp = gdp[['Country Name', '2021']]
gdp.rename(columns={'Country Name':'country', '2021':'GDPpercap'}, inplace=True)
gdp = gdp.merge(regions, how='left', on='country')
gdp = gdp.loc[(gdp['WHO_region'] == 'Africa') | (gdp['country'] == 'Sao Tome and Principe')]
gdp.loc[gdp['country'] == 'Eritrea', 'GDPpercap'] = 642.5082588 #2011
gdp.loc[gdp['country'] == 'South Sudan', 'GDPpercap'] = 1119.651437 #2015
# GHO Under5 Mortality per 1,000 - https://www.who.int/data/gho/data/indicators/indicator-details/GHO/hem-under-five-mortality-rate-(deaths-per-1000-live-births)
under5 = pd.read_excel(OneDrive + '/Data/Under5_Mortality_byCountry.xlsx')
gdp_u5 = gdp.merge(under5, how='left', on='country')

# Treatment Received by Country from World Bank
# https://data.worldbank.org/indicator/SH.MLR.TRET.ZS
# Sources UNICEF, State of the World's Children, Childinfo, and Demographic and Health Surveys
# Indicator: Children with fever receiving antimalarial drugs (% of children under age 5 with fever)
trr = pd.read_csv(OneDrive + '/Data/TreatmentReceived_byCountry.csv')
countries = list(malaria['country'].unique())
trr = trr.loc[trr['Country Name'].isin(countries)]
trr = pd.wide_to_long(trr, stubnames='trr', i=['Country Name'], j='year').reset_index().sort_values(by=['Country Name','year'])
trr = trr.groupby('Country Name')['trr'].last().reset_index().rename(columns={'Country Name':'country'})
trr['trr'] = trr['trr']/100

#treatment failure rates for Afican countries
# Malaria Threats Map https://apps.who.int/malaria/maps/threats/
tfr = pd.read_excel(OneDrive + "Data/MTM_THERAPEUTIC_EFFICACY_STUDY_20220224.xlsx", sheet_name="Data")
tfr = tfr.loc[tfr['PLASMODIUM_SPECIES'] == "P. falciparum"]
tfr = tfr.loc[tfr['TREATMENT_FAILURE_PP'] != "  NA"]
tfr['TREATMENT_FAILURE_PP'] = tfr['TREATMENT_FAILURE_PP'].astype(float) * 0.01
tfr = tfr.loc[tfr['SAMPLE_SIZE'] >= 30]
iso2 = pd.read_stata(OneDrive + "Data/iso2codes.dta")
tfr = tfr.merge(iso2, how='left', on='ISO2')
tfr = tfr.drop(tfr[(tfr['TREATMENT_FAILURE_PP'] > 0.1) & (tfr['DRUG_NAME'] == "DRUG_AL")].index)
tfr = tfr.groupby('country')['TREATMENT_FAILURE_PP'].mean().reset_index()
tfr = tfr.replace("Cote d'Ivoire", "Côte d'Ivoire")
tfr.rename(columns={"TREATMENT_FAILURE_PP": "tfr"}, inplace = True)

# Export for Malaria_Imputation.py
malaria_df = gdp_u5.merge(trr, how='left',on='country')
malaria_df = malaria_df.merge(tfr, how='left',on='country').drop(columns=['WHO_region'])
malaria_df.to_csv(OneDrive + 'Data/malaria_df.csv')

# Run Malaria_Imputation to impute missing values and generate Supplementary Figure 1
from Malaria_Imputation import runImputation

#Imputed data for TRR and TFR from Malaria_Imputation.py
impute = pd.read_csv(OneDrive + 'malaria_imputed.csv')
impute.loc[impute['country'] == 'Botswana', 'trr'] = impute['pred_trr'] 
impute.loc[(impute['country'] == 'Botswana') | 
           (impute['country'] == 'Eswatini') | 
           (impute['country'] == 'Namibia') | 
           (impute['country'] == 'South Africa') |
           (impute['country'] == 'South Sudan'), 'tfr'] = impute['pred_tfr']
impute = impute[['country','trr','tfr']]
malaria = malaria.merge(impute,how='left',on='country')

# Adjust TFRs for countries with out any studies
# malaria.loc[malaria['country'] == 'Botswana', 'tfr_malaria'] = 0.0332 #Kenya
# malaria.loc[malaria['country'] == 'Eswatini', 'tfr_malaria'] = 0.0332 #Kenya
# malaria.loc[malaria['country'] == 'Namibia', 'tfr_malaria'] = 0.0332 #Kenya
# malaria.loc[malaria['country'] == 'South Africa', 'tfr_malaria'] = 0.0332 #Kenya
# malaria.loc[malaria['country'] == 'South Sudan', 'tfr_malaria'] = 0.0447 #Cameroon

#CFRs
low_trans_countries = ['Botswana', 'Comoros', 'Eritrea', 'Eswatini', 'Ethiopia', 'Madagascar', 'Namibia', 'Zimbabwe']

deaths = pd.read_csv(OneDrive + 'Data/Estimated number of malaria deaths by country.csv')
deaths = deaths.loc[(deaths['ParentLocation'] == 'Africa') & (deaths['Period'] == 2017)]
deaths = deaths[['Location','FactValueNumeric']]
deaths.rename(columns={"Location": "country", 'FactValueNumeric':'deaths'}, inplace = True)

cases = pd.read_csv(OneDrive + 'Data/Estimated number of malaria cases by country.csv')
cases = cases.loc[(cases['ParentLocation'] == 'Africa') & (cases['Period'] == 2017)]
cases = cases[['Location','FactValueNumeric']]
cases.rename(columns={"Location": "country", 'FactValueNumeric':'cases'}, inplace = True)

CFR_malaria = deaths.merge(cases, how='left', on='country')
CFR_malaria['CFR_malaria'] = CFR_malaria['deaths'] / CFR_malaria['cases']
CFR_malaria.loc[CFR_malaria['country'].isin(low_trans_countries), 'CFR_malaria'] = 0.00256
CFR_malaria.loc[CFR_malaria['CFR_malaria'] < 0.00256, 'CFR_malaria'] = 0.00256
CFR_malaria = CFR_malaria[['country','CFR_malaria']]
CFR_malaria = CFR_malaria.replace("Côte d’Ivoire", "Côte d'Ivoire")

malaria = malaria.merge(CFR_malaria, how='left', on='country')

# Severe malaria
#sevmal = pd.read_excel(OneDrive + 'data/Severe malaria rates.xlsx')
#malaria = malaria.merge(sevmal, how='left', on='country')

# Population by age group
#pop_url = "https://population.un.org/wpp/Download/Standard/CSV"
countries = list(malaria.country.unique())
pop = pd.read_csv(OneDrive + 'Data/WPP2019_PopulationBySingleAgeSex_2020-2100.csv')
pop = pop.loc[(pop['Time'] >= 2020) & (pop['Time'] < 2031)]
pop = pop.replace("Dem. People's Republic of Korea", "Democratic People's Republic of Korea")
pop = pop.replace("North Macedonia", "The former Yugoslav Republic of Macedonia")
pop = pop.replace("United Kingdom", "United Kingdom of Great Britain and Northern Ireland")
pop = pop.loc[pop['Location'].isin(countries)]
pop = pop[['Location', 'Time', 'AgeGrp', 'PopTotal']]
pop = pop.pivot_table(values='PopTotal', index=['Location', 'Time'], columns='AgeGrp').reset_index()
pop = pop.rename(columns={'Time':'year', 'Location':'country'})
pop['Pop1_4'] = (pop[1] + pop[2] + pop[3] + pop[4])*1000
pop['Pop5_9'] = (pop[5] + pop[6] + pop[7] + pop[8] +  pop[9])*1000
pop = pop[['country', 'year', 1,'Pop1_4', 'Pop5_9']]
pop2 = pop.loc[pop['year'] == 2021]
pop2 = pop2.drop(columns=['year', 1])
pop = pop.drop(columns=['Pop1_4', 'Pop5_9'])
pop = pop.merge(pop2, how='left', on='country')

# pop['month'] = [list(range(1, 13)) for _ in range(pop.shape[0])]
# pop = pop.explode('month').reset_index(drop=True)
# pop['month'] = pop['month'].astype(int)
# pop['year_month'] = pop['year'].astype(str) + '/' + pop['month'].astype(str)
# pop['year_month'] = pd.to_datetime(pop['year_month']).dt.strftime('%Y/%m')
# pop[1] = pop[1]/12

final = malaria.merge(pop, how='left', on='country').sort_values(['WHO_region','country']).set_index(['WHO_region','country']).reset_index()
#final['malaria_inc_rate'] = final['malaria_inc_rate']/12

# # Age-stratafied pop
# final.loc[final['year'] <= 2030, 'inc_byage'] = final['malaria_prev'] * final['5_9prop_est'] / final['Pop5_9']
# final.loc[final['year'] <= 2024, 'inc_byage'] = final['malaria_prev'] * final['1_4prop_est'] / final['Pop1_4']

# Difference VE scenarios
final.loc[final['year'] > 2020, 'VE1'] = .4
final.loc[final['year'] > 2024, 'VE1'] = 0
final.loc[final['year'] == 2021, 'VE2'] = .8
final.loc[final['year'] == 2022, 'VE2'] = .6
final.loc[final['year'] == 2023, 'VE2'] = .4
final.loc[final['year'] == 2024, 'VE2'] = .2
final.loc[final['year'] >= 2025, 'VE2'] = 0
final['VE3'] = .4

# Increasing Resistance Scenario - each country's TFR incrementaly increases to 80% by 2030
final_lst = []
for country in countries:
    data = final.loc[final['country'] == country]
    #data = final.loc[final['country'] ==  "Angola"]
    delta_tfr = (0.8 - data['tfr'].values[0]) / 9
    data.loc[data['year'] == 2021, 'tfr_increasing'] = data['tfr']
    data.loc[data['year'] == 2022, 'tfr_increasing'] = data['tfr'] + delta_tfr
    data.loc[data['year'] == 2023, 'tfr_increasing'] = data['tfr'] + delta_tfr*2
    data.loc[data['year'] == 2024, 'tfr_increasing'] = data['tfr'] + delta_tfr*3
    data.loc[data['year'] == 2025, 'tfr_increasing'] = data['tfr'] + delta_tfr*4
    data.loc[data['year'] == 2026, 'tfr_increasing'] = data['tfr'] + delta_tfr*5
    data.loc[data['year'] == 2027, 'tfr_increasing'] = data['tfr'] + delta_tfr*6
    data.loc[data['year'] == 2028, 'tfr_increasing'] = data['tfr'] + delta_tfr*7
    data.loc[data['year'] == 2029, 'tfr_increasing'] = data['tfr'] + delta_tfr*8
    data.loc[data['year'] == 2030, 'tfr_increasing'] = data['tfr'] + delta_tfr*9
    data.loc[data['year'] == 2031, 'tfr_increasing'] = 0.80
    final_lst.append(data)
final = pd.concat(final_lst) #.drop(columns='index')

# Export
final = final.loc[(final['year'] >= 2020) & (final['year'] < 2031) & (final['WHO_region'] == "Africa") & (final['country'] != 'Cabo Verde')]
final['Pop1'] = final['at_risk'] * final[1] 
final = final.drop(columns=['WHO_region'])
countries_malaria = list(final.country.unique())
final.to_csv(OneDrive + 'Results/Malaria_Data.csv')



