import geopandas as gpd  
import pandas as pd
from shapely.geometry import Polygon,Point
import math 
import numpy as np

def rect_grids(location,accuracy = 500,params='auto'):
    '''
    Generate the rectangular grids in the bounds or shape

    Parameters
    -------
    location : bounds(List) or shape(GeoDataFrame)
        Where to generate grids.
        If bounds, [lon1, lat1, lon2, lat2](WGS84), where lon1 , lat1 are the lower-left coordinates, lon2 , lat2 are the upper-right coordinates
        If shape, it should be GeoDataFrame
    accuracy : number
        Grid size (meter)
    params : List
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat) or (lonStart,latStart,deltaLon,deltaLat,theta), lonStart and latStart are the lower-left coordinates; deltaLon, deltaLat are the length and width of a single grid; theta is the angle of the grid, it will be 0 if not given
        When Gridding parameters is given, accuracy will not be used.                          

    Returns
    -------
    grid : GeoDataFrame
        Grid GeoDataFrame, LONCOL and LATCOL are the index of grids, HBLON and HBLAT are the center of the grids
    params : List
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat) or (lonStart,latStart,deltaLon,deltaLat,theta), lonStart and latStart are the lower-left coordinates; deltaLon, deltaLat are the length and width of a single grid; theta is the angle of the grid, it will be 0 if not given
    '''
    
    if (type(location)==list)|(type(location)==tuple):
        shape = ''
        bounds = location
    elif type(location)==gpd.geodataframe.GeoDataFrame:
        shape = location
        bounds = shape.unary_union.bounds
    else:
        raise Exception('Location should be either bounds(List) or shape(GeoDataFrame)')
    lon1,lat1,lon2,lat2 = bounds
    if (lon1>lon2)|(lat1>lat2)|(abs(lat1)>90)|(abs(lon1)>180)|(abs(lat2)>90)|(abs(lon2)>180):
        raise Exception('Bounds error. The input bounds should be in the order of [lon1,lat1,lon2,lat2]. (lon1,lat1) is the lower left corner and (lon2,lat2) is the upper right corner.')
    latStart = min(lat1, lat2);  
    lonStart = min(lon1, lon2);  
    deltaLon = accuracy * 360 / (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360));  
    deltaLat = accuracy * 360 / (2 * math.pi * 6371004);  
    if params=='auto':
        data = gpd.GeoDataFrame()  
        LONCOL_list = []  
        LATCOL_list = []  
        geometry_list = []  
        HBLON_list = []  
        HBLAT_list = []  
        lonsnum = int((lon2-lon1)/deltaLon)+1  
        latsnum = int((lat2-lat1)/deltaLat)+1  
        for i in range(lonsnum):  
            for j in range(latsnum):  
                HBLON = i*deltaLon + lonStart   
                HBLAT = j*deltaLat + latStart  
                HBLON_1 = (i+1)*deltaLon + lonStart  
                HBLAT_1 = (j+1)*deltaLat + latStart  
                grid_ij = Polygon([  
                (HBLON-deltaLon/2,HBLAT-deltaLat/2),  
                (HBLON_1-deltaLon/2,HBLAT-deltaLat/2),  
                (HBLON_1-deltaLon/2,HBLAT_1-deltaLat/2),  
                (HBLON-deltaLon/2,HBLAT_1-deltaLat/2)]) 
                LONCOL_list.append(i)  
                LATCOL_list.append(j)  
                HBLON_list.append(HBLON)  
                HBLAT_list.append(HBLAT)  
                geometry_list.append(grid_ij)  
        data['LONCOL'] = LONCOL_list  
        data['LATCOL'] = LATCOL_list  
        data['HBLON'] = HBLON_list  
        data['HBLAT'] = HBLAT_list  
        data['geometry'] = geometry_list  
        params = (lonStart,latStart,deltaLon,deltaLat)
    else:
        loncol_a,latcol_a = GPS_to_grids(bounds[0],bounds[1],params)
        loncol_b,latcol_b = GPS_to_grids(bounds[2],bounds[1],params)
        loncol_c,latcol_c = GPS_to_grids(bounds[0],bounds[3],params)
        loncol_d,latcol_d = GPS_to_grids(bounds[2],bounds[3],params)
        loncolstart = min([loncol_a,loncol_b,loncol_c,loncol_d])
        loncolend = max([loncol_a,loncol_b,loncol_c,loncol_d])
        latcolstart = min([latcol_a,latcol_b,latcol_c,latcol_d])
        latcolend = max([latcol_a,latcol_b,latcol_c,latcol_d])
        grid = []
        for i in range(loncolstart,loncolend+1):
            for j in range(latcolstart,latcolend+1):
                grid.append([i,j])
        grid = gpd.GeoDataFrame(grid,columns = ['LONCOL','LATCOL'])
        grid['HBLON'],grid['HBLAT'] = grids_centre(grid['LONCOL'],grid['LATCOL'],params)
        grid = grid[(grid['HBLON']>bounds[0]-params[2])&(grid['HBLON']<bounds[2]+params[2])&(grid['HBLAT']>bounds[1]-params[3])&(grid['HBLAT']<bounds[3]+params[3])]
        grid['geometry'] = gridid_to_polygon(grid['LONCOL'],grid['LATCOL'],params)
        data = grid
    if type(shape) !=gpd.geodataframe.GeoDataFrame:
        return gpd.GeoDataFrame(data),params 
    else:
        data.crs = shape.crs
        data = data[data.intersects(shape.unary_union)]
        return gpd.GeoDataFrame(data),params 


