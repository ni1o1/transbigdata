import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
from .grids import GPS_to_grids,grids_centre
import math 
import numpy as np

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

