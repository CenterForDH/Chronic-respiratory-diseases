import pandas as pd
import numpy as np
from scipy.stats import linregress
from scipy import stats
import warnings
from scipy.stats import t
import matplotlib.pyplot as plt

data=pd.read_csv("database.csv")

def calculate_apc_values(data):
    apc_values = []

    for cause_name in data['location_name'].unique():
        df = data[ (data['location_name'] == cause_name)]
        apc_values_cause = []

        for i in range(1, len(df)):
            start_value = df['val'].iloc[i - 1]
            end_value = df['val'].iloc[i]
            apc = ((end_value - start_value) / start_value) * 100
            apc_values_cause.append(apc)

        # 마지막 연도의 APC는 없으므로 NaN으로 대체
        apc_values_cause.append(float('NaN'))
        apc_values.append(apc_values_cause)

    return apc_values

def calculate_aapc_and_ci(apc_values):
    aapc_values = []
    ci_lower_values = []
    ci_upper_values = []
    apc_values = [[value for value in apc_list if not np.isnan(value)] for apc_list in apc_values]
    for apc_list in apc_values:
        mean_apc = np.mean(apc_list)
        std_error = np.std(apc_list, ddof=1) / np.sqrt(len(apc_list))
        ci = t.interval(0.95, len(apc_list) - 1, loc=mean_apc, scale=std_error)
        aapc_values.append(mean_apc)
        ci_lower_values.append(ci[0])
        ci_upper_values.append(ci[1])

    return aapc_values, ci_lower_values, ci_upper_values

def Covid_AAPC_with_CI(data):
    df=pd.DataFrame()
    result=pd.DataFrame()
    apc_values = calculate_apc_values(data)
    aapc_values, ci_lower_values, ci_upper_values = calculate_aapc_and_ci(apc_values)
    df['location_name']=data['location_name'].unique()
    df['AAPC'] = aapc_values
    
    return df

def make_dataset(measure,cases,data,sex):
    df=data[(data['sex_id']==sex)&(data['cause_name']==cases)&(data['measure_name']==measure)]
    df1=df[(df['year']<=2019)&(df['year']>=2010)]
    df2=df[df['year']>=2019]
    
    final1=Covid_AAPC_with_CI(df1)
    final2=Covid_AAPC_with_CI(df2)
    final=pd.merge(final1, final2,on='location_name',how='left')
    final.rename(columns={'AAPC_x':'pre pandemic AAPC','AAPC_y':'during pandemic AAPC'},inplace=True)
    
    final.to_csv(file_path+'Covid_'+measure+'_'+cases+'.csv',index=False)
    return final

final=make_dataset(measure,cases,data,3)

region_order =["Western Sub-Saharan Africa","Southern Sub-Saharan Africa",
    "Eastern Sub-Saharan Africa","Central Sub-Saharan Africa","Southeast Asia","Oceania","East Asia","South Asia","North Africa and Middle East",
    "Tropical Latin America","Central Latin America","Caribbean","Andean Latin America","Western Europe","Southern Latin America","High-income North America",
    "High-income Asia Pacific","Australasia","Eastern Europe","Central Europe","Central Asia","Global"]
final=final[final['location_name'].isin(region_order)].reset_index(drop=True).sort_values(by='location_name', key=lambda x: x.map({v: i for i, v in enumerate(region_order)}))

# make figure
regions = final['location_name']
bar_width = [0.8 if region != "Global" else 1.2 for region in regions]
locations = np.arange(len(final['location_name'])) * 2

plt.figure(figsize=(8, 8))
plt.rcParams['font.family'] = 'Times New Roman'
ax = plt.gca()  

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_linewidth(1.5)
ax.spines['left'].set_linewidth(1.5)
plt.tick_params(axis='y', labelsize=15)
plt.tick_params(axis='x', labelsize=15)

barh_before = plt.barh(
    locations + np.array(bar_width) / 2,
    final['pre pandemic AAPC'],
    color='mediumorchid',
    height=np.array(bar_width),
    label='Before the COVID-19 pandemic (2010-2019)'
)
barh_after = plt.barh(
    locations - np.array(bar_width) / 2,
    final['during pandemic AAPC'],
    color='mediumseagreen',
    height=np.array(bar_width),
    label='During the COVID-19 pandemic (2019-2021)'
)

plt.yticks(locations, final['location_name'])

plt.xlabel('AAPC', fontsize=20)
plt.ylabel('GBD region', fontsize=20)

labels = ax.get_yticklabels()
for label in labels:
    if label.get_text() == "Global":
        label.set_fontweight('bold')
        label.set_fontsize(18)

plt.legend(ncol=1, fontsize=13, loc='lower left', bbox_to_anchor=(1.04, 0))
plt.show()
