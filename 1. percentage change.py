import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import seaborn as sns

def errorbar(data):
    error_low = data['upper'] - data['val']
    error_up = data['val'] - data['lower']
    
    return (error_low, error_up)

def make_plot(data):
    age_group = data['age_name'].unique()
    change1=data[data['measure_name']=='Prevalence']
    change2=data[data['measure_name']=='Deaths']

    change_errors1 = errorbar(change1)  
    change_errors2 = errorbar(change2) 

    cmap = plt.get_cmap("plasma")
    
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['figure.dpi'] = 300
    
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 8), sharey=True)
    y_positions = list(range(len(age_group)))
    for ax in axes:
        ax.grid(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_linewidth(1.5)
        ax.spines['left'].set_linewidth(1.5)
        ax.tick_params(axis='y', labelsize=13)
        ax.tick_params(axis='x', labelsize=13)
    
    
    for i, age in enumerate(age_group):
        region_data = change1[(change1['age_name'] == age)]
        region_errors = (change_errors1[0][region_data.index], change_errors1[1][region_data.index])
        y_position = i
        axes[0].errorbar(region_data['val'], [y_position] * len(region_data), xerr=region_errors, fmt='o',
                         color=cmap(i / len(age_group)), ecolor='gray', elinewidth=2, capsize=5)
        
        for j, value in enumerate(region_data['val']):
            axes[0].text(value, y_position+0.15, f'{value:.2f}', 
                         va='bottom', ha='center', fontsize=10, color='black')
        axes[0].set_xlabel('Percentage change (1990-2019) (%)',fontsize=15)
        axes[0].set_title('Prevalence',fontsize=18,loc='left', pad=20)   

        #axes[0].set_title('A', size=20, loc='left', pad=10)
    axes[0].set_ylabel('Age group', fontsize=18)
    
    for i, age in enumerate(age_group):
        region_data = change2[(change2['age_name'] == age)]
        region_errors = (change_errors2[0][region_data.index], change_errors2[1][region_data.index])
        y_position = i
        axes[1].errorbar(region_data['val'], [y_position] * len(region_data), xerr=region_errors, fmt='o',
                         color=cmap(i / len(age_group)), ecolor='gray', elinewidth=2, capsize=5)
        for j, value in enumerate(region_data['val']):
            axes[1].text(value, y_position+0.15, f'{value:.2f}', 
                         va='bottom', ha='center', fontsize=10, color='black')
        axes[1].set_xlabel('Percentage change (1990-2021) (%)',fontsize=15)
        axes[1].set_title('Deaths',fontsize=18,loc='left', pad=20) 

    global_val1 = change1[change1['age_name'] == 'Age-standardized']['val'].iloc[0]
    global_val2 = change2[change2['age_name'] == 'Age-standardized']['val'].iloc[0]
    
    for ax in axes:
        ax.set_yticks(range(len(age_group)))
        ax.set_yticklabels(age_group)
        
        for i, ax in enumerate(axes):
            if i == 0: 
                ax.axvline(x=global_val1, color='lightgrey', linestyle='--')
            elif i == 1:  
                ax.axvline(x=global_val2, color='lightgrey', linestyle='--')
        
    plt.tight_layout()
    plt.show()

data=pd.read_csv("database.csv")
data=data[['measure_name','age_name','cause_name','val','upper','lower']]

age_order=['95+ years', '90-94 years', '85-89 years', '80-84 years', '75-79 years', '70-74 years', '65-69 years', 
'60-64 years', '55-59 years', '50-54 years', '45-49 years', '40-44 years', '35-39 years', '30-34 years', '25-29 years', 
'20-24 years', '15-19 years', '10-14 years', '5-9 years', '<5 years', 'Age-standardized']
df=df[df['age_name'].isin(age_order)].reset_index(drop=True).sort_values(by='age_name', key=lambda x: x.map({v: i for i, v in enumerate(age_order)}))

make_plot(df)
