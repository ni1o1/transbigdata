import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
from .grids import GPS_to_grids,grids_centre
import math 
import numpy as np
from .preprocess import *

def busgps_arriveinfo(data,line,stop,col = ['VehicleId','GPSDateTime','lon','lat','stopname'],
                      stopbuffer = 200,mintime = 300,project_epsg = 2416,timegap = 1800,method = 'project',projectoutput = False):
    '''
    输入公交GPS数据、公交线路与站点的GeoDataFrame，该方法能够识别公交的到离站信息
    输入
    -------
    data : DataFrame
        公交GPS数据，单一公交线路，且需要含有车辆ID、GPS时间、经纬度（wgs84）
    line : GeoDataFrame
        公交线型的GeoDataFrame数据，单一公交线路
    stop : GeoDataFrame
        公交站点的GeoDataFrame数据
    col : List
        列名，按[车辆ID,时间,经度,纬度，站点名称字段]的顺序
    stopbuffer : number
        米，站点的一定距离范围，车辆进入这一范围视为到站，离开则视为离站
    mintime : number
        秒，短时间内公交再次到站则需要与前一次的到站数据结合一起计算到离站时间，该参数设置阈值
    project_epsg : number
        匹配时会将数据转换为投影坐标系以计算距离，这里需要给定投影坐标系的epsg代号
    timegap : number
        秒，清洗数据用，多长时间车辆不出现，就视为新的车辆
    method : str
        公交运行图匹配方法，可选'project'或'dislimit'；
        project为直接匹配线路上最近点，匹配速度快；
        dislimit则需要考虑前面点位置，加上距离限制，匹配速度慢。
    projectoutput : bool
        是否输出投影后的数据

    输出
    -------
    arrive_info : DataFrame
        公交到离站信息
    '''
    VehicleId,GPSDateTime,lon,lat,stopcol = col
    #数据清洗
    print('数据清洗中',end = '')
    line.set_crs(crs='epsg:4326',allow_override=True,inplace=True)
    line = line.to_crs(epsg = project_epsg)
    line_buffer = line.copy()
    line_buffer['geometry'] = line_buffer.buffer(200)
    line_buffer = line_buffer.to_crs(epsg = 4326)
    print('.',end = '')
    data = clean_same(data,col=[VehicleId,GPSDateTime,lon,lat])
    print('.',end = '')
    data = clean_outofshape(data,line_buffer,col = [lon,lat],accuracy = 500)
    print('.')
    data = id_reindex(data,VehicleId,timegap = timegap,timecol = GPSDateTime,suffix='')

    print('运行位置匹配中',end = '')
    #利用project方法，将数据点投影至公交线路上
    lineshp = line['geometry'].iloc[0]
    print('.',end = '')
    data['geometry'] = gpd.points_from_xy(data[lon],data[lat])
    data = gpd.GeoDataFrame(data)
    data.set_crs(crs='epsg:4326',allow_override=True,inplace=True)
    print('.',end = '')
    data = data.to_crs(epsg = project_epsg)
    print('.',end = '')
    if method == 'project':
        data['project'] = data['geometry'].apply(lambda r:lineshp.project(r))
    elif method == 'dislimit':
        tmps = []
        #改进的匹配方法
        for vid in data[VehicleId].drop_duplicates():
            print('.',end = '')
            tmp = data[data[VehicleId]==vid].copy()
            gap = 30
            i = 0
            tmp = tmp.sort_values(by = [VehicleId,GPSDateTime]).reset_index(drop=True)
            tmp['project'] = 0
            from shapely.geometry import LineString
            for i in range(len(tmp)-1):
                if i == 0:
                    proj = lineshp.project(tmp.iloc[i]['geometry'])
                    tmp.loc[i,'project'] = proj
                else:
                    proj = tmp['project'].iloc[i]
                dis = tmp.iloc[i+1]['geometry'].distance(tmp.iloc[i]['geometry'])
                if dis == 0:
                    proj1 = proj
                else:
                    proj2 = lineshp.project(tmp.iloc[i+1]['geometry'])
                    if abs(proj2-proj)>dis:
                        proj1 = np.sign(proj2-proj)*dis+proj
                    else:
                        proj1 = proj2
                tmp.loc[i+1,'project'] = proj1
            tmps.append(tmp)
        data = pd.concat(tmps)
    print('.',end = '')
    #公交站点也进行project
    stop = stop.to_crs(epsg = project_epsg)
    stop['project'] = stop['geometry'].apply(lambda r:lineshp.project(r))
    print('.',end = '')
    #标准化时间
    starttime = data[GPSDateTime].min()
    data['time_st'] = (data[GPSDateTime]-starttime).dt.total_seconds()
    BUS_project = data
    print('.')
    from shapely.geometry import LineString,Polygon
    import shapely

    #定义一个空的list存储识别结果
    ls = []

    print('匹配到离站信息...',end = '')
    #对每一辆车遍历
    for car in BUS_project[VehicleId].drop_duplicates():
        print('.',end = '')
        #提取车辆轨迹
        tmp = BUS_project[BUS_project[VehicleId] == car]
        #如果车辆数据点少于1个，则无法构成轨迹
        if len(tmp)>1:
            #对每一个站点识别
            for stopname in stop[stopcol].drop_duplicates():
                #提取站点位置
                position = stop[stop[stopcol] == stopname]['project'].iloc[0]
                #通过缓冲区与线段交集识别到离站轨迹
                buffer_polygon = LineString([[0,position],
                                             [data['time_st'].max(),position]]).buffer(stopbuffer)
                bus_linestring = LineString(tmp[['time_st','project']].values)
                line_intersection = bus_linestring.intersection(buffer_polygon)
                #整理轨迹，提取到离站时间
                if line_intersection.is_empty:
                    #如果为空，说明车辆没有到站信息
                    continue
                else:
                    if type(line_intersection) == shapely.geometry.linestring.LineString:
                        arrive = [line_intersection]
                    else:
                        arrive = list(line_intersection)
                arrive = pd.DataFrame(arrive)
                arrive['arrivetime']= arrive[0].apply(lambda r:r.coords[0][0])
                arrive['leavetime']= arrive[0].apply(lambda r:r.coords[-1][0])

                #通过时间阈值筛选到离站信息
                a = arrive[['arrivetime']].copy()
                a.columns = ['time']
                a['flag'] = 1
                b = arrive[['leavetime']].copy()
                b.columns = ['time']
                b['flag'] = 0
                c = pd.concat([a,b]).sort_values(by = 'time')
                c['time1'] = c['time'].shift(-1)
                c['flag_1'] = ((c['time1']-c['time'])<mintime)&(c['flag']==0)
                c['flag_2'] = c['flag_1'].shift().fillna(False)
                c['flag_3'] = c['flag_1']|c['flag_2']
                c = c[-c['flag_3']]
                arrive_new = c[c['flag'] == 1][['time']].copy()
                arrive_new.columns = ['arrivetime']
                arrive_new['leavetime'] = list(c[c['flag'] == 0]['time'])
                arrive_new[stopcol] = stopname
                arrive_new[VehicleId] = car
                #合并数据
                ls.append(arrive_new)
    #合成一个大表
    arrive_info = pd.concat(ls)
    arrive_info['arrivetime'] = starttime+arrive_info['arrivetime'].apply(lambda r:pd.Timedelta(int(r),unit = 's'))
    arrive_info['leavetime'] = starttime+arrive_info['leavetime'].apply(lambda r:pd.Timedelta(int(r),unit = 's'))
    if projectoutput:
        return arrive_info,data
    else:
        return arrive_info


