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