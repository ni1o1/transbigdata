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
from shapely.geometry import Polygon, Point
import math
import numpy as np
from .coordinates import getdistance
from .gisprocess import merge_polygon


def rect_grids(location, accuracy=500, params='auto'):
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
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.

    Returns
    -------
    grid : GeoDataFrame
        Grid GeoDataFrame,
        LONCOL and LATCOL are the index of grids,
        HBLON and HBLAT are the center of the grids
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.
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
        data = gpd.GeoDataFrame()
        LONCOL_list = []
        LATCOL_list = []
        geometry_list = []
        HBLON_list = []
        HBLAT_list = []
        lonsnum = int((lon2 - lon1) / deltaLon) + 1
        latsnum = int((lat2 - lat1) / deltaLat) + 1
        for i in range(lonsnum):
            for j in range(latsnum):
                HBLON = i * deltaLon + lonStart
                HBLAT = j * deltaLat + latStart
                HBLON_1 = (i + 1) * deltaLon + lonStart
                HBLAT_1 = (j + 1) * deltaLat + latStart
                grid_ij = Polygon([
                    (HBLON - deltaLon / 2, HBLAT - deltaLat / 2),
                    (HBLON_1 - deltaLon / 2, HBLAT - deltaLat / 2),
                    (HBLON_1 - deltaLon / 2, HBLAT_1 - deltaLat / 2),
                    (HBLON - deltaLon / 2, HBLAT_1 - deltaLat / 2)
                ])
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
        params = (lonStart, latStart, deltaLon, deltaLat)
    else:
        loncol_a, latcol_a = GPS_to_grids(bounds[0], bounds[1], params)
        loncol_b, latcol_b = GPS_to_grids(bounds[2], bounds[1], params)
        loncol_c, latcol_c = GPS_to_grids(bounds[0], bounds[3], params)
        loncol_d, latcol_d = GPS_to_grids(bounds[2], bounds[3], params)
        loncolstart = min([loncol_a, loncol_b, loncol_c, loncol_d])
        loncolend = max([loncol_a, loncol_b, loncol_c, loncol_d])
        latcolstart = min([latcol_a, latcol_b, latcol_c, latcol_d])
        latcolend = max([latcol_a, latcol_b, latcol_c, latcol_d])
        grid = []
        for i in range(loncolstart, loncolend + 1):
            for j in range(latcolstart, latcolend + 1):
                grid.append([i, j])
        grid = gpd.GeoDataFrame(grid, columns=['LONCOL', 'LATCOL'])
        grid['HBLON'], grid['HBLAT'] = grids_centre(grid['LONCOL'],
                                                    grid['LATCOL'], params)
        grid = grid[(grid['HBLON'] > bounds[0] - params[2])
                    & (grid['HBLON'] < bounds[2] + params[2])
                    & (grid['HBLAT'] > bounds[1] - params[3]) &
                    (grid['HBLAT'] < bounds[3] + params[3])]
        grid['geometry'] = gridid_to_polygon(grid['LONCOL'], grid['LATCOL'],
                                             params)
        data = grid
    if type(shape) != gpd.geodataframe.GeoDataFrame:
        return gpd.GeoDataFrame(data), params
    else:
        data.crs = shape.crs
        data = data[data.intersects(shape.unary_union)]
        return gpd.GeoDataFrame(data), params


def grid_params(bounds, accuracy=500):
    '''
    Generate gridding params

    Parameters
    -------
    bounds : List
        Bounds of the study area， [lon1, lat1, lon2, lat2](WGS84)
        where lon1 , lat1 are the lower-left coordinates, lon2 , lat2
        are the upper-right coordinates
    accuracy : number
        Grid size (meter)


    Returns
    -------
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.

    Examples
    -------
    >>> import transbigdata as tbd
    >>> bounds = [113.6,22.4,114.8,22.9]
    >>> tbd.grid_params(bounds,accuracy = 500)
    (113.6, 22.4, 0.004872390756896538, 0.004496605206422906)

    '''
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
    return (lonStart, latStart, deltaLon, deltaLat)


def GPS_to_grids(lon, lat, params, from_origin=False):
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
    if len(params) == 4:
        (lonStart, latStart, deltaLon, deltaLat) = params
        theta = 0
    else:
        (lonStart, latStart, deltaLon, deltaLat, theta) = params
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


