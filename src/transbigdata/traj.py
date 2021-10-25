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