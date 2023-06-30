# Malaria Vaccine-Averted Burden
# Post Processing
# Created by Alisa Hamilton

import pandas as pd
import os
from datetime import date
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from functools import reduce
import numpy as np
from datetime import date
import glob
import time

OneDrive = "[Main file path]" + "Code/"
iso3 = pd.read_excel(OneDrive + 'Data/Africa_ISO3.xlsx')
data = pd.read_csv(OneDrive + 'Results/Malaria_MC.csv')
data = data.merge(iso3, how='left', on='country')
data = data.set_index(['country','ISO3','year'])
data = data * 1000

# VE1 - VE 40% then drops to 0% year five
# VE2 - VE starts at 80%, dropping 20 percentage points per year
# VE# - VE remains 40% for whole study period

# Averted for difference VE scenarios
scenarios_avd = ['VE1','VE2','VE3']
for ve in scenarios_avd:
    data['I_avd_'+ve] = data['I_VE0'] - data['I_'+ve]
    data['I_avd_'+ve+'_min'] = data['I_VE0_min'] - data['I_'+ve+'_min']
    data['I_avd_'+ve+'_max'] = data['I_VE0_max'] - data['I_'+ve+'_max']
    
    data['Ires_avd_'+ve] = data['Ires_VE0'] - data['Ires_'+ve]
    data['Ires_avd_'+ve+'_min'] = data['Ires_VE0_min'] - data['Ires_'+ve+'_min']
    data['Ires_avd_'+ve+'_max'] = data['Ires_VE0_max'] - data['Ires_'+ve+'_max']
    
    data['D_avd_'+ve] = data['D_VE0'] - data['D_'+ve]
    data['D_avd_'+ve+'_min'] = data['D_VE0_min'] - data['D_'+ve+'_min']
    data['D_avd_'+ve+'_max'] = data['D_VE0_max'] - data['D_'+ve+'_max']
    
    data['Ires2_avd_'+ve] = data['Ires2_VE0'] - data['Ires2_VE1']
    data['Ires2_avd_'+ve+'_min'] = data['Ires2_VE0_min'] - data['Ires2_'+ve+'_min']
    data['Ires2_avd_'+ve+'_max'] = data['Ires2_VE0_max'] - data['Ires2_'+ve+'_max']

# Totals for whole WHO Africa Region
total = data.copy()
total['Total'] = 'Total'
total = total.groupby('Total')[total.columns].sum()

# By country
bycountry = data.groupby(['country','ISO3'])[total.columns].sum()
bycountry.to_csv(OneDrive + 'Results/Malaria_byCountry.csv')

# per 1,000 Study Participants by country
outcomes = list(bycountry.columns)
bycountry_per1k = bycountry.reset_index()
bycountry_per1k = bycountry_per1k.groupby('country')[outcomes].sum().reset_index()
bycountry_pop1 = pd.read_csv(OneDrive + "Data/CreateChoroplethPlotFiles/Pop1_byCountry.csv").drop(columns=['Unnamed: 0','Country Code'])
bycountry_per1k = bycountry_per1k.merge(bycountry_pop1, how='left',left_on='country',right_on='Country Name').drop(columns='Country Name')
for outcome in outcomes:
    bycountry_per1k[outcome] = bycountry_per1k[outcome] / bycountry_per1k['Pop1'] * 1000
bycountry_per1k.to_csv(OneDrive + 'Results/Malaria_byCountry_per1000.csv')
    
# per 1,000 Study Participants WHO Africa Region (total)
outcomes = list(bycountry.columns)
total_per1k = bycountry.reset_index()
total_per1k['total'] = 'total'
total_per1k = total_per1k.groupby('total')[outcomes].sum().reset_index()
total_pop = sum(bycountry_pop1['Pop1'])
for outcome in outcomes:
    total_per1k[outcome] = total_per1k[outcome] / total_pop * 1000
total_per1k.to_csv(OneDrive + 'Results/Malaria_Total_per1000.csv')

