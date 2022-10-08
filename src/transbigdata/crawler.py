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

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, LineString
import requests
import urllib.request
import urllib.parse
import urllib
import json
import re
from .plotmap import read_mapboxtoken
from .coordinates import (
    gcj02towgs84,
    bd09towgs84,
    bd09mctobd09,
    wgs84togcj02
)


def getadmin(keyword, ak, jscode='', subdistricts=False, timeout=20):
    '''
    Input the keyword and the Amap ak. The output is the GIS file of
    the administrative boundary (Only in China)

    Parameters
    -------
    keywords : str
        The keyword. It might be the city name such as Shengzheng, or
        the administrative code such as 440500
    ak : str
        Amap accesstoken
    jscode : jscode
        Amap safty code
    subdistricts : bool
        Whether to output the information of the administrative district
        boundary
    timeout : number
        Timeout of data fetching

    Returns
    -------
    admin : GeoDataFrame
        Administrative district(WGS84)
    districts : DataFrame
        The information of subdistricts. This can be used to further get
        the boundary of lower level districts
    '''

    # API url
    url = 'https://restapi.amap.com/v3/config/district'
    # Condition
    dict1 = {
        'subdistrict': '3',
        'showbiz': 'false',
        'extensions': 'all',
        'key': ak,
        'jscode': jscode,
        's': 'rsv3',
        'output': 'json',
        'level': 'district',
        'keywords': keyword,
        'platform': 'JS',
        'logversion': '2.0',
        'sdkversion': '1.4.10'
    }
    # 发送请求
    response = requests.get(url,params = dict1,timeout=timeout)
    result = json.loads(response.text)
    if result['info'] == 'INVALID_USER_SCODE':
        raise ValueError('缺少jscode，请将高德开放平台Key中的安全密钥以jscode参数的形式传入该方法')   # pragma: no cover
    # Organize Data
    datas = []
    k = 0
    if result['count']=='0':
        raise ValueError('无法搜素到该行政区划')   # pragma: no cover
    polyline = result['districts'][k]['polyline']
    polyline1 = polyline.split('|')
    res = []
    for polyline2 in polyline1:
        polyline2 = polyline2.split(';')
        p = []
        for i in polyline2:
            a, b = i.split(',')
            p.append([float(a), float(b)])
        x = pd.DataFrame(p)
        x[0], x[1] = gcj02towgs84(x[0], x[1])
        p = x.values
        res.append(Polygon(p))
    data = pd.DataFrame()
    data1 = pd.DataFrame()
    data1['geometry'] = res
    data1 = gpd.GeoDataFrame(data1)
    poly = data1.unary_union
    data['geometry'] = [poly]
    try:
        data['citycode'] = result['districts'][k]['citycode']
    except Exception:   # pragma: no cover
        pass   # pragma: no cover
    try:
        data['adcode'] = result['districts'][k]['adcode']
    except Exception:   # pragma: no cover
        pass   # pragma: no cover
    try:
        data['name'] = result['districts'][k]['name']
    except Exception:   # pragma: no cover
        pass   # pragma: no cover
    try:
        data['level'] = result['districts'][k]['level']
    except Exception:   # pragma: no cover
        pass   # pragma: no cover
    try:
        data['center'] = result['districts'][k]['center']
    except Exception:   # pragma: no cover
        pass   # pragma: no cover
    datas.append(data)
    datas = pd.concat(datas)
    admin = gpd.GeoDataFrame(datas)
    if subdistricts:
        districts = result['districts'][k]['districts']
        districts = pd.DataFrame(districts)
        return admin, districts
    else:   # pragma: no cover
        return admin   # pragma: no cover