def grid_params(bounds,accuracy = 500):
    '''
    Generate gridding params

    Parameters
    -------
    bounds : List
        Bounds of the study area， [lon1, lat1, lon2, lat2](WGS84), where lon1 , lat1 are the lower-left coordinates, lon2 , lat2 are the upper-right coordinates 
    accuracy : number
        Grid size (meter)
                                               

    Returns
    -------
    params : List
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat) or (lonStart,latStart,deltaLon,deltaLat,theta), lonStart and latStart are the lower-left coordinates; deltaLon, deltaLat are the length and width of a single grid; theta is the angle of the grid, it will be 0 if not given

    Examples
    -------
    >>> import transbigdata as tbd
    >>> bounds = [113.6,22.4,114.8,22.9]
    >>> tbd.grid_params(bounds,accuracy = 500)
    (113.6, 22.4, 0.004872390756896538, 0.004496605206422906)
    
    '''
    lon1,lat1,lon2,lat2 = bounds
    if (lon1>lon2)|(lat1>lat2)|(abs(lat1)>90)|(abs(lon1)>180)|(abs(lat2)>90)|(abs(lon2)>180):
        raise Exception('Bounds error. The input bounds should be in the order of [lon1,lat1,lon2,lat2]. (lon1,lat1) is the lower left corner and (lon2,lat2) is the upper right corner.')
    latStart = min(lat1, lat2);  
    lonStart = min(lon1, lon2);  
    deltaLon = accuracy * 360 / (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360));  
    deltaLat = accuracy * 360 / (2 * math.pi * 6371004);  
    return (lonStart,latStart,deltaLon,deltaLat)

def GPS_to_grids(lon,lat,params):
    '''
    Match the GPS data to the grids. The input is the columns of longitude, latitude, and the grids parameter. The output is the grid ID.

    Parameters
    -------
    lon : Series
        The column of longitude
    lat : Series
        The column of latitude
    params : List
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat) or (lonStart,latStart,deltaLon,deltaLat,theta), lonStart and latStart are the lower-left coordinates; deltaLon, deltaLat are the length and width of a single grid; theta is the angle of the grid, it will be 0 if not given
                                            
    Returns
    -------
    LONCOL : Series
        The index of the grid longitude. The two columns LONCOL and LATCOL together can specify a grid.
    LATCOL : Series
        The index of the grid latitude. The two columns LONCOL and LATCOL together can specify a grid.
    '''
    if len(params)==4:
        (lonStart,latStart,deltaLon,deltaLat) = params
        theta = 0
    else:
        (lonStart,latStart,deltaLon,deltaLat,theta) = params
    lon = pd.Series(lon)
    lat = pd.Series(lat)
    costheta = np.cos(theta*np.pi/180)
    sintheta = np.sin(theta*np.pi/180)
    R = np.array([[costheta*deltaLon,-sintheta*deltaLat],
                [sintheta*deltaLon,costheta*deltaLat]])
    coords = np.array([lon,lat]).T
    coords = coords-(np.array([lonStart,latStart])-R[0,:]/2-R[1,:]/2)
    res = np.floor(np.dot(coords,np.linalg.inv(R)))
    loncol = res[:,0].astype(int)
    latcol = res[:,1].astype(int)
    if len(loncol)==1:
        loncol = loncol[0]
        latcol = latcol[0]
    return loncol,latcol
    
