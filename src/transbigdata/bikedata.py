import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
from .grids import GPS_to_grids,grids_centre
import math 
import numpy as np

def bikedata_to_od(data,col = ['BIKE_ID','DATA_TIME','LONGITUDE','LATITUDE','LOCK_STATUS'],startend = None):
    '''
    输入共享单车订单数据（只在开关锁时产生数据），指定列名，提取其中的骑行与停车信息

    输入
    -------
    data : DataFrame
        共享单车订单数据，只在开关锁时产生数据
    col : List
        列名，顺序不能变，分别为[单车ID,时间,经度,纬度,锁状态]，例如['BIKE_ID','DATA_TIME','LONGITUDE','LATITUDE','LOCK_STATUS']
    startend : List
        传入的为[开始时间,结束时间]，如['2018-08-27 00:00:00','2018-08-28 00:00:00']。
        如传入，则考虑（观测时段开始时到单车第一次出现）与（单车最后一次出现到观测时段结束）的骑行与停车，情况。
        
    输出
    -------
    move_data : DataFrame
        骑行订单数据
    stop_data : DataFrame
        停车数据
    '''
    [BIKE_ID,DATA_TIME,LONGITUDE,LATITUDE,LOCK_STATUS] = col
    oddata = data.copy()
    oddata = oddata.sort_values(by = [BIKE_ID,DATA_TIME])
    if startend:
        oddata['tmp_index'] = range(len(oddata))
        #在一天开始的时刻加入记录  
        data_1 = oddata.copy()  
        #对单车ID分组后，依据时间升序排序，得到序号
        data_1['rank'] = data_1.groupby(BIKE_ID)['tmp_index'].rank(method = 'first')  
        data_1 = data_1[data_1['rank']==1]  
        #时间修改为观测时段开始时间
        data_1[DATA_TIME] = startend[0]
        data_1[LOCK_STATUS] = 1
        #在一天开始的时刻加入记录  
        data_2 = oddata.copy()  
        #对单车ID分组后，依据时间升序排序，得到序号
        data_2['rank'] = data_2.groupby(BIKE_ID)['tmp_index'].rank(ascending = False,method = 'first')  
        data_2 = data_2[data_2['rank']==1]  
        #时间修改为观测时段开始时间
        data_2[DATA_TIME] = startend[1]
        data_2[LOCK_STATUS] = 0
        oddata = pd.concat([oddata,data_1,data_2]).sort_values(by = [BIKE_ID,DATA_TIME])
    for i in col:
        oddata[i+'_'] = oddata[i].shift(-1)
    oddata = oddata[oddata[BIKE_ID] == oddata[BIKE_ID+'_']]
    move_data = oddata[(oddata[LOCK_STATUS]==0)&(oddata[LOCK_STATUS+'_']==1)][[BIKE_ID,DATA_TIME,LONGITUDE,LATITUDE,DATA_TIME+'_',LONGITUDE+'_',LATITUDE+'_']]
    move_data.columns = [BIKE_ID,'stime','slon','slat','etime','elon','elat']
    stop_data = oddata[(oddata[LOCK_STATUS]==1)&(oddata[LOCK_STATUS+'_']==0)][[BIKE_ID,DATA_TIME,LONGITUDE,LATITUDE,DATA_TIME+'_',LONGITUDE+'_',LATITUDE+'_']]
    stop_data.columns = [BIKE_ID,'stime','slon','slat','etime','elon','elat']
    return move_data,stop_data