import geopandas as gpd  
import pandas as pd
import numpy as np
from .grids import *

def clean_outofbounds(data,shape,col = ['Lng','Lat'],accuracy=500):
    '''
    剔除超出研究范围的数据

    输入
    -------
    data : DataFrame
        数据
    shape : GeoDataFrame    
        研究范围的GeoDataFrame
    col : List
        经纬度列名
    accuracy : number
        计算原理是先栅格化后剔除，这里定义栅格大小，越小精度越高
    
    输出
    -------
    data1 : DataFrame
        研究范围内的数据
    '''
    Lng,Lat = col
    shape_unary = shape.unary_union
    bounds = shape_unary.bounds
    #栅格化参数
    params = grid_params(bounds,accuracy)
    #数据栅格化
    data1 = data.copy()
    data1['LONCOL'],data1['LATCOL'] = GPS_to_grids(data1[Lng],data1[Lat],params)
    data1_gdf = data1[['LONCOL','LATCOL']].drop_duplicates()
    data1_gdf['geometry'] = gridid_to_polygon(data1_gdf['LONCOL'],data1_gdf['LATCOL'],params)
    data1_gdf = gpd.GeoDataFrame(data1_gdf)
    data1_gdf = data1_gdf[data1_gdf.intersects(shape_unary)]
    data1 = pd.merge(data1,data1_gdf[['LONCOL','LATCOL']]).drop(['LONCOL','LATCOL'],axis = 1)
    return data1

def dataagg(data,shape,col = ['Lng','Lat','count'],accuracy=500):
    '''
    数据集计至小区

    输入
    -------
    data : DataFrame
        数据
    shape : GeoDataFrame
        小区
    col : List
        可传入经纬度两列，如['Lng','Lat']，此时每一列权重为1。也可以传入经纬度和计数列三列，如['Lng','Lat','count']
    accuracy : number
        计算原理是先栅格化后集计，这里定义栅格大小，越小精度越高

    输出
    -------
    aggresult : GeoDataFrame
        小区，其中count列为统计结果
    data1 : DataFrame
        数据，对应上了小区
    '''
    if len(col) == 2:
        Lng,Lat = col
        aggcol = None
    else:
        Lng,Lat,aggcol = col
    shape['index'] = range(len(shape))
    shape_unary = shape.unary_union
    bounds = shape_unary.bounds
    #栅格化参数
    params = grid_params(bounds,accuracy)
    #数据栅格化
    data1 = data.copy()
    data1['LONCOL'],data1['LATCOL'] = GPS_to_grids(data1[Lng],data1[Lat],params)
    data1_gdf = data1[['LONCOL','LATCOL']].drop_duplicates()
    data1_gdf['geometry'] = gpd.points_from_xy(*grids_centre(data1_gdf['LONCOL'],data1_gdf['LATCOL'],params))
    data1_gdf = gpd.GeoDataFrame(data1_gdf)
    data1_gdf = gpd.sjoin(data1_gdf,shape,how = 'left')
    data1 = pd.merge(data1,data1_gdf).drop(['LONCOL','LATCOL'],axis = 1)
    if aggcol:
        aggresult = pd.merge(shape,data1.groupby('index')[aggcol].sum().reset_index()).drop('index',axis = 1)
    else:
        data1['_'] = 1
        aggresult = pd.merge(shape,data1.groupby('index')['_'].sum().rename('count').reset_index()).drop('index',axis = 1)
        data1 = data1.drop('_',axis = 1)
    data1 = data1.drop('index',axis = 1)
    return aggresult,data1

def id_reindex(data,col,new = False,suffix = '_new'):
    '''
    对数据的ID列重新编号

    输入
    -------
    data : DataFrame
        数据 
    col : str
        要重新编号的ID列名
    new : bool
        False，相同ID的新编号相同；True，依据表中的顺序，ID再次出现则编号不同
    suffix : str
        新编号列名的后缀，设置为False时替代原有列名

    输出
    -------
    data1 : DataFrame
        重新编号的数据
    '''
    if suffix == False:
        suffix = ''
    data1 = data.copy()
    if new:
        #新建一列判断是否是新的id
        data1[col+suffix]=data1[col]!=data1[col].shift()
        #累加求和
        data1[col+suffix]=data1[col+suffix].cumsum()-1
    else:
        #提取所有的ID，去重得到个体信息表
        tmp=data1[[col]].drop_duplicates()
        #定义新的编号
        tmp[col+'_']=range(len(tmp))
        #表连接
        data1=pd.merge(data1,tmp,on=col)
        data1[col+suffix] = data1[col+'_']
        if suffix != '_':
            data1 = data1.drop(col+'_',axis = 1)
    return data1