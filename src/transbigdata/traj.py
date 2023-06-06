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
from .preprocess import id_reindex
from .coordinates import getdistance
from .grids import GPS_to_grid
import osmnx as ox
from .coordinates import getdistance
from .gisprocess import ckdnearest_line
import numpy as np
from pykalman import KalmanFilter
from pyproj import CRS

def traj_smooth(data,col = ['id','time','lon', 'lat'],proj = False,process_noise_std = 0.5, measurement_noise_std = 1):
    '''
    Smooth Trajectory Using Kalman Filter.

    Parameters
    ----------
    data: DataFrame
        Trajectory data
    col: list
        Column names of the trajectory data
    proj: bool
        Whether to perform equidistant projection
    process_noise_std: float
        Standard deviation of the process noise
    measurement_noise_std: float
        Standard deviation of the measurement noise

    Returns
    -------
    data: DataFrame
        Smoothed trajectory data
    '''
    id, time, lon, lat = col
    data = data.copy()
    data[time] = pd.to_datetime(data[time])
    data = data.sort_values(by=[id,time])
    # If `proj` is set to `True`, the trajectory points will be converted to equidistant projection coordinates.
    if proj:
        epsg = CRS.from_proj4("+proj=aeqd +lat_0="+str(data[lat].mean())+" +lon_0="+str(data[lon].mean())+" +datum=WGS84")
        data = gpd.GeoDataFrame(data)
        data['geometry'] = gpd.points_from_xy(data[lon],data[lat])
        data.crs = 'epsg:4326'
        data = data.to_crs(epsg)
        data['x'] = data.geometry.x
        data['y'] = data.geometry.y
    else:
        data['x'] = data[lon]
        data['y'] = data[lat]
    # Smooth the trajectory for each ID
    def Kalman_traj_smooth(data,process_noise_std, measurement_noise_std):
        '''
        Smoothing Trajectory Data Using a Kalman Filter

        Parameters
        ----
        data: DataFrame
            Trajectory data, including columns for time, longitude, and latitude.
        process_noise_std: float or list
            Standard deviation of the process noise. If it is a list, it is assumed to be the diagonal elements of the process noise covariance matrix.
        measurement_noise_std: float or list
            Standard deviation of the measurement noise. If it is a list, it is assumed to be the diagonal elements of the measurement noise covariance matrix.

        Returns
        ----
        data: DataFrame
            Smoothed trajectory data.
        '''
        # 拷贝数据，避免修改原始数据
        data = data.copy()
        # 轨迹数据转换为numpy数组
        observations = data[['x', 'y']].values
        timestamps = data[time]
        # F-状态转移矩阵
        transition_matrix = np.array([[1, 0, 1, 0],
                                    [0, 1, 0, 1],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]])
        # H-观测矩阵
        observation_matrix = np.array([[1, 0, 0, 0],
                                    [0, 1, 0, 0]])
        # R-观测噪声协方差矩阵
        # 如果measurement_noise_std是list，则认为是观测噪声协方差矩阵的对角线元素
        if isinstance(measurement_noise_std, list):
            observation_covariance = np.diag(measurement_noise_std)**2  # pragma: no cover
        else:
            observation_covariance = np.eye(2) * measurement_noise_std**2
        # Q-过程噪声协方差矩阵
        # 如果process_noise_std是list，则认为是过程噪声协方差矩阵的对角线元素
        if isinstance(process_noise_std, list):
            transition_covariance = np.diag(process_noise_std)**2   # pragma: no cover
        else:
            transition_covariance = np.eye(4) * process_noise_std**2    
        # 初始状态
        initial_state_mean = [observations[0, 0], observations[0, 1], 0, 0]
        # 初始状态协方差矩阵
        initial_state_covariance = np.eye(4) * 1
        # 初始化卡尔曼滤波器
        kf = KalmanFilter(
            transition_matrices=transition_matrix,
            observation_matrices=observation_matrix,
            initial_state_mean=initial_state_mean,
            initial_state_covariance=initial_state_covariance,
            observation_covariance=observation_covariance,
            transition_covariance=transition_covariance
        )
        # 使用卡尔曼滤波器进行平滑处理
        # 先创建变量存储平滑后的状态
        smoothed_states = np.zeros((len(observations), 4))
        # 将初始状态存储到平滑后的状态中
        smoothed_states[0, :] = initial_state_mean
        # 从第二个状态开始，进行循环迭代
        current_state = initial_state_mean
        current_covariance = initial_state_covariance
        for i in range(1, len(observations)):
            # 计算时间间隔
            dt = (timestamps.iloc[i] - timestamps.iloc[i - 1]).total_seconds()  
            # 更新状态转移矩阵
            kf.transition_matrices = np.array([[1, 0, dt, 0],
                                            [0, 1, 0, dt],
                                            [0, 0, 1, 0],
                                            [0, 0, 0, 1]])
            # 根据当前状态的预测情况与观测结果进行状态估计
            current_state, current_covariance = kf.filter_update(
                current_state, current_covariance, observations[i]
            )
            # 将平滑后的状态存储到变量中
            smoothed_states[i, :] = current_state 
        # 将平滑后的数据结果添加到原始数据中
        data['x'] = smoothed_states[:, 0]
        data['y'] = smoothed_states[:, 1]
        return data
    data = data.groupby(id).apply(lambda x:Kalman_traj_smooth(x,process_noise_std, measurement_noise_std))
    if proj:
        data['geometry'] = gpd.points_from_xy(data['x'],data['y'])
        data.crs = epsg
        data = data.to_crs('epsg:4326')
        data[lon] = data.geometry.x
        data[lat] = data.geometry.y
        data.drop(['x','y','geometry'],axis=1,inplace=True)
    else:
        data[lon] = data['x']
        data[lat] = data['y']
        data.drop(['x','y'],axis=1,inplace=True)
    return data

