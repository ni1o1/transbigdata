import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
from .grids import GPS_to_grids,grids_centre
from .preprocess import id_reindex,clean_same
import math 
import numpy as np

def plot_activity(data,col = ['stime','etime','LONCOL','LATCOL']):
    '''
    输入个体的活动数据（单一个体），绘制活动图
    
    输入
    ----------------
    data : DataFrame
        活动数据集
    col : List
        列名，分别为[活动开始时间，活动结束时间，活动所在栅格经度编号，活动所在栅格纬度编号]
    '''
    stime,etime,LONCOL,LATCOL = col
    activity = data.copy()
    activity['date'] = activity[stime].dt.date
    dates = list(activity['date'].astype(str).drop_duplicates())
    #扩充天
    dates_all = []
    minday = min(dates)
    maxday = max(dates)
    import datetime
    thisdate = minday
    while thisdate != maxday:
        dates_all.append(thisdate)
        thisdate = str((pd.to_datetime(thisdate+' 00:00:00')+datetime.timedelta(days =1)).date())
    dates = dates_all
    #计算活动
    import matplotlib.pyplot as plt
    import numpy as np
    #计算活动持续时间
    activity['duration'] = (activity[etime]-activity[stime]).dt.total_seconds()
    activity = activity[-activity['duration'].isnull()]
    #计算开始结束时间戳
    import time
    activity['ststmp'] = activity[stime].astype(str).apply(lambda x:time.mktime(time.strptime(x,'%Y-%m-%d %H:%M:%S'))).astype('int64')
    activity['etstmp'] = activity[etime].astype(str).apply(lambda x:time.mktime(time.strptime(x,'%Y-%m-%d %H:%M:%S'))).astype('int64')
    #提取活动信息
    activityinfo = activity[[LONCOL,LATCOL]].drop_duplicates()
    indexs = list(range(1,len(activityinfo)+1))
    np.random.shuffle(indexs)
    activityinfo['index'] = indexs
    #定义活动点颜色
    import matplotlib as mpl
    norm = mpl.colors.Normalize(vmin=0,vmax=len(activityinfo))
    from matplotlib.colors import ListedColormap
    import seaborn as sns
    cmap = ListedColormap(sns.hls_palette(n_colors=len(activityinfo), l=.5, s=0.8))
    #绘制活动点分布
    fig     = plt.figure(1,(10,5),dpi = 250)    
    ax      = plt.subplot(111)
    plt.sca(ax)
    for day in range(len(dates)):
        plt.bar(day,height = 24*3600,bottom= 0,width=0.4,color = (0,0,0,0.1))
        stime = dates[day]+' 00:00:00'
        etime = dates[day]+' 23:59:59'
        bars = activity[(activity['stime']<etime) & (activity['etime']>stime)].copy()
        bars['ststmp'] = bars['ststmp'] - time.mktime(time.strptime(stime,'%Y-%m-%d %H:%M:%S'))
        bars['etstmp'] = bars['etstmp'] - time.mktime(time.strptime(stime,'%Y-%m-%d %H:%M:%S'))    
        for row in range(len(bars)):
            plt.bar(day,height = bars['etstmp'].iloc[row]-bars['ststmp'].iloc[row],
                    bottom=bars['ststmp'].iloc[row],
                    color = cmap(norm(activityinfo[(activityinfo[LONCOL] == bars[LONCOL].iloc[row])&
                                                           (activityinfo[LATCOL] == bars[LATCOL].iloc[row])]['index'].iloc[0])))
    plt.xlim(-0.5,len(dates))
    plt.ylim(0,24*3600)
    plt.xticks(range(len(dates)),[i[-5:] for i in dates])
    plt.yticks(range(0,24*3600+1,3600),pd.DataFrame({'t':range(0, 25)})['t'].astype('str')+':00')
    plt.show()

