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
from .grids import (
    grid_params,
    GPS_to_grids,
    grids_centre,
    gridid_to_polygon
)
from .coordinates import getdistance


def clean_same(data, col=['VehicleNum', 'Time', 'Lng', 'Lat']):
    '''
    Delete the data with the same information as the data before and
    after to reduce the amount of data. For example, if several consecutive
    data of an individual have the same information except for the time,
    only the first and last two data can be kept

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        The column name, in the order of [‘Vehicleid, Time’]. It will sort
        by time, and then determine the information of other columns besides
        the time

    Returns
    -------
    data1 : DataFrame
        Cleaned data
    '''
    [VehicleNum, Time, Lng, Lat] = col[:4]
    extra = col[4:]
    data1 = data.copy()
    data1 = data1.drop_duplicates(subset=[VehicleNum, Time])
    data1 = data1.sort_values(by=[VehicleNum, Time])
    data1['issame'] = 0
    for i in [VehicleNum, Lng, Lat]+extra:
        data1['issame'] += (data1[i].shift() == data1[i]
                            ) & (data1[i].shift(-1) == data1[i])
    data1 = data1[-(data1['issame'] == len([VehicleNum, Lng, Lat]+extra))]
    data1 = data1.drop('issame', axis=1)
    return data1


def clean_drift(data, col=['VehicleNum', 'Time', 'Lng', 'Lat'],
                speedlimit=80, dislimit=1000):
    '''
    Delete the drift data. The select principle is that: if the speed of a
    trajectory point is larger than the speed limit with before and after
    points, while the speed between the before and after data is less than
    the speedlimit. The time column in the input data is calculated more
    efficiently if it is in datetime format.

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        Column names, in the order of [‘VehicleNum’, ‘Time’, ‘Lng’, ‘Lat’]
    speedlimit : number
        Speed limitation

    Returns
    -------
    data1 : DataFrame
        Cleaned data
    '''
    [VehicleNum, Time, Lng, Lat] = col
    data1 = data.copy()
    data1 = data1.drop_duplicates(subset=[VehicleNum, Time])
    data1[Time+'_dt'] = pd.to_datetime(data1[Time])
    data1 = data1.sort_values(by=[VehicleNum, Time])
    for i in [VehicleNum, Lng, Lat, Time+'_dt']:
        data1[i+'_pre'] = data1[i].shift()
        data1[i+'_next'] = data1[i].shift(-1)
    data1['dis_pre'] = getdistance(
        data1[Lng],
        data1[Lat],
        data1[Lng+'_pre'],
        data1[Lat+'_pre'])
    data1['dis_next'] = getdistance(
        data1[Lng],
        data1[Lat],
        data1[Lng+'_next'],
        data1[Lat+'_next'])
    data1['dis_prenext'] = getdistance(
        data1[Lng+'_pre'],
        data1[Lat+'_pre'],
        data1[Lng+'_next'],
        data1[Lat+'_next'])
    data1['timegap_pre'] = data1[Time+'_dt'] - data1[Time+'_dt_pre']
    data1['timegap_next'] = data1[Time+'_dt_next'] - data1[Time+'_dt']
    data1['timegap_prenext'] = data1[Time+'_dt_next'] - data1[Time+'_dt_pre']
    data1['speed_pre'] = data1['dis_pre'] / \
        data1['timegap_pre'].dt.total_seconds()*3.6
    data1['speed_next'] = data1['dis_next'] / \
        data1['timegap_next'].dt.total_seconds()*3.6
    data1['speed_prenext'] = data1['dis_prenext'] / \
        data1['timegap_prenext'].dt.total_seconds()*3.6
    if speedlimit:
        data1 = data1[
            -((data1[VehicleNum+'_pre'] == data1[VehicleNum]) &
              (data1[VehicleNum+'_next'] == data1[VehicleNum]) &
                (data1['speed_pre'] > speedlimit) &
              (data1['speed_next'] > speedlimit) &
              (data1['speed_prenext'] < speedlimit))]
    if dislimit:
        data1 = data1[
            -((data1[VehicleNum+'_pre'] == data1[VehicleNum]) &
              (data1[VehicleNum+'_next'] == data1[VehicleNum]) &
              (data1['dis_pre'] > dislimit) &
              (data1['dis_next'] > dislimit) &
              (data1['dis_prenext'] < dislimit))]
    data1 = data1[data.columns]
    return data1


