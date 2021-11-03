import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point,Polygon,shape,LineString
import urllib.request
import json
import CoordinatesConverter

def getbusdata(city,keywords):
    '''
    通过输入城市与关键词，获取公交线路的线型与站点
    输入
    -------
    city : str
        城市
    keywords : List
        关键词，线路名称

    输出
    -------
    data : GeoDataFrame
        生成的公交线路
    stop : GeoDataFrame
        生成的公交站点
    '''
    print('获取城市id:',city,end = '')
    linenames = []
    lines = []
    c = getcitycode(city)
    print('成功')
    stop = []
    for keyword in keywords:
        print(keyword,end = '')
        try:
            for uid in getlineuid(keyword,c):
                linename,coo,stationnames,stationgeo = getlinegeo(uid,c)
                coo = pd.DataFrame(list(pd.DataFrame(coo)[0].str.split(',')))
                coo[0],coo[1] = CoordinatesConverter.bd09towgs84(coo[0],coo[1])
                line = LineString(coo.values)
                linenames.append(linename)
                lines.append(line)
                stops = pd.DataFrame({'stationnames':stationnames})
                stops['linename']=linename
                stops['geo'] = stationgeo
                stops['lon'] = stops['geo'].apply(lambda row:row.split(',')[0])
                stops['lat'] = stops['geo'].apply(lambda row:row.split(',')[1])
                stop.append(stops)
            print('成功')
        except:
            print('失败')
            pass
    data = gpd.GeoDataFrame()
    data['linename'] = linenames
    data['geometry'] = lines
    data['city'] = city
    stop = pd.concat(stop)
    stop['lon'],stop['lat'] = CoordinatesConverter.bd09towgs84(stop['lon'],stop['lat'])
    stop['geometry'] = gpd.points_from_xy(stop['lon'],stop['lat'])
    stop = stop.drop('geo',axis = 1)
    stop = gpd.GeoDataFrame(stop)
    return data,stop


def getcitycode(c):
    url = 'http://map.baidu.com/?qt=s&wd='+urllib.parse.quote(c)
    response1 = urllib.request.urlopen(url,timeout = 5)
    searchinfo=json.loads(response1.read().decode('utf8'))
    return str(searchinfo['content']['code'])
    
def getlinegeo(uid,c):
    url = 'http://map.baidu.com/?qt=bsl&uid='+uid+'&c='+c
    response = urllib.request.urlopen(url,timeout = 5)
    searchinfo=json.loads(response.read().decode('utf8'))
    linename = searchinfo['content'][0]['name']
    stations = searchinfo['content'][0]['stations']
    geo = searchinfo['content'][0]['geo'].split('|')[2][:-1].split(',')
    stationgeo = []
    stationnames = []
    for station in stations:
        stationname = station['name']
        coo = station['geo'].split(';')[1].split('|')[0]
        stationnames.append(stationname)
        stationgeo.append(coo)
    coo=[]
    t=0
    cood = ''
    for each in geo:
        t += 1
        cood += each + ','
        if t == 2:
            t=0
            coo.append(cood[:-1])
            cood = ''
    return linename,coodconvert(coo),stationnames,coodconvert(stationgeo)

    
def getlineuid(keyword,c):
    url = 'http://map.baidu.com/?qt=s&wd='+urllib.parse.quote(keyword)+'&c='+c
    response1 = urllib.request.urlopen(url)
    searchinfo=json.loads(response1.read().decode('utf8'))
    if searchinfo['content'][0]['catalogID'] ==904 or searchinfo['content'][0]['catalogID'] ==905:
        try:
            uidlist = list(pd.DataFrame(searchinfo['content'][8]['blinfo'])['uid'])
        except:
            uidlist = []
        uidlist.append(searchinfo['content'][0]['uid'])
        uidlist.append(searchinfo['content'][1]['uid'])
        return list(set(uidlist))
    else:
        return []
        

def coodconvert(coo):
    coo = pd.DataFrame(list(pd.DataFrame(coo)[0].str.split(','))).astype(float)
    coo[0],coo[1] = CoordinatesConverter.bd09mctobd09(coo[0],coo[1])
    return list(coo[0].astype(str)+','+coo[1].astype(str))


def getline(r2,line_geometry):
    #生成空的list用以存放轨道断面的节点
    ls = []
    #对大部分情况，线段的起点的位置在终点前，在起终点之间生成10个点
    if r2['o_project']<r2['d_project']:
        #numpy的linespace线性插值生成10个点距离线段起点的距离
        tmp1 = np.linspace(r2['o_project'],r2['d_project'],10)
    #对四号线环线，最后一个站点与第一个站点之间的轨道断面需要特殊处理
    if r2['o_project']>r2['d_project']:
        tmp1 = np.linspace(r2['o_project']-line_geometry.length,r2['d_project'],10)
        tmp1[tmp1<0] = tmp1[tmp1<0]+line_geometry.length
    #tmp1存储的是点距离线段起点的距离，将每个距离转换为点要素，并添加到ls中
    for j in tmp1:
        ls.append(line_geometry.interpolate(j))
    #最后，把点序列转换为线型输出
    return LineString(ls)

def split_subwayline(line,stop):
    '''
    用公交/地铁站点对公交/地铁线进行切分，得到断面
    输入
    -------
    line : GeoDataFrame
        公交/地铁线路
    stop : GeoDataFrame
        公交/地铁站点

    输出
    -------
    metro_line_splited : GeoDataFrame
        生成的断面线型
    '''
    lss = []
    #遍历每条轨道线
    for k in range(len(line)):
        r = line.iloc[k]
        #获取轨道线的线型
        line_geometry = r['geometry']
        #提取相应的站点
        tmp = stop[stop['linename'] == r['linename']].copy()
        #生成轨道段
        for i in tmp.columns:
            tmp[i+'1'] = tmp[i].shift(-1)
        tmp = tmp.iloc[:-1]
        tmp = tmp[['stationnames','stationnames1','geometry','geometry1','linename']]
        #提取轨道段起终点在线路上对应的位置
        tmp['o_project'] = tmp['geometry'].apply(lambda r1:r['geometry'].project(r1))
        tmp['d_project'] = tmp['geometry1'].apply(lambda r1:r['geometry'].project(r1))
        #遍历提取轨道段
        tmp['geometry'] = tmp.apply(lambda r2:getline(r2,line_geometry),axis = 1)
        #提取的轨道段放进list中
        lss.append(tmp)
    #遍历完后，合并list里的表，得到轨道断面信息表
    metro_line_splited = pd.concat(lss).drop('geometry1',axis = 1)
    #绘制轨道断面
    return metro_line_splited