def traj_mapmatch(traj,G,col=['lon','lat']):
    '''
    Nearest map matching: Find the nearest point on the road network for each trajectory point.
    When conducting nearest neighbor matching, we need to find the closest road segment on the road network for each trajectory point, and match the trajectory point to that segment. In practice, we can first extract the nodes of the road segments to form a set of points (i.e., extracting each coordinate point from each LineString in the geometry column), then calculate the nearest distance between the trajectory point and this set of points, and finally match the trajectory point to the road segment where the nearest distance's node is located. This process effectively transforms the problem of matching points to lines into a problem of matching points to points.

    Parameters
    -------
    traj : DataFrame
        The trajectory point data set to be matched.
    G : networkx multidigraph
        The road network used for matching, created by osmnx.
    col : list
        The name of the longitude and latitude columns in the trajectory point data set.

    Returns
    -------
    traj_matched : DataFrame
        The trajectory point data set after matching.
    '''
    lon,lat = col
    traj_matched = traj.copy()
    # 将轨迹点数据转换为GeoDataFrame
    traj_matched['geometry'] = gpd.points_from_xy(traj_matched[lon], traj_matched[lat])
    traj_matched = gpd.GeoDataFrame(traj_matched)
    # 将路网转换为GeoDataFrame
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)  
    gdf_edges = gdf_edges[['geometry']].reset_index() # 仅保留几何信息，并重置索引
    # 近邻匹配
    traj_matched = ckdnearest_line(traj_matched,gdf_edges)
    #为每一个轨迹点找到最近点的几何信息
    def get_nearest_point_on_line(r):
        point = r['geometry_x']
        line = r['geometry_y']
        nearestpoint = line.interpolate(line.project(point))
        return nearestpoint
    traj_matched['geometry'] = traj_matched.apply(get_nearest_point_on_line,axis=1)
    #计算轨迹点到最近点的距离（米）
    traj_matched['dist'] = getdistance(
        traj_matched['geometry_x'].x,
        traj_matched['geometry_x'].y,
        traj_matched['geometry'].x,
        traj_matched['geometry'].y)
    #提取经纬度信息
    traj_matched[lon] = traj_matched['geometry'].x
    traj_matched[lat] = traj_matched['geometry'].y
    #删除无用的字段
    traj_matched = traj_matched.drop(['index','geometry_x','geometry_y'],axis = 1)
    return traj_matched

