import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
from .grids import GPS_to_grids,grids_centre
import math 
import numpy as np
def odagg(oddata,params,col = ['slon','slat','elon','elat'],arrow = False,**kwargs):
    '''
    输入OD数据（每一行数据是一个出行），栅格化OD并集计后生成OD的GeoDataFrame
    oddata - 出租车OD数据（清洗好的）
    col - 起终点列名
    params - 栅格化参数
    arrow - 生成的OD地理线型是否包含箭头
    '''
    #将起终点栅格化
    [slon,slat,elon,elat]=col
    oddata['SLONCOL'],oddata['SLATCOL'] = GPS_to_grids(oddata[slon],oddata[slat],params)
    oddata['ELONCOL'],oddata['ELATCOL'] = GPS_to_grids(oddata[elon],oddata[elat],params)
    oddata['count'] = 1
    oddata_agg = oddata.groupby(['SLONCOL','SLATCOL','ELONCOL','ELATCOL'])['count'].count().reset_index()
    #生成起终点栅格中心点位置
    oddata_agg['SHBLON'],oddata_agg['SHBLAT'] = grids_centre(oddata_agg['SLONCOL'],oddata_agg['SLATCOL'],params)
    oddata_agg['EHBLON'],oddata_agg['EHBLAT'] = grids_centre(oddata_agg['ELONCOL'],oddata_agg['ELATCOL'],params)
    from shapely.geometry import LineString    
    #遍历生成OD的LineString对象，并赋值给geometry列  
    if arrow:
        oddata_agg['geometry'] = oddata_agg.apply(lambda r:tolinewitharrow(r['SHBLON'],r['SHBLAT'],r['EHBLON'],r['EHBLAT'],**kwargs),axis = 1)    
    else:
        oddata_agg['geometry'] = oddata_agg.apply(lambda r:LineString([[r['SHBLON'],r['SHBLAT']],[r['EHBLON'],r['EHBLAT']]]),axis = 1)    
    #转换为GeoDataFrame  
    oddata_agg = gpd.GeoDataFrame(oddata_agg)    
    oddata_agg = oddata_agg.sort_values(by = 'count')
    #绘制看看是否能够识别图形信息  
    return oddata_agg


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
    return oddata   


# 定义带箭头的LineString函数
def tolinewitharrow(x1,y1,x2,y2,theta = 20,length = 0.1,pos = 0.8):
    '''
    输入起终点坐标，输出带箭头的LineString
    x1,y1,x2,y2  - 起终点坐标
    theta        - 箭头旋转角度
    length       - 箭头相比于原始线的长度比例，例如原始线的长度为1，length设置为0.3，则箭头大小为0.3
    pos          - 箭头位置，0则在起点，1则在终点
    '''
    import numpy as np
    from shapely.geometry import MultiLineString
    #主线
    l_main = [[x1,y1],[x2,y2]]
    #箭头标记位置
    p1,p2 = (1-pos)*x1+pos*x2,(1-pos)*y1+pos*y2
    #箭头一半
    R = np.array([[np.cos(np.radians(theta)),-np.sin(np.radians(theta))],
                  [np.sin(np.radians(theta)),np.cos(np.radians(theta))]])
    l1 = np.dot(R,np.array([[x1-x2,y1-y2]]).T).T[0]*length+np.array([p1,p2]).T
    l1 = [list(l1),[p1,p2]]
    #箭头另一半
    R = np.array([[np.cos(np.radians(-theta)),-np.sin(np.radians(-theta))],
                  [np.sin(np.radians(-theta)),np.cos(np.radians(-theta))]])
    l2 = np.dot(R,np.array([[x1-x2,y1-y2]]).T).T[0]*length+np.array([p1,p2]).T
    l2 = [list(l2),[p1,p2]]
    return MultiLineString([l_main,l1,l2])
