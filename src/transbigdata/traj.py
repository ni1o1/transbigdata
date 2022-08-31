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
import numpy as np
from .preprocess import id_reindex


def traj_densify(data, col=['Vehicleid', 'Time', 'Lng', 'Lat'], timegap=15):
    '''
    Trajectory densification, ensure that there is a trajectory point each
    timegap seconds

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        The column name, in the sequence of [Vehicleid, Time, lng, lat]
    timegap : number
        The sampling interval (second)

    Returns
    -------
    data1 : DataFrame
        The processed data
    '''
    Vehicleid, Time, Lng, Lat = col
    data[Time] = pd.to_datetime(data[Time])
    data1 = data.copy()
    data1 = data1.drop_duplicates([Vehicleid, Time])
    data1 = id_reindex(data1, Vehicleid)
    data1 = data1.sort_values(by=[Vehicleid+'_new', Time])
    data1['utctime'] = data1[Time].apply(lambda r: int(r.value/1000000000))
    data1['utctime_new'] = data1[Vehicleid+'_new']*10000000000+data1['utctime']
    a = data1.groupby([Vehicleid+'_new']
                      )['utctime'].min().rename('mintime').reset_index()
    b = data1.groupby([Vehicleid+'_new']
                      )['utctime'].max().rename('maxtime').reset_index()
    minmaxtime = pd.merge(a, b)
    mintime = data1['utctime'].min()
    maxtime = data1['utctime'].max()
    timedata = pd.DataFrame(range(mintime, maxtime, timegap), columns=[Time])
    timedata['tmp'] = 1
    minmaxtime['tmp'] = 1
    minmaxtime = pd.merge(minmaxtime, timedata)
    minmaxtime = minmaxtime[(minmaxtime['mintime'] <= minmaxtime[Time]) & (
        minmaxtime['maxtime'] >= minmaxtime[Time])]
    minmaxtime['utctime_new'] = minmaxtime[Vehicleid+'_new'] * \
        10000000000+minmaxtime[Time]
    minmaxtime[Time] = pd.to_datetime(minmaxtime[Time], unit='s')
    data1 = pd.concat([data1, minmaxtime[['utctime_new', Time]]]
                      ).sort_values(by=['utctime_new'])
    data1 = data1.drop_duplicates(['utctime_new'])
    data1[Lng] = data1.set_index('utctime_new')[
        Lng].interpolate(method='index').values
    data1[Lat] = data1.set_index('utctime_new')[
        Lat].interpolate(method='index').values
    data1[Vehicleid] = data1[Vehicleid].ffill()
    data1[Vehicleid] = data1[Vehicleid].bfill()
    data1 = data1.drop([Vehicleid+'_new', 'utctime', 'utctime_new'], axis=1)
    return data1


