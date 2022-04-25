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
from shapely.geometry import Polygon
import math
import numpy as np
from .coordinates import getdistance
from .gisprocess import merge_polygon
import warnings


def area_to_grid(location, accuracy=500, method='rect', params='auto'):
    '''
    Generate the rectangular grids in the bounds or shape

    Parameters
    -------
    location : bounds(List) or shape(GeoDataFrame)
        Where to generate grids.
        If bounds, [lon1, lat1, lon2, lat2](WGS84), where lon1 , lat1 are the
        lower-left coordinates, lon2 , lat2 are the upper-right coordinates
        If shape, it should be GeoDataFrame
    accuracy : number
        Grid size (meter)
    method : str
        rect, tri or hexa
    params : list or dict
        Gridding parameters. 
        See https://transbigdata.readthedocs.io/en/latest/grids.html 
        for detail information about gridding parameters.
        When Gridding parameters is given, accuracy will not be used.

    Returns
    -------
    grid : GeoDataFrame
        Grid GeoDataFrame,
        LONCOL and LATCOL are the index of grids,
        HBLON and HBLAT are the center of the grids
    params : list or dict
        Gridding parameters. 
        See https://transbigdata.readthedocs.io/en/latest/grids.html 
        for detail information about gridding parameters.
    '''

    if (type(location) == list) | (type(location) == tuple):
        shape = ''
        bounds = location
    elif type(location) == gpd.geodataframe.GeoDataFrame:
        shape = location
        bounds = shape.unary_union.bounds
    else:
        raise Exception(
            'Location should be either bounds(List) or shape(GeoDataFrame)')
    lon1, lat1, lon2, lat2 = bounds
    if (lon1 > lon2) | (lat1 > lat2) | (abs(lat1) > 90) | (abs(lon1) > 180) | (
            abs(lat2) > 90) | (abs(lon2) > 180):
        raise Exception(
            'Bounds error. The input bounds should be in the order of \
                [lon1,lat1,lon2,lat2]. (lon1,lat1) is the lower left \
                    corner and (lon2,lat2) is the upper right corner.'
        )
    latStart = min(lat1, lat2)
    lonStart = min(lon1, lon2)
    deltaLon = accuracy * 360 / \
        (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360))
    deltaLat = accuracy * 360 / (2 * math.pi * 6371004)
    if params == 'auto':
        params = {'slon': lonStart,
                  'slat': latStart,
                  'deltalon': deltaLon,
                  'deltalat': deltaLat,
                  'theta': 0,
                  'method': method,
                  'gridsize': accuracy}
    else:
        params = convertparams(params)
        method = params['method']
    if method == 'rect':
        tmppoints = pd.DataFrame(np.array(
            np.meshgrid(
                np.arange(bounds[0] - deltaLon,
                          bounds[2] + deltaLon,
                          deltaLon/3),
                np.arange(bounds[1]-deltaLat,
                          bounds[3]+deltaLat,
                          deltaLat/3))
        ).reshape(2, -1).T,
            columns=['lon', 'lat'])
        tmppoints['LONCOL'], tmppoints['LATCOL'] = GPS_to_grid(
            tmppoints['lon'], tmppoints['lat'], params)
        tmppoints = tmppoints[['LONCOL', 'LATCOL']].drop_duplicates()
        tmppoints['geometry'] = grid_to_polygon(
            [tmppoints['LONCOL'], tmppoints['LATCOL']], params)
        tmppoints = gpd.GeoDataFrame(tmppoints)
    if (method == 'tri') | (method == 'hexa'):
        tmppoints = pd.DataFrame(
            np.array(
                np.meshgrid(
                    np.arange(bounds[0]-deltaLon,
                              bounds[2] + deltaLon,
                              deltaLon/3),
                    np.arange(bounds[1]+deltaLat,
                              bounds[3]-deltaLat,
                              deltaLat/3))
            ).reshape(2, -1).T, columns=['lon', 'lat'])
        tmppoints['loncol_1'],\
            tmppoints['loncol_2'],\
            tmppoints['loncol_3'] = GPS_to_grid(
            tmppoints['lon'], tmppoints['lat'], params)
        tmppoints = tmppoints[['loncol_1',
                               'loncol_2', 'loncol_3']].drop_duplicates()
        tmppoints['geometry'] = grid_to_polygon(
            [tmppoints['loncol_1'],
             tmppoints['loncol_2'],
             tmppoints['loncol_3']], params)
        tmppoints = gpd.GeoDataFrame(tmppoints)
    data = tmppoints
    params['gridsize'] = accuracy
    if type(shape) != gpd.geodataframe.GeoDataFrame:
        grid = gpd.GeoDataFrame(data)
        return grid, params
    else:
        data.crs = shape.crs
        data = data[data.intersects(shape.unary_union)]
        grid = gpd.GeoDataFrame(data)
        return grid, params


def area_to_params(location, accuracy=500, method='rect'):
    '''
    Generate gridding params

    Parameters
    -------
    location : bounds(List) or shape(GeoDataFrame)
        Where to generate grids.
        If bounds, [lon1, lat1, lon2, lat2](WGS84), where lon1 , lat1 are the
        lower-left coordinates, lon2 , lat2 are the upper-right coordinates
        If shape, it should be GeoDataFrame
    accuracy : number
        Grid size (meter)
    method : str
        rect, tri or hexa


    Returns
    -------
    params : list or dict
        Gridding parameters. 
        See https://transbigdata.readthedocs.io/en/latest/grids.html 
        for detail information about gridding parameters.

    '''
    if (type(location) == list) | (type(location) == tuple):
        shape = ''
        bounds = location
    elif type(location) == gpd.geodataframe.GeoDataFrame:
        shape = location
        bounds = shape.unary_union.bounds
    lon1, lat1, lon2, lat2 = bounds
    if (lon1 > lon2) | (lat1 > lat2) | (abs(lat1) > 90) | (abs(lon1) > 180) | (
            abs(lat2) > 90) | (abs(lon2) > 180):
        raise Exception(
            'Bounds error. The input bounds should be in the order \
                of [lon1,lat1,lon2,lat2]. (lon1,lat1) is the lower left \
                    corner and (lon2,lat2) is the upper right corner.'
        )
    latStart = min(lat1, lat2)
    lonStart = min(lon1, lon2)
    deltaLon = accuracy * 360 / \
        (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360))
    deltaLat = accuracy * 360 / (2 * math.pi * 6371004)
    params = [lonStart, latStart, deltaLon, deltaLat]
    params = convertparams(params)
    params['gridsize'] = accuracy
    params['method'] = method
    return params