def traj_clean_redundant(data, col=['VehicleNum', 'Time', 'Lng', 'Lat']):
    '''
    Delete the data with the same information as the data before and
    after to reduce the amount of data. For example, if several consecutive
    data of an individual have the same information except for the time,
    only the first and last two data can be kept

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        The column name, in the order of [‘Vehicleid, Time’]. It will sort
        by time, and then determine the information of other columns besides
        the time

    Returns
    -------
    data1 : DataFrame
        Cleaned data
    '''
    [VehicleNum, Time, Lng, Lat] = col[:4]
    extra = col[4:]
    data1 = data.copy()
    data1 = data1.drop_duplicates(subset=[VehicleNum, Time])
    data1 = data1.sort_values(by=[VehicleNum, Time])
    data1['issame'] = 0
    for i in [VehicleNum, Lng, Lat]+extra:
        data1['issame'] += (data1[i].shift() == data1[i]
                            ) & (data1[i].shift(-1) == data1[i])
    data1 = data1[-(data1['issame'] == len([VehicleNum, Lng, Lat]+extra))]
    data1 = data1.drop('issame', axis=1)
    return data1

def traj_clean_drift(data, col=['VehicleNum', 'Time', 'Lng', 'Lat'],
                     method='twoside',
                     speedlimit=80,
                     dislimit=1000,
                     anglelimit=30):
    '''
    Delete the drift in the trajectory data. The drift is defined as the data with a speed greater than the speed limit or the distance between the current point and the next point is greater than the distance limit or the angle between the current point, the previous point, and the next point is smaller than the angle limit. The speed limit is 80km/h by default, and the distance limit is 1000m by default. The method of cleaning drift data is divided into two methods: ‘oneside’ and ‘twoside’. The ‘oneside’ method is to consider the speed of the current point and the next point, and the ‘twoside’ method is to consider the speed of the current point, the previous point, and the next point.

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        Column names, in the order of [‘VehicleNum’, ‘Time’, ‘Lng’, ‘Lat’]
    method : string
        Method of cleaning drift data, including ‘oneside’ and ‘twoside’
    speedlimit : number
        Speed limitation
    dislimit : number
        Distance limit
    anglelimit : number
        Angle limit

    Returns
    -------
    data1 : DataFrame
        Cleaned data
    '''
    [VehicleNum, Time, Lng, Lat] = col
    data1 = data.copy()
    data1 = data1.drop_duplicates(subset=[VehicleNum, Time])
    data1[Time+'_dt'] = pd.to_datetime(data1[Time])
    data1 = data1.sort_values(by=[VehicleNum, Time])

    #计算前后点距离、时间差、速度
    for i in [VehicleNum, Lng, Lat, Time+'_dt']:
        data1[i+'_pre'] = data1[i].shift()
        data1[i+'_next'] = data1[i].shift(-1)

    data1['dis_pre'] = getdistance(
        data1[Lng],
        data1[Lat],
        data1[Lng+'_pre'],
        data1[Lat+'_pre'])
    data1['dis_next'] = getdistance(
        data1[Lng],
        data1[Lat],
        data1[Lng+'_next'],
        data1[Lat+'_next'])
    data1['dis_prenext'] = getdistance(
        data1[Lng+'_pre'],
        data1[Lat+'_pre'],
        data1[Lng+'_next'],
        data1[Lat+'_next'])
    
    #计算前后点时间差
    data1['timegap_pre'] = data1[Time+'_dt'] - data1[Time+'_dt_pre']
    data1['timegap_next'] = data1[Time+'_dt_next'] - data1[Time+'_dt']
    data1['timegap_prenext'] = data1[Time+'_dt_next'] - data1[Time+'_dt_pre']

    #计算前后点速度
    data1['speed_pre'] = data1['dis_pre'] / \
        data1['timegap_pre'].dt.total_seconds()*3.6
    data1['speed_next'] = data1['dis_next'] / \
        data1['timegap_next'].dt.total_seconds()*3.6
    data1['speed_prenext'] = data1['dis_prenext'] / \
        data1['timegap_prenext'].dt.total_seconds()*3.6

    #余弦定理计算夹角
    angle_cos = (data1['dis_pre']**2+data1['dis_next']**2-data1['dis_prenext']**2)/(2*data1['dis_pre']*data1['dis_next'])
    angle_cos = np.maximum(np.minimum(angle_cos, 1), -1)
    data1['angle'] = np.degrees(np.arccos(angle_cos))

    #以速度限制删除异常点
    if speedlimit:
        if method == 'oneside':
            data1 = data1[
                -((data1[VehicleNum+'_pre'] == data1[VehicleNum]) &
                  (data1['speed_pre'] > speedlimit))]
        elif method == 'twoside':
            data1 = data1[
                -((data1[VehicleNum+'_pre'] == data1[VehicleNum]) &
                  (data1[VehicleNum+'_next'] == data1[VehicleNum]) &
                    (data1['speed_pre'] > speedlimit) &
                    (data1['speed_next'] > speedlimit) &
                    (data1['speed_prenext'] < speedlimit))]
    #以距离限制删除异常点
    if dislimit:
        if method == 'oneside':
            data1 = data1[
                -((data1[VehicleNum+'_pre'] == data1[VehicleNum]) &
                  (data1['dis_pre'] > dislimit))]
        elif method == 'twoside':
            data1 = data1[
                -((data1[VehicleNum+'_pre'] == data1[VehicleNum]) &
                  (data1[VehicleNum+'_next'] == data1[VehicleNum]) &
                    (data1['dis_pre'] > dislimit) &
                    (data1['dis_next'] > dislimit) &
                    (data1['dis_prenext'] < dislimit))]
    #以角度限制删除异常点
    if anglelimit:
        data1 = data1[
            -((data1[VehicleNum+'_pre'] == data1[VehicleNum]) &
              (data1[VehicleNum+'_next'] == data1[VehicleNum]) &
                (data1['angle'] < anglelimit))]
    data1 = data1[data.columns]
    return data1