def grids_centre(loncol, latcol, params, from_origin=False):
    '''
    The center location of the grid. The input is the grid ID and
    parameters, the output is the grid center location.

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
    if len(params) == 4:
        (lonStart, latStart, deltaLon, deltaLat) = params
        theta = 0
    else:
        (lonStart, latStart, deltaLon, deltaLat, theta) = params
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


def gridid_to_polygon(loncol, latcol, params):
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
    if len(params) == 4:
        (lonStart, latStart, deltaLon, deltaLat) = params
        theta = 0
    else:
        (lonStart, latStart, deltaLon, deltaLat, theta) = params
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


def gridid_sjoin_shape(data, shape, params, col=['LONCOL', 'LATCOL']):
    '''
    Input the two columns of grid ID, the geographic polygon and gridding
    paramters. The output is the grid.

    Parameters
    -------
    data : DataFrame
        Data, with two columns of grid ID
    shape : GeoDataFrame
        Geographic polygon
    params : List
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.
    col : List
        Column names [LONCOL,LATCOL]

    Returns
    -------
    data1 : DataFrame
        Data gridding and mapping to the corresponding geographic polygon
    '''
    LONCOL, LATCOL = col
    data1 = data.copy()
    data1 = gpd.GeoDataFrame(data1)
    data1['geometry'] = gridid_to_polygon(data1[LONCOL], data1[LATCOL], params)
    data1 = gpd.sjoin(data1, shape)
    return data1


def grid_params_optimize(data,
                         initialparams,
                         col=['uid', 'lon', 'lat'],
                         method='centerdist',
                         printlog=False,
                         sample=0):
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
    method : str
        The method to optimize: centerdist, gini, gridscount
    printlog : bool
        Whether to print log or not
    sample : int
        Sample the data as input, if 0 it will not perform sampling

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
    times = 1000
    theta_lambda = 90

    if len(params) == 4:
        params = [*params, 0]
    [uid, lon, lat] = col
    try:
        from sko.GA import GA
    except ImportError:
        raise ImportError(
            "Please install scikit-opt, run following code "
            "in cmd: pip install scikit-opt")

    def grids_index_gini(gpsdata, params, col=['longitude', 'latitude']):
        [lon, lat] = col
        data = gpsdata.copy()
        data['LONCOL'], data['LATCOL'] = GPS_to_grids(data[lon],
                                                      data[lat],
                                                      params=params)
        data['count'] = 1
        data = data.groupby(['LONCOL', 'LATCOL'])['count'].sum().reset_index()

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
        data['LONCOL'], data['LATCOL'] = GPS_to_grids(data[lon],
                                                      data[lat],
                                                      params=params)
        data['HBLON'], data['HBLAT'] = grids_centre(data['LONCOL'],
                                                    data['LATCOL'],
                                                    params=params)
        data['dist'] = getdistance(data['HBLON'], data['HBLAT'], data[lon],
                                   data[lat])
        return data['dist'].quantile(0.5)

    def grids_index_gridscount(gpsdata, params, col=[uid, lon, lat]):
        [uid, lon, lat] = col
        data = gpsdata.copy()
        data['LONCOL'], data['LATCOL'] = GPS_to_grids(data[lon],
                                                      data[lat],
                                                      params=params)
        return data[[
            uid, 'LONCOL', 'LATCOL'
        ]].drop_duplicates().groupby(uid)['LONCOL'].count().quantile(0.5)

    if method == "centerdist":

        def f_centerdist(x):
            return grids_index_centerdist(trajdata, [
                params[0] + x[0] / times, params[1] + x[1] / times, params[2],
                params[3], x[2] / theta_lambda
            ],
                col=[lon, lat])

        f = f_centerdist

    elif method == "gini":

        def f_gini(x):
            return -grids_index_gini(trajdata, [
                params[0] + x[0] / times, params[1] + x[1] / times, params[2],
                params[3], x[2] / theta_lambda
            ],
                col=[lon, lat])

        f = f_gini
    elif method == "gridscount":

        def f_gridscount(x):
            return grids_index_gridscount(trajdata, [
                params[0] + x[0] / times, params[1] + x[1] / times, params[2],
                params[3], x[2] / theta_lambda
            ],
                col=[uid, lon, lat])

        f = f_gridscount
    else:
        raise Exception('Method should be one of: centerdist,gini,gridscount')

    ga = GA(func=f,
            n_dim=3,
            size_pop=50,
            max_iter=300,
            prob_mut=0.001,
            lb=[0, 0, 0],
            ub=[params[2] * times, params[3] * times, 90 * theta_lambda],
            precision=1e-7)
    result = ga.run()

    x = result[0]
    params_optimized = [
        params[0] + x[0] / times, params[1] + x[1] / times, params[2],
        params[3], x[2] / theta_lambda
    ]

    if printlog:
        print('Optimized index ' + method + ':', f(result[0]))
        print('Optimized gridding params:', params_optimized)
        print('Optimizing cost:')
        import pandas as pd
        import matplotlib.pyplot as plt
        Y_history = pd.DataFrame(ga.all_history_Y)
        _, ax = plt.subplots(2, 1)
        ax[0].plot(Y_history.index, Y_history.values, '.', color='red')
        Y_history.min(axis=1).cummin().plot(kind='line')

        plt.show()
        # 生成点的geodataframe
        trajdata['geometry'] = gpd.points_from_xy(trajdata[lon], trajdata[lat])
        trajdata = gpd.GeoDataFrame(trajdata)
        # 效果
        trajdata['LONCOL'], trajdata['LATCOL'] = GPS_to_grids(
            trajdata[lon], trajdata[lat], params=params_optimized)
        grids = trajdata.drop_duplicates(subset=['LONCOL', 'LATCOL']).copy()
        grids['geometry'] = gridid_to_polygon(grids['LONCOL'],
                                              grids['LATCOL'],
                                              params=params_optimized)
        grids = gpd.GeoDataFrame(grids)
        print('Result:')
        import matplotlib.pyplot as plt
        plt.figure(1, (8, 8), dpi=300)
        ax = plt.subplot(111)
        plt.sca(ax)
        plt.axis('off')
        trajdata.plot(ax=ax, markersize=0.3)
        grids.plot(lw=1,
                   edgecolor=(0.8, 0.8, 0.8, 1),
                   facecolor=(0, 0, 0, 0.05),
                   ax=ax)

        plt.show()
    return params_optimized


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
        Gridding parameters (lonStart, latStart, deltaLon, deltaLat) or
        (lonStart, latStart, deltaLon, deltaLat, theta).
        lonStart and latStart are the lower-left coordinates;
        deltaLon, deltaLat are the length and width of a single grid;
        theta is the angle of the grid, it will be 0 if not given.
        When Gridding parameters is given, accuracy will not be used.

    Examples
    -------
    >>> import transbigdata as tbd
    >>> bounds = [113.6, 22.4, 113.605, 22.405]
    >>> grid,params = tbd.rect_grids(bounds,500)
    >>> params_regenerated = tbd.regenerate_params(grid)
    '''
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
    return params


