# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ---
#
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
#
# ---

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import re

pd.options.display.max_columns = None

# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
#
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
#
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
#
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
#
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}

aa = pd.read_csv("City_Zhvi_AllHomes.csv")

dc_states = pd.DataFrame.from_dict(states, orient='index')

bb = pd.read_table("university_towns.txt", header=None,names=["university"])
bb.head(10)

cc = pd.read_excel("gdplev.xls")
cc.head(23)

recession = pd.read_excel("gdplev.xls",skiprows=(range(0,7)))


def get_list_of_university_towns():

    bb = pd.read_table("university_towns.txt", header=None,names=["university"])
    '''
    Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''

    State= []
    RegionName =[]
    for i, k in enumerate(bb["university"]):
        if(k[-6:]=="[edit]"):
            term = k[:-6]
            term = term.strip()
            
        else:
            State.append(term)
            term2 = bb['university'][i].split("(")[0]
            term2 =term2.strip()
            RegionName.append(term2)
    
    data = {"State":State,"RegionName":RegionName}

    df = pd.DataFrame(data)
    df = df.reindex(columns = ['State','RegionName'])

    return df


get_list_of_university_towns()


def get_recession_start():
    
    '''
    Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3
    '''
    
    recession = pd.read_excel("gdplev.xls",skiprows=(range(0,219)), usecols=(4,5))
    recession.columns = ['Quarter','GDP']
    
    for i in range(len(recession)-2):
        if(recession['GDP'][i]>recession['GDP'][i+1] and recession['GDP'][i+1]>recession['GDP'][i+2]):
            return recession['Quarter'][i]


get_recession_start()


# +
def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    recession = pd.read_excel("gdplev.xls",skiprows=(range(0,219)), usecols=(4,5))
    recession.columns = ['Quarter','GDP']
    
    for i in range(len(recession)-2):
        if(recession['GDP'][i]>recession['GDP'][i+1] and recession['GDP'][i+1]>recession['GDP'][i+2] and recession['GDP'][i+2]<recession['GDP'][i+3] and recession['GDP'][i+3]<recession['GDP'][i+4]) :
            return recession['Quarter'][i+4]


# -

get_recession_end()


# +
def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    recession = pd.read_excel("gdplev.xls",skiprows=(range(0,219)), usecols=(4,5))
    recession.columns = ['Quarter','GDP']
    for i in range(len(recession)-2):
        if(recession['GDP'][i]>recession['GDP'][i+1] and recession['GDP'][i+1]>recession['GDP'][i+2] and recession['GDP'][i+2]<recession['GDP'][i+3] and recession['GDP'][i+3]<recession['GDP'][i+4]) :
            return recession['Quarter'][i+2]
    


# -

get_recession_bottom()


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    
    '''
    aa = pd.read_csv("City_Zhvi_AllHomes.csv")
    global states
    aa = aa[aa.columns.drop(list(aa.filter(regex='199')))]
    dc_states = pd.DataFrame.from_dict(states, orient='index')
    
    dc_states.reset_index(inplace=True)
    dc_states.columns = ['State','StateName']
    
    aamain = aa.iloc[:,:6]
    aaquarter = aa.iloc[:,6:]
    
    
    res = (aaquarter.groupby(pd.PeriodIndex(aaquarter.columns, freq='Q'), axis=1)
                  .mean()
                  .rename(columns=lambda c: str(c).lower()))
    mainQ = aamain.join(res)
    mainMerge = mainQ.merge(dc_states,left_on='State', right_on='State', right_index=False)
    mainMerge.set_index(['StateName','RegionName'],inplace=True)
    mainMerge.drop(['RegionID','State','Metro','CountyName','SizeRank'],axis=1, inplace=True)
    #mainMerge.reset_index(inplace=True)

    
    
    
    return mainMerge



convert_housing_data_to_quarters()


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    df = convert_housing_data_to_quarters()
    university_towns = get_list_of_university_towns()
    
    df['differ'] = df[get_recession_start()] / df[get_recession_bottom()]
    df['university'] = np.nan
    
    for i,k in enumerate(df.index):
        
        if k[1] in list(university_towns['RegionName']):
            df['university'][i]=True
        else:
            df['university'][i] =False

    df.dropna(subset=['differ'],inplace=True)
    
    university_towns_mean=df['differ'][df['university']==1]
    not_university_mean = df['differ'][df['university']==0]
    t,p = ttest_ind(not_university_mean, university_towns_mean)
    
    mean_result = "university town" if np.mean(university_towns_mean) < np.mean(not_university_mean) else "non-university town"

    p_result = True if p<0.01 else False

    
            
    
    
    return p_result, p, mean_result

run_ttest()