def grids_centre(loncol,latcol,params):
    '''
    The center location of the grid. The input is the grid ID and parameters, the output is the grid center location.

    Parameters
    -------
    LONCOL : Series
        The index of the grid longitude. The two columns LONCOL and LATCOL together can specify a grid.
    LATCOL : Series
        The index of the grid latitude. The two columns LONCOL and LATCOL together can specify a grid.
    params : List
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat) or (lonStart,latStart,deltaLon,deltaLat,theta), lonStart and latStart are the lower-left coordinates; deltaLon, deltaLat are the length and width of a single grid; theta is the angle of the grid, it will be 0 if not given
                                              
    Returns
    -------
    HBLON : Series
        The longitude of the grid center
    HBLAT : Series
        The latitude of the grid center
    '''
    if len(params)==4:
        (lonStart,latStart,deltaLon,deltaLat) = params
        theta = 0
    else:
        (lonStart,latStart,deltaLon,deltaLat,theta) = params
    loncol = pd.Series(loncol)
    latcol = pd.Series(latcol)
    costheta = np.cos(theta*np.pi/180)
    sintheta = np.sin(theta*np.pi/180)
    R = np.array([[costheta*deltaLon,-sintheta*deltaLat],
                [sintheta*deltaLon,costheta*deltaLat]])
    hblonhblat = np.dot(np.array([loncol.values,latcol.values]).T,R)+np.array([lonStart,latStart])
    hblon = hblonhblat[:,0]
    hblat = hblonhblat[:,1]
    if len(hblon)==1:
        hblon = hblon[0]
        hblat = hblat[0]
    return hblon,hblat


def gridid_to_polygon(loncol,latcol,params):
    '''
    Generate the geometry column based on the grid ID. The input is the grid ID, the output is the geometry.

    Parameters
    -------
    LONCOL : Series
        The index of the grid longitude. The two columns LONCOL and LATCOL together can specify a grid.
    LATCOL : Series
        The index of the grid latitude. The two columns LONCOL and LATCOL together can specify a grid.
    params : List
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat) or (lonStart,latStart,deltaLon,deltaLat,theta), lonStart and latStart are the lower-left coordinates; deltaLon, deltaLat are the length and width of a single grid; theta is the angle of the grid, it will be 0 if not given
                                               
    Returns
    -------
    geometry : Series
        The column of grid geographic polygon
    '''
    if len(params)==4:
        (lonStart,latStart,deltaLon,deltaLat) = params
        theta = 0
    else:
        (lonStart,latStart,deltaLon,deltaLat,theta) = params
    loncol = pd.Series(loncol)
    latcol = pd.Series(latcol)
    costheta = np.cos(theta*np.pi/180)
    sintheta = np.sin(theta*np.pi/180)
    R = np.array([[costheta*deltaLon,-sintheta*deltaLat],
                [sintheta*deltaLon,costheta*deltaLat]])
    res_a = np.array([loncol.values-0.5,latcol.values-0.5]).T
    res_b = np.array([loncol.values+0.5,latcol.values-0.5]).T
    res_c = np.array([loncol.values+0.5,latcol.values+0.5]).T
    res_d = np.array([loncol.values-0.5,latcol.values+0.5]).T
    hblonhblat_a = np.dot(res_a,R)+np.array([lonStart,latStart])
    hblonhblat_b = np.dot(res_b,R)+np.array([lonStart,latStart])
    hblonhblat_c = np.dot(res_c,R)+np.array([lonStart,latStart])
    hblonhblat_d = np.dot(res_d,R)+np.array([lonStart,latStart])
    a = hblonhblat_a
    b = hblonhblat_b
    c = hblonhblat_c
    d = hblonhblat_d
    from shapely.geometry import Polygon
    return [Polygon([a[i],b[i],c[i],d[i],a[i]]) for i in range(len(a))]