'''
Triangle grids
'''


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
    gridid : Series
        The index of the triangle grid.
    '''
    lon = pd.Series(lon, name='lon')
    lat = pd.Series(lat, name='lat')
    if len(params) == 4:
        (lonStart, latStart, deltaLon, deltaLat) = params
        theta = 0
    else:
        (lonStart, latStart, deltaLon, deltaLat, theta) = params
    loncol_1, _ = GPS_to_grids(lon, lat,
                               params=[*params[:4], theta+0],
                               from_origin=True)
    loncol_2, _ = GPS_to_grids(lon, lat,
                               params=[*params[:4], theta+60],
                               from_origin=True)
    loncol_3, _ = GPS_to_grids(lon, lat,
                               params=[*params[:4], theta+120],
                               from_origin=True)
    gridid = list(pd.Series(loncol_1).astype(str)+',' +
                  pd.Series(loncol_2).astype(str)+',' +
                  pd.Series(loncol_3).astype(str))
    return gridid


def gettripoints(loncol_1, loncol_2, loncol_3, params):
    # Get triangle vertix coords from gridid and params
    if len(params) == 4:
        (lonStart, latStart, deltaLon, deltaLat) = params
        theta = 0
    else:
        (lonStart, latStart, deltaLon, deltaLat, theta) = params
    flag = (loncol_1+loncol_2+loncol_3)
    x1, y1 = grids_centre(
        loncol_1+flag % 2, np.zeros(len(loncol_1))-5,
        params=[params[0], params[1], params[2], params[3], theta+0])
    x2, y2 = grids_centre(
        loncol_1+flag % 2, np.zeros(len(loncol_1))+5,
        params=[params[0], params[1], params[2], params[3], theta+0])
    x3, y3 = grids_centre(
        loncol_2+(flag+1) % 2, np.zeros(len(loncol_2))-5,
        params=[params[0], params[1], params[2], params[3], theta+60])
    x4, y4 = grids_centre(
        loncol_2+(flag+1) % 2, np.zeros(len(loncol_2))+5,
        params=[params[0], params[1], params[2], params[3], theta+60])
    x5, y5 = grids_centre(
        loncol_3+flag % 2, np.zeros(len(loncol_3))-5,
        params=[params[0], params[1], params[2], params[3], theta+120])
    x6, y6 = grids_centre(
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


def gridid_to_polygon_tri(gridid, params):
    '''
    Generate the geometry column based on the grid ID.
    The input is the grid ID, the output is the geometry.

    Parameters
    -------
    gridid : Series
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
    gridid = pd.Series(gridid, name='gridid')
    if len(params) == 4:
        (lonStart, latStart, deltaLon, deltaLat) = params
        theta = 0
    else:
        (lonStart, latStart, deltaLon, deltaLat, theta) = params

    gridid_tmp = gridid.apply(lambda r: r.split(','))
    loncol_1 = gridid_tmp.apply(lambda r: r[0]).astype(int)
    loncol_2 = gridid_tmp.apply(lambda r: r[1]).astype(int)
    loncol_3 = gridid_tmp.apply(lambda r: r[2]).astype(int)

    testpoint = gettripoints(loncol_1, loncol_2, loncol_3, params)

    geometry = testpoint.apply(
        lambda r: Polygon(np.array([[r['p1_x'], r['p1_y']],
                                    [r['p2_x'], r['p2_y']],
                                    [r['p3_x'], r['p3_y']]]).round(6)), axis=1)
    return geometry