def busgps_onewaytime(arrive_info,start,end,col = ['VehicleId','stopname']):
    '''
    输入到离站信息表arrive_info与起终点名称，计算单程耗时
    输入
    -------
    arrive_info : DataFrame
        公交到离站数据
    start : Str
        起点站名字
    end : Str
        终点站名字
    col : List
        字段列名[车辆ID,站点名称]

    
    输出
    -------
    onewaytime : DataFrame
        公交单程耗时
    '''
    #上行
    #将起终点的信息提取后合并到一起
    #终点站的到达时间
    [VehicleId,stopname] = col
    a = arrive_info[arrive_info[stopname] == end][['arrivetime',stopname,VehicleId]]
    #起点站的离开时间
    b = arrive_info[arrive_info[stopname] == start][['leavetime',stopname,VehicleId]]
    a.columns = ['time',stopname,VehicleId]
    b.columns = ['time',stopname,VehicleId]
    #合并信息
    c = pd.concat([a,b])
    #排序后提取每一单程的出行时间
    c = c.sort_values(by = [VehicleId,'time'])
    for i in c.columns:
        c[i+'1'] = c[i].shift(-1)
    #提取以申昆路枢纽站为起点，延安东路外滩为终点的趟次
    c = c[(c[VehicleId] == c[VehicleId+'1'])&
          (c[stopname]==start)&
          (c[stopname+'1']==end)]
    #计算该趟出行的持续时间
    c['duration'] = (c['time1'] - c['time']).dt.total_seconds()
    #标识该趟出行的时间中点在哪一个小时
    c['shour'] = c['time'].dt.hour
    c['方向'] = start+'-'+end
    #储存为c1变量
    c1 = c.copy()
    #下行
    a = arrive_info[arrive_info[stopname] == start][['arrivetime',stopname,VehicleId]]
    b = arrive_info[arrive_info[stopname] == end][['leavetime',stopname,VehicleId]]
    a.columns = ['time',stopname,VehicleId]
    b.columns = ['time',stopname,VehicleId]
    c = pd.concat([a,b])
    c = c.sort_values(by = [VehicleId,'time'])
    for i in c.columns:
        c[i+'1'] = c[i].shift(-1)
    c = c[(c[VehicleId] == c[VehicleId+'1'])&(c[stopname]==end)&(c[stopname+'1']==start)]
    c['duration'] = (c['time1'] - c['time']).dt.total_seconds()
    c['shour'] = c['time'].dt.hour
    c['方向'] = end+'-'+start
    c2 = c.copy()
    onewaytime = pd.concat([c1,c2])
    return onewaytime