def GPS_to_grid(lon, lat, params):
    '''
    Match the GPS data to the grids. The input is the columns of
    longitude, latitude, and the grids parameter. The output is the grid ID.

    Parameters
    -------
    lon : Series
        The column of longitude
    lat : Series
        The column of latitude
    params : list or dict
        Gridding parameters. 
        See https://transbigdata.readthedocs.io/en/latest/grids.html 
        for detail information about gridding parameters.

    Returns
    -------

    `Rectangle grids`
    [LONCOL,LATCOL] : list
        The two columns LONCOL and LATCOL together can specify a grid.

    `Triangle and Hexagon grids`
    [loncol_1,loncol_2,loncol_3] : list
        The index of the grid latitude. The two columns LONCOL and
        LATCOL together can specify a grid.
    '''
    params = convertparams(params)
    method = params['method']
    if method == 'rect':
        loncol, latcol = GPS_to_grids_rect(lon, lat, params)
        return [loncol, latcol]
    if method == 'tri':
        loncol_1, loncol_2, loncol_3 = GPS_to_grids_tri(lon, lat, params)
        return [loncol_1, loncol_2, loncol_3]
    if method == 'hexa':
        loncol_1, loncol_2, loncol_3 = GPS_to_grids_hexa(lon, lat, params)
        return [loncol_1, loncol_2, loncol_3]


def grid_to_centre(gridid, params):
    '''
    The center location of the grid. The input is the grid ID and
    parameters, the output is the grid center location.

    Parameters
    -------
    gridid : list
        if `Rectangle grids`
        [LONCOL,LATCOL] : Series
            The two columns LONCOL and LATCOL together can specify a grid.

        if `Triangle and Hexagon grids`
        [loncol_1,loncol_2,loncol_3] : Series
            The index of the grid latitude. The two columns LONCOL and
            LATCOL together can specify a grid.
    params : list or dict
        Gridding parameters. 
        See https://transbigdata.readthedocs.io/en/latest/grids.html 
        for detail information about gridding parameters.

    Returns
    -------
    HBLON : Series
        The longitude of the grid center
    HBLAT : Series
        The latitude of the grid center
    '''
    params = convertparams(params)
    method = params['method']
    if method == 'rect':
        loncol, latcol = gridid
        loncol = pd.Series(loncol, name='loncol')
        latcol = pd.Series(latcol, name='latcol')
        return grid_to_centre_rect(loncol, latcol, params, from_origin=False)
    if method == 'tri':
        loncol_1, loncol_2, loncol_3 = gridid
        loncol_1 = pd.Series(loncol_1, name='loncol_1')
        loncol_2 = pd.Series(loncol_2, name='loncol_2')
        loncol_3 = pd.Series(loncol_3, name='loncol_3')
        testpoint = gettripoints(loncol_1, loncol_2, loncol_3, params)
        hblon = ((testpoint['p1_x']+testpoint['p2_x'] +
                 testpoint['p3_x'])/3).values
        hblat = ((testpoint['p1_y']+testpoint['p2_y'] +
                 testpoint['p3_y'])/3).values
        return hblon, hblat
    if method == 'hexa':
        loncol_1, loncol_2, loncol_3 = gridid
        loncol_1 = pd.Series(loncol_1, name='loncol_1')
        loncol_2 = pd.Series(loncol_2, name='loncol_2')
        loncol_3 = pd.Series(loncol_3, name='loncol_3')
        lonStart = params['slon']
        latStart = params['slat']
        deltaLon = params['deltalon']
        deltaLat = params['deltalat']
        theta = params['theta']
        params = [lonStart, latStart, deltaLon, deltaLat, theta]
        x1, y1 = grid_to_centre_rect(
            loncol_1, np.zeros(len(loncol_1))-5,
            params=[params[0], params[1], params[2], params[3], theta+0])
        x2, y2 = grid_to_centre_rect(
            loncol_1, np.zeros(len(loncol_1))+5,
            params=[params[0], params[1], params[2], params[3], theta+0])
        x3, y3 = grid_to_centre_rect(
            loncol_2, np.zeros(len(loncol_2))-5,
            params=[params[0], params[1], params[2], params[3], theta+60])
        x4, y4 = grid_to_centre_rect(
            loncol_2, np.zeros(len(loncol_2))+5,
            params=[params[0], params[1], params[2], params[3], theta+60])
        x1 = pd.Series(x1)
        x2 = pd.Series(x2)
        x3 = pd.Series(x3)
        x4 = pd.Series(x4)
        y1 = pd.Series(y1)
        y2 = pd.Series(y2)
        y3 = pd.Series(y3)
        y4 = pd.Series(y4)

        def intersection(x1, y1, x2, y2, x3, y3, x4, y4):
            if np.allclose((x2[0]-x1[0]), 0):
                return x1, (x1-x3)*(y3-y4)/(x3-x4)+y3
            elif np.allclose((x3[0]-x4[0]), 0):
                return x3, (x3-x1)*(y1-y2)/(x1-x2)+y1
            x = (x1*(y2-y1)/(x2-x1)-x3/(x4-x3)*(y4-y3)+y3-y1) / \
                ((y2-y1)/(x2-x1)-(y4-y3)/(x4-x3))
            y = (x-x1)*(y2-y1)/(x2-x1)+y1
            return x, y
        hblon, hblat = intersection(x1, y1, x2, y2, x3, y3, x4, y4)
        return hblon.values, hblat.values


