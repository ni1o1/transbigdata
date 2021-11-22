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

def data_summary(data,col = ['Vehicleid','Time'],show_sample_duration = False):
    '''
    输入数据，打印数据概况
    
    输入
    -------
    data : DataFrame
        轨迹点数据
    col : List
        列名，按[个体ID，时间]的顺序
    show_sample_duration : bool
        是否输出个体采样间隔信息
    '''
    [Vehicleid,Time] = col
    print('数据量')
    print('-----------------')
    print('数据总量 :',len(data),'条')
    Vehicleid_count = data[Vehicleid].value_counts()
    print('个体总量 :',len(Vehicleid_count),'个')
    print('个体数据量均值 :',round(Vehicleid_count.mean(),2),'条')
    print('个体数据量上四分位 :',round(Vehicleid_count.quantile(0.75),2),'条')
    print('个体数据量中位数 :',round(Vehicleid_count.quantile(0.5),2),'条')
    print('个体数据量下四分位 :',round(Vehicleid_count.quantile(0.25),2),'条')
    print('')
    print('数据时间段')
    print('-----------------')
    print('开始时间 :',data[Time].min())
    print('结束时间 :',data[Time].max())
    print('')
    if show_sample_duration:
        sd = sample_duration(data, col=[Vehicleid, Time])
        print('个体采样间隔')
        print('-----------------')
        print('均值 :',round(sd['duration'].mean(),2),'秒')
        print('上四分位 :',round(sd['duration'].quantile(0.75),2),'秒')
        print('中位数 :',sd['duration'].quantile(0.5),'秒')
        print('下四分位 :',round(sd['duration'].quantile(0.25),2),'秒')