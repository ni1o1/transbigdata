import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
import math 
import numpy as np
def rect_grids(bounds,accuracy = 500):
    '''
    输入经纬度范围bounds，输出栅格GeoDataFrame
    '''
    #导入math包  
    #划定栅格划分范围
    lon1 = bounds[0]
    lat1 = bounds[1]
    lon2 = bounds[2]
    lat2 = bounds[3]
    #取得左下角的经纬度  
    latStart = min(lat1, lat2);  
    lonStart = min(lon1, lon2);  
    #计算栅格的经纬度增加量大小▲Lon和▲Lat，地球半径取6371004米  
    deltaLon = accuracy * 360 / (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360));  
    deltaLat = accuracy * 360 / (2 * math.pi * 6371004);  
    #定义空的GeoDataFrame表，再往里加栅格  
    data = gpd.GeoDataFrame()  
    #定义空的list，后面循环一次就往里面加东西  
    LONCOL_list = []  
    LATCOL_list = []  
    geometry_list = []  
    HBLON_list = []  
    HBLAT_list = []  
    #计算行列要生成的栅格数量  
    #lon方向是lonsnum个栅格  
    lonsnum = int((lon2-lon1)/deltaLon)+1  
    #lat方向是latsnum个栅格  
    latsnum = int((lat2-lat1)/deltaLat)+1  
    for i in range(lonsnum):  
        for j in range(latsnum):  
            #第i列，第j行的栅格中心点坐标  
            HBLON = i*deltaLon + lonStart   
            HBLAT = j*deltaLat + latStart  
            #用周围的栅格推算三个顶点的位置
            HBLON_1 = (i+1)*deltaLon + lonStart  
            HBLAT_1 = (j+1)*deltaLat + latStart  
            #生成栅格的Polygon形状  
            grid_ij = Polygon([  
            (HBLON-deltaLon/2,HBLAT-deltaLat/2),  
            (HBLON_1-deltaLon/2,HBLAT-deltaLat/2),  
            (HBLON_1-deltaLon/2,HBLAT_1-deltaLat/2),  
            (HBLON-deltaLon/2,HBLAT_1-deltaLat/2)]) 
            #把生成的数据都加入到前面定义的空list里面  
            LONCOL_list.append(i)  
            LATCOL_list.append(j)  
            HBLON_list.append(HBLON)  
            HBLAT_list.append(HBLAT)  
            geometry_list.append(grid_ij)  
    #为geopandas文件的每一列赋值为刚刚的list  
    data['LONCOL'] = LONCOL_list  
    data['LATCOL'] = LATCOL_list  
    data['HBLON'] = HBLON_list  
    data['HBLAT'] = HBLAT_list  
    data['geometry'] = geometry_list  
    params = (lonStart,latStart,deltaLon,deltaLat)
    return data,params 

def grid_params(bounds,accuracy = 500):
    '''
    输入经纬度范围bounds，输出栅格参数
    '''
    #划定栅格划分范围
    lon1 = bounds[0]
    lat1 = bounds[1]
    lon2 = bounds[2]
    lat2 = bounds[3]
    #取得左下角的经纬度  
    latStart = min(lat1, lat2);  
    lonStart = min(lon1, lon2);  
    #计算栅格的经纬度增加量大小▲Lon和▲Lat，地球半径取6371004米  
    deltaLon = accuracy * 360 / (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360));  
    deltaLat = accuracy * 360 / (2 * math.pi * 6371004);  
    return (lonStart,latStart,deltaLon,deltaLat)

def GPS_to_grids(lon,lat,params):
    '''
    输入GPS经纬度，输出栅格编号
    '''
    (lonStart,latStart,deltaLon,deltaLat) = params
    loncol = ((lon - (lonStart - deltaLon / 2))/deltaLon).astype('int')  
    latcol = ((lat - (latStart - deltaLat / 2))/deltaLat).astype('int')   
    return loncol,latcol
def grids_centre(loncol,latcol,params):
    '''
    输入栅格编号与栅格化参数，输出栅格中心点坐标
    '''
    (lonStart,latStart,deltaLon,deltaLat) = params
    hblon = loncol*deltaLon + lonStart #格子编号*格子宽+起始横坐标=格子中心横坐标  
    hblat = latcol*deltaLat + latStart
    return hblon,hblat