def grid_to_polygon(gridid, params):
    '''
    Generate the geometry column based on the grid ID.
    The input is the grid ID, the output is the geometry.
    Support rectangle, triangle and hexagon grids

    Parameters
    -------
    gridid : list
        if `Rectangle grids`
        [LONCOL,LATCOL] : Series
            The two columns LONCOL and LATCOL together can specify a grid.

        if `Triangle and Hexagon grids`
        [loncol_1,loncol_2,loncol_3] : Series
            The index of the grid latitude. The two columns LONCOL and
            LATCOL together can specify a grid.

    params : list or dict
        Gridding parameters. 
        See https://transbigdata.readthedocs.io/en/latest/grids.html 
        for detail information about gridding parameters.

    Returns
    -------
    geometry : Series
        The column of grid geographic polygon

    '''
    params = convertparams(params)
    method = params['method']

    if method == 'rect':
        loncol, latcol = gridid
        return gridid_to_polygon_rect(loncol, latcol, params)
    if method == 'tri':
        loncol_1, loncol_2, loncol_3 = gridid
        return gridid_to_polygon_tri(loncol_1, loncol_2, loncol_3, params)
    if method == 'hexa':
        loncol_1, loncol_2, loncol_3 = gridid
        return gridid_to_polygon_hexa(loncol_1, loncol_2, loncol_3, params)


def grid_to_area(data, shape, params, col=['LONCOL', 'LATCOL']):
    '''
    Input the two columns of grid ID, the geographic polygon and gridding
    paramters. The output is the grid.

    Parameters
    -------
    data : DataFrame
        Data, with two columns of grid ID
    shape : GeoDataFrame
        Geographic polygon
    params : list or dict
        Gridding parameters. 
        See https://transbigdata.readthedocs.io/en/latest/grids.html 
        for detail information about gridding parameters.
    col : List
        Column names [LONCOL,LATCOL] for rect grids or
        [loncol_1,loncol_2,loncol_3] for tri and hexa grids

    Returns
    -------
    data1 : DataFrame
        Data gridding and mapping to the corresponding geographic polygon
    '''
    params = convertparams(params)
    data1 = data[col].drop_duplicates().copy()
    data1 = gpd.GeoDataFrame(data1)
    if params['method'] == 'rect':
        LONCOL, LATCOL = col
        data1['geometry'] = gpd.points_from_xy(*grid_to_centre(
            [data1[LONCOL], data1[LATCOL]], params))
    elif params['method'] in ['tri', 'hexa']:
        loncol_1, loncol_2, loncol_3 = col
        data1['geometry'] = gpd.points_from_xy(*grid_to_centre(
            [data1[loncol_1], data1[loncol_2], data1[loncol_3]], params))
    data1 = gpd.sjoin(data1, shape)
    data1 = pd.merge(data, data1, on=col)
    return data1


def grid_to_params(grid):
    '''
    Regenerate gridding params from grid. Only support rect grids now.

    Parameters
    -------
    grid : GeoDataFrame
        grids generated by transbigdata


    Returns
    -------
    params : list or dict
        Gridding parameters. 
        See https://transbigdata.readthedocs.io/en/latest/grids.html 
        for detail information about gridding parameters.

    '''
    # 该方法未来计划增加对三角形与六边形网格支持
    grid_coord = np.array(grid['geometry'].iloc[0].exterior.coords)
    loncol = grid['LONCOL'].iloc[0]
    latcol = grid['LATCOL'].iloc[0]
    hblon = grid['geometry'].iloc[0].centroid.x
    hblat = grid['geometry'].iloc[0].centroid.y
    grid_coord = grid_coord - grid_coord[0]
    x = grid_coord[1]
    y = grid_coord[3]
    R = np.array([x, y])
    lonstart, latstart = np.array([hblon, hblat
                                   ]) - R[0, :] * loncol - R[1, :] * latcol
    deltalon = (x[0]**2 + y[0]**2).sum()**0.5
    deltalat = (x[1]**2 + y[1]**2).sum()**0.5
    theta = np.arccos(x[0] / deltalon) * 180 / np.pi
    if np.allclose(theta, 0):
        params = [lonstart, latstart, deltalon, deltalat]
    else:
        params = [lonstart, latstart, deltalon, deltalat, theta]
    params = convertparams(params)
    return params


