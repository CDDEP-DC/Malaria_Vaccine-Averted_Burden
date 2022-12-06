# Malaria Vaccine-Averted Burden
# MC Simulation to generate uncertainty intervals
# Created by Alisa Hamilton and Fardad Haghpanah

import pandas as pd
import numpy as np
from tqdm import tqdm
pd.options.mode.chained_assignment = None  # default='warn'
import multiprocessing as mp
import time
start_time = time.time()

#set directory
#OneDrive = "/Users/alisahamilton/Library/CloudStorage/OneDrive-CenterforDiseaseDynamics,Economics&Policy/HIV Malaria Vaccine/2. Code/"
OneDrive = "/Users/Fardad/OneDrive - Center for Disease Dynamics, Economics & Policy/HIV Malaria Vaccine/2. Code/"

# parameters
c = 0.7 #coverage

#preprocessing
data1 = pd.read_csv(OneDrive + "Results/Malaria_Data.csv")

def runMC(data1):
    #OneDrive = "/Users/alisahamilton/Library/CloudStorage/OneDrive-CenterforDiseaseDynamics,Economics&Policy/HIV Malaria Vaccine/2. Code/"
    OneDrive = "/Users/Fardad/OneDrive - Center for Disease Dynamics, Economics & Policy/HIV Malaria Vaccine/2. Code/"
    
    # preprocessing
    data1 = data1.loc[(data1['year'] != 2020)]
    data1['VE0'] = 0 # Baseline - no vaccine 
    data1['coverage'] = .7
    # data1 = data1[['country','year','Pop1', 'coverage', 'inc_byage', # ADD ORIGINAL VARIABLES AND DO CALC LATER
    #            'trr','tfr','tfr_increasing',
    #            'CFR_malaria','VE0', 'VE1', 'VE2', 'VE3']]
    countries = list(data1['country'].unique())
    scenarios = ['VE0', 'VE1', 'VE2', 'VE3']
    
    # Parameter ranges
    pop_error_range = [0.9, 1.1]
    trr_error_range = [0.8, 1.2] #treatment received rate
    tfr_error_range = [0.8, 1.2] #treatment failure rate
    cfr_error_range = [0.8, 1.2] #case fatality rate

    mc_lst = []
    for i in tqdm(range(1000)):
       
        scenarios = ['VE0', 'VE1', 'VE2', 'VE3']
        # 'VE0' = baseline (0% for all 10 years)
        # 'VE1' = 40% for 4 years then 0
        # 'VE2' = 40% for 10 years
        # 'VE3' = 80%, 60%, 40%, 20%, 0% by fourth year
        
        #age-stratefied incidence rates
        prev = np.random.triangular(data1['malaria_prev_min'], data1['malaria_prev'], data1['malaria_prev_max']) #WHO prev
        # prop1_4 = np.random.triangular(data1['1_4prop_min'], data1['1_4prop_est'], data1['1_4prop_max'])
        # prop5_9 = np.random.triangular(data1['5_9prop_min'], data1['5_9prop_est'], data1['5_9prop_max'])
        
        #error ranges for parameters without CIs in data
        pop_error = np.random.triangular(pop_error_range[0],1, pop_error_range[1])
        trr_error = np.random.triangular(trr_error_range[0],1, trr_error_range[1])
        tfr_error = np.random.triangular(tfr_error_range[0],1, tfr_error_range[1])
        cfr_error = np.random.triangular(cfr_error_range[0],1, cfr_error_range[1])
        
        #age-stratefied incidence rates
        data1.loc[data1['year'] <= 2030, 'inc_byage'] = prev * data1['5_9prop_est'] / data1['Pop5_9']
        data1.loc[data1['year'] <= 2024, 'inc_byage'] = prev * data1['1_4prop_est'] / data1['Pop1_4']
             
        ve_lst = []
        for ve in scenarios:
            country_lst = []
            for country in countries:
                data = data1.loc[data1['country'] == country]
                # trr = np.random.uniform(data['trr_lower'].values[0], data['trr_upper'].values[0])
                # tfr = np.random.uniform(data['tfr_lower'].values[0], data['tfr_upper'].values[0])
                #data = data1.loc[data1['country'] == "Angola"]
                #data['CFR_malaria'] = .0029  
                #cfr = data['CFR_malaria']               
                data['Pop1'] = data['Pop1'] * pop_error
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
                    data2.loc[data2['year'] == 2021, 'D_vax'] = data2['I_vax'] * data['CFR_malaria'] * cfr_error
                    data2.loc[data2['year'] == 2021, 'D_novax'] = data2['I_novax'] * data['CFR_malaria'] * cfr_error
                    for index, row in data2.iterrows():
                        data2.loc[data2['year'] != 2021, 'uP_vax'] = data2['Pop1'] * c - data2['P_vax'] - data2['D_vax'].shift()
                        data2.loc[data2['year'] != 2021, 'NotVaxd'] = data2['NotVaxd'].shift() - data2['D_novax'].shift()
                        data2.loc[data2['year'] != 2021, 'U_vax'] =  data2['uP_vax'] * (1 - data2['inc_byage'])
                        data2['U_novax'] = data2['NotVaxd'] * (1 - data2['inc_byage'])
                        data2['I_vax'] = data2['uP_vax'] * data2['inc_byage']
                        data2['I_novax'] = data2['NotVaxd'] * data2['inc_byage']
                        data2['D_vax'] = data2['I_vax'] * data['CFR_malaria'] * cfr_error
                        data2['D_novax'] = data2['I_novax'] * data['CFR_malaria'] * cfr_error
                    data2['year'] = data2['year'] + (cohort-1)
                    cohort_lst.append(data2)
                data3 = pd.concat(cohort_lst)
                country_lst.append(data3)
            malaria = pd.concat(country_lst).sort_values(by=['country', 'cohort', 'year'])
            malaria['I'] = malaria['I_vax'] + malaria['I_novax']
            malaria['D'] = malaria['D_vax'] + malaria['D_novax']
            malaria['Ires'] = malaria['I'] * malaria['trr'] * malaria['tfr'] * trr_error * tfr_error
            malaria['Ires2'] = malaria['I'] * malaria['trr'] * malaria['tfr_increasing'] * trr_error * tfr_error
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
        mc_lst.append(final)
        
    return pd.concat(mc_lst) #sort_values(by=['country','year']).reset_index()
               