def traj_segment(data,groupby_col = ['id','moveid'],retain_col = ['time','lon','lat']):
    """
    Segment the trajectory in order and return the starting and ending information of each segment.
    This function can segment GPS trajectory data, calculate the start and end information of each segment, and store the results in a DataFrame object. The input of this function includes a pandas DataFrame object containing GPS trajectory data,  field names for grouping, and field names to be retained. The output is a pandas DataFrame object containing the starting and ending information of each segment, where each row represents a trajectory segment.

    Parameters
    -------
    data : DataFrame
        The trajectory data needs to be sorted beforehand.
    groupby_col : List
        A list of strings specifying the groupby fields to be used for segmentation.
    retain_col : List
        A list of strings specifying the fields to be retained.

    Returns
    -------
    data : DataFrame
        Containing the starting and ending information of each segment, where each row represents a trajectory segment.
    """
    data = data.copy()
    # 1. Generate the starting and ending information of each segment
    sdata = data.drop_duplicates(subset=groupby_col,keep='first')[groupby_col+retain_col]
    edata = data.drop_duplicates(subset=groupby_col,keep='last')[groupby_col+retain_col]
    # 2. Rename the fields
    sdata.rename(columns = dict(zip(retain_col,['s'+col for col in retain_col])),inplace=True)
    edata.rename(columns = dict(zip(retain_col,['e'+col for col in retain_col])),inplace=True)
    # 3. Merge the starting and ending information of each segment
    data = pd.merge(sdata,edata,on = groupby_col,how = 'inner')
    return data


def traj_slice(traj_data, slice_data, traj_col=['vid', 'time'], slice_col = ['vid','stime','etime','tripid']):
    '''
    Slice the trajectory data according to the slice data.
    This method extracts data from a given set of trajectory data(traj_data) based on a specified time period(slice_data).

    Parameters
    -------
    traj_data : DataFrame
        Trajectory data, containing the trajectory of each vehicle
    slice_data : DataFrame
        Slice data, containing the start time, end time and vehicleid of each slice
    traj_col : List
        The column name of trajectory data, in the sequence of [VehicleNum, Time]
    slice_col : List
        The column name of slice data, in the sequence of [VehicleNum_slice, Stime, Etime, SliceId]

    Returns
    -------
    data_sliced : DataFrame
        The sliced trajectory data

    Example
    -------
    >>> tbd.traj_slice(GPSData, move, traj_col=['vid', 'time'], slice_col = ['vid','stime','etime','tripid'])
        
    '''
    GPSData = traj_data.copy()
    SliceData = slice_data.copy()
    VehicleNum, Time  = traj_col
    VehicleNum_slice,Stime, Etime, SliceId = slice_col

    # Convert the time format to datetime
    GPSData[Time] = pd.to_datetime(GPSData[Time])
    SliceData[Stime] = pd.to_datetime(SliceData[Stime])-pd.Timedelta(seconds=0.01)
    SliceData[Etime] = pd.to_datetime(SliceData[Etime])+pd.Timedelta(seconds=0.01)

    # Extract start and end points of the slice
    slice_s = SliceData[[VehicleNum_slice, Stime,SliceId]].copy()
    slice_s.columns = [VehicleNum, Time, SliceId]
    slice_s['flag'] = 1
    slice_e = SliceData[[VehicleNum_slice, Etime,SliceId]].copy()
    slice_e.columns = [VehicleNum, Time, SliceId]
    slice_e['flag'] = -1

    # Concatenate the start and end points of the slice
    data_sliced = pd.concat([GPSData, slice_s, slice_e])
    data_sliced = data_sliced.sort_values(by=[VehicleNum, Time])
    data_sliced[SliceId] = data_sliced[SliceId].ffill()

    # Extract the trajectory data in the slice
    data_sliced['flag'] = data_sliced['flag'].fillna(0)
    data_sliced['flag1'] = data_sliced.groupby(VehicleNum)['flag'].cumsum()
    data_sliced[VehicleNum] = data_sliced[VehicleNum].ffill()
    data_sliced = data_sliced[(data_sliced['flag1'] == 1) &
                              (data_sliced['flag'] == 0) &
                            (-data_sliced[VehicleNum].isnull())]
    data_sliced[SliceId] = data_sliced[SliceId].ffill()
    data_sliced.drop(['flag','flag1'], axis=1, inplace=True)
    
    return data_sliced

