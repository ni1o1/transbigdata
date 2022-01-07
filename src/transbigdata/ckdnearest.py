
#定义函数，用cKDTree匹配点与点
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
import itertools
from operator import itemgetter
from CoordinatesConverter import getdistance 
#定义KDTree的函数
def ckdnearest(dfA_origin,dfB_origin,Aname = ['lon','lat'],Bname = ['lon','lat']):
    '''
    输入两个DataFrame，分别指定经纬度列名，为表A匹配表B中最近点，并计算距离
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
def ckdnearest_line(gdfA, gdfB):
    '''
    输入两个geodataframe，其中gdfA为点，gdfB为线，该方法会为gdfA表连接上gdfB中最近的线，并添加距离字段dsit
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