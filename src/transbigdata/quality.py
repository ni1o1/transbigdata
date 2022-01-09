import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
from .grids import GPS_to_grids,grids_centre
import math 
import numpy as np

def sample_duration(data,col = ['Vehicleid','Time']):
    '''
    Calculate the data sampling interval.
    
    Parameters
    -------
    data : DataFrame
        Data
    col : List
        The column name, in the order of [‘Vehicleid’, ‘Time’]
    
    Returns
    -------
    sample_duration : DataFrame
        A Series with the column name duration, the content is the sampling interval of the data, in seconds
    '''
    [Vehicleid,Time] = col
    data1 = data.copy()
    data1[Time] = pd.to_datetime(data1[Time])
    data1 = data1.sort_values(by = [Vehicleid,Time])
    data1[Vehicleid+'1'] = data1[Vehicleid].shift(-1)
    data1[Time+'1'] = data1[Time].shift(-1)
    data1['duration'] = (data1[Time+'1']-data1[Time]).dt.total_seconds()
    data1 = data1[data1[Vehicleid+'1']==data1[Vehicleid]]
    sample_duration = data1[['duration']]
    return sample_duration

def data_summary(data,col = ['Vehicleid','Time'],show_sample_duration = False,roundnum = 4):
    '''
    Output the general information of the dataset.
    
    Parameters
    -------
    data : DataFrame
        The trajectory points data
    col : List
        The column name, in the order of [‘Vehicleid’, ‘Time’]
    show_sample_duration : bool
        Whether to output individual sampling interval
    roundnum : number
        Number of decimal places
    '''
    [Vehicleid,Time] = col
    print('Amount of data')
    print('-----------------')
    print('Total number of data items: ',len(data))
    Vehicleid_count = data[Vehicleid].value_counts()
    print('Total number of individuals: ',len(Vehicleid_count))
    print('Data volume of individuals(Mean): ',round(Vehicleid_count.mean(),roundnum))
    print('Data volume of individuals(Upper quartile): ',round(Vehicleid_count.quantile(0.75),roundnum))
    print('Data volume of individuals(Median): ',round(Vehicleid_count.quantile(0.5),roundnum))
    print('Data volume of individuals(Lower quartile): ',round(Vehicleid_count.quantile(0.25),roundnum))
    print('')
    print('Data time period')
    print('-----------------')
    print('Start time: ',data[Time].min())
    print('End time: ',data[Time].max())
    print('')
    if show_sample_duration:
        sd = sample_duration(data, col=[Vehicleid, Time])
        print('Sampling interval')
        print('-----------------')
        print('Mean: ',round(sd['duration'].mean(),roundnum),'s')
        print('Upper quartile: ',round(sd['duration'].quantile(0.75),roundnum),'s')
        print('Median: ',round(sd['duration'].quantile(0.5),roundnum),'s')
        print('Lower quartile: ',round(sd['duration'].quantile(0.25),roundnum),'s')