def traj_densify(data, col=['Vehicleid', 'Time', 'Lng', 'Lat'], timegap=15):
    '''
    Trajectory densification, ensure that there is a trajectory point each
    timegap seconds

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        The column name, in the sequence of [Vehicleid, Time, lng, lat]
    timegap : number
        The sampling interval (second)

    Returns
    -------
    data1 : DataFrame
        The processed data
    '''
    Vehicleid, Time, Lng, Lat = col
    data[Time] = pd.to_datetime(data[Time])
    data1 = data.copy()
    data1 = data1.drop_duplicates([Vehicleid, Time])
    data1 = id_reindex(data1, Vehicleid)
    data1 = data1.sort_values(by=[Vehicleid+'_new', Time])
    data1['utctime'] = data1[Time].apply(lambda r: int(r.value/1000000000))
    data1['utctime_new'] = data1[Vehicleid+'_new']*10000000000+data1['utctime']
    a = data1.groupby([Vehicleid+'_new']
                      )['utctime'].min().rename('mintime').reset_index()
    b = data1.groupby([Vehicleid+'_new']
                      )['utctime'].max().rename('maxtime').reset_index()
    minmaxtime = pd.merge(a, b)
    mintime = data1['utctime'].min()
    maxtime = data1['utctime'].max()
    timedata = pd.DataFrame(range(mintime, maxtime, timegap), columns=[Time])
    timedata['tmp'] = 1
    minmaxtime['tmp'] = 1
    minmaxtime = pd.merge(minmaxtime, timedata)
    minmaxtime = minmaxtime[(minmaxtime['mintime'] <= minmaxtime[Time]) & (
        minmaxtime['maxtime'] >= minmaxtime[Time])]
    minmaxtime['utctime_new'] = minmaxtime[Vehicleid+'_new'] * \
        10000000000+minmaxtime[Time]
    minmaxtime[Time] = pd.to_datetime(minmaxtime[Time], unit='s')
    data1 = pd.concat([data1, minmaxtime[['utctime_new', Time]]]
                      ).sort_values(by=['utctime_new'])
    data1 = data1.drop_duplicates(['utctime_new'])
    data1[Lng] = data1.set_index('utctime_new')[
        Lng].interpolate(method='index').values
    data1[Lat] = data1.set_index('utctime_new')[
        Lat].interpolate(method='index').values
    data1[Vehicleid] = data1[Vehicleid].ffill()
    data1[Vehicleid] = data1[Vehicleid].bfill()
    data1 = data1.drop([Vehicleid+'_new', 'utctime', 'utctime_new'], axis=1)
    return data1


