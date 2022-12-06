# Malaria Vaccine-Averted Burden
# Imputing treatment received and treatment failure rates from GDP per capita and under 5 mortality per 1,000
# Created by Alexander Tulchinsky
        
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
    
def runImputation():
    OneDrive = "[Main file path]"
    
    ## set numpyro platform to cpu because I don't have the right kind of gpu
    pn.set_platform("cpu")
    ## tell numpyro to use 6 cores (this many chains can run in parallel)
    pn.set_host_device_count(6)
    
    get_ipython().run_line_magic('config', 'InlineBackend.figure_formats = ["svg"]')
    #plt.style.use("dark_background")
    warnings.formatwarning = lambda message, category, *args, **kwargs: "{}: {}\n".format(category.__name__, message)
    
    ## jax wants float32's by default, but sometimes it helps to use higher-precision floats:
    HIPREC = True
    
    if HIPREC: 
        pn.enable_x64()
        fl = np.float64
        toint = np.int64
    else:
        fl = np.float32
        toint = np.int32
    
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
    
    d = pd.read_csv(OneDrive + "Data/malaria_df.csv")
    
    ## standardize all variables (use z-scores)
    ##   -- makes setting Bayesian priors much easier
    ## use the log of GDP (makes the distribution symmetrical)
    d['G'] = z(np.log(d['GDPpercap'].values))
    d['U'] = z(d['U5_mortality'])
    d['R'] = z(d['trr'])
    d['F'] = z(d['tfr'])
    
    #pd.plotting.scatter_matrix(d_nona[['G','U','R','F']],diagonal='kde',figsize=[8,6],range_padding=0.2,alpha=0.8);
    
    ## seaborn pairplot() shows pairwise regessions
    # Title: Pairwise Ordinary Least Squares (OLS) Regressions for GDP per capita, Under five mortality, TRR, and TFR
    sns.pairplot(d[['G','U','R','F']],kind='reg')
    pair_plot = sns.pairplot(d[['G','U','R','F']],kind='reg')
    pair_plot.savefig(OneDrive + 'Results/Malaria_Imputation.png')
    
    ## drop the row where trr is missing
    dR = d.dropna(subset=['trr'])
    
    ## this is a basic linear regression model
    ##  G and U are predictors, R is the output variable (ignoring F for now)
    
    def model(G,U,R):
        ## set priors for the model coefficients:
        aR = sample("aR",Norm()) ## this is the intercept
        bGR = sample("bGR",Norm()) ## effect of G on R
        bUR = sample("bUR",Norm()) ## effect of U on R
        bGUR = sample("bGUR",Norm()) ## this is the G x U interaction term
    
        ## the linear model equation:
        R_mean = deterministic("R_mean", aR + bGR*G + bUR*U + bGUR*G*U)
    
        ## prior for the standard deviation of the output variable (the error term):
        sd = sample("sd", dist.Exponential(1.0))
    
        ## the likelihood of the observed values of R:
        sample("R", dist.Normal(R_mean,sd), obs=R)
    
    ## put the data in a dict, match the field names to the names of the function parameters in model()
    dat = {'G': arr(dR['G']), 'U': arr(dR['U']), 'R': arr(dR['R']) }
    
    ## run the MCMC sampler on the model
    mR = MCMC(NUTS(model, target_accept_prob=0.8), num_warmup=500, num_samples=500, num_chains=4)
    mR.run(key(), **dat)
    
    ## estimates of the model coefficients:
    az.summary(mR,var_names=['~R_mean'])
    
    ## put the predictions in a separate df
    d_pred = d.copy(deep=True)
    
    ## use samples from the posterior parameter distributions to make predictions:
    post = mR.get_samples()
    
    ## use the data for G and U to predict R 
    ##  (R=None because we are now predicting R, instead of using its observed values to estimate parameters)
    post_pred = Predictive(model, post)(key(), G=d['G'].values, U=d['U'].values, R=None)
    pred_R = post_pred['R_mean']
    
    ## convert the standardized values back to the scale of the original variable
    pred_trr = pred_R * d['trr'].std() + d['trr'].mean()
    
    ## hpdi = 'high probability density interval' (the bayesian version of confidence intervals)
    ci_trr = hpdi(pred_trr)
    
    d_pred['pred_trr'] = pred_trr.mean(axis=0)
    d_pred['trr_lower'] = ci_trr[0]
    d_pred['trr_upper'] = ci_trr[1]
    
    d_pred[0:10]
    
    ## to include tfr, drop all nans (note this throws away data points where we have trr but not tfr)
    d_nona = d.dropna()
    
    ## this is a basic multivariate model; predictors are G and U, output vars R and F
    
    def model(G,U,R,F):
        ## set priors for the model coefficients
        aR = sample("aR",Norm())
        bGR = sample("bGR",Norm())
        bUR = sample("bUR",Norm())
        bGUR = sample("bGUR",Norm())
        aF = sample("aF",Norm())
        bGF = sample("bGF",Norm())
        bUF = sample("bUF",Norm())
        bGUF = sample("bGUF",Norm())
    
        ## the linear model equations:
        R_mean = deterministic("R_mean", aR + bGR*G + bUR*U + bGUR*G*U)
        F_mean = deterministic("F_mean", aF + bGF*G + bUF*U + bGUF*G*U)
        
        ## for a multivariate model, the output is a multivariate distribution
        ##  so we have to estimate the covariance between the output variables
        ## prior for the standard deviations of R and F:
        sd_vec = sample("sd_vec", dist.Exponential(1.0), sample_shape=(2,))
        ## prior for the correlation matrix:
        Rho = sample("Rho", dist.LKJ(2,2))
        ## multiply the standard deviations by the correlation matrix to get the variance-covariance matrix:
        Sigma = np.outer(sd_vec,sd_vec) * Rho
        ## the means of R and F come from the linear model above, just stack them together
        Mu = np.stack([R_mean,F_mean],axis=1)
    
        ## if we're using this model to make predictions, we won't pass it the output variables
        if R is None or F is None:
            sample("RF", dist.MultivariateNormal(Mu,Sigma), obs=None)
        ## otherwise calculate the likelihood of the observed data
        ##  (have to stack the values along axis 1 so the observed and estimated values line up correctly)
        else:
            sample("RF", dist.MultivariateNormal(Mu,Sigma), obs=np.stack([R,F],axis=1))
    
    ## put the data in a dict
    dat = {'G': arr(d_nona['G']), 'U': arr(d_nona['U']), 'R': arr(d_nona['R']), 'F': arr(d_nona['F'])}
    
    ## run the MCMC sampler on the model
    mRF = MCMC(NUTS(model, target_accept_prob=0.8), num_warmup=500, num_samples=500, num_chains=4)
    mRF.run(key(), **dat)
    
    ## the estimated model coefficients:
    az.summary(mRF, var_names=['~F_mean','~R_mean'])
    
    ## use posterior parameter samples to make predictions
    post = mRF.get_samples()
    df = d_nona
    
    ## bayesian confidence intervals
    F_ci = hpdi(post['F_mean'])
    R_ci = hpdi(post['R_mean'])
    
    ## plot the predicted values of R against the actual observed values
    ##  note that this model is pretty bad at making predictions
    plot(df['R'],df['R'],"--")
    plt.xlabel("observed")
    plt.ylabel("predicted")
    scatter(df['R'],post['R_mean'].mean(0))
    for (i,x) in enumerate(df['R'].values):
        plot([x,x], R_ci[:,i])
    
    ## observed F vs predicted F, also bad
    plot(df['F'],df['F'],"--")
    plt.xlabel("observed")
    plt.ylabel("predicted")
    scatter(df['F'],post['F_mean'].mean(0))
    for (i,x) in enumerate(df['F'].values):
        plot([x,x], F_ci[:,i])
    
    ## show the regression of R on U
    x = d_nona['U'].values
    ## set G to its average value (0, because it's standardized) and use U to predict R
    post_pred = Predictive(model, post, )(key(), G=0, U=x, R=None, F=None)
    
    plt.scatter(df['U'],df['R'])
    plt.plot(x,post_pred['R_mean'].mean(0))
    ci = hpdi(post_pred['R_mean'])
    az.plot_hdi(x, hdi_data=ci.T); ## arviz plot_hdi automatically plots bayesian high-density intervals
    
    ## use the multivariate model to make predictions
    post = mRF.get_samples()
    
    ## posterior predictions using observed values of G and U
    post_pred = Predictive(model, post)(key(), G=d['G'].values, U=d['U'].values, R=None, F=None)
    
    ## convert predicted R and F back to the scale of the original variables
    pred_trr = d['trr'].std() * post_pred['R_mean'] + d['trr'].mean()
    pred_tfr = d['tfr'].std() * post_pred['F_mean'] + d['tfr'].mean()
    
    ## calculate HPDIs
    ci_trr = hpdi(pred_trr)
    ci_tfr = hpdi(pred_tfr)
    
    ## store predictions in a separate df
    d_predRF = d.copy(deep=True)
    
    d_predRF['pred_trr'] = pred_trr.mean(axis=0)
    d_predRF['trr_lower'] = ci_trr[0]
    d_predRF['trr_upper'] = ci_trr[1]
    d_predRF['pred_tfr'] = pred_tfr.mean(axis=0)
    d_predRF['tfr_lower'] = ci_tfr[0]
    d_predRF['tfr_upper'] = ci_tfr[1]
    
    ## note predicted trr for Botswana is different than from the simpler model
    ## but I don't trust this one because we threw out 4 important data points
    d_predRF[0:10]
    
    ## let's actually impute the missing values of tff instead of dropping them
    
    ## drop the one record where trr and tff are both missing, we can't do anything with that one
    d_imp = d.dropna(subset=['trr'])
    
    ## this is the same multivariate model as above, but with an extra parameter so we can tell it which F's are missing
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
    
    mRF_imp = MCMC(NUTS(model, target_accept_prob=0.8), num_warmup=2000, num_samples=2000, num_chains=4)
    mRF_imp.run(key(), **dat)
    
    ## Rho[0,1] is the correlation between R and F
    az.summary(mRF_imp,var_names=['~F_mean','~R_mean'])
    reg_results = az.summary(mRF_imp,var_names=['~F_mean','~R_mean'])
    
    ## making predictions same way as before
    post = mRF_imp.get_samples()
    
    ## note this model function requires one extra argument (= None because it's only needed when estimating
    ##   parameters, not when making predictions)
    post_pred = Predictive(model, post)(key(), G=d['G'].values, U=d['U'].values, R=None, F=None, F_nan_idxs=None)
    
    ## convert predictions to original variable scale
    pred_trr = d['trr'].std() * post_pred['R_mean'] + d['trr'].mean()
    pred_tfr = d['tfr'].std() * post_pred['F_mean'] + d['tfr'].mean()
    
    ## hpdi's
    ci_trr = hpdi(pred_trr)
    ci_tfr = hpdi(pred_tfr)
    
    ## store predictions
    d_predRF_imp = d.copy(deep=True)
    d_predRF_imp['pred_trr'] = pred_trr.mean(axis=0)
    d_predRF_imp['trr_lower'] = ci_trr[0]
    d_predRF_imp['trr_upper'] = ci_trr[1]
    d_predRF_imp['pred_tfr'] = pred_tfr.mean(axis=0)
    d_predRF_imp['tfr_lower'] = ci_tfr[0]
    d_predRF_imp['tfr_upper'] = ci_tfr[1]
    
    ## note that we got basically the same prediction for Botswana's trr as we did with the
    ##  simple univariate model (where we also only dropped one row)
    
    ## but now we also have predictions for the five missing tfr's
    ##   (they're probably not very good predictions, but it's the best we can do with this data)
    
    d_predRF_imp
    d_predRF_imp.to_csv(OneDrive + 'Results/malaria_imputed.csv',index=False)
    
    ## below I plotted the observed trr's (x axis) against predicted trr's (y axis)
    ##
    ## note that the simple univariate and multivariate imputation models are almost identical
    ## while the one where we dropped missing tff's is worse, especially at low values of trr
    ## so I trust the 0.12 trr prediction for Botswana more than the 0.19
    ##   (the real value is probably lower than 0.12)
    
    ## the simple univariate model
    test_df = d_pred
    plot(test_df['trr'],test_df['trr'],'--')
    scatter(test_df['trr'],test_df['pred_trr']);
    
    ## multivariate, but drop missing tff's
    test_df = d_predRF
    plot(test_df['trr'],test_df['trr'],'--')
    scatter(test_df['trr'],test_df['pred_trr']);
    
    ## multivariate imputation
    test_df = d_predRF_imp
    plot(test_df['trr'],test_df['trr'],'--')
    scatter(test_df['trr'],test_df['pred_trr']);
    
    
    