def hexagon_grids(bounds,accuracy = 500):
    '''
    Generate hexagonal grids in the bounds

    Parameters
    -------
    bounds : List
        Create the bounds, [lon1, lat1, lon2, lat2](WGS84), where lon1 , lat1 are the lower-left coordinates, lon2 , lat2 are the upper-right coordinates
    accuracy : number
        Side length of hexagon (m)
                                               
    Returns
    -------
    hexagon : GeoDataFrame
        hexagon grid’s geographic polygon
    ''' 
    lon1,lat1,lon2,lat2 = bounds
    if (lon1>lon2)|(lat1>lat2)|(abs(lat1)>90)|(abs(lon1)>180)|(abs(lat2)>90)|(abs(lon2)>180):
        raise Exception('Bounds error. The input bounds should be in the order of [lon1,lat1,lon2,lat2]. (lon1,lat1) is the lower left corner and (lon2,lat2) is the upper right corner.')
    latStart = min(lat1, lat2);  
    lonStart = min(lon1, lon2);  
    latEnd = max(lat1, lat2);  
    lonEnd = max(lon1, lon2);  
    origin = gpd.GeoDataFrame([Point(lonStart,latStart),Point(lonEnd,latEnd)],columns = ['geometry'])
    origin.crs = {'init':'epsg:4326'}
    origin = origin.to_crs(epsg = 3857)
    x_o = origin['geometry'].iloc[0].x
    y_o = origin['geometry'].iloc[0].y
    x_d = origin['geometry'].iloc[1].x
    y_d = origin['geometry'].iloc[1].y

    lonsnum = (x_d-x_o)/accuracy
    latsnum = (y_d-y_o)/accuracy
    #1
    xs = np.arange(0,lonsnum,3)
    ys = np.arange(0,latsnum,2*(3/4)**0.5)
    xs = pd.DataFrame(xs,columns = ['x'])
    xs['tmp'] = 1
    ys = pd.DataFrame(ys,columns = ['y'])
    ys['tmp'] = 1
    df1 = pd.merge(xs,ys)
    #2
    xs = np.arange(1.5,lonsnum,3)
    ys = np.arange((3/4)**0.5,latsnum,2*(3/4)**0.5)
    xs = pd.DataFrame(xs,columns = ['x'])
    xs['tmp'] = 1
    ys = pd.DataFrame(ys,columns = ['y'])
    ys['tmp'] = 1
    df2 = pd.merge(xs,ys)
    df = pd.concat([df1,df2])
    df['x'],df['y'] = x_o+df['x']*accuracy,y_o+df['y']*accuracy
    def get_hexagon(x,y,accuracy):
        return Polygon([(x-accuracy,y),
             (x-accuracy/2,y+accuracy*(3/4)**0.5),
             (x+accuracy/2,y+accuracy*(3/4)**0.5),
             (x+accuracy,y),
             (x+accuracy/2,y-accuracy*(3/4)**0.5),
             (x-accuracy/2,y-accuracy*(3/4)**0.5),
             (x-accuracy,y)
            ]) 
    df['geometry'] = df.apply(lambda r:get_hexagon(r['x'],r['y'],accuracy),axis = 1)
    df = gpd.GeoDataFrame(df)
    df.crs = {'init':'epsg:3857'}
    df = df.to_crs(epsg = 4326)
    df = df[['geometry']]
    df['ID'] = range(len(df))
    return df


def gridid_sjoin_shape(data,shape,params,col = ['LONCOL','LATCOL']):
    '''
    Input the two columns of grid ID, the geographic polygon and gridding paramters. The output is the grid.
    
    Parameters
    -------
    data : DataFrame
        Data, with two columns of grid ID
    shape : GeoDataFrame
        Geographic polygon
    params : List
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat) or (lonStart,latStart,deltaLon,deltaLat,theta), lonStart and latStart are the lower-left coordinates; deltaLon, deltaLat are the length and width of a single grid; theta is the angle of the grid, it will be 0 if not given
    col : List
        Column names [LONCOL,LATCOL]

    Returns
    -------
    data1 : DataFrame
        Data gridding and mapping to the corresponding geographic polygon
    '''
    LONCOL,LATCOL = col
    data1 = data.copy()
    data1 = gpd.GeoDataFrame(data1)
    data1['geometry'] = gridid_to_polygon(data1[LONCOL],data1[LATCOL],params)
    data1 = gpd.sjoin(data1,shape)
    return data1

