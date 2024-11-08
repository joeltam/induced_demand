# %%
import pandas as pd
import numpy as np
import re
import os

## Read data for Table 1
# CA_PRD = pd.DataFrame()
# for year in range(2001, 2023):
#     tab = 'Table 1' if year >= 2017 else f'{year} PRD_Table 1'
#     temp = pd.read_excel(pd.ExcelFile(f'HPMS2001_2022_PRD/{year}_PRD.xlsx'), tab)
#     temp = temp[temp.iloc[:, 0]=='STATE HIGHWAYS']
#     temp = temp.dropna(axis=1, how='all')
#     temp.columns = ['Jurisdiction', 'Total Maintained Miles', 'Lane Miles', 'Annual VMT (Millions)']    
#     CA_PRD = pd.concat([CA_PRD, temp])

# CA_PRD.reset_index(drop=True, inplace=True)
# CA_PRD.head()
# %% 
# Function to read highway miles data from Table 5
CA_PRD = pd.DataFrame()
for year in range(2001, 2023):
    tab = 'Table 1' if year >= 2017 else f'{year} PRD_Table 1'
    temp = pd.read_excel(pd.ExcelFile(f'HPMS2001_2022_PRD/{year}_PRD.xlsx'), tab)
    # temp = temp[temp.iloc[:, 0]=='TOTAL']
    temp = temp[temp.iloc[:, 0].isin(['TOTAL', 'STATEWIDE TOTAL'])]
    temp = temp.dropna(axis=1, how='all')
    temp.columns = ['Jurisdiction', 'Total Maintained Miles', 'Lane Miles', 'Annual VMT (Millions)']
    CA_PRD = pd.concat([CA_PRD, temp])
    # print(f'{year} successful')

CA_PRD.reset_index(drop=True, inplace=True)
# %%
# Uses Table 5
def hwymiles(county):
    TAB5_PRD = pd.DataFrame()
    for year in range(2001, 2023):
        tab = 'Table 5' if year >= 2017 else f'{year} PRD_Table 5'
        temp = pd.read_excel(pd.ExcelFile(f'HPMS2001_2022_PRD/{year}_PRD.xlsx'), tab)
        temp = temp.dropna(axis=1, how='all')
        temp = temp[temp.iloc[:, 0]==f'{county}']
        temp.columns = ['County', 'City Roads', 'County Roads', 'State Highway', 'Federal Agencies', 
                        'Other State Agencies', 'Other Local Agencies', 'Other Agencies', 'Total']
        temp['Year'] = year
        TAB5_PRD = pd.concat([TAB5_PRD, temp])

    TAB5_PRD.reset_index(drop=True, inplace=True)
    TAB5_PRD['Year'] = np.arange(2001, 2023)

    return TAB5_PRD

def VMT(county):
    TAB6_PRD = pd.DataFrame()
    for year in range(2001, 2023):
        try:
            tab = 'Table 6' if year >= 2017 else f'{year} PRD_Table 6'
            temp = pd.read_excel(pd.ExcelFile(f'HPMS2001_2022_PRD/{year}_PRD.xlsx'), tab)
        except ValueError:
            temp = pd.DataFrame([[np.nan]*8], columns=['County', 'NA', 'Rural Miles', 'Urban Miles', 'Total Miles', 'Rural DVMT', 'Urban DVMT', 'Total DVMT'])
            temp['Year'] = year
            TAB6_PRD = pd.concat([TAB6_PRD, temp])
            continue
        except Exception as e:
            continue

        temp = temp.dropna(axis=1, how='all')
        temp = temp[temp.iloc[:, 0].str.contains(f"^{re.escape(county)}\s+TOTAL$", case=False, na=False)]
        # temp = temp[temp.iloc[:, 0] == 'ALAMEDA STATE HIGHWAY']
        temp.columns = ['County', 'NA', 'Rural Miles', 'Urban Miles', 'Total Miles', 'Rural DVMT', 'Urban DVMT', 'Total DVMT']
        temp['Year'] = year
        TAB6_PRD = pd.concat([TAB6_PRD, temp])

    TAB6_PRD.reset_index(drop=True, inplace=True)

    value_2007 = TAB6_PRD.loc[(TAB6_PRD['Year'] == 2007), 'Total DVMT'].values[0]
    value_2010 = TAB6_PRD.loc[(TAB6_PRD['Year'] == 2010), 'Total DVMT'].values[0]
    value_2008 = value_2007 + (value_2010 - value_2007) / 3
    value_2009 = value_2007 + 2 * (value_2010 - value_2007) / 3

    TAB6_PRD.loc[(TAB6_PRD['Year'] == 2008), 'Total DVMT'] = value_2008
    TAB6_PRD.loc[(TAB6_PRD['Year'] == 2009), 'Total DVMT'] = value_2009

    return TAB6_PRD
