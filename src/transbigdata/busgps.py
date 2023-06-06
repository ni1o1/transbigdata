'''
BSD 3-Clause License

Copyright (c) 2021, Qing Yu
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import LineString
import shapely
from .preprocess import (
    clean_outofshape,
    id_reindex
)
from .traj import(
    traj_clean_redundant
)



def busgps_arriveinfo(data, line, stop, col=[
        'VehicleId', 'GPSDateTime', 'lon', 'lat', 'stopname'],
        stopbuffer=200, mintime=300,    disgap = 200, project_epsg='auto',
        timegap=1800,  projectoutput=False):
    '''
    Input bus GPS data, bus route and station GeoDataFrame, this
    method can identify the bus arrival and departure information

    Parameters
    -------
    data : DataFrame
        Bus GPS data. It should be the data from one bus route,
        and need to contain vehicle ID, GPS time, latitude and
        longitude (wgs84)
    line : GeoDataFrame
        GeoDataFrame for the bus line
    stop : GeoDataFrame
        GeoDataFrame for bus stops
    col : List
        Column names, in the order of [vehicle ID, time, longitude,
        latitude, station name]
    stopbuffer : number
        Meter. When the vehicle approaches the station within this
        certain distance, it is considered to be arrive at the station.
    mintime : number
        Seconds. Within a short period of time that the bus arrive
        at bus station again, it will not be consider as another arrival
    disgap : number
        Meter. The distance between the front point and the back point
        of the vehicle, which is used to determine whether the vehicle
        is moving or not
    project_epsg : number
        The matching algorithm will convert the data into a projection
        coordinate system to calculate the distance, here the epsg code
        of the projection coordinate system is given
    timegap : number
        Seconds. For how long the vehicle does not appear, it will be
        considered as a new vehicle
    projectoutput : bool
        Whether to output the projected data

    Returns
    -------
    arrive_info : DataFrame
        Bus arrival and departure information
    '''
    data = data.copy()
    line = line.copy()
    stop = stop.copy()
    VehicleId, GPSDateTime, lon, lat, stopcol = col
    # Clean data
    print('Cleaning data', end='')

    if project_epsg=='auto':
        from pyproj import CRS
        # 计算数据点的平均经纬度
        meanlat = data[lat].mean()
        meanlon = data[lon].mean()
        project_epsg = CRS.from_proj4("+proj=aeqd +lat_0="+str(meanlat)+" +lon_0="+str(meanlon)+" +datum=WGS84")# 生成投影坐标系，等距方位投影

    line.crs = {'init':'epsg:4326'}  
    line = line.to_crs(project_epsg)
    line_buffer = line.copy()
    line_buffer['geometry'] = line_buffer.buffer(200)
    line_buffer = line_buffer.to_crs(epsg=4326)
    print('.', end='')
    data = traj_clean_redundant(data, col=[VehicleId, GPSDateTime, lon, lat])
    print('.', end='')
    data = clean_outofshape(data, line_buffer, col=[lon, lat], accuracy=500)
    print('.')
    data = data.sort_values(by=[VehicleId, GPSDateTime])
    # Reindex data
    print('Position matching', end='')
    # project data points onto bus LineString
    lineshp = line['geometry'].iloc[0]
    print('.', end='')
    data['geometry'] = gpd.points_from_xy(data[lon], data[lat])
    data = gpd.GeoDataFrame(data)
    data.set_crs(crs='epsg:4326', allow_override=True, inplace=True)
    print('.', end='')
    data = data.to_crs(project_epsg)
    print('.', end='')

    data['project'] = data['geometry'].apply(lineshp.project)
    

    # 设定时间与距离阈值阈值

    # 比较相邻两条数据的信息
    data[GPSDateTime+'_pre'] = data[GPSDateTime].shift()
    data[VehicleId+'_pre'] = data[VehicleId].shift()
    data['project_pre'] = data['project'].shift()
    #定义三个条件
    # 1.车辆位置发生了变化
    condition1 = abs(data['project_pre']-data['project'])>disgap
    # 2.相邻两条数据"时间间隔大于30分钟"
    condition2 = (data[GPSDateTime]-data[GPSDateTime+'_pre']).dt.total_seconds()>timegap
    # 3."本来这一条记录就是新车"
    condition3 = data[VehicleId+'_pre']!=data[VehicleId]
    data['condition1'] = condition1
    data['condition2'] = condition2
    data['condition3'] = condition3
    # 标记新车辆
    data['flag'] = (condition1 & condition2)|condition3
    # 重新编号
    data[VehicleId+'_new'] = data['flag'].cumsum()
    # 重新编号后的车辆ID
    reid = data[[VehicleId+'_new',VehicleId]].drop_duplicates()
    
    print('.', end='')
    # Project bus stop to bus line
    stop = stop.to_crs(project_epsg)
    stop['project'] = stop['geometry'].apply(lineshp.project)
    print('.', end='')
    starttime = data[GPSDateTime].min()
    data['time_st'] = (data[GPSDateTime]-starttime).dt.total_seconds()
    BUS_project = data
    print('.')
    def get_arrive_info(
            one_bus_data, 
            position,
            stopbuffer = 100
    ):
        '''
        通过线与面的交集，识别到离站信息
        输入：
            one_bus_data：某一辆车的运行图数据
            position：站点位置
            stopbuffer：到站判定的缓冲区间隔
        输出：
            line_intersection：车辆轨迹与buffer的交集
        '''
        from shapely.geometry import LineString
        #站点周边100米缓冲区
        buffer_polygon = LineString([[0,position],
                                    [24*3600,position]]).buffer(stopbuffer)
        #生成车辆轨迹的linestring
        bus_linestring = LineString(one_bus_data[['time_st','project']].values)
        #提取车辆轨迹与buffer的交集
        line_intersection = bus_linestring.intersection(buffer_polygon)
        return line_intersection
    #定义函数
    def get_arrive_leave(line_intersection):
        '''
        从运行图中提取其中的到离站轨迹
        输入：
            line_intersection：车辆轨迹与buffer的交集
        输出：
            arrive：到站信息
        '''
        import shapely
        # 如果没有到离站，则为空
        arrive = []
        if line_intersection.is_empty:
            return pd.DataFrame()
        # 如果只包含一次到离站，则类型为LineString
        elif type(line_intersection) == shapely.geometry.linestring.LineString:
            arrive = [line_intersection]
        # 如果包含多次到离站，则类型为MultiLineString，需要将其拆分为多个LineString
        elif type(line_intersection) == shapely.geometry.multilinestring.MultiLineString:
            arrive = list(line_intersection.geoms)
        #构建为DataFrame
        arrive = pd.DataFrame(arrive)
        #取每一次到离站时间戳
        arrive['arrive_timestamp']= arrive[0].apply(lambda r:r.coords[0][0])
        arrive['leave_timestamp']= arrive[0].apply(lambda r:r.coords[-1][0])
        return arrive
    def merge_arrive(arrive,stopname,vid,mintime = 300):
        '''
        本函数用于合并到离站信息
        输入：
            arrive：到离站信息
            stopname：站点名
            VehicleId：车辆ID
            mintime：时间阈值
        输出：
            arrive_new：合并后的到离站信息
        '''
        #步骤①
        a = arrive[['arrive_timestamp']]  
        a.columns = ['time']  
        a['flag'] = 1  
        b = arrive[['leave_timestamp']]  
        b.columns = ['time']  
        b['flag'] = 0  
        c = pd.concat([a,b]).sort_values(by = 'time')  
        #步骤②
        c['time1'] = c['time'].shift(-1)  
        c['flag_1'] = ((c['time1']-c['time'])<mintime)&(c['flag']==0)  
        c['flag_2'] = c['flag_1'].shift().fillna(False)  
        c['flag_3'] = c['flag_1']|c['flag_2']  
        #步骤③
        c = c[-c['flag_3']]  
        #步骤④
        arrive_new = c[c['flag'] == 1][['time']]  
        arrive_new.columns = ['arrive_timestamp']  
        arrive_new['leave_timestamp'] = list(c[c['flag'] == 0]['time'])  
        arrive_new[stopcol] = stopname  
        arrive_new[VehicleId+'_new'] = vid 
        return arrive_new 
    #定义一个空的list存储识别结果
    ls = []
    #对每一辆车遍历
    print('Matching arrival and leaving info...', end='')
    for vid in BUS_project[VehicleId+'_new'].drop_duplicates():
        print('.', end='')
        #提取车辆运行图
        one_bus_data = BUS_project[BUS_project[VehicleId+'_new'] == vid]
        #如果车辆数据点少于等于1个，则无法构成轨迹
        if len(one_bus_data)==1:
            continue
        else:
            #对每一个站点识别
            for stopname in stop[stopcol].drop_duplicates():
                #提取站点位置
                position = stop[stop[stopcol] == stopname]['project'].iloc[0]
                #通过线与面的交集，识别到离站信息
                line_intersection = get_arrive_info(one_bus_data,position,stopbuffer = stopbuffer)
                arrive = get_arrive_leave(line_intersection)
                if len(arrive)==0:
                    continue
                arrive_new = merge_arrive(arrive,stopname,vid,mintime = mintime)
                #合并数据
                ls.append(arrive_new)
    #将到离站信息合并
    arrive_info = pd.concat(ls)

    arrive_info['arrivetime'] = starttime + \
        arrive_info['arrive_timestamp'].apply(
            lambda r: pd.Timedelta(int(r), unit='s'))
    arrive_info['leavetime'] = starttime + \
        arrive_info['leave_timestamp'].apply(
            lambda r: pd.Timedelta(int(r), unit='s'))
    arrive_info = pd.merge(arrive_info, reid)
    arrive_info = arrive_info.drop(['arrive_timestamp', 'leave_timestamp',VehicleId+'_new'], axis=1)
    if projectoutput:
        return arrive_info, data # pragma: no cover
    else:
        return arrive_info


def busgps_onewaytime(arrive_info, start, end,
                      col=['VehicleId', 'stopname',
                           'arrivetime', 'leavetime']):
    '''
    Input the departure information table drive_info and the station
    information table stop to calculate the one-way travel time

    Parameters
    -------
    arrive_info : DataFrame
        The departure information table drive_info
    start : Str
        Starting station name
    end : Str
        Ending station name
    col : List
        Column name [vehicle ID, station name,arrivetime,leavetime]


    Returns
    -------
    onewaytime : DataFrame
        One-way travel time of the bus
    '''
    # For one direction
    # The information of start and end points is extracted and merged together
    # Arrival time of terminal
    [VehicleId, stopname, arrivetime, leavetime] = col
    arrive_info[arrivetime] = pd.to_datetime(arrive_info[arrivetime])
    arrive_info[leavetime] = pd.to_datetime(arrive_info[leavetime])
    a = arrive_info[arrive_info[stopname] ==
                    end][[arrivetime, stopname, VehicleId]]
    # Departure time of starting station
    b = arrive_info[arrive_info[stopname] ==
                    start][[leavetime, stopname, VehicleId]]
    a.columns = ['time', stopname, VehicleId]
    b.columns = ['time', stopname, VehicleId]
    # Concat data
    c = pd.concat([a, b])
    # After sorting, extract the travel time of each one-way trip
    c = c.sort_values(by=[VehicleId, 'time'])
    for i in c.columns:
        c[i+'1'] = c[i].shift(-1)
    c = c[(c[VehicleId] == c[VehicleId+'1']) &
          (c[stopname] == start) &
          (c[stopname+'1'] == end)]
    # Calculate the duration of the trip
    c['duration'] = (c['time1'] - c['time']).dt.total_seconds()
    c['shour'] = c['time'].dt.hour
    c['direction'] = start+'-'+end
    c1 = c.copy()
    # Do the same for the other direction
    a = arrive_info[arrive_info[stopname] ==
                    start][['arrivetime', stopname, VehicleId]]
    b = arrive_info[arrive_info[stopname] ==
                    end][['leavetime', stopname, VehicleId]]
    a.columns = ['time', stopname, VehicleId]
    b.columns = ['time', stopname, VehicleId]
    c = pd.concat([a, b])
    c = c.sort_values(by=[VehicleId, 'time'])
    for i in c.columns:
        c[i+'1'] = c[i].shift(-1)
    c = c[(c[VehicleId] == c[VehicleId+'1']) &
          (c[stopname] == end) & (c[stopname+'1'] == start)]
    c['duration'] = (c['time1'] - c['time']).dt.total_seconds()
    c['shour'] = c['time'].dt.hour
    c['direction'] = end+'-'+start
    c2 = c.copy()
    onewaytime = pd.concat([c1, c2])
    return onewaytime
