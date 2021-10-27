import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
from .grids import GPS_to_grids,grids_centre
import math 
import numpy as np

def sample_duration(data,col = ['Vehicleid','Time']):
    '''
    统计数据采样间隔
    
    输入
    -------
    data : DataFrame
        数据
    col : List
        列名，按[个体ID,时间]的顺序
    
    输出
    -------
    sample_duration : DataFrame
        一列的数据表，列名为duration，内容是数据的采样间隔，单位秒
    '''
    [Vehicleid,Time] = col
    data[Time] = pd.to_datetime(data[Time])
    data1 = data.copy()
    data1 = data1.sort_values(by = [Vehicleid,Time])
    data1[Vehicleid+'1'] = data1[Vehicleid].shift(-1)
    data1[Time+'1'] = data1[Time].shift(-1)
    data1['duration'] = (data1[Time+'1']-data1[Time]).dt.total_seconds()
    data1 = data1[data1[Vehicleid+'1']==data1[Vehicleid]]
    sample_duration = data1[['duration']]
    return sample_duration
