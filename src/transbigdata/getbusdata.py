import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon,LineString
import urllib.request
import json
import CoordinatesConverter
from urllib import parse

def getadmin(keyword,ak,subdistricts = False):
    '''
    Input the keyword and the Amap ak. The output is the GIS file of the administrative boundary (Only in China)
    
    Parameters
    -------
    keywords : str
        The keyword. It might be the city name such as Shengzheng, or the administrative code such as 440500
    ak : str
        Amap accesstoken
    subdistricts : bool
        Whether to output the information of the administrative district boundary

    Returns
    -------
    admin : GeoDataFrame
        Administrative district
    districts : DataFrame
        The information of subdistricts. This can be used to further get the boundary of lower level districts
    '''
    
    #API url
    url = 'https://restapi.amap.com/v3/config/district?'
    #Condition
    dict1 = {
    'subdistrict':'3',
        'showbiz':'false',
        'extensions':'all',
        'key':ak,
        's':'rsv3',
        'output':'json',
        'level':'district',
        'keywords':keyword,
        'platform':'JS',
        'logversion':'2.0',
        'sdkversion':'1.4.10'
    }
    url_data = parse.urlencode(dict1)
    url = url+url_data
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    webpage = response.read()
    result = json.loads(webpage.decode('utf8','ignore'))
    #Organize Data
    datas = []
    k = 0
    polyline = result['districts'][k]['polyline']
    polyline1 = polyline.split('|')
    res = []
    for polyline2 in polyline1:
        polyline2 = polyline2.split(';')
        p = []
        for i in polyline2:
            a,b = i.split(',')
            p.append([float(a),float(b)])
        x = pd.DataFrame(p)
        x[0],x[1] = CoordinatesConverter.gcj02towgs84(x[0],x[1])
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
    except:
        pass
    try:
        data['adcode'] = result['districts'][k]['adcode']
    except:
        pass
    try:
        data['name'] = result['districts'][k]['name']
    except:
        pass
    try:
        data['level'] = result['districts'][k]['level']
    except:
        pass
    try:
        data['center'] = result['districts'][k]['center']
    except:
        pass
    datas.append(data)
    datas = pd.concat(datas)
    admin = gpd.GeoDataFrame(datas)
    if subdistricts:
        districts = result['districts'][k]['districts']
        districts = pd.DataFrame(districts)
        return admin,districts
    else:
        return admin



def getbusdata(city,keywords):
    '''
    Obtain the geographic information of the bus station and bus line from the map service (Only in China)

    Parameters
    -------
    city : str
        city name
    keywords : List
        Keyword, the line name

    Returns
    -------
    data : GeoDataFrame
        The generated bus line
    stop : GeoDataFrame
        The generated bus station
    '''
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
    def getcitycode(c):
        url = 'http://map.baidu.com/?qt=s&wd='+urllib.parse.quote(c)
        response1 = urllib.request.urlopen(url,timeout = 60)
        searchinfo=json.loads(response1.read().decode('utf8'))
        return str(searchinfo['content']['code'])
    def getlinegeo(uid,c):
        url = 'http://map.baidu.com/?qt=bsl&uid='+uid+'&c='+c
        response = urllib.request.urlopen(url,timeout = 60)
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
        def coodconvert(coo):
            coo = pd.DataFrame(list(pd.DataFrame(coo)[0].str.split(','))).astype(float)
            coo[0],coo[1] = CoordinatesConverter.bd09mctobd09(coo[0],coo[1])
            return list(coo[0].astype(str)+','+coo[1].astype(str))
        return linename,coodconvert(coo),stationnames,coodconvert(stationgeo)
    print('Obtaining city id:',city,end = '')
    linenames = []
    lines = []
    c = getcitycode(city)
    print('success')
    stop = []
    uids = []
    
    for keyword in keywords:
        print(keyword)
        for uid in getlineuid(keyword,c):
            if uid not in uids:
                try:
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
                    print(linename+' success')
                    uids.append(uid)
                except:
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
    data['line'] = data['linename'].str.split('(').apply(lambda r:r[0])
    stop['line'] = stop['linename'].str.split('(').apply(lambda r:r[0])
    stop['id'] = range(len(stop))
    stop['id'] = stop.groupby('linename')['id'].rank()
    data = data.drop_duplicates(subset = ['linename'])
    stop = stop.drop_duplicates(subset = ['linename','stationnames'])
    return data,stop

