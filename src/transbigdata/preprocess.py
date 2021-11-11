import geopandas as gpd  
import pandas as pd
import numpy as np
from .grids import *
from CoordinatesConverter import getdistance



def clean_same(data,col = ['VehicleNum','Time','Lng','Lat']):
    '''
    删除信息与前后数据相同的数据以减少数据量
    如：某个体连续n条数据除了时间以外其他信息都相同，则可以只保留首末两条数据
    
    输入
    -------
    data : DataFrame
        数据
    col : List
        列名，按[个体ID,时间,经度,纬度]的顺序，可以传入更多列。会以时间排序，再判断除了时间以外其他列的信息
    
    输出
    -------
    data1 : DataFrame
        清洗后的数据
    '''
    [VehicleNum,Time,Lng,Lat] = col[:4]
    extra = col[4:]
    data1 = data.copy()
    data1 = data1.drop_duplicates(subset = [VehicleNum,Time])
    data1 = data1.sort_values(by = [VehicleNum,Time])
    data1['issame'] = 0
    for i in [VehicleNum,Lng,Lat]+extra:
        data1['issame'] += (data1[i].shift()==data1[i])&(data1[i].shift(-1)==data1[i])   
    data1 = data1[-(data1['issame'] == len([VehicleNum,Lng,Lat]+extra))]
    data1 = data1.drop('issame',axis = 1)
    return data1

def clean_drift(data,col = ['VehicleNum','Time','Lng','Lat'],speedlimit = 80,dislimit = 1000):
    '''
    删除漂移数据。条件是，此数据与前后的速度都大于speedlimit，但前后数据之间的速度却小于speedlimit。
    传入的数据中时间列如果为datetime格式则计算效率更快
    
    输入
    -------
    data : DataFrame
        数据
    col : List
        列名，按[个体ID,时间,经度,纬度]的顺序
    speedlimit : number
        速度阈值
    
    输出
    -------
    data1 : DataFrame
        清洗后的数据
    '''
    [VehicleNum,Time,Lng,Lat] = col
    data1 = data.copy()
    data1 = data1.drop_duplicates(subset = [VehicleNum,Time])
    data1[Time+'_dt'] = pd.to_datetime(data1[Time])
    data1 = data1.sort_values(by = [VehicleNum,Time])
    for i in [VehicleNum,Lng,Lat,Time+'_dt']:
        data1[i+'_pre'] = data1[i].shift()
        data1[i+'_next'] = data1[i].shift(-1)
    data1['dis_pre'] = getdistance(data1[Lng],data1[Lat],data1[Lng+'_pre'],data1[Lat+'_pre'])
    data1['dis_next'] = getdistance(data1[Lng],data1[Lat],data1[Lng+'_next'],data1[Lat+'_next'])
    data1['dis_prenext'] = getdistance(data1[Lng+'_pre'],data1[Lat+'_pre'],data1[Lng+'_next'],data1[Lat+'_next'])
    data1['timegap_pre'] = data1[Time+'_dt'] - data1[Time+'_dt_pre']
    data1['timegap_next'] = data1[Time+'_dt_next'] - data1[Time+'_dt']
    data1['timegap_prenext'] = data1[Time+'_dt_next'] - data1[Time+'_dt_pre']
    data1['speed_pre'] = data1['dis_pre']/data1['timegap_pre'].dt.total_seconds()*3.6
    data1['speed_next'] = data1['dis_next']/data1['timegap_next'].dt.total_seconds()*3.6
    data1['speed_prenext'] = data1['dis_prenext']/data1['timegap_prenext'].dt.total_seconds()*3.6
    if speedlimit:
        #条件是，此数据与前后的速度都大于speedlimit，但前后数据之间的速度却小于speedlimit
        data1 = data1[-((data1[VehicleNum+'_pre'] == data1[VehicleNum])&(data1[VehicleNum+'_next'] == data1[VehicleNum])&\
        (data1['speed_pre']>speedlimit)&(data1['speed_next']>speedlimit)&(data1['speed_prenext']<speedlimit))]
    if dislimit:
        #条件是，此数据与前后的距离都大于dislimit，但前后数据之间的距离却小于dislimit
        data1 = data1[-((data1[VehicleNum+'_pre'] == data1[VehicleNum])&(data1[VehicleNum+'_next'] == data1[VehicleNum])&\
        (data1['dis_pre']>dislimit)&(data1['dis_next']>dislimit)&(data1['dis_prenext']<dislimit))]
    data1 = data1[data.columns]
    return data1

def clean_outofbounds(data,bounds,col = ['Lng','Lat']):
    '''
    剔除超出研究范围的数据

    输入
    -------
    data : DataFrame
        数据
    bounds : List    
        研究范围的左下右上经纬度坐标，顺序为[lon1,lat1,lon2,lat2]
    col : List
        经纬度列名
    
    输出
    -------
    data1 : DataFrame
        清洗后的数据
    '''
    Lng,Lat = col
    data1 = data.copy()
    data1 = data1[(data1[Lng]>bounds[0])&(data1[Lng]<bounds[2])&(data1[Lat]>bounds[1])&(data1[Lat]<bounds[3])]
    return data1