def gridid_to_polygon(loncol,latcol,params):
    '''
    输入栅格编号与栅格化参数，输出栅格的Polygon列
    '''
    (lonStart,latStart,deltaLon,deltaLat) = params
    HBLON = loncol*deltaLon + lonStart   
    HBLAT = latcol*deltaLat + latStart  
    #用周围的栅格推算三个顶点的位置
    HBLON_1 = (loncol+1)*deltaLon + lonStart  
    HBLAT_1 = (latcol+1)*deltaLat + latStart  
    df = pd.DataFrame()
    df['HBLON'] = HBLON
    df['HBLAT'] = HBLAT
    df['HBLON_1'] = HBLON_1
    df['HBLAT_1'] = HBLAT_1
    return df.apply(lambda r:Polygon([  
    (r['HBLON']-deltaLon/2,r['HBLAT']-deltaLat/2),  
    (r['HBLON_1']-deltaLon/2,r['HBLAT']-deltaLat/2),  
    (r['HBLON_1']-deltaLon/2,r['HBLAT_1']-deltaLat/2),  
    (r['HBLON']-deltaLon/2,r['HBLAT_1']-deltaLat/2)]),axis = 1)

def hexagon_grids(bounds,accuracy = 500):
    '''
    输入经纬度范围bounds，输出六边形栅格GeoDataFrame
    ''' 
    #划定栅格划分范围
    (lon1,lat1,lon2,lat2) = bounds
    #取得左下角的经纬度  
    latStart = min(lat1, lat2);  
    lonStart = min(lon1, lon2);  
    latEnd = max(lat1, lat2);  
    lonEnd = max(lon1, lon2);  
    origin = gpd.GeoDataFrame([Point(lonStart,latStart),Point(lonEnd,latEnd)],columns = ['geometry'])
    origin.crs = {'init':'epsg:4326'}
    origin = origin.to_crs(epsg = 3857)
    x_o = origin['geometry'].iloc[0].x
    y_o = origin['geometry'].iloc[0].y
    x_d = origin['geometry'].iloc[1].x
    y_d = origin['geometry'].iloc[1].y

    lonsnum = (x_d-x_o)/accuracy
    latsnum = (y_d-y_o)/accuracy
    #1
    xs = np.arange(0,lonsnum,3)
    ys = np.arange(0,latsnum,2*(3/4)**0.5)
    xs = pd.DataFrame(xs,columns = ['x'])
    xs['tmp'] = 1
    ys = pd.DataFrame(ys,columns = ['y'])
    ys['tmp'] = 1
    df1 = pd.merge(xs,ys)
    #2
    xs = np.arange(1.5,lonsnum,3)
    ys = np.arange((3/4)**0.5,latsnum,2*(3/4)**0.5)
    xs = pd.DataFrame(xs,columns = ['x'])
    xs['tmp'] = 1
    ys = pd.DataFrame(ys,columns = ['y'])
    ys['tmp'] = 1
    df2 = pd.merge(xs,ys)
    df = pd.concat([df1,df2])
    df['x'],df['y'] = x_o+df['x']*accuracy,y_o+df['y']*accuracy
    def get_hexagon(x,y,accuracy):
        return Polygon([(x-accuracy,y),
             (x-accuracy/2,y+accuracy*(3/4)**0.5),
             (x+accuracy/2,y+accuracy*(3/4)**0.5),
             (x+accuracy,y),
             (x+accuracy/2,y-accuracy*(3/4)**0.5),
             (x-accuracy/2,y-accuracy*(3/4)**0.5),
             (x-accuracy,y)
            ]) 
    df['geometry'] = df.apply(lambda r:get_hexagon(r['x'],r['y'],accuracy),axis = 1)
    df = gpd.GeoDataFrame(df)
    df.crs = {'init':'epsg:3857'}
    df = df.to_crs(epsg = 4326)
    df = df[['geometry']]
    df['ID'] = range(len(df))
    return df