def grid_params_optimize(data,
                         initialparams,
                         col=['uid', 'lon', 'lat'],
                         optmethod='centerdist',
                         printlog=False,
                         sample=0,
                         pop=15,
                         max_iter=50,
                         w=0.1,
                        c1=0.5,
                        c2=0.5):
    '''
    Optimize the grid params

    Parameters
    -------
    data : DataFrame
        Trajectory data
    initialparams : List
        Initial griding params
    col : List
        Column names [uid,lon,lat]
    optmethod : str
        The method to optimize: centerdist, gini, gridscount
    printlog : bool
        Whether to print detail result
    sample : int
        Sample the data as input, if 0 it will not perform sampling
    pop,max_iter,w,c1,c2:
        Params in PSO from scikit-opt

    Returns
    -------
    params_optimized : List
        Optimized params
    '''
    if sample > 0:
        trajdata = data.sample(sample)
    else:
        trajdata = data.copy()
    params = initialparams
    times = 10
    theta_lambda = 1

    params = convertparams(params)
    method = params['method']

    [uid, lon, lat] = col
    try:
        from sko.PSO import PSO
    except ImportError:
        raise ImportError(
            "Please install scikit-opt, run following code "
            "in cmd: pip install scikit-opt")

    def grids_index_gini(gpsdata, params, col=['longitude', 'latitude']):
        [lon, lat] = col
        data = gpsdata.copy()
        if params['method'] == 'rect':
            data['LONCOL'], data['LATCOL'] = GPS_to_grid(data[lon],
                                                         data[lat],
                                                         params=params)
            data['count'] = 1
            data = data.groupby(['LONCOL', 'LATCOL'])[
                'count'].sum().reset_index()
        elif (params['method'] == 'tri') | (params['method'] == 'hexa'):
            data['loncol_1'],\
                data['loncol_2'],\
                data['loncol_3'] = GPS_to_grid(data[lon],
                                               data[lat],
                                               params=params)
            data['count'] = 1
            data = data.groupby(['loncol_1', 'loncol_2', 'loncol_3'])[
                'count'].sum().reset_index()

        def GiniIndex(p):
            N = len(p)
            Q = np.mean(p)
            G = 2 / (N * (N - 1)) * (
                (N + 1) * np.sum(p) - 2 * np.sum([(N - (i + 1) + 1) * p[i]
                                                  for i in range(len(p))]))
            return G / (2 * Q)

        Gini = GiniIndex(list(data['count']))
        return Gini

    def grids_index_centerdist(gpsdata, params, col=[lon, lat]):
        [lon, lat] = col
        data = gpsdata.copy()
        data['HBLON'], data['HBLAT'] = grid_to_centre(
            GPS_to_grid(data[lon],
                        data[lat],
                        params=params),
            params=params)
        data['dist'] = getdistance(data['HBLON'], data['HBLAT'], data[lon],
                                   data[lat])
        return data['dist'].quantile(0.5)

    def grids_index_gridscount(gpsdata, params, col=[uid, lon, lat]):
        [uid, lon, lat] = col
        data = gpsdata.copy()
        if params['method'] == 'rect':
            data['LONCOL'], data['LATCOL'] = GPS_to_grid(data[lon],
                                                         data[lat],
                                                         params=params)
            return data[[
                uid, 'LONCOL', 'LATCOL'
            ]].drop_duplicates().groupby(uid)['LONCOL'].count().quantile(0.5)
        elif (params['method'] == 'tri') | (params['method'] == 'hexa'):
            data['loncol_1'],\
                data['loncol_2'],\
                data['loncol_3'] = GPS_to_grid(data[lon],
                                               data[lat],
                                               params=params)
            return data[[
                uid, 'loncol_1', 'loncol_2', 'loncol_3'
            ]].drop_duplicates().groupby(uid)['loncol_1'].count().quantile(0.5)

    if optmethod == "centerdist":

        def f_centerdist(x):
            return grids_index_centerdist(trajdata, {
                'slon': params['slon'] + x[0] / times,
                'slat': params['slat'] + x[1] / times,
                'deltalon': params['deltalon'],
                'deltalat': params['deltalat'],
                'method': params['method'],
                'theta': x[2] / theta_lambda,
            },
                col=[lon, lat])

        f = f_centerdist

    elif optmethod == "gini":

        def f_gini(x):
            return -grids_index_gini(trajdata, {
                'slon': params['slon'] + x[0] / times,
                'slat': params['slat'] + x[1] / times,
                'deltalon': params['deltalon'],
                'deltalat': params['deltalat'],
                'method': params['method'],
                'theta': x[2] / theta_lambda,
            },
                col=[lon, lat])

        f = f_gini
    elif optmethod == "gridscount":

        def f_gridscount(x):
            return grids_index_gridscount(trajdata, {
                'slon': params['slon'] + x[0] / times,
                'slat': params['slat'] + x[1] / times,
                'deltalon': params['deltalon'],
                'deltalat': params['deltalat'],
                'method': params['method'],
                'theta': x[2] / theta_lambda,
            },
                col=[uid, lon, lat])

        f = f_gridscount
    else:
        raise Exception('Method should be one of: centerdist,gini,gridscount')

    pso = PSO(func=f,
            n_dim=3,
            pop=pop, 
            max_iter=max_iter,
            lb=[0, 0, 0],
            ub=[params['deltalon'] * times, params['deltalat']
                * times, 90 * theta_lambda],
            w=w, 
            c1=c1, 
            c2=c2)
    result = pso.run()

    x = result[0]
    params_optimized = {
        'slon': params['slon'] + x[0] / times,
        'slat': params['slat'] + x[1] / times,
        'deltalon': params['deltalon'],
        'deltalat': params['deltalat'],
        'theta': x[2] / theta_lambda,
        'method': method
    }

    if printlog:
        print('Optimized index ' + optmethod + ':', f(result[0]))
        print('Optimized gridding params:', params_optimized)
        import matplotlib.pyplot as plt
        plt.figure(1, (14, 5), dpi=300)
        ax = plt.subplot(121)
        plt.plot(pso.gbest_y_hist)
        plt.ylabel('Cost')
        plt.xlabel('Iters')
        plt.title('Optimize cost')
        # 生成点的geodataframe
        trajdata['geometry'] = gpd.points_from_xy(trajdata[lon], trajdata[lat])
        trajdata = gpd.GeoDataFrame(trajdata)
        # 效果
        if method == 'rect':
            trajdata['LONCOL'], trajdata['LATCOL'] = GPS_to_grid(
                trajdata[lon], trajdata[lat], params=params_optimized)
            grids = trajdata.drop_duplicates(
                subset=['LONCOL', 'LATCOL']).copy()
            grids['geometry'] = grid_to_polygon([grids['LONCOL'],
                                                grids['LATCOL']],
                                                params=params_optimized)
        elif (method == 'tri') | (method == 'hexa'):
            result = GPS_to_grid(
                trajdata[lon], trajdata[lat], params=params_optimized)
            trajdata['loncol_1'], trajdata['loncol_2'], trajdata['loncol_3'] = result
            grids = trajdata.drop_duplicates(
                subset=['loncol_1', 'loncol_2', 'loncol_3']).copy()
            grids['geometry'] = grid_to_polygon([grids['loncol_1'],
                                                grids['loncol_2'],
                                                grids['loncol_3']],
                                                params=params_optimized)
        grids = gpd.GeoDataFrame(grids)

        ax = plt.subplot(122)
        plt.sca(ax)
        plt.axis('off')
        trajdata.plot(ax=ax, markersize=0.3)
        grids.plot(lw=1,
                   edgecolor=(0.8, 0.8, 0.8, 1),
                   facecolor=(0, 0, 0, 0.05),
                   ax=ax)
        plt.title('Gridding result')
        plt.show()
    return params_optimized