def grid_params_gini(data,col = ['lon','lat'],accuracy = 500,gini = 'max',gap = 10,sample = 10000):
    '''
    Obtain the best griding param
    Parameters
    ----------
    data : DataFrame
        data
    col : List
        Column names [lon,lat]
    accuracy : number
        Size of the grids
    gini : number
        min,max,or median
    gap : number
        the step of the algorithm
    sample : number
        sample rate

    Returns
    ----------
    params : List
        calculated params
    '''
    trajdata = data.copy()
    if len(trajdata)>sample:
        trajdata = trajdata.sample(sample)
    lon,lat = col
    lon1 = trajdata[lon].mean()
    lat1 = trajdata[lat].mean()
    bounds = [lon1,lat1,lon1,lat1]
    params = grid_params(bounds,accuracy = accuracy)
    lonstart,latstart,deltalon,deltalat = params
    x = np.linspace(lonstart,lonstart+deltalon,gap)
    y = np.linspace(latstart,latstart+deltalat,gap)
    xx,yy = np.meshgrid(x,y)
    tmp1 = pd.DataFrame()
    xx=xx.reshape(1,-1)
    yy=yy.reshape(1,-1)
    tmp1['lon'] = xx[0]
    tmp1['lat'] = yy[0]
    r = tmp1.iloc[0]
    def GiniIndex(p):
        cum = np.cumsum(sorted(np.append(p, 0)))
        sum = cum[-1]
        x = np.array(range(len(cum))) / len(p)
        y = cum / sum
        B = np.trapz(y, x=x)
        A = 0.5 - B
        G = A / (A + B)
        return G
    def getgini(r):
        lon1,lat1 = r['lon'], r['lat']
        params_tmp=[lon1,lat1,deltalon,deltalat]
        tmp = pd.DataFrame()
        tmp['LONCOL'],tmp['LATCOL'] = GPS_to_grids(trajdata[lon], trajdata[lat], params_tmp)
        tmp['count'] = 1
        tmp = tmp.groupby(['LONCOL','LATCOL'])['count'].sum().reset_index()
        Gini = GiniIndex(list(tmp['count']))
        return Gini
    tmp1['gini'] = tmp1.apply(lambda r:getgini(r),axis = 1)
    if gini == 'max':
        r = tmp1[tmp1['gini'] == tmp1['gini'].max()].iloc[0]
        print('Gini index: '+str(r['gini']))
    elif gini == 'min':
        r = tmp1[tmp1['gini'] == tmp1['gini'].min()].iloc[0]
        print('Gini index: '+str(r['gini']))
    elif gini == 'median':
        tmp1['tmp'] = abs(tmp1['gini']-tmp1['gini'].median())
        tmp1 = tmp1.sort_values(by = 'tmp')
        r = tmp1.iloc[0]
        print('Gini index: '+str(r['gini']))
    else:
        raise Exception('Error setting of gini') 
    params = [r['lon'],r['lat'],deltalon,deltalat]
    return params

def regenerate_params(grid):
    '''
    Regenerate gridding params from grid.

    Parameters
    -------
    grid : GeoDataFrame
        grids generated by transbigdata 
                                               

    Returns
    -------
    params : List
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat) or (lonStart,latStart,deltaLon,deltaLat,theta), lonStart and latStart are the lower-left coordinates; deltaLon, deltaLat are the length and width of a single grid; theta is the angle of the grid, it will be 0 if not given

    Examples
    -------
    >>> import transbigdata as tbd
    >>> bounds = [113.6, 22.4, 113.605, 22.405]
    >>> grid,params = tbd.rect_grids(bounds,500)
    >>> tbd.regenerate_params(grid)
    [113.60000000000001, 22.400000000000002, 0.004863669213932553, 0.004496605206423254]
    '''
    grid_coord = np.array(grid['geometry'].iloc[0].exterior.coords)
    loncol = grid['LONCOL'].iloc[0]
    latcol = grid['LATCOL'].iloc[0]
    hblon = grid['geometry'].iloc[0].centroid.x
    hblat = grid['geometry'].iloc[0].centroid.y
    grid_coord = grid_coord-grid_coord[0]
    x = grid_coord[1]
    y = grid_coord[3]
    R = np.array([x,y])
    lonstart,latstart = np.array([hblon,hblat])-R[0,:]*loncol-R[1,:]*latcol
    deltalon = (x[0]**2+y[0]**2).sum()**0.5
    deltalat = (x[1]**2+y[1]**2).sum()**0.5
    theta = np.arccos(x[0]/deltalon)*180/np.pi
    if np.allclose(theta,0):
        params = [lonstart,latstart,deltalon,deltalat]
    else:
        params = [lonstart,latstart,deltalon,deltalat,theta]
    return params
