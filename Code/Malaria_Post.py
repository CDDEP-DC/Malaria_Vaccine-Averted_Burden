#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: alisahamilton
Created June 2022
"""

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
scenarios = ['VE1','VE2','VE3']
for ve in scenarios:
    data['I_'+ve+'_avd'] = data['I_VE0'] - data['I_'+ve]
    data['I_'+ve+'_avd_min'] = data['I_VE0_min'] - data['I_'+ve+'_min']
    data['I_'+ve+'_avd_max'] = data['I_VE0_max'] - data['I_'+ve+'_max']
    
    data['Ires_'+ve+'_avd'] = data['Ires_VE0'] - data['Ires_'+ve]
    data['Ires_'+ve+'_avd_min'] = data['Ires_VE0_min'] - data['Ires_'+ve+'_min']
    data['Ires_'+ve+'_avd_max'] = data['Ires_VE0_max'] - data['Ires_'+ve+'_max']
    
    data['D_'+ve+'_avd'] = data['D_VE0'] - data['D_'+ve]
    data['D_'+ve+'_avd_min'] = data['D_VE0_min'] - data['D_'+ve+'_min']
    data['D_'+ve+'_avd_max'] = data['D_VE0_max'] - data['D_'+ve+'_max']
    
    data['Ires2_'+ve+'_avd'] = data['Ires2_VE0'] - data['Ires2_VE1']
    data['Ires2_'+ve+'_avd_min'] = data['Ires2_VE0_min'] - data['Ires2_'+ve+'_min']
    data['Ires2_'+ve+'_avd_max'] = data['Ires2_VE0_max'] - data['Ires2_'+ve+'_max']

# Totals for whole WHO Africa Region
total = data.copy()
total['Total'] = 'Total'
total = total.groupby('Total')[total.columns].sum()

# By country and year
bycountry = data.groupby(['country','ISO3'])[total.columns].sum()
bycountry.to_csv(OneDrive + 'Results/Malaria_byCountry.csv')
bycountry = data.groupby(['country'])[total.columns].sum()
bycountry.to_excel(OneDrive + 'Results/Malaria_byCountry.xlsx')

byyear = data.groupby('year')[total.columns].sum()
for ve in scenarios:
    byyear['I_'+ve+'_cum'] = byyear['I_'+ve+'_avd'].cumsum()
    byyear['I_'+ve+'_cum_min'] = byyear['I_'+ve+'_avd_min'].cumsum()
    byyear['I_'+ve+'_cum_max'] = byyear['I_'+ve+'_avd_max'].cumsum()
    
    byyear['Ires_'+ve+'_cum'] = byyear['Ires_'+ve+'_avd'].cumsum()
    byyear['Ires_'+ve+'_cum_min'] = byyear['Ires_'+ve+'_avd_min'].cumsum()
    byyear['Ires_'+ve+'_cum_max'] = byyear['Ires_'+ve+'_avd_max'].cumsum()
    
    byyear['D_'+ve+'_cum'] = byyear['D_'+ve+'_avd'].cumsum()
    byyear['D_'+ve+'_cum_min'] = byyear['D_'+ve+'_avd_min'].cumsum()
    byyear['D_'+ve+'_cum_max'] = byyear['D_'+ve+'_avd_max'].cumsum()
    
    byyear['Ires2_'+ve+'_cum'] = byyear['Ires2_'+ve+'_avd'].cumsum()
    byyear['Ires2_'+ve+'_cum_min'] = byyear['Ires2_'+ve+'_avd_min'].cumsum()
    byyear['Ires2_'+ve+'_cum_max'] = byyear['Ires2_'+ve+'_avd_max'].cumsum()

byyear = byyear[['I_VE1_cum','I_VE1_cum_min', 'I_VE1_cum_max',
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
                 'Ires2_VE3_cum','Ires2_VE3_cum_min', 'Ires2_VE3_cum_max']]

#byyear.to_csv(OneDrive + 'Results/Malaria_byYear.csv')

scenarios = ['VE1','VE2','VE3']
#scenarios_lst = []
outcomes = ['I_','Ires_','D_','Ires2_']
outcomes_lst = []
for ve in scenarios:
    for x in outcomes:
        #ve = 'VE1'
        #x = 'I_'
        df = byyear[[x+ve+'_cum',x+ve+'_cum_min', x+ve+'_cum_max']]
        df['VE'] = ve
        df['outcome'] = x
        df.rename(columns={x+ve+'_cum': "est", x+ve+'_cum_min':'min', x+ve+'_cum_max':'max'}, inplace = True)
        df['outcome'] = df['outcome'].str.replace("_","")
        outcomes_lst.append(df)
    outcomes_all = pd.concat(outcomes_lst)
outcomes_all.to_csv(OneDrive + 'Results/Malaria_byYear.csv')









# total = total[['I_VE0','I_VE0_min','I_VE0_max', 'Ires_VE0','Ires_VE0_min','Ires_VE0_max', 'D_VE0','D_VE0_min','D_VE0_max',
#                  'I_VE1_avd','I_VE1_avd_min','I_VE1_avd_max','Ires_VE1_avd','Ires_VE1_avd_min','Ires_VE1_avd_max','D_VE1_avd','D_VE1_avd_min','D_VE1_avd_max',
#                  'I_VE2_avd','I_VE2_avd_min','I_VE2_avd_max','Ires_VE2_avd','Ires_VE2_avd_min','Ires_VE2_avd_max','D_VE2_avd','D_VE2_avd_min','D_VE2_avd_max',
#                  'I_VE3_avd','I_VE3_avd_min','I_VE3_avd_max','Ires_VE3_avd','Ires_VE3_avd_min','Ires_VE3_avd_max','D_VE3_avd','D_VE3_avd_min','D_VE3_avd_max']]

   
        