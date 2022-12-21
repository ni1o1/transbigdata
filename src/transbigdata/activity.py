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
import math

def entropy(sequence):
    '''
    Calculate entropy.

    Parameters
    ----------------
    sequence : List,DataFrame,Series
        sequence data

    Returns
    ----------------
    entropy : Number
    '''
    if not isinstance(sequence,list)|\
        isinstance(sequence,pd.DataFrame)|\
        isinstance(sequence,pd.Series):
        raise TypeError('Sequence must be List,DataFrame,Series') # pragma: no cover
    sequence = pd.DataFrame(sequence)
    r_1 = sequence[0].value_counts().reset_index()
    r_1[0] /= r_1[0].sum()
    entropy = -(r_1[0]*np.log(r_1[0])/np.log(2)).sum()
    return entropy

def entropy_rate(sequence):
    '''
    Calculate entropy rate.
    Reference: Goulet-Langlois, G., Koutsopoulos, H. N., Zhao, Z., & Zhao, J. (2017). Measuring regularity of individual travel patterns. IEEE Transactions on Intelligent Transportation Systems, 19(5), 1583-1592.
    
    Parameters
    ----------------
    sequence : List,DataFrame,Series
        sequence data

    Returns
    ----------------
    entropy_rate : Number
    '''
    if not isinstance(sequence,list)|\
        isinstance(sequence,pd.DataFrame)|\
        isinstance(sequence,pd.Series):
        raise TypeError('Sequence must be List,DataFrame,Series') # pragma: no cover
    sequence = pd.DataFrame(sequence,columns = ['key'])
    #对item编号排序
    sequence = sequence.reindex().reset_index()
    sequence_item = sequence['key'].drop_duplicates().reset_index().rename(columns = {'index':'Id'})
    sequence = pd.merge(sequence,sequence_item).sort_values('index')
    #序列
    sequence = list(sequence['Id'].astype(str))
    #BWT
    sequences = []
    for i in range(len(sequence)):
        sequence_new_1 = sequence[0:i]
        sequence_new_2 = sequence[i:]
        sequence_new = ','.join(sequence_new_2+sequence_new_1)
        sequences.append(sequence_new)
    sequences = sorted(sequences)
    sorted_rotations = [i.split(',')[-1] for i in sequences]

    #对序列分割为多个n**0.5长度的段
    sorted_rotations = pd.DataFrame(sorted_rotations)
    n = len(sorted_rotations)
    sorted_rotations['group'] = range(n)
    sorted_rotations['group'] /= n**0.5
    sorted_rotations['group'] = sorted_rotations['group'].astype(int)
    entropy_rate = sorted_rotations.groupby(['group']).apply(lambda r:entropy(r[0])).mean()
    return entropy_rate


def ellipse_params(data, col=['lon', 'lat'], confidence=95, epsg=None):
    '''
    confidence ellipse parameter estimation for point data

    Parameters
    -------
    data : DataFrame
        point data
    confidence : number
        confidence level: 99，95 or 90
    epsg : number
        If given, the original coordinates are transformed from WGS84 to
        the given EPSG coordinate system for confidence ellipse parameter
        estimation
    col: List
        Column names, [lon，lat]

    Returns
    -------
    params: List
        Centroid ellipse parameters[pos,width,height,theta,area,oblateness]
        Respectively [Center point coordinates, minor axis, major axis,
        angle, area, oblateness]
    '''
    lon, lat = col
    if confidence == 99:
        nstd = 9.210**0.5   # pragma: no cover
    if confidence == 95:
        nstd = 5.991**0.5   # pragma: no cover
    if confidence == 90:
        nstd = 4.605**0.5    # pragma: no cover
    points = data.copy()
    points = gpd.GeoDataFrame(points)
    points['geometry'] = gpd.points_from_xy(points[lon], points[lat])
    if epsg:
        points.crs = {'init': 'epsg:4326'}   # pragma: no cover
        points = points.to_crs(epsg=epsg)   # pragma: no cover
    point_np = np.array([points.geometry.x, points.geometry.y]).T
    pos = point_np.mean(axis=0)
    cov = np.cov(point_np, rowvar=False)
    vals, vecs = np.linalg.eigh(cov)
    theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
    width, height = 2 * nstd * np.sqrt(vals)
    area = width/2*height/2*math.pi
    oblateness = (height-width)/height

    ellip_params = [pos, width, height, theta, area, oblateness]
    return ellip_params


def ellipse_plot(ellip_params, ax, **kwargs):
    '''
    Enter the parameters of the confidence ellipse and plot the confidence
    ellipse

    输入
    -------
    ellip_params : List
        Centroid ellipse parameters[pos,width,height,theta,area,oblateness]
        Respectively[Center point coordinates, minor axis, major axis, angle
        , area, oblateness]

    ax : matplotlib.axes._subplots.AxesSubplot
        Where to plot
    '''
    [pos, width, height, theta, area, alpha] = ellip_params
    from matplotlib.patches import Ellipse
    ellip = Ellipse(xy=pos, width=width, height=height,
                    angle=theta, linestyle='-', **kwargs)
    ax.add_artist(ellip)

def plot_activity(data,
                         col=['stime', 'etime', 'group'],
                         figsize=(10, 5),
                         dpi=250,
                         shuffle=True,
                         xticks_rotation=0,
                         xticks_gap=1,
                         yticks_gap=1,
                         fontsize=12):
    '''
    Plot the activity plot of individual

    Parameters
    ----------------
    data : DataFrame
        activity information of one person
    col : List
        The column name. [starttime,endtime,group] of activities, `group` control the color
    figsize : List
        The figure size
    dpi : Number
        The dpi of the figure
    shuffle : bool
        Whether to shuffle the activity
    xticks_rotation : Number
        rotation angle of xticks
    xticks_gap : Number
        gap of xticks
    yticks_gap : Number
        gap of yticks
    fontsize : Number
        font size of xticks and yticks
    '''
    stime, etime, group = col
    activity = data.copy()
    activity['date'] = activity[stime].dt.date
    dates = list(activity['date'].astype(str).drop_duplicates())
    dates_all = []
    minday = min(dates)
    maxday = max(dates)
    import datetime
    thisdate = minday
    while thisdate != maxday:  # pragma: no cover
        dates_all.append(thisdate)  # pragma: no cover
        thisdate = str((pd.to_datetime(thisdate+' 00:00:00') +  # pragma: no cover
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
    activityinfo = pd.DataFrame(activity[group].drop_duplicates().sort_values())
    indexs = list(range(1, len(activityinfo)+1))
    if shuffle:
        np.random.shuffle(indexs)
    activityinfo['index'] = indexs
    import matplotlib as mpl
    norm = mpl.colors.Normalize(vmin=1, vmax=len(activityinfo)+1)
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
                                (activityinfo[group] == bars[group].
                                 iloc[row]) 
                            ]['index'].iloc[0])))
    plt.xlim(-0.5, len(dates))
    plt.ylim(0, 24*3600)
    xticks_dates = range(0, len(dates), xticks_gap)
    plt.xticks(xticks_dates, [dates[i][-5:] for i in xticks_dates],
               rotation=xticks_rotation, fontsize=fontsize)

    plt.yticks(range(0, 24*3600+1, yticks_gap*3600),
               pd.DataFrame({'t': range(0, 25, yticks_gap)})[
        't'].astype('str')+':00',
        fontsize=fontsize)
    plt.show()

'''Old namespace'''

mobile_plot_activity = plot_activity