if __name__ == "__main__":
    # initializing the processes
    numproc = int(mp.cpu_count()-1)
    pools = mp.Pool(processes=numproc)
    # prepare input data
    #OneDrive = "/Users/alisahamilton/Library/CloudStorage/OneDrive-CenterforDiseaseDynamics,Economics&Policy/HIV Malaria Vaccine/2. Code/"
    OneDrive = "/Users/Fardad/OneDrive - Center for Disease Dynamics, Economics & Policy/HIV Malaria Vaccine/2. Code/"
    data1 = pd.read_csv(OneDrive + "Results/Malaria_Data.csv")
    scenarios = ['VE0', 'VE1', 'VE2', 'VE3']
    cohorts = [1,2,3,4,5,6,7,8,9,10]
    countries = list(data1['country'].unique())
    countryList = np.array_split(countries, numproc)
    inputData = []
    for i in range(numproc):
        inputData.append(data1.loc[data1['country'].isin(countryList[i]), :].reset_index(drop=True))
    # mp
    mc_lst = pools.map(runMC, inputData)
    # print(mc_lst)
    

    # post processing
    # mc_lst = [mc_lst[i][0] for i in range(len(mc_lst))]
    # mc_lst = np.array(mc_lst).flatten()
    mc_dfs = pd.concat(mc_lst) #.sort_values(by=['country','year', 'I_novax']).reset_index()
    # print(mc_dfs)

    # Uncertainty intervals    
    mc_mins = mc_dfs.groupby(['country','year'])[['I_VE0', 'D_VE0', 'Ires_VE0', 'Ires2_VE0',
                                                  'I_VE1', 'D_VE1', 'Ires_VE1', 'Ires2_VE1',
                                                  'I_VE2', 'D_VE2', 'Ires_VE2', 'Ires2_VE2',
                                                  'I_VE3', 'D_VE3', 'Ires_VE3', 'Ires2_VE3']].min().reset_index()
    
    mc_mins = mc_mins.rename(columns={'I_VE0':'I_VE0_min', 'D_VE0':'D_VE0_min', 'Ires_VE0':'Ires_VE0_min', 'Ires2_VE0':'Ires2_VE0_min',
                                      'I_VE1':'I_VE1_min', 'D_VE1':'D_VE1_min', 'Ires_VE1':'Ires_VE1_min', 'Ires2_VE1':'Ires2_VE1_min',
                                      'I_VE2':'I_VE2_min', 'D_VE2':'D_VE2_min', 'Ires_VE2':'Ires_VE2_min', 'Ires2_VE2':'Ires2_VE2_min',
                                      'I_VE3':'I_VE3_min', 'D_VE3':'D_VE3_min', 'Ires_VE3':'Ires_VE3_min', 'Ires2_VE3':'Ires2_VE3_min'})
    
    mc_maxs = mc_dfs.groupby(['country','year'])[['I_VE0', 'D_VE0', 'Ires_VE0', 'Ires2_VE0',
                                                  'I_VE1', 'D_VE1', 'Ires_VE1', 'Ires2_VE1',
                                                  'I_VE2', 'D_VE2', 'Ires_VE2', 'Ires2_VE2',
                                                  'I_VE3', 'D_VE3', 'Ires_VE3', 'Ires2_VE3']].max().reset_index()
    
    mc_maxs = mc_maxs.rename(columns={'I_VE0':'I_VE0_max', 'D_VE0':'D_VE0_max', 'Ires_VE0':'Ires_VE0_max', 'Ires2_VE0':'Ires2_VE0_max',
                                      'I_VE1':'I_VE1_max', 'D_VE1':'D_VE1_max', 'Ires_VE1':'Ires_VE1_max', 'Ires2_VE1':'Ires2_VE1_max',
                                      'I_VE2':'I_VE2_max', 'D_VE2':'D_VE2_max', 'Ires_VE2':'Ires_VE2_max', 'Ires2_VE2':'Ires2_VE2_max',
                                      'I_VE3':'I_VE3_max', 'D_VE3':'D_VE3_max', 'Ires_VE3':'Ires_VE3_max', 'Ires2_VE3':'Ires2_VE3_max'})

    # point estimates
    mc_est = pd.read_csv(OneDrive + 'Results/Malaria_PE.csv')
    #mc_mins['year_month'] = mc_mins['year_month'].apply(int)
    #mc_maxs['year_month'] = mc_maxs['year_month'].apply(int)
    final = mc_est.merge(mc_mins, how='left', on=['country','year'])
    final = final.merge(mc_maxs, how='left', on=['country','year'])
    final = final[['country', 'year',  'I_VE0','I_VE0_min','I_VE0_max',
                                       'Ires_VE0','Ires_VE0_min','Ires_VE0_max',
                                       'D_VE0','D_VE0_min','D_VE0_max',
                                       'Ires2_VE0','Ires2_VE0_min','Ires2_VE0_max',  
                                       
                                       'I_VE1','I_VE1_min','I_VE1_max', 
                                       'Ires_VE1','Ires_VE1_min','Ires_VE1_max',
                                       'D_VE1','D_VE1_min','D_VE1_max', 
                                       'Ires2_VE1','Ires2_VE1_min','Ires2_VE1_max',
                                       
                                       'I_VE2','I_VE2_min','I_VE2_max',
                                       'Ires_VE2','Ires_VE2_min','Ires_VE2_max',
                                       'D_VE2','D_VE2_min','D_VE2_max', 
                                       'Ires2_VE2','Ires2_VE2_min','Ires2_VE2_max',
                                       
                                       'I_VE3','I_VE3_min','I_VE3_max',
                                       'Ires_VE3','Ires_VE3_min','Ires_VE3_max',
                                       'D_VE3','D_VE3_min','D_VE3_max',
                                       'Ires2_VE3','Ires2_VE3_min','Ires2_VE3_max']]
    
    final = final.set_index(['country', 'year'])

    final.to_csv(OneDrive + '/Results/Malaria_MC.csv')

print("--- %s seconds ---" % (time.time() - start_time))     




