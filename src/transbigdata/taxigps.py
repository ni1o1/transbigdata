import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
from .grids import GPS_to_grids,grids_centre
import math 
import numpy as np

def clean_taxi_status(data,col = ['VehicleNum','Time','OpenStatus'],timelimit = None):
    '''
    删除出租车数据中载客状态瞬间变化的记录，这些记录的存在会影响出行订单判断。
    判断条件为:如果对同一辆车，上一条记录与下一条记录的载客状态都与本条记录不同，则本条记录应该删去
    
    输入
    -------
    data : DataFrame
        数据
    col : List
        列名，按[车辆ID,时间,载客状态]的顺序
    timelimit : number
        可选，单位为秒，上一条记录与下一条记录的时间小于该时间阈值才予以删除
    
    输出
    -------
    data1 : DataFrame
        清洗后的数据
    '''
    data1 = data.copy()
    [VehicleNum,Time,OpenStatus] = col
    if timelimit:
        data1[Time] = pd.to_datetime(data1[Time])
        data1 = data1[-((data1[OpenStatus].shift(-1) == data1[OpenStatus].shift())&\
                        (data1[OpenStatus] != data1[OpenStatus].shift())&\
                        (data1[VehicleNum].shift(-1) == data1[VehicleNum].shift())&\
                        (data1[VehicleNum] == data1[VehicleNum].shift())&\
                       ((data1[Time].shift(-1) - data1[Time].shift()).dt.total_seconds()<=timelimit)
                       )]
    else:
        data1 = data1[-((data1[OpenStatus].shift(-1) == data1[OpenStatus].shift())&\
                    (data1[OpenStatus] != data1[OpenStatus].shift())&\
                    (data1[VehicleNum].shift(-1) == data1[VehicleNum].shift())&\
                    (data1[VehicleNum] == data1[VehicleNum].shift()))]
    return data1




def taxigps_to_od(data,col = ['VehicleNum','Stime','Lng','Lat','OpenStatus']):
    '''
    输入出租车GPS数据,提取OD
    data - 出租车GPS数据（清洗好的）
    col - 数据中各列列名，需要按顺序[车辆id，时间，经度，纬度，载客状态]
    '''
    [VehicleNum,Stime,Lng,Lat,OpenStatus]=col
    data1 = data[col]
    data1 = data1.sort_values(by = [VehicleNum,Stime])
    #构建StatusChange列
    data1['StatusChange'] = data1[OpenStatus] - data1[OpenStatus].shift()
    #筛选出行开始和结束信息  
    oddata = data1[((data1['StatusChange'] == -1)|  
                   (data1['StatusChange'] == 1))&    
                   (data1[VehicleNum].shift() == data1[VehicleNum])]  
    #删去无用的列  
    oddata = oddata.drop([OpenStatus],axis = 1)   
    #首先给oddata更改列名  
    oddata.columns = [VehicleNum, 'stime', 'slon', 'slat', 'StatusChange']  
    #把一个订单的两行数据整理成一行  
    oddata['etime'] = oddata['stime'].shift(-1)  
    oddata['elon'] = oddata['slon'].shift(-1)  
    oddata['elat'] = oddata['slat'].shift(-1)  
    #筛选正确的订单OD数据：StatusChange == 1；shift后的数据属于同一个出租车  
    oddata = oddata[(oddata['StatusChange'] == 1)&  
                      (oddata[VehicleNum] == oddata[VehicleNum].shift(-1))]  
    #去掉StatusChange列
    oddata = oddata.drop('StatusChange',axis = 1)  
    oddata['ID'] = range(len(oddata))
    return oddata   


def taxigps_traj_point(data,oddata,col=['Vehicleid', 'Time', 'Lng', 'Lat', 'OpenStatus']):
    '''
    输入出租车数据与OD数据，提取载客与空载的行驶路径点
    
    输入
    -------
    data : DataFrame
        出租车GPS数据，字段名由col变量指定
    oddata : DataFrame
        出租车OD数据
    col : List
        列名，按[车辆ID,时间,经度,纬度,载客状态]的顺序

    输出
    -------
    data_deliver : DataFrame
        载客轨迹点
    data_idle : DataFrame
        空载轨迹点
    '''
    VehicleNum, Time, Lng, Lat, OpenStatus = col
    oddata1 = oddata.copy()
    odata = oddata1[[VehicleNum,'stime','slon','slat','ID']].copy()
    odata.columns = [VehicleNum,Time, Lng, Lat,'ID']
    odata.loc[:,'flag'] = 1
    odata.loc[:,OpenStatus] = -1
    ddata = oddata1[[VehicleNum,'etime','elon','elat','ID']].copy()
    ddata.columns = [VehicleNum,Time, Lng, Lat,'ID']
    ddata.loc[:,'flag'] = -1
    ddata.loc[:,OpenStatus] = -1
    data1 = pd.concat([data,odata,ddata])
    data1 = data1.sort_values(by = [VehicleNum,Time,OpenStatus])
    data1['flag'] = data1['flag'].fillna(0)
    data1['flag'] = data1.groupby(VehicleNum)['flag'].cumsum()
    data1['ID'] = data1['ID'].ffill()
    data_deliver = data1[(data1['flag']==1)&(-data1['ID'].isnull())&(data1[OpenStatus]!=-1)]
    data_idle = data1[(data1['flag']==0)&(-data1['ID'].isnull())&(data1[OpenStatus]!=-1)]
    return data_deliver,data_idle
