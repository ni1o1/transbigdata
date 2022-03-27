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
from .grids import GPS_to_grids
from .preprocess import id_reindex, clean_same


def plot_activity(data, col=['stime', 'etime', 'LONCOL', 'LATCOL'],
                  figsize=(10, 5), dpi=250):
    '''
    Plot the activity plot of individual

    Parameters
    ----------------
    data : DataFrame
        activity information of one person
    col : List
        The column name.[starttime,endtime,LONCOL,LATCOL] of activities
    '''
    stime, etime, LONCOL, LATCOL = col
    activity = data.copy()
    activity['date'] = activity[stime].dt.date
    dates = list(activity['date'].astype(str).drop_duplicates())
    dates_all = []
    minday = min(dates)
    maxday = max(dates)
    import datetime
    thisdate = minday
    while thisdate != maxday:
        dates_all.append(thisdate)
        thisdate = str((pd.to_datetime(thisdate+' 00:00:00') +
                       datetime.timedelta(days=1)).date())
    dates = dates_all
    import matplotlib.pyplot as plt
    import numpy as np
    activity['duration'] = (activity[etime]-activity[stime]).dt.total_seconds()
    activity = activity[-activity['duration'].isnull()]
    import time
    activity['ststmp'] = activity[stime].astype(str).apply(
        lambda x: time.mktime(
            time.strptime(x, '%Y-%m-%d %H:%M:%S'))).astype('int64')
    activity['etstmp'] = activity[etime].astype(str).apply(
        lambda x: time.mktime(
            time.strptime(x, '%Y-%m-%d %H:%M:%S'))).astype('int64')
    activityinfo = activity[[LONCOL, LATCOL]].drop_duplicates()
    indexs = list(range(1, len(activityinfo)+1))
    np.random.shuffle(indexs)
    activityinfo['index'] = indexs
    import matplotlib as mpl
    norm = mpl.colors.Normalize(vmin=0, vmax=len(activityinfo))
    from matplotlib.colors import ListedColormap
    import seaborn as sns
    cmap = ListedColormap(sns.hls_palette(
        n_colors=len(activityinfo), l=.5, s=0.8))
    plt.figure(1, figsize, dpi)
    ax = plt.subplot(111)
    plt.sca(ax)
    for day in range(len(dates)):
        plt.bar(day, height=24*3600, bottom=0, width=0.4, color=(0, 0, 0, 0.1))
        stime = dates[day]+' 00:00:00'
        etime = dates[day]+' 23:59:59'
        bars = activity[(activity['stime'] < etime) &
                        (activity['etime'] > stime)].copy()
        bars['ststmp'] = bars['ststmp'] - \
            time.mktime(time.strptime(stime, '%Y-%m-%d %H:%M:%S'))
        bars['etstmp'] = bars['etstmp'] - \
            time.mktime(time.strptime(stime, '%Y-%m-%d %H:%M:%S'))
        for row in range(len(bars)):
            plt.bar(day,
                    height=bars['etstmp'].iloc[row]-bars['ststmp'].iloc[row],
                    bottom=bars['ststmp'].iloc[row],
                    color=cmap(
                        norm(
                            activityinfo[
                                (activityinfo[LONCOL] == bars[LONCOL].
                                 iloc[row]) &
                                (activityinfo[LATCOL] ==
                                 bars[LATCOL].iloc[row])
                            ]['index'].iloc[0])))
    plt.xlim(-0.5, len(dates))
    plt.ylim(0, 24*3600)
    plt.xticks(range(len(dates)), [i[-5:] for i in dates])
    plt.yticks(range(0, 24*3600+1, 3600),
               pd.DataFrame({'t': range(0, 25)})['t'].astype('str')+':00')
    plt.show()


def traj_stay_move(data, params,
                   col=['ID', 'dataTime', 'longitude', 'latitude'],
                   activitytime=1800):
    '''
    Input trajectory data and gridding parameters, identify stay and move

    Parameters
    ----------------
    data : DataFrame
        trajectory data
    params : List
        gridding parameters
    col : List
        The column name, in the order of ['ID','dataTime','longitude',
        'latitude']
    activitytime : Number
        How much time to regard as activity

    Returns
    ----------------
    stay : DataFrame
        stay information
    move : DataFrame
        move information
    '''
    uid, timecol, lon, lat = col
    trajdata = data.copy()
    trajdata[timecol] = pd.to_datetime(trajdata[timecol])
    trajdata['LONCOL'], trajdata['LATCOL'] = GPS_to_grids(
        trajdata[lon], trajdata[lat], params)
    trajdata = clean_same(trajdata, col=[uid, timecol, 'LONCOL', 'LATCOL'])
    trajdata['stime'] = trajdata[timecol]
    trajdata['etime'] = trajdata[timecol].shift(-1)
    trajdata[uid+'_next'] = trajdata[uid].shift(-1)
    trajdata = trajdata[trajdata[uid+'_next'] == trajdata[uid]]
    trajdata['duration'] = (
        trajdata['etime'] - trajdata['stime']).dt.total_seconds()
    activity = trajdata[[uid, lon, lat, 'stime',
                         'etime', 'duration', 'LONCOL', 'LATCOL']]
    activity = activity[activity['duration'] >= activitytime].rename(
        columns={lon: 'lon', lat: 'lat'})
    stay = activity.copy()
    activity['stime_next'] = activity['stime'].shift(-1)
    activity['elon'] = activity['lon'].shift(-1)
    activity['elat'] = activity['lat'].shift(-1)
    activity['ELONCOL'] = activity['LONCOL'].shift(-1)
    activity['ELATCOL'] = activity['LATCOL'].shift(-1)
    activity[uid+'_next'] = activity[uid].shift(-1)
    activity = activity[activity[uid+'_next'] == activity[uid]
                        ].drop(['stime', 'duration', uid+'_next'], axis=1)
    activity = activity.rename(columns={'lon': 'slon',
                                        'lat': 'slat',
                                        'etime': 'stime',
                                        'stime_next': 'etime',
                                        'LONCOL': 'SLONCOL',
                                        'LATCOL': 'SLATCOL',
                                        })
    activity['duration'] = (
        activity['etime'] - activity['stime']).dt.total_seconds()
    move = activity.copy()
    return stay, move


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
                geometry.append(None)
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
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return super(NpEncoder, self).default(obj)
    f = open(path, mode='w')
    json.dump(data, f, cls=NpEncoder)
    f.close()