def getbusdata(city, keywords, accurate=True, timeout=20):
    '''
    Obtain the geographic information of the bus station and bus line from
    the map service (Only in China)

    Parameters
    -------
    city : str
        city name
    keywords : list
        Keyword, the line name
    accurate : bool
        Accurate matching
    timeout : number
        Timeout of data fetching

    Returns
    -------
    data : GeoDataFrame
        The generated bus line(WGS84)
    stop : GeoDataFrame
        The generated bus station(WGS84)
    '''
    def getlineuid(keyword, c, acc=True):
        url = 'http://map.baidu.com/?qt=s&wd=' + \
            urllib.parse.quote(keyword)+'&c='+c+'&from=webmap'
        response = requests.get(url)
        searchinfo = json.loads(response.text)
        try:
            res = pd.DataFrame(searchinfo['content'])
            if acc:
                res = list(res[(res['geo_type'] == 1) &
                           (res['acc_flag'] == 1)]['uid'])
                return res
            else:
                res = list(res[res['geo_type'] == 1]['uid'])   # pragma: no cover
                return res   # pragma: no cover
        except Exception:   # pragma: no cover
            return []   # pragma: no cover

    def getcitycode(c):
        url = 'http://map.baidu.com/?qt=s&wd='+urllib.parse.quote(c)
        response1 = requests.get(url, timeout=timeout)
        searchinfo = json.loads(response1.text)
        return str(searchinfo['content']['code'])

    def getlinegeo(uid, c):
        url = 'http://map.baidu.com/?qt=bsl&uid='+uid+'&c='+c+"&auth=1"
        response1 = requests.get(url, timeout=timeout)
        searchinfo = json.loads(response1.text)
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
        coo = []
        t = 0
        cood = ''
        for each in geo:
            t += 1
            cood += each + ','
            if t == 2:
                t = 0
                coo.append(cood[:-1])
                cood = ''

        def coodconvert(coo):
            coo = pd.DataFrame(
                list(pd.DataFrame(coo)[0].str.split(','))).astype(float)
            coo[0], coo[1] = bd09mctobd09(coo[0], coo[1])
            return list(coo[0].astype(str)+','+coo[1].astype(str))
        return (
            linename,
            coodconvert(coo),
            stationnames,
            coodconvert(stationgeo)
        )
    print('Obtaining city id:', city, end='')
    linenames = []
    lines = []
    c = getcitycode(city)
    print('success')
    stop = []
    uids = []
    if type(keywords) != list:
        keywords = [str(keywords)]   # pragma: no cover
    for keyword in keywords:
        print(keyword)
        for uid in getlineuid(keyword, c, accurate):
            if uid not in uids:
                try:
                    linename, coo, stationnames, stationgeo = getlinegeo(
                        uid, c)
                    coo = pd.DataFrame(
                        list(pd.DataFrame(coo)[0].str.split(',')))
                    coo[0], coo[1] = bd09towgs84(coo[0], coo[1])
                    line = LineString(coo.values)
                    linenames.append(linename)
                    lines.append(line)
                    stops = pd.DataFrame({'stationnames': stationnames})
                    stops['linename'] = linename
                    stops['geo'] = stationgeo
                    stops['lon'] = stops['geo'].apply(
                        lambda row: row.split(',')[0])
                    stops['lat'] = stops['geo'].apply(
                        lambda row: row.split(',')[1])
                    stop.append(stops)
                    print(linename+' success')
                    uids.append(uid)
                except Exception:  # pragma: no cover
                    pass  # pragma: no cover
    if len(stop) == 0:
        print('No such busline')   # pragma: no cover
        return gpd.GeoDataFrame(), gpd.GeoDataFrame()   # pragma: no cover
    data = gpd.GeoDataFrame()
    data['linename'] = linenames
    data['geometry'] = lines
    data['city'] = city
    stop = pd.concat(stop)
    stop['lon'], stop['lat'] = bd09towgs84(stop['lon'], stop['lat'])
    stop['geometry'] = gpd.points_from_xy(stop['lon'], stop['lat'])
    stop = stop.drop('geo', axis=1)
    stop = gpd.GeoDataFrame(stop)
    data['line'] = data['linename'].str.split('(').apply(lambda r: r[0])
    stop['line'] = stop['linename'].str.split('(').apply(lambda r: r[0])
    stop['id'] = range(len(stop))
    stop['id'] = stop.groupby('linename')['id'].rank()
    data = data.drop_duplicates(subset=['linename'])
    stop = stop.drop_duplicates(subset=['linename', 'stationnames'])
    return data, stop