def traj_stay_move(data,params,col = ['ID','dataTime','longitude','latitude'],activitytime = 1800):
    '''
    输入轨迹数据与栅格化参数，识别活动与出行
    
    输入
    ----------------
    data : DataFrame
        轨迹数据集
    params : List
        栅格化参数
    col : List
        数据的列名[个体，时间，经度，纬度]顺序
    activitytime : Number
        多长时间识别为停留
        
    输出
    ----------------
    stay : DataFrame
        个体停留信息
    move : DataFrame
        个体移动信息
    '''
    uid,timecol,lon,lat = col
    trajdata = data.copy()
    #时间处理
    trajdata[timecol] = pd.to_datetime(trajdata[timecol])
    #栅格化
    trajdata['LONCOL'],trajdata['LATCOL'] = GPS_to_grids(trajdata[lon], trajdata[lat], params)
    trajdata = clean_same(trajdata,col = [uid,timecol,'LONCOL','LATCOL'])
    trajdata['stime'] = trajdata[timecol]
    trajdata['etime'] = trajdata[timecol].shift(-1)
    trajdata[uid+'_next'] = trajdata[uid].shift(-1)
    trajdata = trajdata[trajdata[uid+'_next']==trajdata[uid]]
    trajdata['duration'] = (trajdata['etime']- trajdata['stime']).dt.total_seconds()
    activity = trajdata[[uid,lon,lat,'stime','etime','duration','LONCOL','LATCOL']]
    #提取活动点
    activity = activity[activity['duration']>=activitytime].rename(columns = {lon:'lon',lat:'lat'})
    stay = activity.copy()
    #提取出行
    activity['stime_next'] = activity['stime'].shift(-1)
    activity['elon'] = activity['lon'].shift(-1)
    activity['elat'] = activity['lat'].shift(-1)
    activity['ELONCOL'] = activity['LONCOL'].shift(-1)
    activity['ELATCOL'] = activity['LATCOL'].shift(-1)
    activity[uid+'_next'] = activity[uid].shift(-1)
    activity = activity[activity[uid+'_next'] == activity[uid]].drop(['stime','duration',uid+'_next'],axis = 1)
    activity = activity.rename(columns = {'lon':'slon',
                                          'lat':'slat',
                                          'etime':'stime',
                                          'stime_next':'etime',
                                          'LONCOL':'SLONCOL',
                                          'LATCOL':'SLATCOL',
                                         })
    activity['duration'] = (activity['etime']- activity['stime']).dt.total_seconds()
    move = activity.copy()
    return stay,move

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

def traj_sparsify(data,col = ['Vehicleid','Time','Lng','Lat'],timegap = 15,method = 'subsample'):
    '''
    轨迹点稀疏化。轨迹数据采样频率过高的时候，数据量太大，不便于部分对数据频率要求不是那么高的研究的分析。
    这个函数可以将采样间隔扩大，缩减数据量。
    
    输入
    -------
    data : DataFrame
        数据
    col : List
        列名，按[车辆ID,时间,经度,纬度]的顺序
    timegap : number
        单位为秒，每隔多长时间一个轨迹点
    method : str
        可选interpolate插值或subsample子采样
    
    输出
    -------
    data1 : DataFrame
        处理后的数据
    '''
    Vehicleid,Time,Lng,Lat = col
    data[Time] = pd.to_datetime(data[Time], unit='s')
    data1 = data.copy()
    data1 = data1.drop_duplicates([Vehicleid,Time])
    data1 = id_reindex(data1,Vehicleid)
    data1 = data1.sort_values(by=[Vehicleid+'_new',Time])
    data1['utctime'] = data1[Time].apply(lambda r:int(r.value/1000000000))
    data1['utctime_new'] = data1[Vehicleid+'_new']*10000000000+data1['utctime']
    if method == 'interpolate':
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
        data1 = pd.merge(minmaxtime['utctime_new'],data1)
        data1 = data1.drop([Vehicleid+'_new','utctime','utctime_new'],axis = 1)
    if method == 'subsample':
        data1['utctime_new']=(data1['utctime_new']/timegap).astype(int)
        data1 = data1.drop_duplicates(subset = ['utctime_new'])
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

