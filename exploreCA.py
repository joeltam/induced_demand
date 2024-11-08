# %% 
import pandas as pd
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt
from patsy import dmatrices
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.linear_model import LinearRegression

ca = pd.read_excel('Historical.xlsx')
ca['Log State Highway VMT'] = np.log(ca['State Highway VMT'])
ca['Log State Highway Lane Miles'] = np.log(ca['State Highway Lane Miles'])
ca['Log Population'] = np.log(ca['Population'])
ca['Log Per Capita Income'] = np.log(ca['Per Capita Income'])
ca['Log Total Personal Income'] = np.log(ca['Total Personal Income'])
ca['Log Unemployment Rate'] = np.log(ca['Unemployment Rate'])

# %% 
ca = ca[ca['Year'] >= 1963]
# ca = ca[ca['Year'] >= 1976]
## Cervero Hansen Timeframe
# ca = ca[(ca['Year'] >= 1976) & (ca['Year'] <= 1997)]
ca.columns = ca.columns.str.replace(' ', '_')

# %% 
plt.plot(ca['Year'], ca['State_Highway_Lane_Miles'], label = 'Lane Miles')
plt.plot(ca['Year'], ca['State_Highway_Maintained_Miles'], label = 'Maintained Miles')
plt.legend()
plt.show()

# %% 

# # Additional Features
# ca['Poly'] = np.log(ca['State_Highway_Lane_Miles']**2)
# ca['Interaction'] = ca['Log_Population'] * ca['Log_State_Highway_Lane_Miles']

# Data for Linear Regression
X = ca[['Log_Population', 'Log_State_Highway_Lane_Miles', 'Log_Per_Capita_Income']]

logmodel = LinearRegression()
logmodel.fit(X, ca['Log_State_Highway_VMT'])

coef_list = [logmodel.coef_.tolist()]
r2_list = [round(logmodel.score(X, ca['Log_State_Highway_VMT']), 5)]

print('coef:', logmodel.coef_)
print('int:', round(logmodel.intercept_, 5))
print('r^2:', round(logmodel.score(X, ca['Log_State_Highway_VMT']), 5))

plt.figure(figsize=(5,2.5))
plt.plot(ca['Year'], ca['Log_State_Highway_VMT'], label = 'Reported VMT')
plt.plot(ca['Year'], logmodel.predict(X), label = 'Predicted VMT')
plt.grid()
plt.legend()
plt.show()

coef_df = pd.DataFrame(coef_list, columns=['total_pop_coef', 'total_lane_miles_coef', 'total_income_coef'])
coef_df['r^2'] = r2_list

print('Coefficients of Entire CA')
print(coef_df)

# Calculate VIF Factors
y, X = dmatrices('State_Highway_VMT ~ State_Highway_Lane_Miles + Population + Per_Capita_Income', data=ca, return_type='dataframe')
vif = pd.DataFrame()
vif["VIF Factor"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
vif["features"] = X.columns
print(vif)

# 1966 Timeframe
ca =ca = ca[ca['Year'] >= 1966]
X = ca[['State_Highway_Lane_Miles',
        'Population', 
        'Per_Capita_Income'
        # 'Total_Personal_Income',
        # 'Unemployment_Rate'
        ]]

model = LinearRegression()
model.fit(X, ca['State_Highway_VMT'])
print('coef:', model.coef_)
print('int:', round(model.intercept_, 5))
print('r^2:', round(model.score(X, ca['State_Highway_VMT']), 5))

plt.figure(figsize=(10,5))
plt.plot(ca['Year'], ca['State_Highway_VMT'], label = 'Reported VMT')
plt.plot(ca['Year'], model.predict(X), label = 'Predicted VMT')
plt.grid()
plt.title('1976-1997')
plt.legend()
plt.show()

# VIF
y, X = dmatrices('State_Highway_VMT ~ State_Highway_Lane_Miles + Population + Per_Capita_Income + Total_Personal_Income', data=ca, return_type='dataframe')

vif = pd.DataFrame()
vif["VIF Factor"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
vif["features"] = X.columns
print(vif)