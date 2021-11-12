import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
from .grids import GPS_to_grids,grids_centre
from .preprocess import id_reindex
import math 
import numpy as np

def traj_densify(data,col = ['Vehicleid','Time','Lng','Lat'],timegap = 15):
    '''
    轨迹点增密，确保每隔timegap秒会有一个轨迹点
    
    输入
    -------
    data : DataFrame
        数据
    col : List
        列名，按[车辆ID,时间,经度,纬度]的顺序
    timegap : number
        单位为秒，每隔多长时间插入一个轨迹点
    
    输出
    -------
    data1 : DataFrame
        处理后的数据
    '''
    Vehicleid,Time,Lng,Lat = col
    data[Time] = pd.to_datetime(data[Time])
    data1 = data.copy()
    data1 = data1.drop_duplicates([Vehicleid,Time])
    data1 = id_reindex(data1,Vehicleid)
    data1 = data1.sort_values(by=[Vehicleid+'_new',Time])
    data1['utctime'] = data1[Time].apply(lambda r:int(r.value/1000000000))
    data1['utctime_new'] = data1[Vehicleid+'_new']*10000000000+data1['utctime']
    a = data1.groupby([Vehicleid+'_new'])['utctime'].min().rename('mintime').reset_index()
    b = data1.groupby([Vehicleid+'_new'])['utctime'].max().rename('maxtime').reset_index()
    minmaxtime = pd.merge(a,b)
    mintime = data1['utctime'].min()
    maxtime = data1['utctime'].max()
    timedata = pd.DataFrame(range(mintime,maxtime,timegap),columns = [Time])
    timedata['tmp'] = 1
    minmaxtime['tmp'] = 1
    minmaxtime = pd.merge(minmaxtime,timedata)
    minmaxtime = minmaxtime[(minmaxtime['mintime']<=minmaxtime[Time])&(minmaxtime['maxtime']>=minmaxtime[Time])]
    minmaxtime['utctime_new'] = minmaxtime[Vehicleid+'_new']*10000000000+minmaxtime[Time]
    minmaxtime[Time] = pd.to_datetime(minmaxtime[Time],unit = 's')
    data1 = pd.concat([data1,minmaxtime[['utctime_new',Time]]]).sort_values(by = ['utctime_new'])
    data1 = data1.drop_duplicates(['utctime_new'])
    data1[Lng] =data1.set_index('utctime_new')[Lng].interpolate(method = 'index').values
    data1[Lat] =data1.set_index('utctime_new')[Lat].interpolate(method = 'index').values
    data1[Vehicleid]=data1[Vehicleid].ffill()
    data1[Vehicleid]=data1[Vehicleid].bfill()
    data1 = data1.drop([Vehicleid+'_new','utctime','utctime_new'],axis = 1)
    return data1

def points_to_traj(traj_points,col = ['Lng','Lat','ID']):
    '''
    输入轨迹点，生成轨迹线型的GeoDataFrame
    
    输入
    -------
    traj_points : DataFrame
        轨迹点数据
    col : List
        列名，按[经度,纬度,轨迹编号]的顺序

    输出
    -------
    traj : GeoDataFrame
        生成的轨迹数据
    '''
    [Lng,Lat,ID] = col 
    traj = gpd.GeoDataFrame()
    from shapely.geometry import LineString
    geometry = []
    traj_id = []
    for i in traj_points[ID].drop_duplicates():
        coords = traj_points[traj_points[ID]==i][[Lng,Lat]].values
        traj_id.append(i)
        if len(coords)>=2:
            geometry.append(LineString(coords))
        else:
            geometry.append(None)
    traj[ID] = traj_id
    traj['geometry'] = geometry
    traj = gpd.GeoDataFrame(traj)
    return traj


def points_to_traj(traj_points,col = ['Lng','Lat','ID'],timecol = None):
    '''
    输入轨迹点，生成轨迹线型的GeoDataFrame

    输入
    -------
    traj_points : DataFrame
        轨迹点数据
    col : List
        列名，按[经度,纬度,轨迹编号]的顺序
    timecol : str
        可选，时间列的列名，如果给了则输出带有[经度,纬度,高度,时间]的geojson，可放入kepler中可视化轨迹

    输出
    -------
    traj : GeoDataFrame或json
        生成的轨迹数据，如果timecol没定义则为GeoDataFrame，否则为json
    '''
    [Lng,Lat,ID] = col 
    if timecol:
        geometry = []
        traj_id = []
        for i in traj_points[ID].drop_duplicates():
            coords = traj_points[traj_points[ID]==i][[Lng,Lat,timecol]]
            coords[timecol] = coords[timecol].apply(lambda r:int(r.value/1000000000))
            coords['altitude'] = 0
            coords = coords[[Lng,Lat,'altitude',timecol]].values.tolist()
            traj_id.append(i)
            if len(coords)>=2:
                geometry.append({
                    "type": "Feature",
                    "properties":{ "ID":  i},
                    "geometry": {"type": "LineString",
                                 "coordinates":coords}})
        traj = {"type": "FeatureCollection",
                   "features": geometry}
    else:
        traj = gpd.GeoDataFrame()
        from shapely.geometry import LineString
        geometry = []
        traj_id = []
        for i in traj_points[ID].drop_duplicates():
            coords = traj_points[traj_points[ID]==i][[Lng,Lat]].values
            traj_id.append(i)
            if len(coords)>=2:
                geometry.append(LineString(coords))
            else:
                geometry.append(None)
        traj[ID] = traj_id
        traj['geometry'] = geometry
        traj = gpd.GeoDataFrame(traj)
    return traj

def dumpjson(data,path):
    '''
    输入json数据，存储为文件。这个方法主要是解决numpy数值型无法兼容json包报错的问题

    输入
    -------
    data : json
        要储存的json数据
    path : str
        保存的路径

    '''
    import json
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return super(NpEncoder, self).default(obj)
    f = open(path,mode = 'w')
    json.dump(data,f,cls=NpEncoder) 
    f.close()