# %%
county_list = [
    "ALAMEDA", "ALPINE", "AMADOR", "BUTTE", "CALAVERAS", "COLUSA", "CONTRA COSTA",
    "DEL NORTE", "EL DORADO", "FRESNO", "GLENN", "HUMBOLDT", "IMPERIAL", "INYO", "KERN",
    "KINGS", "LAKE", "LASSEN", "LOS ANGELES", "MADERA", "MARIN", "MARIPOSA", "MENDOCINO",
    "MERCED", "MODOC", "MONO", "MONTEREY", "NAPA", "NEVADA", "ORANGE", "PLACER", "PLUMAS",
    "RIVERSIDE", "SACRAMENTO", "SAN BENITO", "SAN BERNARDINO", "SAN DIEGO", "SAN FRANCISCO",
    "SAN JOAQUIN", "SAN LUIS OBISPO", "SAN MATEO", "SANTA BARBARA", "SANTA CLARA", "SANTA CRUZ",
    "SHASTA", "SIERRA", "SISKIYOU", "SOLANO", "SONOMA", "STANISLAUS", "SUTTER", "TEHAMA",
    "TRINITY", "TULARE", "TUOLUMNE", "VENTURA", "YOLO", "YUBA"
]

fips_codes = [str(i).zfill(3) for i in range(1, len(county_list) * 2 + 1, 2)]
county = pd.DataFrame({'County': county_list, 'FIPS Code': fips_codes})

county['ID'] = county['County'].str.replace(' ', '').str[:4]
numbers = np.arange(0,10)
new_array = []

for id in county['ID']:
    for number in numbers:
        new_string = f"CA{id}{number}POP"
        new_array.append(new_string)

file_names = []
for i in new_array:
    file_name = f'cty_pop/{i}.xls'
    if os.path.isfile(file_name):
        file_names.append(i)

file_names = sorted(list(set(file_names)))
county['FileName'] = file_names

percent_change = []
for i in county['FileName']:
    df = pd.read_excel(f'cty_pop/{i}.xls').iloc[41:]['Unnamed: 1'].reset_index(drop=True).to_frame().astype(float).rename(columns={'Unnamed: 1': 'Population'})
    df['% Change'] = df/(df.values[0]) - 1
    percent_change.append(df['% Change'].iloc[-1])

county['Pop % Change'] = percent_change

county_2022_dvmt = []
county_max_dvmt = []

for i in county['County']:
    county_2022_dvmt.append(VMT(i)['Total DVMT'].iloc[-1])
    county_max_dvmt.append(VMT(i)['Total DVMT'].max())

county['2022 DVMT'] = county_2022_dvmt
county['Max DVMT'] = county_max_dvmt

hwy_miles_change = []
city_miles_change = []
hwy_miles = []
city_miles = []


for i in county['County']:
    miles = hwymiles(i)
    miles['Highway % Change'] = (miles['State Highway'] / miles.loc[miles['Year'] == 2001, 'State Highway'].values[0] - 1)
    # miles['City % Change'] = (miles['City Roads'] / miles.loc[miles['Year'] == 2001, 'City Roads'].values[0] - 1)
    if miles.loc[miles['Year'] == 2001, 'City Roads'].values[0] != 0:
        miles['City % Change'] = (miles['City Roads'] / miles.loc[miles['Year'] == 2001, 'City Roads'].values[0] - 1)
    else:
        miles['City % Change'] = np.nan

    hwy_miles_change.append(miles['Highway % Change'].iloc[-1])
    city_miles_change.append(miles['City % Change'].iloc[-1])
    hwy_miles.append(miles['State Highway'].iloc[-1])
    city_miles.append(miles['City Roads'].iloc[-1])

county['Highway % Change'] = hwy_miles_change
county['City Roads % Change'] = city_miles_change
county['2022 Highway Miles'] = hwy_miles
county['2022 City Miles'] = city_miles
# %%