def clean_outofbounds(data, bounds, col=['Lng', 'Lat']):
    '''
    The input is the latitude and longitude coordinates of the lower
    left and upper right of the study area and exclude data that are
    outside the study area

    Parameters
    -------
    data : DataFrame
        Data
    bounds : List
        Latitude and longitude of the lower left and upper right of
        the study area, in the order of [lon1, lat1, lon2, lat2]
    col : List
        Column name of longitude and latitude

    Returns
    -------
    data1 : DataFrame
        Data within the scope of the study
    '''
    lon1, lat1, lon2, lat2 = bounds
    if (lon1 > lon2) | (lat1 > lat2) | (abs(lat1) > 90) | (
            abs(lon1) > 180) | (abs(lat2) > 90) | (abs(lon2) > 180):
        raise Exception(
            'Bounds error. The input bounds should be in the order \
of [lon1,lat1,lon2,lat2]. (lon1,lat1) is the lower left corner and \
(lon2,lat2) is the upper right corner.')
    Lng, Lat = col
    data1 = data.copy()
    data1 = data1[(data1[Lng] > bounds[0]) & (data1[Lng] < bounds[2]) & (
        data1[Lat] > bounds[1]) & (data1[Lat] < bounds[3])]
    return data1


def clean_outofshape(data, shape, col=['Lng', 'Lat'], accuracy=500):
    '''
    Input the GeoDataFrame of the study area and exclude the data beyond
    the study area

    Parameters
    -------
    data : DataFrame
        Data
    shape : GeoDataFrame
        The GeoDataFrame of the study area
    col : List
        Column name of longitude and latitude
    accuracy : number
        The size of grid. The principle is to do the data gridding first
        and then do the data cleaning. The smaller the size is, the higher
        accuracy it has

    Returns
    -------
    data1 : DataFrame
        Data within the scope of the study
    '''
    Lng, Lat = col
    shape_unary = shape.unary_union
    bounds = shape_unary.bounds
    params = grid_params(bounds, accuracy)
    data1 = data.copy()
    data1['LONCOL'], data1['LATCOL'] = GPS_to_grids(
        data1[Lng], data1[Lat], params)
    data1_gdf = data1[['LONCOL', 'LATCOL']].drop_duplicates()
    data1_gdf['geometry'] = gridid_to_polygon(
        data1_gdf['LONCOL'], data1_gdf['LATCOL'], params)
    data1_gdf = gpd.GeoDataFrame(data1_gdf)
    data1_gdf = data1_gdf[data1_gdf.intersects(shape_unary)]
    data1 = pd.merge(data1, data1_gdf[['LONCOL', 'LATCOL']]).drop(
        ['LONCOL', 'LATCOL'], axis=1)
    return data1


def clean_traj(data, col=['uid', 'str_time', 'lon', 'lat'], tripgap=1800,
               disgap=50000, speedlimit=80):
    '''
    A combo for trajectory data cleaning, including defining the the time
    length threshold considered as a new trip, and the distance threshold
    considered as a new trip

    Parameters
    -------
    data : DataFrame
        Trajectory data
    col : List
        Column names, in the order of [‘VehicleNum’, ‘Time’, ‘Lng’, ‘Lat’]
    tripgap : number
        The time length threshold considered as a new trip
    disgap : number
        The distance threshold considered as a new trip
    speedlimit : number
        Speed limit

    Returns
    -------
    data1 : DataFrame
        Cleaned data
    '''
    uid, timecol, lon, lat = col
    data[timecol] = pd.to_datetime(data[timecol])
    data = data.sort_values(by=[uid, timecol])
    cols = []
    for i in data.columns:
        if i not in [uid, timecol, lon, lat]:
            cols.append(i)
    data = clean_same(data, col=[uid, timecol, lon, lat]+cols)
    data = clean_drift(data, col=[uid, timecol, lon, lat],
                       speedlimit=speedlimit)
    data = id_reindex(data, uid, timecol=timecol, timegap=tripgap)
    data = data.rename(columns={uid+'_new': 'tripid'})
    data = id_reindex_disgap(
        data, col=['tripid', lon, lat], disgap=disgap, suffix='')
    data1 = data.copy()
    data1['lon1'] = data1[lon].shift(-1)
    data1['lat1'] = data1[lat].shift(-1)
    data1['tripid1'] = data1['tripid'].shift(-1)
    data1 = data1[data1['tripid'] == data1['tripid1']]
    data1['dis'] = getdistance(
        data1[lon], data1[lat], data1['lon1'], data1['lat1'])
    a = data1.groupby(['tripid'])['dis'].sum()
    a = a[-(a < 50)].reset_index()['tripid']
    data = pd.merge(data, a)
    data = data.drop('tripid', axis=1)
    data = id_reindex(data, uid, timecol=timecol, timegap=tripgap)
    data = data.rename(columns={uid+'_new': 'tripid'})
    data = id_reindex_disgap(
        data, col=['tripid', lon, lat], disgap=disgap, suffix='')
    return data


