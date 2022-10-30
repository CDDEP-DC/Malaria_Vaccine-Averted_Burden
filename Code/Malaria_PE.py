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
start_time = time.time()

#set directory
OneDrive = "/Users/alisahamilton/Library/CloudStorage/OneDrive-CenterforDiseaseDynamics,Economics&Policy/HIV Malaria Vaccine/2. Code/"

scenarios = ['VE0', 'VE1', 'VE2', 'VE3']
# 'VE0' = baseline (0% for all 10 years)
# 'VE1' = 40% for 4 years then 0
# 'VE2' = 40% for 10 years
# 'VE3' = 80%, 60%, 40%, 20%, 0% by fourth year

# parameters
c = 0.7 #coverage
tsr = 0.693 # treatment seeking rate
trr = 0.757 # treatment received rate

#preprocessing
data1 = pd.read_csv(OneDrive + "Results/Malaria_Data.csv")
data1 = data1.loc[(data1['inc_byage'] != 0) & (data1['year'] != 2020)]
data1['VE0'] = 0 # Baseline - no vaccine 
data1['coverage'] = .7
data1 = data1[['country','year','Pop1', 'coverage', 'inc_byage','tfr_malaria','tfr_increasing','CFR_malaria','VE0', 'VE1', 'VE2', 'VE3']]
countries = list(data1['country'].unique())

ve_lst = []
for ve in scenarios:
    country_lst = []
    for country in countries:
        data = data1.loc[data1['country'] == country]
        #data = data1.loc[data1['country'] == "Angola"]
        #data['CFR_malaria'] = .0029  
        #cfr = data['CFR_malaria']               
        data['VE'] = data[ve]
        data['cohort'] = np.r_[:len(data)] % 10 + 1
        data['cohort'] = data['cohort']
        data_temp = data[['year', 'Pop1', 'cohort']]
        data_temp['times'] = 10
        data_temp = data_temp.loc[data_temp.index.repeat(data_temp.times)].reset_index(drop=True)
        data_temp['year'] = np.r_[:len(data_temp)] % 10 + 1
        data_temp['year'] = data_temp['year'] + 2020
        data_temp = data_temp.drop(columns='times')
        data = data.merge(data_temp, how='outer', on=['year'])
        data = data.sort_values(by=['Pop1_y','year'])
        data = data.drop(columns=['Pop1_x', 'cohort_x'])
        data = data.rename(columns={'Pop1_y':'Pop1', 'cohort_y':'cohort'})
        data = data.loc[data['cohort'] !=0]
        cohorts = [1,2,3,4,5,6,7,8,9,10]
        cohort_lst = []
        for cohort in cohorts:
            #cohort = 2
            data2 = data.loc[data['cohort'] == cohort]
            data2['P_vax'] = data2['Pop1'] * c  * data2['VE']
            data2.loc[data2['year'] == 2021, 'uP_vax'] = data2['Pop1'] * c - data2['P_vax']
            data2.loc[data2['year'] == 2021, 'NotVaxd'] = data2['Pop1'] * (1-c)
            data2.loc[data2['year'] == 2021, 'U_vax'] =  data2['uP_vax'] * (1 - data2['inc_byage'])
            data2.loc[data2['year'] == 2021, 'U_novax'] = data2['NotVaxd'] * (1 - data2['inc_byage'])
            data2.loc[data2['year'] == 2021, 'I_vax'] = data2['uP_vax'] * data2['inc_byage']
            data2.loc[data2['year'] == 2021, 'I_novax'] = data2['NotVaxd'] * data2['inc_byage']
            data2.loc[data2['year'] == 2021, 'D_vax'] = data2['I_vax'] * data['CFR_malaria']
            data2.loc[data2['year'] == 2021, 'D_novax'] = data2['I_novax'] * data['CFR_malaria']
            for index, row in data2.iterrows():
                data2.loc[data2['year'] != 2021, 'uP_vax'] = data2['Pop1'] * c - data2['P_vax'] - data2['D_vax'].shift()
                data2.loc[data2['year'] != 2021, 'NotVaxd'] = data2['NotVaxd'].shift() - data2['D_novax'].shift()
                data2.loc[data2['year'] != 2021, 'U_vax'] =  data2['uP_vax'] * (1 - data2['inc_byage'])
                data2['U_novax'] = data2['NotVaxd'] * (1 - data2['inc_byage'])
                data2['I_vax'] = data2['uP_vax'] * data2['inc_byage']
                data2['I_novax'] = data2['NotVaxd'] * data2['inc_byage']
                data2['D_vax'] = data2['I_vax'] * data['CFR_malaria']
                data2['D_novax'] = data2['I_novax'] * data['CFR_malaria']
            data2['year'] = data2['year'] + (cohort-1)
            cohort_lst.append(data2)
        data3 = pd.concat(cohort_lst)
        country_lst.append(data3)
    malaria = pd.concat(country_lst).sort_values(by=['country', 'cohort', 'year'])
    malaria['I'] = malaria['I_vax'] + malaria['I_novax']
    malaria['D'] = malaria['D_vax'] + malaria['D_novax']
    malaria['Ires'] = malaria['I'] * tsr * trr * malaria['tfr_malaria']
    malaria['Ires2'] = malaria['I'] * tsr * trr * malaria['tfr_increasing']
    malaria = malaria.loc[malaria['year'] <=2030]
    malaria = malaria.groupby(['country', 'year'])[['I', 'D', 'Ires', 'Ires2']].sum().reset_index()
    malaria['scenario'] = ve
    ve_lst.append(malaria)
final = pd.concat(ve_lst)
final = pd.pivot_table(final, values=['I', 'D', 'Ires', 'Ires2'], index=['country','year'], columns='scenario')
final.columns = ['_'.join(col).strip() for col in final.columns.values]
final = final.reset_index()
final = final[['country', 'year', 'I_VE0', 'D_VE0', 'Ires_VE0', 'Ires2_VE0',
                                  'I_VE1', 'D_VE1', 'Ires_VE1', 'Ires2_VE1',
                                  'I_VE2', 'D_VE2', 'Ires_VE2', 'Ires2_VE2',
                                  'I_VE3', 'D_VE3', 'Ires_VE3', 'Ires2_VE3']]
final.to_csv(OneDrive + 'Results/Malaria_PE.csv')
   
print("--- %s seconds ---" % (time.time() - start_time)) 
   
        
        