'''
Utils
'''


def grid_to_centre_rect(loncol, latcol, params, from_origin=False):
    '''
    The center location of the grid for rect grids. The input is the
    grid ID and parameters, the output is the grid center location.

    Parameters
    -------
    LONCOL : Series
        The index of the grid longitude. The two columns LONCOL and
        LATCOL together can specify a grid.
    LATCOL : Series
        The index of the grid latitude. The two columns LONCOL and
        LATCOL together can specify a grid.
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.
    from_origin : bool
        If True, lonStart and latStart are the lower left of the first
        grid.
        If False, lonStart and latStart are the center of the first
        grid.

    Returns
    -------
    HBLON : Series
        The longitude of the grid center
    HBLAT : Series
        The latitude of the grid center
    '''
    params = convertparams(params)
    lonStart = params['slon']
    latStart = params['slat']
    deltaLon = params['deltalon']
    deltaLat = params['deltalat']
    theta = params['theta']

    loncol = pd.Series(loncol)
    latcol = pd.Series(latcol)
    costheta = np.cos(theta * np.pi / 180)
    sintheta = np.sin(theta * np.pi / 180)
    R = np.array([[costheta * deltaLon, -sintheta * deltaLat],
                  [sintheta * deltaLon, costheta * deltaLat]])
    if from_origin:
        hblonhblat = np.dot(np.array([loncol.values, latcol.values]).T,
                            R) + np.array([lonStart, latStart]) - (
                                R[0, :] / 2 + R[1, :] / 2)
    else:
        hblonhblat = np.dot(np.array([loncol.values, latcol.values]).T,
                            R) + np.array([lonStart, latStart])
    hblon = hblonhblat[:, 0]
    hblat = hblonhblat[:, 1]
    if len(hblon) == 1:
        hblon = hblon[0]
        hblat = hblat[0]
    return hblon, hblat


def GPS_to_grids_rect(lon, lat, params, from_origin=False):
    '''
    Match the GPS data to the grids. The input is the columns of
    longitude, latitude, and the grids parameter. The output is the grid ID.

    Parameters
    -------
    lon : Series
        The column of longitude
    lat : Series
        The column of latitude
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.
    from_origin : bool
        If True, lonStart and latStart are the lower left of the first
        grid.
        If False, lonStart and latStart are the center of the first
        grid.

    Returns
    -------
    LONCOL : Series
        The index of the grid longitude. The two columns LONCOL and
        LATCOL together can specify a grid.
    LATCOL : Series
        The index of the grid latitude. The two columns LONCOL and
        LATCOL together can specify a grid.
    '''
    params = convertparams(params)
    lonStart = params['slon']
    latStart = params['slat']
    deltaLon = params['deltalon']
    deltaLat = params['deltalat']
    theta = params['theta']

    lon = pd.Series(lon)
    lat = pd.Series(lat)
    costheta = np.cos(theta * np.pi / 180)
    sintheta = np.sin(theta * np.pi / 180)
    R = np.array([[costheta * deltaLon, -sintheta * deltaLat],
                  [sintheta * deltaLon, costheta * deltaLat]])
    coords = np.array([lon, lat]).T
    if from_origin:
        coords = coords - (np.array([lonStart, latStart]))
    else:
        coords = coords - (np.array([lonStart, latStart]) - R[0, :] / 2 -
                           R[1, :] / 2)
    res = np.floor(np.dot(coords, np.linalg.inv(R)))
    loncol = res[:, 0].astype(int)
    latcol = res[:, 1].astype(int)
    if len(loncol) == 1:
        loncol = loncol[0]
        latcol = latcol[0]
    return loncol, latcol


def GPS_to_grids_tri(lon, lat, params):
    '''
    Match the GPS data to the grids. The input is the columns of
    longitude, latitude, and the grids parameter. The output is the grid ID.

    Parameters
    -------
    lon : Series
        The column of longitude
    lat : Series
        The column of latitude
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.

    Returns
    -------
    loncol_1,loncol_2,loncol_3 : Series
        The index of the triangle grid.
    '''
    lon = pd.Series(lon, name='lon')
    lat = pd.Series(lat, name='lat')

    params = convertparams(params)
    lonStart = params['slon']
    latStart = params['slat']
    deltaLon = params['deltalon']
    deltaLat = params['deltalat']
    theta = params['theta']
    params = [lonStart, latStart, deltaLon, deltaLat, theta]

    loncol_1, _ = GPS_to_grids_rect(lon, lat,
                                    params=[*params[:4], theta+0],
                                    from_origin=True)
    loncol_2, _ = GPS_to_grids_rect(lon, lat,
                                    params=[*params[:4], theta+60],
                                    from_origin=True)
    loncol_3, _ = GPS_to_grids_rect(lon, lat,
                                    params=[*params[:4], theta+120],
                                    from_origin=True)
    return loncol_1, loncol_2, loncol_3


