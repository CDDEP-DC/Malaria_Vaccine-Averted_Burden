# Malaria Vaccine-Averted Burden
# Impute values for countries with missing TRR, pcr, and PCR 
# Created by Alexander Tulchinsky


## Python version       : 3.11.3
## numpyro   : 0.12.0
## arviz     : 0.15.1
## matplotlib: 3.7.1
## jax       : 0.4.10
## seaborn   : 0.12.2
## pandas    : 2.0.2

import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, scatter
import arviz as az
import pandas as pd
import seaborn as sns

import jax
import jax.numpy as np ## jax's version of numpy
from jax.numpy import array as arr
from jax import lax, random
from jax.scipy.special import expit as logistic
from jax.scipy.special import logit

import numpyro as pn
from numpyro import sample, deterministic
import numpyro.distributions as dist
from numpyro.distributions import Normal as Norm
from numpyro.infer import MCMC, NUTS, Predictive
from numpyro.diagnostics import print_summary, hpdi

import warnings

## set numpyro platform to cpu because I don't have the right kind of gpu
pn.set_platform("cpu")
## tell numpyro to use 4 cores (this many chains can run in parallel)
pn.set_host_device_count(4)

## jax wants float32's by default, but sometimes it helps to use higher-precision floats:
pn.enable_x64()
fl = np.float64
toint = np.int64

## set path name
path = '/Users/alisahamilton/Library/CloudStorage/OneDrive-CenterforDiseaseDynamics,Economics&Policy/HIV Malaria Vaccine/2. Code/'

## z score
def z(x):
    return (x - x.mean()) / x.std()

## for jax's RNG
def key_gen(seed = random.PRNGKey(8927)):
    def key():
        nonlocal seed
        seed, new_key = random.split(seed)
        return new_key
    return key

key = key_gen()

##
##
## read data
d = pd.read_csv(path + "Data/malaria_df.csv").drop(columns='Unnamed: 0')

## standardize all variables (use z-scores)
##   -- makes setting Bayesian priors much easier
## use the log of GDP (makes the distribution symmetrical)
d['G'] = z(np.log(d['GDPpercap'].values))
d['U'] = z(d['U5_mortality'])
d['R'] = z(d['trr'])
d['F'] = z(d['pcr'])

## seaborn pairplot() shows pairwise regessions;  save figure to file
sns.pairplot(d[['G','U','R','F']],kind='reg').savefig(path + "Results/malaria_plot_pcr.png")

## let's actually impute the missing values of tff instead of dropping them
##
## drop the one record where trr and tff are both missing, we can't do anything with that one
d_imp = d.dropna(subset=['trr'])

## multivariate model, with an extra parameter so we can tell it which F's are missing
def model(G, U, R, F, F_nan_idxs):
    #priors
    aF = sample("aF",Norm())
    bGF = sample("bGF",Norm())
    bUF = sample("bUF",Norm())
    bGUF = sample("bGUF",Norm())
    aR = sample("aR",Norm())
    bGR = sample("bGR",Norm())
    bUR = sample("bUR",Norm())
    bGUR = sample("bGUR",Norm())

    #linear model
    F_mean = deterministic("F_mean", aF + bGF*G + bUF*U + bGUF*G*U)
    R_mean = deterministic("R_mean", aR + bGR*G + bUR*U + bGUR*G*U)

    #multivariate model needs a variance-covariance matrix
    sd_vec = sample("sd_vec", dist.Exponential(1.0), sample_shape=(2,))
    Rho = sample("Rho", dist.LKJ(2,2))
    Mu = np.stack([R_mean,F_mean],axis=1)
    Sigma = np.outer(sd_vec,sd_vec) * Rho

    ## if a list of missing F indices is provided, impute the missing values
    if F_nan_idxs is None:
        F_with_imputed = None
    else:
        ## each imputed value gets its own probability distribution, with the mean and sd from above
        F_impute = sample("F_impute", Norm(np.mean(F_mean), sd_vec[1]).expand([len(F_nan_idxs)]).mask(False))
        ## merge the observed values with the imputed values
        F_with_imputed = F.at[F_nan_idxs].set(F_impute)
        ## this is bayesian imputation, so we need a likelihood function:
        sample("F", Norm(np.mean(F_mean),sd_vec[1]), obs=F_with_imputed)

    ## if observed output vals were provided, calculate the likelihood
    if R is None or F is None:
        sample("RF", dist.MultivariateNormal(Mu,Sigma), obs=None)
    else:
        ## use the observed and imputed values of F
        sample("RF", dist.MultivariateNormal(Mu,Sigma), obs=np.stack([R,F_with_imputed],axis=1))

## nonzero() is a trick for getting the indices where isnan() is true
dat = {'G': arr(d_imp['G']), 'U': arr(d_imp['U']), 'R': arr(d_imp['R']), 'F': arr(d_imp['F']), 
    'F_nan_idxs': np.nonzero(np.isnan(arr(d_imp['F'])))[0]  }

## run MCMC
mRF_imp = MCMC(NUTS(model, target_accept_prob=0.8), num_warmup=2000, num_samples=2000, num_chains=4)
mRF_imp.run(key(), **dat)

## inferred parameter values
## Rho[0,1] is the correlation between R and F
## save to csv
az.summary(mRF_imp,var_names=['~F_mean','~R_mean']).to_csv(path + "Results/malaraia_params_pcr.csv")

## making predictions based on posterior distributions
post = mRF_imp.get_samples()

## (= None because it's only needed when estimating parameters, not when making predictions)
post_pred = Predictive(model, post)(key(), G=d['G'].values, U=d['U'].values, R=None, F=None, F_nan_idxs=None)

## convert predictions to original variable scale
pred_trr = d['trr'].std() * post_pred['R_mean'] + d['trr'].mean()
pred_pcr = d['pcr'].std() * post_pred['F_mean'] + d['pcr'].mean()

## hpdi's
ci_trr = hpdi(pred_trr)
ci_pcr = hpdi(pred_pcr)

## store predictions
d_predRF_imp = d.copy(deep=True)
d_predRF_imp['pred_trr'] = pred_trr.mean(axis=0)
d_predRF_imp['trr_lower'] = ci_trr[0]
d_predRF_imp['trr_upper'] = ci_trr[1]
d_predRF_imp['pred_pcr'] = pred_pcr.mean(axis=0)
d_predRF_imp['pcr_lower'] = ci_pcr[0]
d_predRF_imp['pcr_upper'] = ci_pcr[1]

## save imputed values to csv
d_predRF_imp.to_csv(path + 'Data/malaria_imputed_pcr.csv',index=False)