def split_subwayline(line,stop):
    '''
    To slice the metro line with metro stations to obtain metro section information (This step is useful in subway passenger flow visualization)

    Parameters
    -------
    line : GeoDataFrame
        Bus/metro lines
    stop : GeoDataFrame
        Bus/metro stations

    Returns
    -------
    metro_line_splited : GeoDataFrame
        Generated section line shape
    '''
    def getline(r2,line_geometry):
        ls = []
        if r2['o_project']<=r2['d_project']:
            tmp1 = np.linspace(r2['o_project'],r2['d_project'],10)
        if r2['o_project']>r2['d_project']:
            tmp1 = np.linspace(r2['o_project']-line_geometry.length,r2['d_project'],10)
            tmp1[tmp1<0] = tmp1[tmp1<0]+line_geometry.length
        for j in tmp1:
            ls.append(line_geometry.interpolate(j))
        return LineString(ls)
    lss = []
    for k in range(len(line)):
        r = line.iloc[k]
        line_geometry = r['geometry']
        tmp = stop[stop['linename'] == r['linename']].copy()
        for i in tmp.columns:
            tmp[i+'1'] = tmp[i].shift(-1)
        tmp = tmp.iloc[:-1]
        tmp = tmp[['stationnames','stationnames1','geometry','geometry1','linename']]
        tmp['o_project'] = tmp['geometry'].apply(lambda r1:r['geometry'].project(r1))
        tmp['d_project'] = tmp['geometry1'].apply(lambda r1:r['geometry'].project(r1))
        tmp['geometry'] = tmp.apply(lambda r2:getline(r2,line_geometry),axis = 1)
        lss.append(tmp)
    metro_line_splited = pd.concat(lss).drop('geometry1',axis = 1)
    return metro_line_splited


def metro_network(stop,traveltime = 3,transfertime = 5,nxgraph = True):
    '''
    Inputting the metro station data and outputting the network topology model. The graph generated relies on NetworkX.

    Parameters
    -------
    stop : GeoDataFrame
        Bus/metro stations
    traveltime : number
        Travel time per section
    transfertime : number
        Travel time per transfer
    nxgraph : bool
        Default True, if True then output the network G constructed by NetworkX, if False then output the edges1(line section),edge2(station transfer), and the node of the network

    Returns
    -------
    G : networkx.classes.graph.Graph
        Network G built by networkx. Output when the nxgraph parameter is True
    edge1 : DataFrame
        Network edge for line section. Output when the nxgraph parameter is False
    edge2 : DataFrame
        Network edge for transfering. Output when the nxgraph parameter is False
    node : List
        Network nodes. Output when the nxgraph parameter is False
    '''
    linestop = stop.copy()
    for i in linestop.columns:
        linestop[i+'1'] = linestop[i].shift(-1)
    linestop = linestop[linestop['linename'] == linestop['linename1']].copy()
    linestop = linestop.rename(columns = {'stationnames':'ostop','stationnames1':'dstop'})
    linestop['ostation'] = linestop['line']+linestop['ostop']
    linestop['dstation'] = linestop['line']+linestop['dstop']
    edge1 = linestop[['ostation','dstation']].copy()
    edge1['duration'] = traveltime
    linestop = stop.copy()
    linestop['station'] = linestop['line'] + linestop['stationnames']
    tmp = linestop.groupby(['stationnames'])['linename'].count().rename('count').reset_index()
    tmp = pd.merge(linestop,tmp[tmp['count']>2]['stationnames'],on = 'stationnames')
    tmp = tmp[['stationnames','line','station']].drop_duplicates()
    tmp = pd.merge(tmp,tmp,on ='stationnames')
    edge2 =tmp[tmp['line_x'] != tmp['line_y']][['station_x','station_y']]
    edge2['duration'] = transfertime
    edge2.columns = edge1.columns
    edge = edge1.append(edge2)
    node = list(edge['ostation'].drop_duplicates())
    if nxgraph:
        import networkx as nx
        G = nx.Graph()
        G.add_nodes_from(node)
        G.add_weighted_edges_from(edge.values)
        return G
    else:
        return edge1,edge2,node

