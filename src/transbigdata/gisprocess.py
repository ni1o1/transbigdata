
import numpy as np
import pandas as pd
from CoordinatesConverter import gcj02tobd09,bd09togcj02,wgs84togcj02,gcj02towgs84,wgs84tobd09,bd09towgs84,getdistance
from scipy.spatial import cKDTree
import itertools
from operator import itemgetter
import geopandas as gpd

#定义函数，用cKDTree匹配点与点
#定义KDTree的函数
def ckdnearest(dfA_origin,dfB_origin,Aname = ['lon','lat'],Bname = ['lon','lat']):
    '''
    输入两个DataFrame，分别指定经纬度列名，为表A匹配表B中最近点，并计算距离
    输入
    -------
    dfA_origin : DataFrame
        表A
    dfB_origin : DataFrame
        表B
    Aname : List
        表A中经纬度列字段
    Bname : List
        表B中经纬度列字段

    输出
    -------
    gdf : DataFrame
        为A匹配到B上最近点的表
    '''
    gdA = dfA_origin.copy()
    gdB = dfB_origin.copy()
    from scipy.spatial import cKDTree
    #为gdB表的点建立KDTree
    btree = cKDTree(gdB[Bname].values)
    #在gdB的KDTree中查询gdA的点,dist为距离,idx为gdB中离gdA最近的坐标点
    dist,idx = btree.query(gdA[Aname].values,k = 1)
    #构建匹配的结果
    gdA['index'] = idx
    gdB['index'] = range(len(gdB))
    gdf = pd.merge(gdA,gdB,on = 'index')
    #计算
    if (Aname[0] == Bname[0])&(Aname[1] == Bname[1]):
        gdf['dist'] = getdistance(gdf[Aname[0]+'_x'],gdf[Aname[1]+'_y'],gdf[Bname[0]+'_x'],gdf[Bname[1]+'_y'])
    else:
        gdf['dist'] = getdistance(gdf[Aname[0]],gdf[Aname[1]],gdf[Bname[0]],gdf[Bname[1]])
    return gdf
def ckdnearest_point(gdA, gdB):
    '''
    输入两个geodataframe，gdfA、gdfB均为点，该方法会为gdfA表连接上gdfB中最近的点，并添加距离字段dsit
    输入
    -------
    gdA : GeoDataFrame
        表A，点要素
    gdB : GeoDataFrame
        表B，点要素

    输出
    -------
    gdf : GeoDataFrame
        为A匹配到B上最近点的表
    '''
    #提取gdA中的所有点要素
    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    #提取gdB中的所有点要素
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    #为gdB表的点建立KDTree
    btree = cKDTree(nB)
    #在gdB的KDTree中查询gdA的点,dist为距离,idx为gdB中离gdA最近的坐标点
    dist, idx = btree.query(nA, k=1)
    #构建匹配的结果
    gdA['dist'] = dist
    gdA['index'] = idx
    gdB['index'] = range(len(gdB))
    gdf = pd.merge(gdA,gdB,on = 'index')
    return gdf