def clean_outofshape(data,shape,col = ['Lng','Lat'],accuracy=500):
    '''
    剔除超出研究区域的数据

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
        清洗后的数据
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

def clean_traj(data,col = ['uid','str_time','lon','lat'],tripgap = 1800,disgap = 50000,speedlimit = 80):
    '''
    轨迹数据清洗组合拳
    输入
    -------
    data : DataFrame
        轨迹数据
    col : List
        列名，以[个体id,时间,经度,纬度]排列
    tripgap : number
        多长的时间视为新的出行
    disgap : number
        多长距离视为新的出行
    speedlimit : number
        车速限制
    
    输出
    -------
    data1 : DataFrame
        清洗后的数据
    '''
    uid,timecol,lon,lat = col
    data[timecol] = pd.to_datetime(data[timecol])
    #出行识别
    data = data.sort_values(by = [uid,timecol])
    cols = []
    for i in data.columns:
        if i not in [uid,timecol,lon,lat]:
            cols.append(i)
    #清洗
    data = clean_same(data,col = [uid,timecol,lon,lat]+cols)
    #简单清洗漂移数据
    data = clean_drift(data,col = [uid, timecol, lon, lat],
        speedlimit=speedlimit)
    #出行识别
    data = id_reindex(data,uid,timecol = timecol,timegap = tripgap)
    data = data.rename(columns = {uid+'_new':'tripid'})
    #距离太大就编号为新的出行
    data = id_reindex_disgap(data,col = ['tripid',lon,lat],disgap=disgap,suffix='')
    #距离太短的出行剔除
    data1 = data.copy()
    data1['lon1'] = data1[lon].shift(-1)
    data1['lat1'] = data1[lat].shift(-1)
    data1['tripid1'] = data1['tripid'].shift(-1)
    data1 = data1[data1['tripid']==data1['tripid1']]
    data1['dis'] = getdistance(data1[lon],data1[lat],data1['lon1'],data1['lat1'])
    a = data1.groupby(['tripid'])['dis'].sum()
    a = a[-(a<50)].reset_index()['tripid']
    data = pd.merge(data,a)
    #再重新编号
    data = data.drop('tripid',axis = 1)
    data = id_reindex(data,uid,timecol = timecol,timegap = tripgap)
    data = data.rename(columns = {uid+'_new':'tripid'})
    #大距离筛选出行
    data = id_reindex_disgap(data,col = ['tripid',lon,lat],disgap=disgap,suffix='')
    return data


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

def id_reindex_disgap(data,col = ['uid','lon','lat'],disgap=1000,suffix = '_new'):
    '''
    对数据的ID列重新编号，如果相邻两条记录超过距离，则编号为新id
    
    输入
    -------
    data : DataFrame
        数据 
    col : str
        要重新编号的ID列名
    disgap : number
        如果个体轨迹超过一定距离，则编号为新的个体。
    suffix : str
        新编号列名的后缀
        
    输出
    -------
    data1 : DataFrame
        重新编号的数据
    '''
    uid,lon,lat = col
    data1 = data.copy()
    data1[uid+suffix] = ((data1[uid].shift()!=data1[uid])|
                    (getdistance(data1[lon],data1[lat],data1[lon].shift(),data1[lat].shift())>disgap)).astype(int).cumsum()-1
    a = data1.groupby([uid+suffix])[lon].count()
    data1 = pd.merge(data1,a[a>1].reset_index()[[uid+suffix]])
    return data1

def id_reindex(data,col,new = False,timegap = None,timecol = None,suffix = '_new',sample = None):
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
    timegap : number
        如果个体在一段时间内没出现（timegap为时间阈值），则编号为新的个体。此参数与timecol同时设定才有效果。
    timecol : str
        时间字段名称，此参数与timegap同时设定才有效果。
    suffix : str
        新编号列名的后缀，设置为False时替代原有列名
    sample : int
        传入数值，对重新编号的个体进行抽样
        
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
    if (timegap is not None)&(timecol is not None):
        data1[timecol] = pd.to_datetime(data1[timecol])
        data1 = data1.sort_values(by = [col+suffix,timecol])
        #此时两个条件：时间间隔大于30分钟或者本来这一条记录就是新车
        data1[col+suffix] = ((data1[col+suffix].shift()!=data1[col+suffix])|
                        ((data1[timecol]-data1[timecol].shift()).dt.total_seconds()>timegap)).astype(int).cumsum()-1

    if sample:
        tmp = data1[col+suffix].drop_duplicates().sample(sample)
        data1 = pd.merge(data1,tmp)
    return data1

def odagg(oddata,params,col = ['slon','slat','elon','elat'],arrow = False,**kwargs):
    '''
    输入OD数据（每一行数据是一个出行），栅格化OD并集计后生成OD的GeoDataFrame
    oddata - OD数据（清洗好的）
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