def dataagg(data, shape, col=['Lng', 'Lat', 'count'], accuracy=500):
    '''
    Aggregate data to traffic zone

    Parameters
    -------
    data : DataFrame
        The origin DataFrame
    shape : GeoDataFrame
        The shape of the traffic zone
    col : List
        You can either choose to input two columns, i.e., [‘Lng’,’Lat’], or
        to input three columns, i.e., [‘Lng’,’Lat’,’count’]”, where count
        means the points count
    accuracy : number
        The idea is to first implement data gridding and then the aggregation.
        Here, the grid size will be determined. The less the size is, the
        higher the accuracy will have.

    Returns
    -------
    aggresult : GeoDataFrame
        Traffic zone. The count column is the output result
    data1 : DataFrame
        The zone-matched data
    '''
    if len(col) == 2:
        Lng, Lat = col
        aggcol = None
    else:
        Lng, Lat, aggcol = col
    shape['index'] = range(len(shape))
    shape_unary = shape.unary_union
    bounds = shape_unary.bounds
    params = grid_params(bounds, accuracy)
    data1 = data.copy()
    data1['LONCOL'], data1['LATCOL'] = GPS_to_grids(
        data1[Lng], data1[Lat], params)
    data1_gdf = data1[['LONCOL', 'LATCOL']].drop_duplicates()
    data1_gdf['geometry'] = gpd.points_from_xy(
        *grids_centre(data1_gdf['LONCOL'], data1_gdf['LATCOL'], params))
    data1_gdf = gpd.GeoDataFrame(data1_gdf)
    data1_gdf = gpd.sjoin(data1_gdf, shape, how='left')
    data1 = pd.merge(data1, data1_gdf).drop(['LONCOL', 'LATCOL'], axis=1)
    if aggcol:
        aggresult = pd.merge(shape, data1.groupby('index')[
                             aggcol].sum().reset_index()).drop('index', axis=1)
    else:
        data1['_'] = 1
        aggresult = pd.merge(shape, data1.groupby('index')['_'].sum().rename(
            'count').reset_index()).drop('index', axis=1)
        data1 = data1.drop('_', axis=1)
    data1 = data1.drop('index', axis=1)
    return aggresult, data1


def id_reindex_disgap(data, col=['uid', 'lon', 'lat'], disgap=1000,
                      suffix='_new'):
    '''
    Renumber the ID columns of the data，If two adjacent records exceed the
    distance, the number is the new ID

    Parameters
    -------
    data : DataFrame
        Data
    col : str
        Name of the ID column to be re-indexed
    disgap : number
        If two adjacent records exceed this distance, the number is the
        new ID
    suffix : str
        The suffix of the new column. When set to False, the former column
        will be replaced

    Returns
    -------
    data1 : DataFrame
        Renumbered data
    '''
    uid, lon, lat = col
    data1 = data.copy()
    data1[uid+suffix] = (
        (data1[uid].shift() != data1[uid]) |
        (getdistance(data1[lon],
                     data1[lat],
                     data1[lon].shift(),
                     data1[lat].shift()) > disgap)).astype(int).cumsum()-1
    a = data1.groupby([uid+suffix])[lon].count()
    data1 = pd.merge(data1, a[a > 1].reset_index()[[uid+suffix]])
    return data1


def id_reindex(data, col, new=False, timegap=None, timecol=None,
               suffix='_new', sample=None):
    '''
    Renumber the ID columns of the data

    Parameters
    -------
    data : DataFrame
        Data
    col : str
        Name of the ID column to be re-indexed
    new : bool
        False: the new number of the same ID will be the same index;
        True: according to the order of the table, the origin ID appears
        again with different index
    timegap : number
        If an individual does not appear for a period of time (timegap is
        the time threshold), it is numbered as a new individual. This parameter
        should be set with timecol to take effect.
    timecol : str
        The column name of time, it should be set with timegap to take effect
    suffix : str
        The suffix of the new column. When set to False, the former column will
        be replaced
    sample : int (optional)
        To desampling the data

    Returns
    -------
    data1 : DataFrame
        Renumbered data
    '''
    if not suffix:
        suffix = ''
    data1 = data.copy()
    if new:
        data1[col+suffix] = data1[col] != data1[col].shift()
        data1[col+suffix] = data1[col+suffix].cumsum()-1
    else:
        tmp = data1[[col]].drop_duplicates()
        tmp[col+'_'] = range(len(tmp))
        data1 = pd.merge(data1, tmp, on=col)
        data1[col+suffix] = data1[col+'_']
        if suffix != '_':
            data1 = data1.drop(col+'_', axis=1)
    if (timegap is not None) & (timecol is not None):
        data1[timecol] = pd.to_datetime(data1[timecol])
        data1 = data1.sort_values(by=[col+suffix, timecol])
        data1[col+suffix] = (
            (data1[col+suffix].shift() != data1[col+suffix]) |
            ((data1[timecol]-data1[timecol].shift()).dt.total_seconds()
             > timegap)).astype(int).cumsum()-1

    if sample:
        tmp = data1[col+suffix].drop_duplicates().sample(sample)
        data1 = pd.merge(data1, tmp)
    return data1