# By year
byyear = data.groupby('year')[total.columns].sum()
scenarios_all = ['VE0','VE1','VE2','VE3']
for ve in scenarios_all:
    byyear['I_'+ve+'_cum'] = byyear['I_'+ve].cumsum()
    byyear['I_'+ve+'_cum_min'] = byyear['I_'+ve+'_min'].cumsum()
    byyear['I_'+ve+'_cum_max'] = byyear['I_'+ve+'_max'].cumsum()
    
    byyear['Ires_'+ve+'_cum'] = byyear['Ires_'+ve].cumsum()
    byyear['Ires_'+ve+'_cum_min'] = byyear['Ires_'+ve+'_min'].cumsum()
    byyear['Ires_'+ve+'_cum_max'] = byyear['Ires_'+ve+'_max'].cumsum()
    
    byyear['D_'+ve+'_cum'] = byyear['D_'+ve].cumsum()
    byyear['D_'+ve+'_cum_min'] = byyear['D_'+ve+'_min'].cumsum()
    byyear['D_'+ve+'_cum_max'] = byyear['D_'+ve+'_max'].cumsum()
    
    byyear['Ires2_'+ve+'_cum'] = byyear['Ires2_'+ve].cumsum()
    byyear['Ires2_'+ve+'_cum_min'] = byyear['Ires2_'+ve+'_min'].cumsum()
    byyear['Ires2_'+ve+'_cum_max'] = byyear['Ires2_'+ve+'_max'].cumsum()

for ve in scenarios_avd:
    byyear['I_avd_'+ve+'_cum'] = byyear['I_avd_'+ve].cumsum()
    byyear['I_avd_'+ve+'_cum_min'] = byyear['I_avd_'+ve+'_min'].cumsum()
    byyear['I_avd_'+ve+'_cum_max'] = byyear['I_avd_'+ve+'_max'].cumsum()
    
    byyear['Ires_avd_'+ve+'_cum'] = byyear['Ires_avd_'+ve].cumsum()
    byyear['Ires_avd_'+ve+'_cum_min'] = byyear['Ires_avd_'+ve+'_min'].cumsum()
    byyear['Ires_avd_'+ve+'_cum_max'] = byyear['Ires_avd_'+ve+'_max'].cumsum()
    
    byyear['D_avd_'+ve+'_cum'] = byyear['D_avd_'+ve].cumsum()
    byyear['D_avd_'+ve+'_cum_min'] = byyear['D_avd_'+ve+'_min'].cumsum()
    byyear['D_avd_'+ve+'_cum_max'] = byyear['D_avd_'+ve+'_max'].cumsum()
    
    byyear['Ires2_avd_'+ve+'_cum'] = byyear['Ires2_avd_'+ve].cumsum()
    byyear['Ires2_avd_'+ve+'_cum_min'] = byyear['Ires2_avd_'+ve+'_min'].cumsum()
    byyear['Ires2_avd_'+ve+'_cum_max'] = byyear['Ires2_avd_'+ve+'_max'].cumsum()
    
outcomes_all = ['I_','Ires_','D_','Ires2_',]
outcomes_all_lst = []
for ve in scenarios_all:
    for x in outcomes_all:
        #ve = 'VE1'
        #x = 'I_'
        df = byyear[[x+ve+'_cum',x+ve+'_cum_min', x+ve+'_cum_max']]
        df['VE'] = ve
        df['outcome'] = x
        df.rename(columns={x+ve+'_cum': "est", x+ve+'_cum_min':'min', x+ve+'_cum_max':'max'}, inplace = True)
        outcomes_all_lst.append(df)
outcomes_all = pd.concat(outcomes_all_lst)

outcomes_avd = ['I_avd_','Ires_avd_','D_avd_','Ires2_avd_']
outcomes_avd_lst = []
for ve in scenarios_avd:
    for x in outcomes_avd:
        #ve = 'VE1'
        #x = 'I_'
        df = byyear[[x+ve+'_cum',x+ve+'_cum_min', x+ve+'_cum_max']]
        df['VE'] = ve
        df['outcome'] = x
        df.rename(columns={x+ve+'_cum': "est", x+ve+'_cum_min':'min', x+ve+'_cum_max':'max'}, inplace = True)
        outcomes_avd_lst.append(df)
outcomes_avd = pd.concat(outcomes_avd_lst)


# Oucomes per 1,000 by year
byyear_final = outcomes_all.append(outcomes_avd)
byyear_outcomes = ['est','min','max']
for outcome in byyear_outcomes:
    byyear_final[outcome] = byyear_final[outcome] / total_pop * 1000

byyear_final.to_csv(OneDrive + 'Results/Malaria_byYear.csv')

