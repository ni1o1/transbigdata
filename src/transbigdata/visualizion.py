from .traj import points_to_traj
import pandas as pd
import numpy as np
from .grids import *
from .odprocess import *

def visualization_trip(trajdata,col = ['Lng','Lat','ID','Time'],zoom = 'auto',height=500):
    '''
    输入轨迹数据与列名，生成kepler的可视化
    
    输入
    -------
    trajdata : DataFrame
        轨迹点数据
    col : List
        列名，按[经度,纬度,轨迹编号,时间]的顺序
    zoom : number
        地图缩放等级,默认'auto'自动选择
    height : number
        地图图框高度

    输出
    -------
    vmap : keplergl.keplergl.KeplerGl
        keplergl提供的可视化
    '''
    try:
        from keplergl import KeplerGl
    except:
        raise Exception('请安装keplergl，在终端或命令提示符中运行pip install keplergl，然后重启Python') 
    print('整理轨迹数据...')
    [Lng,Lat,ID,timecol] = col
    trajdata[timecol] = pd.to_datetime(trajdata[timecol])
    trajdata = trajdata.sort_values(by = [ID,timecol])
    traj = points_to_traj(trajdata,col = [Lng,Lat,ID],timecol = timecol)
    #获取基本参数
    ls = []
    for i in range(len(traj['features'])):
        ls.append(traj['features'][i]['geometry']['coordinates'][0])
        ls.append(traj['features'][i]['geometry']['coordinates'][-1])
    ls = pd.DataFrame(ls)
    lon_center,lat_center,starttime = ls[0].mean(),ls[1].mean(),ls[3].min()
    if zoom == 'auto':
        lon_min,lon_max = ls[0].quantile(0.05),ls[0].quantile(0.95)
        zoom = 8.5-np.log(lon_max-lon_min)/np.log(2)
    print('生成可视化...')
    #创建一个KeplerGl对象
    vmap = KeplerGl(config = {
        "version": "v1",
        "config":
        {        "visState":
            {
                "filters": [],
                "layers": [
                {
                    "id": "hizm36i",
                    "type": "trip",
                    "config":
                    {
                        "dataId": "trajectory",
                        "label": "trajectory",
                        "color": [255,255,255],
                        "highlightColor": [255, 255, 0, 255],
                        "columns":
                        {
                            "geojson": "_geojson"
                        },
                        "isVisible": True,
                    },
                }],
                "layerBlending": "additive",
                "animationConfig":
                {
                    "currentTime": starttime,
                    "speed": 0.1
                }
            },
            "mapState":
            {
                "bearing": 0,
                "latitude": lat_center,
                "longitude": lon_center,
                "pitch": 0,
                "zoom": zoom,
            },
        }},
    data = {'trajectory':traj},height=height)
    #激活KeplerGl对象到jupyter的窗口中
    return vmap