def get_isochrone_amap(lon, lat, reachtime, ak, jscode='', mode=2, timeout=20):
    '''
    Obtain the isochrone from Amap reachcricle

    Parameters
    -------
    lon : float
        Longitude of the start point(WGS84)
    lat : float
        Latitude of the start point(WGS84)
    reachtime : number
        Reachtime of the isochrone
    ak : str
        Amap access token
    jscode : jscode
        Amap safty code
    mode : int or str
        Travel mode, should be 0(bus), 1(subway), 2(bus+subway)
    timeout : number
        Timeout of data fetching

    Returns
    -------
    isochrone : GeoDataFrame
        The isochrone GeoDataFrame(WGS84)
    '''
    strategy = str(mode)
    if strategy not in ['0', '1', '2']:
        raise ValueError(   # pragma: no cover
            'Travel mode, should be 0(bus), 1(subway), 2(bus+subway)')   # pragma: no cover
    lon, lat = wgs84togcj02(lon, lat)
    url = 'http://restapi.amap.com/v3/direction/reachcircle'
    dict1 = {
        'key': ak,
        'jscode': jscode,
        'location': str(round(float(lon), 6))+','+str(round(float(lat), 6)),
        'time': reachtime,
        'output': 'json',
        's': 'rsv3',
        'extensions': 'all',
        'strategy': str(strategy)
    }
    response = requests.get(url,params = dict1,timeout=timeout)
    result = json.loads(response.text)
    
    P_all = []
    for each in result['polylines']:
        data = each['outer']
        ll = re.split('[,;]', data)
        ll = np.reshape(ll, (int(len(ll)/2), 2))
        l2 = []
        for i in ll:
            l2.append((gcj02towgs84(float(i[0]), float(i[1]))))
        P_all.append(Polygon(l2))

    a = gpd.GeoSeries(P_all)
    g = gpd.GeoSeries(a[a.is_valid].unary_union)
    g = gpd.GeoDataFrame(g, columns=['geometry'])
    g['lon'] = lon
    g['lat'] = lat
    g['reachtime'] = reachtime
    return g


def get_isochrone_mapbox(lon, lat, reachtime, access_token='auto',
                         mode='driving', timeout=20):
    '''
    Obtain the isochrone from mapbox isochrone

    Parameters
    -------
    lon : float
        Longitude of the start point(WGS84)
    lat : float
        Latitude of the start point(WGS84)
    reachtime : number
        Reachtime of the isochrone
    access_token : str
        Mapbox access token, if `auto` it will use the preset access token
    mode : bool
        Travel mode, should be `driving`, `walking` or `cycling`
    timeout : number
        Timeout of data fetching

    Returns
    -------
    isochrone : GeoDataFrame
        The isochrone GeoDataFrame(WGS84)
    '''
    if access_token == 'auto':
        access_token = read_mapboxtoken()   # pragma: no cover
    if mode not in ['driving', 'walking', 'cycling']:
        raise ValueError(   # pragma: no cover
            'Travel mode should be `driving`, `walking` or `cycling`')   # pragma: no cover
    url = 'https://api.mapbox.com/isochrone/v1/mapbox/'+mode+'/' +\
        str(lon)+','+str(lat)+'?contours_minutes='+str(reachtime) +\
        '&polygons=true&access_token='+access_token
    response = requests.get(url,timeout = timeout)
    result = json.loads(response.text)
    isochrone = gpd.GeoDataFrame.from_features(result)
    isochrone['lon'] = lon
    isochrone['lat'] = lat
    isochrone['reachtime'] = reachtime
    return isochrone[['lon', 'lat', 'reachtime', 'geometry']]