def GPS_to_grids_hexa(lon, lat, params):
    '''
    Match the GPS data to the grids. The input is the columns of
    longitude, latitude, and the grids parameter. The output is the grid ID.

    Parameters
    -------
    lon : Series
        The column of longitude
    lat : Series
        The column of latitude
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.

    Returns
    -------
    loncol_1,loncol_2,loncol_3 : Series
        The index of the hexagon grid.
    '''
    lon = pd.Series(lon, name='lon')
    lat = pd.Series(lat, name='lat')
    params = convertparams(params)
    lonStart = params['slon']
    latStart = params['slat']
    deltaLon = params['deltalon']
    deltaLat = params['deltalat']
    theta = params['theta']
    params = [lonStart, latStart, deltaLon, deltaLat, theta]

    loncol_1, _ = GPS_to_grids_rect(lon, lat,
                                    params=[*params[:4], theta+0],
                                    from_origin=True)
    loncol_2, _ = GPS_to_grids_rect(lon, lat,
                                    params=[*params[:4], theta+60],
                                    from_origin=True)
    loncol_3, _ = GPS_to_grids_rect(lon, lat,
                                    params=[*params[:4], theta+120],
                                    from_origin=True)
    tmp = pd.DataFrame()
    tmp['lon'] = lon
    tmp['lat'] = lat
    tmp['loncol_1'] = loncol_1
    tmp['loncol_2'] = loncol_2
    tmp['loncol_3'] = loncol_3
    tmp['id'] = range(len(tmp))
    tmp1 = tmp[['loncol_1', 'loncol_2', 'loncol_3']].drop_duplicates()
    loncol_1 = tmp1['loncol_1']
    loncol_2 = tmp1['loncol_2']
    loncol_3 = tmp1['loncol_3']
    center = pd.concat(
        [pd.DataFrame(
            np.array(
                [loncol_1+1, loncol_2+1, loncol_3+1,
                 loncol_1, loncol_2, loncol_3]).T),
         pd.DataFrame(
            np.array(
                [loncol_1+1, loncol_2+1, loncol_3,
                 loncol_1, loncol_2, loncol_3]).T),
         pd.DataFrame(
            np.array(
                [loncol_1+1, loncol_2, loncol_3,
                 loncol_1, loncol_2, loncol_3]).T),
         pd.DataFrame(
            np.array(
                [loncol_1, loncol_2+1, loncol_3+1,
                 loncol_1, loncol_2, loncol_3]).T),
         pd.DataFrame(
            np.array(
                [loncol_1, loncol_2, loncol_3+1,
                 loncol_1, loncol_2, loncol_3]).T),
         pd.DataFrame(
             np.array(
                 [loncol_1, loncol_2, loncol_3,
                  loncol_1, loncol_2, loncol_3]).T)]).drop_duplicates()
    center.columns = ['i', 'j', 'k', 'loncol_1', 'loncol_2', 'loncol_3']
    center = center[((((center['i']-1) % 3) == 0) &
                     (((center['j']-1) % 3) == 0) &
                     (((center['k']) % 3) == 0)) |
                    ((((center['i']-2) % 3) == 0) &
                     (((center['j']) % 3) == 0) &
                     (((center['k']+2) % 3) == 0)) |
                    ((((center['i']) % 3) == 0) &
                     (((center['j']+1) % 3) == 0) &
                     (((center['k']+1) % 3) == 0))
                    ]
    tmp = pd.merge(tmp, center, on=['loncol_1', 'loncol_2', 'loncol_3'])
    tmp = tmp.sort_values(by='id')
    loncol_1 = tmp['i'].values
    loncol_2 = tmp['j'].values
    loncol_3 = tmp['k'].values
    return loncol_1, loncol_2, loncol_3


def gridid_to_polygon_rect(loncol, latcol, params):
    '''
    Generate the geometry column based on the grid ID.
    The input is the grid ID, the output is the geometry.

    Parameters
    -------
    LONCOL : Series
        The index of the grid longitude.
        The two columns LONCOL and LATCOL together can specify a grid.
    LATCOL : Series
        The index of the grid latitude.
        The two columns LONCOL and LATCOL together can specify a grid.
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.

    Returns
    -------
    geometry : Series
        The column of grid geographic polygon
    '''
    params = convertparams(params)
    lonStart = params['slon']
    latStart = params['slat']
    deltaLon = params['deltalon']
    deltaLat = params['deltalat']
    theta = params['theta']
    loncol = pd.Series(loncol)
    latcol = pd.Series(latcol)
    costheta = np.cos(theta * np.pi / 180)
    sintheta = np.sin(theta * np.pi / 180)
    R = np.array([[costheta * deltaLon, -sintheta * deltaLat],
                  [sintheta * deltaLon, costheta * deltaLat]])
    res_a = np.array([loncol.values - 0.5, latcol.values - 0.5]).T
    res_b = np.array([loncol.values + 0.5, latcol.values - 0.5]).T
    res_c = np.array([loncol.values + 0.5, latcol.values + 0.5]).T
    res_d = np.array([loncol.values - 0.5, latcol.values + 0.5]).T
    hblonhblat_a = np.dot(res_a, R) + np.array([lonStart, latStart])
    hblonhblat_b = np.dot(res_b, R) + np.array([lonStart, latStart])
    hblonhblat_c = np.dot(res_c, R) + np.array([lonStart, latStart])
    hblonhblat_d = np.dot(res_d, R) + np.array([lonStart, latStart])
    a = hblonhblat_a
    b = hblonhblat_b
    c = hblonhblat_c
    d = hblonhblat_d
    from shapely.geometry import Polygon
    return [Polygon([a[i], b[i], c[i], d[i], a[i]]) for i in range(len(a))]