'''
hexagon
'''


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
    gridid : Series
        The index of the hexagon grid.
    '''
    lon = pd.Series(lon, name='lon')
    lat = pd.Series(lat, name='lat')
    if len(params) == 4:
        (lonStart, latStart, deltaLon, deltaLat) = params
        theta = 0
    else:
        (lonStart, latStart, deltaLon, deltaLat, theta) = params
    loncol_1, _ = GPS_to_grids(lon, lat,
                               params=[*params[:4], theta+0],
                               from_origin=True)
    loncol_2, _ = GPS_to_grids(lon, lat,
                               params=[*params[:4], theta+60],
                               from_origin=True)
    loncol_3, _ = GPS_to_grids(lon, lat,
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
    tmp['gridid'] = tmp['i'].astype(
        str)+','+tmp['j'].astype(str)+','+tmp['k'].astype(str)
    return list(tmp['gridid'])


def gridid_to_polygon_hexa(gridid, params):
    '''
    Generate the geometry column based on the grid ID.
    The input is the grid ID, the output is the geometry.

    Parameters
    -------
    gridid : Series
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
    gridid = pd.Series(gridid, name='gridid')
    gridid_tmp = gridid.apply(lambda r: r.split(','))
    i = gridid_tmp.apply(lambda r: r[0]).astype(int)
    j = gridid_tmp.apply(lambda r: r[1]).astype(int)
    k = gridid_tmp.apply(lambda r: r[2]).astype(int)
    tmp = pd.concat([pd.DataFrame(np.array([i-1, j-1, k-1, gridid]).T),
                     pd.DataFrame(np.array([i-1, j-1, k, gridid]).T),
                     pd.DataFrame(np.array([i-1, j, k, gridid]).T),
                     pd.DataFrame(np.array([i, j-1, k-1, gridid]).T),
                     pd.DataFrame(np.array([i, j, k-1, gridid]).T),
                     pd.DataFrame(np.array([i, j, k, gridid]).T)])
    tmp.columns = ['loncol_1', 'loncol_2', 'loncol_3', 'gridid']
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
    tmp = merge_polygon(tmp, 'gridid')
    geometry = pd.merge(gridid, tmp)['geometry']
    return geometry


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
    lon, lat,  lon_err, lat_err = decode_exactly(geohash)
    lats = "%.*f" % (max(1, int(round(-np.log10(lat_err)))) - 1, lat)
    lons = "%.*f" % (max(1, int(round(-np.log10(lon_err)))) - 1, lon)
    if '.' in lats:
        lats = lats.rstrip('0')
    if '.' in lons:
        lons = lons.rstrip('0')
    return lons, lats


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
