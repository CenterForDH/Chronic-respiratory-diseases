import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import scipy as sp
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter, FuncFormatter

def fit_poisson_and_predict(data):
    poisson_model = smf.poisson('val ~ year', data=data).fit()
    data['Predicted'] = poisson_model.predict(data)
    predictions = poisson_model.get_prediction(data)
    ci = predictions.conf_int()
    return poisson_model, data, ci

def format_yaxis(value, tick_number):
    return f"{int(value):,}"


death=pd.read_csv("data/final_number.csv")
pop=pd.read_csv("data/final_pop.csv")

pre_death=death[death['year']<2020]
during_death=death[death['year']>=2020]
pre_pop=pop[pop['year']<2020]
during_pop=pop[pop['year']>=2020]

pre_death=pd.merge(pre_death, pre_pop, on=['location_name','sex_name','year','age_name'], how='left')

df=pre_death[pre_death['cause_name']==cause_name]
df_during=during_death[during_death['cause_name']==cause_name]

results=pd.DataFrame()
for sex in df['sex_name'].unique():
    for country in df['location_name'].unique():
        for age_group in df['age_name'].unique():
            train_df = df[(df['location_name'] == country) & (df['age_name'] == age_group) & (df['sex_name'] == sex)]
            y = train_df['val']
            
            X=sm.add_constant(train_df['pop'])
            
            poisson_model=sm.GLM(y, X, family=sm.families.Poisson()).fit()
            
            predict_df = during_pop[(during_pop['location_name'] == country) & (during_pop['age_name'] == age_group) & (during_pop['sex_name'] == sex)]
            X_pred = sm.add_constant(predict_df['pop'])
            predictions = poisson_model.predict(X_pred)
            predict_df['predicted'] = predictions
            predict_df['intercept'] = poisson_model.params['const']
            predict_df['slope'] = poisson_model.params['pop']
            
            conf = poisson_model.conf_int()
            predict_df['CI_Lower'] = conf.loc['const'][0]
            predict_df['CI_Upper'] = conf.loc['const'][1]
            
            
            results=pd.concat([results,predict_df],axis=0).reset_index(drop=True)

results = pd.merge(results, df_during, on=['location_name', 'year', 'age_name', 'sex_name'], how='left', suffixes=('_pred', '_obs'))

results['Excess_Number'] = results['val'] - results['predicted']
results['Excess_Ratio'] = results['val'] / results['predicted']

results=pd.concat([df,results],axis=0).reset_index(drop=True)

n_cols = 3
n_rows = int(np.ceil(len(age_groups) / n_cols))
plt.rcParams['font.family'] = 'serif'
fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))

if n_rows == 1 and n_cols == 1:
    axes = np.array([axes])
axes = axes.flatten()
plot_index = 0  


# Figure 
for age_group in age_groups:
    age_data = results[(results['age_name'] == age_group) & 
                       (results['location_name'] == 'Global') & 
                       (results['sex_name'] == 'Both')]
    
    if age_data.empty:
        continue

    ax = axes[plot_index]  
    plot_index += 1  

    poisson_model, data, ci = fit_poisson_and_predict(age_data)
    data_sorted = data.sort_values('year')
    ci_sorted = np.array([ci[:, 0][np.argsort(data['year'])], ci[:, 1][np.argsort(data['year'])]])

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)

    ax.scatter(age_data['year'], age_data['val'], color='mediumseagreen', alpha=0.7, s=50, label="Actual Data")
    ax.scatter(age_data['year'], age_data['predicted'], color='royalblue', alpha=0.7, s=50, label="Predicted Data")

    ax.plot(data_sorted['year'], data_sorted['Predicted'], color='mediumseagreen', label='Poisson Regression Line')
    ax.fill_between(data_sorted['year'], ci_sorted[0], ci_sorted[1], color='mediumseagreen', alpha=0.2, label='95% Confidence Interval')

    ax.yaxis.set_major_formatter(FuncFormatter(format_yaxis))

    min_y = ci.min() * 0.9
    max_y = ci.max() * 1.1
    ax.set_ylim(min_y, max_y)
    
    ax.set_title(f"{abc_groups[plot_index-1]}{age_group}", size=20, loc='left', pad=20)
    ax.set_xlabel("Year", fontsize=15)

    if plot_index % n_cols == 1:
        ax.set_ylabel(val + " deaths", fontsize=15)

    if age_group == '≥ 75 years':
        ax.legend(fontsize='small', loc='lower right')

for j in range(plot_index, len(axes)):
    ax = axes[j]
    ax.axis('off')

plt.tight_layout()
plt.show()