def visualization_od(oddata,col = ['slon','slat','elon','elat'],zoom = 'auto',height=500,accuracy = 500,mincount = 0):
    '''
    输入od数据与列名，生成kepler的可视化
    
    输入
    -------
    oddata : DataFrame
        od数据
    col : List
        列名，可输入不带权重的OD，按[起点经度，起点纬度，终点经度，终点纬度]的顺序，此时会自动集计。
        也可输入带权重的OD，按[起点经度，起点纬度，终点经度，终点纬度，数量]的顺序。
    zoom : number
        地图缩放等级,默认'auto'自动选择
    height : number
        地图图框高度
    accuracy : number
        集计的栅格大小
    mincount : number
        最小的od数，少于这个的od就不显示了

    输出
    -------
    vmap : keplergl.keplergl.KeplerGl
        keplergl提供的可视化
    '''
    try:
        from keplergl import KeplerGl
    except:
        raise Exception('请安装keplergl，在终端或命令提示符中运行pip install keplergl，然后重启Python') 
    import numpy as np
    if len(col)==4:
        slon,slat,elon,elat = col
        lon1 = oddata[slon].quantile(0.01)
        lon2 = oddata[slon].quantile(0.99)
        lat1 = oddata[slat].quantile(0.01)
        lat2 = oddata[slat].quantile(0.99)
        #定义研究范围
        bounds = [lon1,lat1,lon2,lat2]
        #获取栅格化参数
        params = grid_params(bounds = bounds,accuracy = accuracy)
        #栅格化OD并集计
        od_gdf = odagg_grid(oddata,params,col = col)
        if zoom == 'auto':
            zoom = 8.5-np.log(lon2-lon1)/np.log(2)
        lon_center,lat_center = (lon2+lon1)/2,(lat2+lat1)/2
        lon1,lat1,lon2,lat2,count='SHBLON','SHBLAT','EHBLON','EHBLAT','count'
    if len(col)==5:
        slon,slat,elon,elat,count=col
        lon1 = oddata[slon].quantile(0.01)
        lon2 = oddata[slon].quantile(0.99)
        lat1 = oddata[slat].quantile(0.01)
        lat2 = oddata[slat].quantile(0.99)
        lon_center,lat_center = (lon2+lon1)/2,(lat2+lat1)/2
        if zoom == 'auto':
            zoom = 8.5-np.log(lon2-lon1)/np.log(2)
        od_gdf = oddata
        lon1,lat1,lon2,lat2,count=col
    od_gdf = od_gdf[od_gdf[count]>=mincount]
    height = 500
    vmap = KeplerGl(config = {
        'version': 'v1',
        'config':
        {
            'visState':
            {
                'filters': [],
                'layers': [
                {
                    'id': 'd3s4dcp',
                    'type': 'arc',
                    'config':
                    {
                        'dataId': 'od',
                        'label': 'shb -> ehb arc',
                        'color': [146, 38, 198],
                        'highlightColor': [252, 242, 26, 255],
                        'columns':
                        {
                            'lat0': lat1,
                            'lng0': lon1,
                            'lat1': lat2,
                            'lng1': lon2
                        },
                        'isVisible': True,
                        'visConfig':
                        {
                            'opacity': 1,
                            'thickness': 2,
                            'colorRange':
                            {
                                'name': 'Global Warming 8',
                                'type': 'sequential',
                                'category': 'Uber',
                                'colors': ['#4C0035',
                                    '#650031',
                                    '#7F0023',
                                    '#98000A',
                                    '#B21800',
                                    '#CB4600',
                                    '#E57F00',
                                    '#FFC300'
                                ]
                            },
                            'sizeRange': [0, 3.5],
                            'targetColor': None
                        },
                        'hidden': False,
                        'textLabel': [
                        {
                            'field': None,
                            'color': [255, 255, 255],
                            'size': 18,
                            'offset': [0, 0],
                            'anchor': 'start',
                            'alignment': 'center'
                        }]
                    },
                    'visualChannels':
                    {
                        'colorField':
                        {
                            'name': count,
                            'type': 'integer'
                        },
                        'colorScale': 'quantile',
                        'sizeField':
                        {
                            'name': count,
                            'type': 'integer'
                        },
                        'sizeScale': 'log'
                    }
                }],
                'interactionConfig':
                {
                    'tooltip':
                    {
                        'fieldsToShow':
                        {
                            'od': [
                            {
                                'name': lon1,
                                'format': None
                            },
                            {
                                'name': lat1,
                                'format': None
                            },
                            {
                                'name': lon2,
                                'format': None
                            },
                            {
                                'name': lat2,
                                'format': None
                            },
                            {
                                'name': count,
                                'format': None
                            }]
                        },
                        'compareMode': False,
                        'compareType': 'absolute',
                        'enabled': True
                    },
                    'brush':
                    {
                        'size': 0.5,
                        'enabled': False
                    },
                    'geocoder':
                    {
                        'enabled': False
                    },
                    'coordinate':
                    {
                        'enabled': False
                    }
                },
                'layerBlending': 'normal',
                'splitMaps': [],
                'animationConfig':
                {
                    'currentTime': None,
                    'speed': 1
                }
            },
            'mapState':
            {
                'bearing': 24.18348623853211,
                'dragRotate': True,
                'latitude': lat_center,
                'longitude': lon_center,
                'pitch': 23.707784107832463,
                'zoom': zoom,
                'isSplit': False
            },
            'mapStyle':
            {
                'styleType': 'dark',
                'topLayerGroups':
                {},
                'visibleLayerGroups':
                {
                    'label': True,
                    'road': True,
                    'border': False,
                    'building': True,
                    'water': True,
                    'land': True,
                    '3d building': False
                },
                'threeDBuildingColor': [9.665468314072013,
                    17.18305478057247,
                    31.1442867897876
                ],
                'mapStyles':
                {}
            }
        }
    },data = {'od':od_gdf},height=height)
    return vmap