def traj_sparsify(data, col=['Vehicleid', 'Time', 'Lng', 'Lat'], timegap=15,
                  method='subsample'):
    '''
    Trajectory sparsify. When the sampling frequency of trajectory data is too
    high, the amount of data is too large, which is not convenient for the
    analysis of some studies that require less data frequency. This function
    can expand the sampling interval and reduce the amount of data.

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        The column name, in the sequence of [Vehicleid, Time, lng, lat]
    timegap : number
        Time gap between trajectory point
    method : str
        'interpolate' or 'subsample'

    Returns
    -------
    data1 : DataFrame
        Sparsified trajectory data
    '''
    Vehicleid, Time, Lng, Lat = col
    data[Time] = pd.to_datetime(data[Time], unit='s')
    data1 = data.copy()
    data1 = data1.drop_duplicates([Vehicleid, Time])
    data1 = id_reindex(data1, Vehicleid)
    data1 = data1.sort_values(by=[Vehicleid+'_new', Time])
    data1['utctime'] = data1[Time].apply(lambda r: int(r.value/1000000000))
    data1['utctime_new'] = data1[Vehicleid+'_new']*10000000000+data1['utctime']
    if method == 'interpolate':
        a = data1.groupby([Vehicleid+'_new']
                          )['utctime'].min().rename('mintime').reset_index()
        b = data1.groupby([Vehicleid+'_new']
                          )['utctime'].max().rename('maxtime').reset_index()
        minmaxtime = pd.merge(a, b)
        mintime = data1['utctime'].min()
        maxtime = data1['utctime'].max()
        timedata = pd.DataFrame(
            range(mintime, maxtime, timegap), columns=[Time])
        timedata['tmp'] = 1
        minmaxtime['tmp'] = 1
        minmaxtime = pd.merge(minmaxtime, timedata)
        minmaxtime = minmaxtime[(minmaxtime['mintime'] <= minmaxtime[Time]) & (
            minmaxtime['maxtime'] >= minmaxtime[Time])]
        minmaxtime['utctime_new'] = minmaxtime[Vehicleid+'_new'] * \
            10000000000+minmaxtime[Time]
        minmaxtime[Time] = pd.to_datetime(minmaxtime[Time], unit='s')
        data1 = pd.concat([
            data1, minmaxtime[['utctime_new', Time]]
        ]).sort_values(by=['utctime_new'])
        data1 = data1.drop_duplicates(['utctime_new'])
        data1[Lng] = data1.set_index('utctime_new')[
            Lng].interpolate(method='index').values
        data1[Lat] = data1.set_index('utctime_new')[
            Lat].interpolate(method='index').values
        data1[Vehicleid] = data1[Vehicleid].ffill()
        data1[Vehicleid] = data1[Vehicleid].bfill()
        data1 = pd.merge(minmaxtime['utctime_new'], data1)
        data1 = data1.drop(
            [Vehicleid+'_new', 'utctime', 'utctime_new'], axis=1)
    if method == 'subsample':
        data1['utctime_new'] = (data1['utctime_new']/timegap).astype(int)
        data1 = data1.drop_duplicates(subset=['utctime_new'])
        data1 = data1.drop(
            [Vehicleid+'_new', 'utctime', 'utctime_new'], axis=1)
    return data1


def points_to_traj(traj_points, col=['Lng', 'Lat', 'ID'], timecol=None):
    '''
    Input trajectory, generate GeoDataFrame

    Parameters
    -------
    traj_points : DataFrame
        trajectory data
    col : List
        The column name, in the sequence of [lng, lat,trajectoryid]
    timecol : str(Optional)
        Optional, the column name of the time column. If given, the geojson
        with [longitude, latitude, altitude, time] in returns can be put into
        the Kepler to visualize the trajectory

    Returns
    -------
    traj : GeoDataFrame
        Generated trajectory
    '''
    [Lng, Lat, ID] = col
    if timecol:
        geometry = []
        traj_id = []
        for i in traj_points[ID].drop_duplicates():
            coords = traj_points[traj_points[ID] == i][[Lng, Lat, timecol]]
            coords[timecol] = coords[timecol].apply(
                lambda r: int(r.value/1000000000))
            coords['altitude'] = 0
            coords = coords[[Lng, Lat, 'altitude', timecol]].values.tolist()
            traj_id.append(i)
            if len(coords) >= 2:
                geometry.append({
                    "type": "Feature",
                    "properties": {"ID":  i},
                    "geometry": {"type": "LineString",
                                 "coordinates": coords}})
        traj = {"type": "FeatureCollection",
                "features": geometry}
    else:
        traj = gpd.GeoDataFrame()
        from shapely.geometry import LineString
        geometry = []
        traj_id = []
        for i in traj_points[ID].drop_duplicates():
            coords = traj_points[traj_points[ID] == i][[Lng, Lat]].values
            traj_id.append(i)
            if len(coords) >= 2:
                geometry.append(LineString(coords))
            else:
                geometry.append(None) # pragma: no cover
        traj[ID] = traj_id
        traj['geometry'] = geometry
        traj = gpd.GeoDataFrame(traj)
    return traj


def dumpjson(data, path):
    '''
    Input the json data and save it as a file. This method is suitable for
    sovling the problem that numpy cannot be compatiable with json package.

    Parameters
    -------
    data : json
        The json data to be saved


    path : str
        The storage path

    '''
    import json

    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)  # pragma: no cover
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return super(NpEncoder, self).default(obj)  # pragma: no cover
    f = open(path, mode='w')
    json.dump(data, f, cls=NpEncoder)
    f.close()