def traj_sparsify(data, col=['Vehicleid', 'Time', 'Lng', 'Lat'], timegap=15,
                  method='subsample'):
    '''
    Trajectory sparsify. When the sampling frequency of trajectory data is too
    high, the amount of data is too large, which is not convenient for the
    analysis of some studies that require less data frequency. This function
    can expand the sampling interval and reduce the amount of data.

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        The column name, in the sequence of [Vehicleid, Time, lng, lat]
    timegap : number
        Time gap between trajectory point
    method : str
        'interpolate' or 'subsample'

    Returns
    -------
    data1 : DataFrame
        Sparsified trajectory data
    '''
    Vehicleid, Time, Lng, Lat = col
    data[Time] = pd.to_datetime(data[Time], unit='s')
    data1 = data.copy()
    data1 = data1.drop_duplicates([Vehicleid, Time])
    data1 = id_reindex(data1, Vehicleid)
    data1 = data1.sort_values(by=[Vehicleid+'_new', Time])
    data1['utctime'] = data1[Time].apply(lambda r: int(r.value/1000000000))
    data1['utctime_new'] = data1[Vehicleid+'_new']*10000000000+data1['utctime']
    if method == 'interpolate':
        a = data1.groupby([Vehicleid+'_new']
                          )['utctime'].min().rename('mintime').reset_index()
        b = data1.groupby([Vehicleid+'_new']
                          )['utctime'].max().rename('maxtime').reset_index()
        minmaxtime = pd.merge(a, b)
        mintime = data1['utctime'].min()
        maxtime = data1['utctime'].max()
        timedata = pd.DataFrame(
            range(mintime, maxtime, timegap), columns=[Time])
        timedata['tmp'] = 1
        minmaxtime['tmp'] = 1
        minmaxtime = pd.merge(minmaxtime, timedata)
        minmaxtime = minmaxtime[(minmaxtime['mintime'] <= minmaxtime[Time]) & (
            minmaxtime['maxtime'] >= minmaxtime[Time])]
        minmaxtime['utctime_new'] = minmaxtime[Vehicleid+'_new'] * \
            10000000000+minmaxtime[Time]
        minmaxtime[Time] = pd.to_datetime(minmaxtime[Time], unit='s')
        data1 = pd.concat([
            data1, minmaxtime[['utctime_new', Time]]
        ]).sort_values(by=['utctime_new'])
        data1 = data1.drop_duplicates(['utctime_new'])
        data1[Lng] = data1.set_index('utctime_new')[
            Lng].interpolate(method='index').values
        data1[Lat] = data1.set_index('utctime_new')[
            Lat].interpolate(method='index').values
        data1[Vehicleid] = data1[Vehicleid].ffill()
        data1[Vehicleid] = data1[Vehicleid].bfill()
        data1 = pd.merge(minmaxtime['utctime_new'], data1)
        data1 = data1.drop(
            [Vehicleid+'_new', 'utctime', 'utctime_new'], axis=1)
    if method == 'subsample':
        data1['utctime_new'] = (data1['utctime_new']/timegap).astype(int)
        data1 = data1.drop_duplicates(subset=['utctime_new'])
        data1 = data1.drop(
            [Vehicleid+'_new', 'utctime', 'utctime_new'], axis=1)
    return data1