#定义函数，用cKDTree匹配点与线
def ckdnearest_line(gdfA, gdfB):
    '''
    输入两个geodataframe，其中gdfA为点，gdfB为线，该方法会为gdfA表连接上gdfB中最近的线，并添加距离字段dsit
    输入
    -------
    gdA : GeoDataFrame
        表A，点要素
    gdB : GeoDataFrame
        表B，线要素

    输出
    -------
    gdf : GeoDataFrame
        为A匹配到B中最近的线
    '''
    #提取gdA中的所有点要素
    A = np.concatenate(
        [np.array(geom.coords) for geom in gdfA.geometry.to_list()])
    #把gdfB的几何坐标提取到B，此时B为一个大list中包含多个小list，每个小list代表一个几何图形，小list中为坐标
    #B=[[[要素1坐标1],[要素1坐标2],...],[[要素2坐标1],[要素2坐标2],...]]
    B = [np.array(geom.coords) for geom in gdfB.geometry.to_list()]
    #B_ix代表B中的每个坐标点分别属于B中的哪个几何图形
    B_ix = tuple(itertools.chain.from_iterable(
        [itertools.repeat(i, x) for i, x in enumerate(list(map(len, B)))]))
    #把B表展开，B=[[要素1坐标1],[要素1坐标2],...,[要素2坐标2],[要素2坐标2],...]
    B = np.concatenate(B)
    #为B表建立KDTree
    ckd_tree = cKDTree(B)
    #在B的KDTree中查询A的点,dist为距离,idx为B中离A最近的坐标点
    dist, idx = ckd_tree.query(A, k=1)
    #由坐标点对应到几何要素
    idx = itemgetter(*idx)(B_ix)
    #构建匹配的结果
    gdfA['dist'] = dist
    gdfA['index'] = idx
    gdfB['index'] = range(len(gdfB))
    gdf = pd.merge(gdfA,gdfB,on = 'index')
    return gdf

#打断线
def splitline_with_length(Centerline,maxlength = 100):
    '''
    输入线GeoDataFrame要素，打断为最大长度maxlength的小线段
    输入
    -------
    Centerline : GeoDataFrame
        线要素
    maxlength : number
        打断的线段最大长度

    输出
    -------
    splitedline : GeoDataFrame
        打断后的线
    '''
    def splitline(route,maxlength):
        routelength = route.length
        from shapely.geometry import LineString
        lss = []
        for k in range(int(routelength/maxlength)+1):
            if k == int(routelength/maxlength):
                lm = routelength
            else:
                lm = (k+1)*maxlength
            a = np.linspace(k*maxlength,lm,10)
            ls = []
            for l in a:
                ls.append(route.interpolate(l))
            lss.append(LineString(ls))
        lss = gpd.GeoDataFrame(lss,columns = ['geometry'])
        return lss
    lsss = []
    for i in range(len(Centerline)):
        route = Centerline['geometry'].iloc[i]
        lss = splitline(route,maxlength)
        lss['id'] = i
        lsss.append(lss)
    lsss = pd.concat(lsss)
    lsss['length'] = lsss.length
    splitedline = lsss
    return splitedline

def merge_polygon(data,col):
    '''
    输入多边形GeoDataFrame数据，以及分组列名col，对不同组别进行分组的多边形进行合并
    
    输入
    -------
    data : GeoDataFrame
        多边形数据
    col : str
        分组列名

    输出
    -------
    data1 : GeoDataFrame
        合并后的面
    '''
    groupnames = []
    geometries = []
    for i in data[col].drop_duplicates():
        groupnames.append(i)
        geometries.append(data[data[col]==i].unary_union)
    data1 = gpd.GeoDataFrame()
    data1['geometry'] = geometries
    data1[col] = groupnames
    return data1

def polyon_exterior(data,minarea = 0):
    '''
    输入多边形GeoDataFrame数据，对多边形取外边界构成新多边形
    
    输入
    -------
    data : GeoDataFrame
        多边形数据
    minarea : number
        最小面积，小于这个面积的面全部剔除
        
    输出
    -------
    data1 : GeoDataFrame
        处理后的面
    '''
    data1 = data.copy()
    def polyexterior(p):
        from shapely.geometry import Polygon,MultiPolygon
        if type(p)==MultiPolygon:
            geometries = []
            for i in p:
                poly = Polygon(i.exterior)
                if minarea>0:
                    if poly.area>minarea:
                        geometries.append(poly)
                else:
                    geometries.append(poly)
            return MultiPolygon(geometries)
        if type(p)==Polygon:
            return Polygon(p.exterior)
    data1['geometry'] = data1['geometry'].apply(lambda r:polyexterior(r))
    data1 = data1[-data1['geometry'].is_empty]
    return data1