def gettripoints(loncol_1, loncol_2, loncol_3, params):
    # Get triangle vertix coords from gridid and params
    params = convertparams(params)
    lonStart = params['slon']
    latStart = params['slat']
    deltaLon = params['deltalon']
    deltaLat = params['deltalat']
    theta = params['theta']
    params = [lonStart, latStart, deltaLon, deltaLat, theta]

    flag = (loncol_1+loncol_2+loncol_3)
    x1, y1 = grid_to_centre_rect(
        loncol_1+flag % 2, np.zeros(len(loncol_1))-5,
        params=[params[0], params[1], params[2], params[3], theta+0])
    x2, y2 = grid_to_centre_rect(
        loncol_1+flag % 2, np.zeros(len(loncol_1))+5,
        params=[params[0], params[1], params[2], params[3], theta+0])
    x3, y3 = grid_to_centre_rect(
        loncol_2+(flag+1) % 2, np.zeros(len(loncol_2))-5,
        params=[params[0], params[1], params[2], params[3], theta+60])
    x4, y4 = grid_to_centre_rect(
        loncol_2+(flag+1) % 2, np.zeros(len(loncol_2))+5,
        params=[params[0], params[1], params[2], params[3], theta+60])
    x5, y5 = grid_to_centre_rect(
        loncol_3+flag % 2, np.zeros(len(loncol_3))-5,
        params=[params[0], params[1], params[2], params[3], theta+120])
    x6, y6 = grid_to_centre_rect(
        loncol_3+flag % 2, np.zeros(len(loncol_3))+5,
        params=[params[0], params[1], params[2], params[3], theta+120])
    x1 = pd.Series(x1)
    x2 = pd.Series(x2)
    x3 = pd.Series(x3)
    x4 = pd.Series(x4)
    x5 = pd.Series(x5)
    x6 = pd.Series(x6)
    y1 = pd.Series(y1)
    y2 = pd.Series(y2)
    y3 = pd.Series(y3)
    y4 = pd.Series(y4)
    y5 = pd.Series(y5)
    y6 = pd.Series(y6)

    def intersection(x1, y1, x2, y2, x3, y3, x4, y4):
        if np.allclose((x2[0]-x1[0]), 0):
            return x1, (x1-x3)*(y3-y4)/(x3-x4)+y3
        elif np.allclose((x3[0]-x4[0]), 0):
            return x3, (x3-x1)*(y1-y2)/(x1-x2)+y1
        x = (x1*(y2-y1)/(x2-x1)-x3/(x4-x3)*(y4-y3)+y3-y1) / \
            ((y2-y1)/(x2-x1)-(y4-y3)/(x4-x3))
        y = (x-x1)*(y2-y1)/(x2-x1)+y1
        return x, y

    testpoint = pd.DataFrame()
    testpoint['p1_x'], testpoint['p1_y'] = intersection(
        x1, y1, x2, y2, x3, y3, x4, y4)
    testpoint['p2_x'], testpoint['p2_y'] = intersection(
        x5, y5, x6, y6, x3, y3, x4, y4)
    testpoint['p3_x'], testpoint['p3_y'] = intersection(
        x1, y1, x2, y2, x5, y5, x6, y6)
    return testpoint.round(6)


def gridid_to_polygon_tri(loncol_1, loncol_2, loncol_3, params):
    '''
    Generate the geometry column based on the grid ID.
    The input is the grid ID, the output is the geometry.

    Parameters
    -------
    loncol_1,loncol_2,loncol_3 : Series
        The index of the triangle grid.
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.

    Returns
    -------
    geometry : Series
        The column of grid geographic polygon
    '''
    params = convertparams(params)
    lonStart = params['slon']
    latStart = params['slat']
    deltaLon = params['deltalon']
    deltaLat = params['deltalat']
    theta = params['theta']
    params = [lonStart, latStart, deltaLon, deltaLat, theta]

    loncol_1 = pd.Series(loncol_1, name='i')
    loncol_2 = pd.Series(loncol_2, name='j')
    loncol_3 = pd.Series(loncol_3, name='k')

    testpoint = gettripoints(loncol_1, loncol_2, loncol_3, params)

    geometry = testpoint.apply(
        lambda r: Polygon(np.array([[r['p1_x'], r['p1_y']],
                                    [r['p2_x'], r['p2_y']],
                                    [r['p3_x'], r['p3_y']]]).round(6)), axis=1)
    return list(geometry)


def gridid_to_polygon_hexa(loncol_1, loncol_2, loncol_3, params):
    '''
    Generate the geometry column based on the grid ID.
    The input is the grid ID, the output is the geometry.

    Parameters
    -------
    loncol_1,loncol_2,loncol_3 : Series
        The index of the hexagon grid.
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.

    Returns
    -------
    geometry : Series
        The column of grid geographic polygon
    '''
    i = pd.Series(loncol_1, name='i')
    j = pd.Series(loncol_2, name='j')
    k = pd.Series(loncol_3, name='k')
    gridid = pd.DataFrame(np.array([i, j, k]).T, columns=['i', 'j', 'k'])
    tmp = pd.concat([pd.DataFrame(np.array([i-1, j-1, k-1, i, j, k]).T),
                     pd.DataFrame(np.array([i-1, j-1, k, i, j, k]).T),
                     pd.DataFrame(np.array([i-1, j, k, i, j, k]).T),
                     pd.DataFrame(np.array([i, j-1, k-1, i, j, k]).T),
                     pd.DataFrame(np.array([i, j, k-1, i, j, k]).T),
                     pd.DataFrame(np.array([i, j, k, i, j, k]).T)])
    tmp.columns = ['loncol_1', 'loncol_2', 'loncol_3', 'i', 'j', 'k']
    tmp['geometry'] = list(
        gettripoints(
            tmp['loncol_1'],
            tmp['loncol_2'],
            tmp['loncol_3'], params).apply(
            lambda r: Polygon(
                np.array([[r['p1_x'], r['p1_y']],
                          [r['p2_x'], r['p2_y']],
                          [r['p3_x'], r['p3_y']]]).round(6)), axis=1))
    tmp = gpd.GeoDataFrame(tmp)
    tmp['gridid'] = tmp['i'].astype(
        'str')+','+tmp['j'].astype('str')+','+tmp['k'].astype('str')
    tmp1 = merge_polygon(tmp, 'gridid')
    geometry = pd.merge(gridid, pd.merge(
        tmp1, tmp[['gridid', 'i', 'j', 'k']].drop_duplicates()))['geometry']
    return list(geometry)