def traj_stay_move(data, params,
                     col=['ID', 'dataTime', 'longitude', 'latitude'],
                     activitytime=1800):
    '''
    Input trajectory data and gridding parameters, identify stay and move

    Parameters
    ----------------
    data : DataFrame
        trajectory data
    params : List
        gridding parameters
    col : List
        The column name, in the order of ['ID','dataTime','longitude',
        'latitude']
    activitytime : Number
        How much time to regard as activity

    Returns
    ----------------
    stay : DataFrame
        stay information
    move : DataFrame
        move information
    '''
    uid, timecol, lon, lat = col
    # Identify stay
    data = data.sort_values(by=col[:2])
    stay = data.copy()
    stay = stay.rename(columns={lon: 'lon', lat: 'lat', timecol: 'stime'})
    stay['stime'] = pd.to_datetime(stay['stime'])
    stay['LONCOL'], stay['LATCOL'] = GPS_to_grid(
        stay['lon'], stay['lat'], params)
    # Number the status
    stay['status_id'] = ((stay['LONCOL'] != stay['LONCOL'].shift()) |
                         (stay['LATCOL'] != stay['LATCOL'].shift()) |
                         (stay[uid] != stay[uid].shift())).astype(int)
    stay['status_id'] = stay.groupby([uid])['status_id'].cumsum()
    stay = stay.drop_duplicates(
        subset=[uid, 'status_id'], keep='first').copy()
    stay['etime'] = stay['stime'].shift(-1)
    stay = stay[stay[uid] == stay[uid].shift(-1)].copy()
    # Remove the duration shorter than given activitytime
    stay['duration'] = (pd.to_datetime(stay['etime']) -
                        pd.to_datetime(stay['stime'])).dt.total_seconds()
    stay = stay[stay['duration'] >= activitytime].copy()
    stay = stay[[uid, 'stime', 'LONCOL', 'LATCOL',
                 'etime', 'lon', 'lat', 'duration']]
    
    # Add the first and last two data points for each ID in the Stay dataset before conducting move detection, so that the movement patterns of individuals at the beginning and end of the study period can also be identified.
    first_data = data.drop_duplicates(subset=[uid],keep='first').copy()
    last_data = data.drop_duplicates(subset=[uid],keep='last').copy()
    first_data['stime'] = first_data[timecol]
    first_data['etime'] = first_data[timecol]
    first_data['duration'] = 0
    first_data['lon'] = first_data[lon]
    first_data['lat'] = first_data[lat]
    first_data['LONCOL'], first_data['LATCOL'] = GPS_to_grid(
        first_data['lon'], first_data['lat'], params)
    first_data = first_data[[uid, 'stime', 'LONCOL', 'LATCOL',
                    'etime', 'lon', 'lat', 'duration']]

    last_data['stime'] = last_data[timecol]
    last_data['etime'] = last_data[timecol]
    last_data['duration'] = 0
    last_data['lon'] = last_data[lon]
    last_data['lat'] = last_data[lat]
    last_data['LONCOL'], last_data['LATCOL'] = GPS_to_grid(
        last_data['lon'], last_data['lat'], params)
    last_data = last_data[[uid, 'stime', 'LONCOL', 'LATCOL',
                    'etime', 'lon', 'lat', 'duration']]
    # Identify move
    move = pd.concat([first_data,stay,last_data],axis=0).sort_values(by=[uid,'stime'])
    move['stime_next'] = move['stime'].shift(-1)
    move['elon'] = move['lon'].shift(-1)
    move['elat'] = move['lat'].shift(-1)
    move['ELONCOL'] = move['LONCOL'].shift(-1)
    move['ELATCOL'] = move['LATCOL'].shift(-1)
    move[uid+'_next'] = move[uid].shift(-1)
    move = move[move[uid+'_next'] == move[uid]
                ].drop(['stime', 'duration', uid+'_next'], axis=1)
    move = move.rename(columns={'lon': 'slon',
                                'lat': 'slat',
                                'etime': 'stime',
                                'stime_next': 'etime',
                                'LONCOL': 'SLONCOL',
                                'LATCOL': 'SLATCOL',
                                })
    move['duration'] = (
        move['etime'] - move['stime']).dt.total_seconds()
    
    move['moveid'] = range(len(move))
    stay['stayid'] = range(len(stay))
    return stay, move



def traj_to_linestring(traj_points, col=['Lng', 'Lat', 'ID'], timecol=None):
    '''
    Input trajectory, generate GeoDataFrame

    Parameters
    -------
    traj_points : DataFrame
        trajectory data
    col : List
        The column name, in the sequence of [lng, lat,trajectoryid]
    timecol : str(Optional)
        Optional, the column name of the time column. If given, the geojson
        with [longitude, latitude, altitude, time] in returns can be put into
        the Kepler to visualize the trajectory

    Returns
    -------
    traj : GeoDataFrame
        Generated trajectory
    '''
    [Lng, Lat, ID] = col
    if timecol:
        geometry = []
        traj_id = []
        for i in traj_points[ID].drop_duplicates():
            coords = traj_points[traj_points[ID] == i][[Lng, Lat, timecol]]
            coords[timecol] = coords[timecol].apply(
                lambda r: int(r.value/1000000000))
            coords['altitude'] = 0
            coords = coords[[Lng, Lat, 'altitude', timecol]].values.tolist()
            traj_id.append(i)
            if len(coords) >= 2:
                geometry.append({
                    "type": "Feature",
                    "properties": {"ID":  i},
                    "geometry": {"type": "LineString",
                                 "coordinates": coords}})
        traj = {"type": "FeatureCollection",
                "features": geometry}
    else:
        traj = gpd.GeoDataFrame()
        from shapely.geometry import LineString
        geometry = []
        traj_id = []
        for i in traj_points[ID].drop_duplicates():
            coords = traj_points[traj_points[ID] == i][[Lng, Lat]].values
            traj_id.append(i)
            if len(coords) >= 2:
                geometry.append(LineString(coords))
            else:
                geometry.append(LineString([coords[0],coords[0]])) # pragma: no cover
        traj[ID] = traj_id
        traj['geometry'] = geometry
        traj = gpd.GeoDataFrame(traj)
    return traj