def visualization_data(data,col =  ['lon','lat'],accuracy = 500,height = 500,maptype = 'point',zoom = 'auto'):
    '''
    输入数据点，集计并可视化
    
    输入
    -------
    data : DataFrame
        数据点分布
    col : List
        列名，可输入不带权重的OD，按[经度，纬度]的顺序，此时会自动集计。
        也可输入带权重的OD，按[经度，纬度，数量]的顺序。
    zoom : number
        地图缩放等级,默认'auto'自动选择
    height : number
        地图图框高度
    accuracy : number
        集计的栅格大小
    maptype : str
        出图类型，'point'或者'heatmap'

    输出
    -------
    vmap : keplergl.keplergl.KeplerGl
        keplergl提供的可视化
    '''
    try:
        from keplergl import KeplerGl
    except:
        raise Exception('请安装keplergl，在终端或命令提示符中运行pip install keplergl，然后重启Python') 
    if len(col)==2:
        lon,lat = col[0],col[1]
        count = 'count'
        bounds = [data[lon].min(),data[lat].min(),data[lon].max(),data[lat].max()]
        lon_center,lat_center = data[lon].mean(),data[lat].mean()
        if zoom == 'auto':
            lon_min,lon_max = data[lon].quantile(0.05),data[lon].quantile(0.95)
            zoom = 8.5-np.log(lon_max-lon_min)/np.log(2)
        params = grid_params(bounds,accuracy = accuracy)
        data['LONCOL'],data['LATCOL']= GPS_to_grids(data[lon],data[lat],params)
        data[count] = 1
        data = data.groupby(['LONCOL','LATCOL'])['count'].sum().reset_index().reset_index()
        data['geometry'] = gridid_to_polygon(data['LONCOL'],data['LATCOL'],params)
        data[lon],data[lat] = grids_centre(data['LONCOL'],data['LATCOL'],params)
        data = gpd.GeoDataFrame(data)
        
    if len(col)==3:
        lon,lat,count = col
        bounds = [data[lon].min(),data[lat].min(),data[lon].max(),data[lat].max()]
        lon_center,lat_center = data[lon].mean(),data[lat].mean()
        if zoom == 'auto':
            lon_min,lon_max = data[lon].quantile(0.05),data[lon].quantile(0.95)
            zoom = 8.5-np.log(lon_max-lon_min)/np.log(2)
        params = grid_params(bounds,accuracy = accuracy)
        data['LONCOL'],data['LATCOL']= GPS_to_grids(data[lon],data[lat],params)
        data = data.groupby(['LONCOL','LATCOL'])[count].sum().reset_index()
        data['geometry'] = gridid_to_polygon(data['LONCOL'],data['LATCOL'],params)
        data[lon],data[lat] = grids_centre(data['LONCOL'],data['LATCOL'],params)
        
        data = gpd.GeoDataFrame(data)
        
    if maptype == 'heatmap':
        vmap = KeplerGl(config = {'version': 'v1',
         'config': {'visState': {'filters': [],
           'layers': [{'id': 'vpefba0o',
             'type': 'heatmap',
             'config': {'dataId': 'data',
              'label': 'Point',
              'color': [18, 147, 154],
              'highlightColor': [252, 242, 26, 255],
              'columns': {'lat': lat, 'lng': lon},
              'isVisible': True,
              'visConfig': {'opacity': 0.8,
               'colorRange': {'name': 'Global Warming',
                'type': 'sequential',
                'category': 'Uber',
                'colors': ['#5A1846',
                 '#900C3F',
                 '#C70039',
                 '#E3611C',
                 '#F1920E',
                 '#FFC300']},
               'radius': 23},
              'hidden': False,
              'textLabel': [{'field': None,
                'color': [255, 255, 255],
                'size': 18,
                'offset': [0, 0],
                'anchor': 'start',
                'alignment': 'center'}]},
             'visualChannels': {'weightField': {'name':count, 'type': 'integer'},
              'weightScale': 'linear'}}],
           'interactionConfig': {'tooltip': {'fieldsToShow': {'data': [{'name': count,
                'format': None}]},
             'compareMode': False,
             'compareType': 'absolute',
             'enabled': True},
            'brush': {'size': 0.5, 'enabled': False},
            'geocoder': {'enabled': False},
            'coordinate': {'enabled': False}},
           'layerBlending': 'normal',
           'splitMaps': [],
           'animationConfig': {'currentTime': None, 'speed': 1}},
                    'mapState':
                    {
                        'bearing': 0,
                        'dragRotate': True,
                        'latitude': lat_center,
                        'longitude': lon_center,
                        'pitch': 0,
                        'zoom': zoom,
                        'isSplit': False
                    },
                    'mapStyle':
                    {
                        'styleType': 'dark',
                        'topLayerGroups':
                        {},
                        'visibleLayerGroups':
                        {
                            'label': True,
                            'road': True,
                            'border': False,
                            'building': True,
                            'water': True,
                            'land': True,
                            '3d building': False
                        },
                        'threeDBuildingColor': [9.665468314072013,
                            17.18305478057247,
                            31.1442867897876
                        ],
                        'mapStyles':
                        {}
                    }}},data = {'data':data},height=height)
    else:
        vmap = KeplerGl(config = {'version': 'v1',
         'config': {'visState': {'filters': [],
           'layers': [    {'id': 'ytak0zp',
     'type': 'geojson',
     'config': {'dataId': count,
      'label': 'count',
      'color': [34, 63, 154],
      'highlightColor': [252, 242, 26, 255],
      'columns': {'geojson': 'geometry'},
      'isVisible': True,
      'visConfig': {'opacity': 0.8,
       'strokeOpacity': 0.8,
       'thickness': 0.5,
       'strokeColor': [218, 112, 191],
       'colorRange': {'name': 'Global Warming',
        'type': 'sequential',
        'category': 'Uber',
        'colors': ['#5A1846',
         '#900C3F',
         '#C70039',
         '#E3611C',
         '#F1920E',
         '#FFC300']},
       'strokeColorRange': {'name': 'Global Warming',
        'type': 'sequential',
        'category': 'Uber',
        'colors': ['#5A1846',
         '#900C3F',
         '#C70039',
         '#E3611C',
         '#F1920E',
         '#FFC300']},
       'radius': 10,
       'sizeRange': [0, 10],
       'radiusRange': [0, 50],
       'heightRange': [0, 500],
       'elevationScale': 5,
       'enableElevationZoomFactor': True,
       'stroked': False,
       'filled': True,
       'enable3d': False,
       'wireframe': False},
      'hidden': False,
      'textLabel': [{'field': None,
        'color': [255, 255, 255],
        'size': 18,
        'offset': [0, 0],
        'anchor': 'start',
        'alignment': 'center'}]},
     'visualChannels': {'colorField': {'name': count, 'type': 'integer'},
      'colorScale': 'quantile',
      'strokeColorField': None,
      'strokeColorScale': 'quantile',
      'sizeField': None,
      'sizeScale': 'linear',
      'heightField': None,
      'heightScale': 'linear',
      'radiusField': None,
      'radiusScale': 'linear'}}],
           'layerBlending': 'normal',
           'splitMaps': [],
           'animationConfig': {'currentTime': None, 'speed': 1}},
          'mapState': {'bearing': 0,
           'dragRotate': False,
           'latitude': data[lat].mean(),
           'longitude': data[lon].mean(),
           'pitch': 0,
           'zoom': 10,
           'isSplit': False}}},
        data = {count:data},height=height)
        
    
    return vmap