def convertparams(params):
    # Convertparams from list to dict
    if (type(params) == list) | (type(params) == tuple):
        if len(params) == 4:
            lonStart, latStart, deltaLon, deltaLat = params
            theta = 0
            method = 'rect'
        elif len(params) == 5:
            lonStart, latStart, deltaLon, deltaLat, theta = params
            method = 'rect'
        elif len(params) == 6:
            lonStart, latStart, deltaLon, deltaLat, theta, method = params
        dicparams = dict()
        dicparams['slon'] = lonStart
        dicparams['slat'] = latStart
        dicparams['deltalon'] = deltaLon
        dicparams['deltalat'] = deltaLat
        dicparams['theta'] = theta
        dicparams['method'] = method
    else:
        dicparams = params
        if 'theta' not in dicparams:
            dicparams['theta'] = 0
        if 'method' not in dicparams:
            dicparams['method'] = 'rect'
    if dicparams['method'] not in ['rect', 'tri', 'hexa']:
        raise ValueError('Method should be `rect`,`tri` or `hexa`')
    return dicparams


'''
Old namespace
'''


def regenerate_params(*args, **kwargs):
    warnings.warn("This method is renamed as transbigdata.grid_to_params")
    return grid_to_params(*args, **kwargs)


def grid_params(*args, **kwargs):
    warnings.warn("This method is renamed as transbigdata.area_to_params")
    return area_to_params(*args, **kwargs)


def GPS_to_grids(*args, **kwargs):
    warnings.warn("This method is renamed as transbigdata.GPS_to_grid")
    return GPS_to_grid(*args, **kwargs)


def rect_grids(*args, **kwargs):
    warnings.warn("This method is renamed as transbigdata.area_to_grid")
    return area_to_grid(*args, **kwargs)


def gridid_sjoin_shape(*args, **kwargs):
    warnings.warn("This method is renamed as transbigdata.grid_to_area")
    return grid_to_area(*args, **kwargs)


def grids_centre(loncol, latcol, params):
    warnings.warn("This method is renamed as transbigdata.grid_to_centre")
    return grid_to_centre([loncol, latcol], params)


def gridid_to_polygon(loncol, latcol, params):
    warnings.warn("This method is renamed as transbigdata.grid_to_polygon")
    return grid_to_polygon([loncol, latcol], params)


'''
Geohash
'''

__base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
__decodemap = {}
for i in range(len(__base32)):
    __decodemap[__base32[i]] = i
del i


def decode_exactly(geohash):
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    lat_err, lon_err = 90.0, 180.0
    is_even = True
    for c in geohash:
        cd = __decodemap[c]
        for mask in [16, 8, 4, 2, 1]:
            if is_even:
                lon_err /= 2
                if cd & mask:
                    lon_interval = (
                        (lon_interval[0]+lon_interval[1])/2, lon_interval[1])
                else:
                    lon_interval = (
                        lon_interval[0], (lon_interval[0]+lon_interval[1])/2)
            else:
                lat_err /= 2
                if cd & mask:
                    lat_interval = (
                        (lat_interval[0]+lat_interval[1])/2, lat_interval[1])
                else:
                    lat_interval = (
                        lat_interval[0], (lat_interval[0]+lat_interval[1])/2)
            is_even = not is_even
    lat = (lat_interval[0] + lat_interval[1]) / 2
    lon = (lon_interval[0] + lon_interval[1]) / 2
    return lon, lat,  lon_err, lat_err


def decode(geohash):
    lon, lat,  _, _ = decode_exactly(geohash)
    return lon, lat


def encode(longitude, latitude, precision=12):
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    even = True
    i = 1
    while len(geohash) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude > mid:
                ch |= bits[bit]
                lon_interval = (mid, lon_interval[1])
            else:
                lon_interval = (lon_interval[0], mid)
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude > mid:
                ch |= bits[bit]
                lat_interval = (mid, lat_interval[1])
            else:
                lat_interval = (lat_interval[0], mid)
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash += __base32[ch]
            bit = 0
            ch = 0
        i += 1
    return ''.join(geohash)


def geohash_encode(lon, lat, precision=12):
    '''
    Input latitude and longitude and precision, and encode geohash code

    Parameters
    -------
    lon : Series
        longitude Series
    lat : Series
        latitude Series
    precision : number
        geohash precision

    Returns
    -------
    geohash : Series
        encoded geohash Series
    '''
    tmp = pd.DataFrame()
    tmp['lon'] = lon
    tmp['lat'] = lat
    geohash = tmp.apply(lambda r: encode(
        r['lon'], r['lat'], precision), axis=1)
    return geohash


def geohash_decode(geohash):
    '''
    Decode geohash code

    Parameters
    -------
    geohash : Series
        encoded geohash Series

    Returns
    -------
    lon : Series
        decoded longitude Series
    lat : Series
        decoded latitude Series
    '''
    lonslats = geohash.apply(lambda r: decode(r))
    lon = lonslats.apply(lambda r: r[0])
    lat = lonslats.apply(lambda r: r[1])
    return lon, lat


def geohash_togrid(geohash):
    '''
    Input geohash code to generate geohash grid cell

    Parameters
    -------
    geohash : Series
        encoded geohash Series

    Returns
    -------
    poly : Series
        grid cell polygon for geohash
    '''
    lonslats = geohash.apply(lambda r: decode_exactly(r))

    def topoly(r):
        (lon, lat, lon_err, lat_err) = r
        from shapely.geometry import Polygon
        return Polygon([[lon-lon_err, lat-lat_err],
                        [lon-lon_err, lat+lat_err],
                        [lon+lon_err, lat+lat_err],
                        [lon+lon_err, lat-lat_err],
                        [lon-lon_err, lat-lat_err],
                        ])
    poly = lonslats.apply(lambda r: topoly(r))
    return poly
