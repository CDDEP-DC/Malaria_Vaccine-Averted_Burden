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

OneDrive = "/Users/alisahamilton/Library/CloudStorage/OneDrive-CenterforDiseaseDynamics,Economics&Policy/HIV Malaria Vaccine/2. Code/"
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
bycountry = data.groupby(['country'])[total.columns].sum()
bycountry.to_excel(OneDrive + 'Results/Malaria_byCountry.xlsx')

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
    
byyear_cum = byyear[['I_VE0_cum','I_VE0_cum_min', 'I_VE0_cum_max',
                    'Ires_VE0_cum','Ires_VE0_cum_min', 'Ires_VE0_cum_max',
                    'D_VE0_cum','D_VE0_cum_min', 'D_VE0_cum_max',
                    'Ires2_VE0_cum','Ires2_VE0_cum_min', 'Ires2_VE0_cum_max',

                    'I_VE1_cum','I_VE1_cum_min', 'I_VE1_cum_max',
                    'Ires_VE1_cum','Ires_VE1_cum_min', 'Ires_VE1_cum_max',
                    'D_VE1_cum','D_VE1_cum_min', 'D_VE1_cum_max',
                    'Ires2_VE1_cum','Ires2_VE1_cum_min', 'Ires2_VE1_cum_max',

                    'I_VE2_cum','I_VE2_cum_min', 'I_VE2_cum_max',
                    'Ires_VE2_cum','Ires_VE2_cum_min', 'Ires_VE2_cum_max',
                    'D_VE2_cum','D_VE2_cum_min', 'D_VE2_cum_max',
                    'Ires2_VE2_cum','Ires2_VE2_cum_min', 'Ires2_VE2_cum_max',

                    'I_VE3_cum','I_VE3_cum_min', 'I_VE3_cum_max',
                    'Ires_VE3_cum','Ires_VE3_cum_min', 'Ires_VE3_cum_max',
                    'D_VE3_cum','D_VE3_cum_min', 'D_VE3_cum_max',
                    'Ires2_VE3_cum','Ires2_VE3_cum_min', 'Ires2_VE3_cum_max',

                    'I_avd_VE1_cum','I_avd_VE1_cum_min', 'I_avd_VE1_cum_max',
                    'Ires_avd_VE1_cum','Ires_avd_VE1_cum_min', 'Ires_avd_VE1_cum_max',
                    'D_avd_VE1_cum','D_avd_VE1_cum_min', 'D_avd_VE1_cum_max',
                    'Ires2_avd_VE1_cum','Ires2_avd_VE1_cum_min', 'Ires2_avd_VE1_cum_max',
            
                    'I_avd_VE2_cum','I_avd_VE2_cum_min', 'I_avd_VE2_cum_max',
                    'Ires_avd_VE2_cum','Ires_avd_VE2_cum_min', 'Ires_avd_VE2_cum_max',
                    'D_avd_VE2_cum','D_avd_VE2_cum_min', 'D_avd_VE2_cum_max',
                    'Ires2_avd_VE2_cum','Ires2_avd_VE2_cum_min', 'Ires2_avd_VE2_cum_max',
                 
                    'I_avd_VE3_cum','I_avd_VE3_cum_min', 'I_avd_VE3_cum_max',
                    'Ires_avd_VE3_cum','Ires_avd_VE3_cum_min', 'Ires_avd_VE3_cum_max',
                    'D_avd_VE3_cum','D_avd_VE3_cum_min', 'D_avd_VE3_cum_max',
                    'Ires2_avd_VE3_cum','Ires2_avd_VE3_cum_min', 'Ires2_avd_VE3_cum_max']]

outcomes_all = ['I_','Ires_','D_','Ires2_',]
outcomes_all_lst = []
for ve in scenarios_all:
    for x in outcomes_all:
        #ve = 'VE1'
        #x = 'I_'
        df = byyear_cum[[x+ve+'_cum',x+ve+'_cum_min', x+ve+'_cum_max']]
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
        df = byyear_cum[[x+ve+'_cum',x+ve+'_cum_min', x+ve+'_cum_max']]
        df['VE'] = ve
        df['outcome'] = x
        df.rename(columns={x+ve+'_cum': "est", x+ve+'_cum_min':'min', x+ve+'_cum_max':'max'}, inplace = True)
        outcomes_avd_lst.append(df)
outcomes_avd = pd.concat(outcomes_avd_lst)

byyear_final = outcomes_all.append(outcomes_avd)
byyear_final.to_csv(OneDrive + 'Results/Malaria_byYear.csv')

   
        
