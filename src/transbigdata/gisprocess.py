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

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
import itertools
from operator import itemgetter
import geopandas as gpd
import math
from .coordinates import getdistance


def ckdnearest(dfA_origin,
               dfB_origin,
               Aname=['lon', 'lat'],
               Bname=['lon', 'lat']):
    '''
    Search the nearest points in dfB_origin for dfA_origin,
    and calculate the distance

    Parameters
    -------
    dfA_origin : DataFrame
        DataFrame A
    dfB_origin : DataFrame
        DataFrame B
    Aname : List
        The column of lng and lat in DataFrame A
    Bname : List
        The column of lng and lat in DataFrame A

    Returns
    -------
    gdf : DataFrame
        The output DataFrame
    '''
    if len(dfA_origin) == 0:
        raise Exception('The input DataFrame dfA is empty')
    if len(dfB_origin) == 0:
        raise Exception('The input DataFrame dfB is empty')
    gdA = dfA_origin.copy()
    gdB = dfB_origin.copy()
    from scipy.spatial import cKDTree
    btree = cKDTree(gdB[Bname].values)
    dist, idx = btree.query(gdA[Aname].values, k=1)
    gdA['index'] = idx
    gdB['index'] = range(len(gdB))
    gdf = pd.merge(gdA, gdB, on='index')
    if (Aname[0] == Bname[0]) & (Aname[1] == Bname[1]):
        gdf['dist'] = getdistance(
            gdf[Aname[0]+'_x'],
            gdf[Aname[1]+'_y'],
            gdf[Bname[0]+'_x'],
            gdf[Bname[1]+'_y'])
    else:
        gdf['dist'] = getdistance(
            gdf[Aname[0]],
            gdf[Aname[1]],
            gdf[Bname[0]],
            gdf[Bname[1]])
    return gdf


def ckdnearest_point(gdA, gdB):
    '''
    This method will match the nearest points in gdfB to gdfA,
    and add a new column called dist

    Parameters
    -------
    gdA : GeoDataFrame
        GeoDataFrame A, point geometry

    gdB : GeoDataFrame
        GeoDataFrame B, point geometry

    Returns
    -------
    gdf : DataFrame
        The output DataFrame
    '''
    if len(gdA) == 0:
        raise Exception('The input GeoDataFrame gdfA is empty')
    if len(gdB) == 0:
        raise Exception('The input GeoDataFrame gdfB is empty')
    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdA['dist'] = dist
    gdA['index'] = idx
    gdB['index'] = range(len(gdB))
    gdf = pd.merge(gdA, gdB, on='index')
    return gdf


def ckdnearest_line(gdfA, gdfB):
    '''
    This method will seach from gdfB to find the nearest line to
    the point in gdfA.

    Parameters
    -------
    gdA : GeoDataFrame
        GeoDataFrame A, point geometry

    gdB : GeoDataFrame
        GeoDataFrame B, linestring geometry

    Returns
    -------
    gdf : DataFrame
        Searching the nearset linestring in gdfB for the point in gdfA
    '''
    if len(gdfA) == 0:
        raise Exception('The input GeoDataFrame gdfA is empty')
    if len(gdfB) == 0:
        raise Exception('The input GeoDataFrame gdfB is empty')
    A = np.concatenate(
        [np.array(geom.coords) for geom in gdfA.geometry.to_list()])
    B = [np.array(geom.coords) for geom in gdfB.geometry.to_list()]
    B_ix = tuple(itertools.chain.from_iterable(
        [itertools.repeat(i, x) for i, x in enumerate(list(map(len, B)))]))
    B = np.concatenate(B)
    ckd_tree = cKDTree(B)
    dist, idx = ckd_tree.query(A, k=1)
    idx = itemgetter(*idx)(B_ix)
    gdfA['dist'] = dist
    gdfA['index'] = idx
    gdfB['index'] = range(len(gdfB))
    gdf = pd.merge(gdfA, gdfB, on='index')
    return gdf


def splitline_with_length(Centerline, maxlength=100):
    '''
    The intput is the linestring GeoDataFrame. The splited line’s
    length wull be no longer than maxlength

    Parameters
    -------
    Centerline : GeoDataFrame
        Linestring geometry
    maxlength : number
        The maximum length of the splited line

    Returns
    -------
    splitedline : GeoDataFrame
        Splited line
    '''
    def splitline(route, maxlength):
        routelength = route.length
        from shapely.geometry import LineString
        lss = []
        for k in range(int(routelength/maxlength)+1):
            if k == int(routelength/maxlength):
                lm = routelength
            else:
                lm = (k+1)*maxlength
            a = np.linspace(k*maxlength, lm, 10)
            ls = []
            for line in a:
                ls.append(route.interpolate(line))
            lss.append(LineString(ls))
        lss = gpd.GeoDataFrame(lss, columns=['geometry'])
        return lss
    lsss = []
    for i in range(len(Centerline)):
        route = Centerline['geometry'].iloc[i]
        lss = splitline(route, maxlength)
        lss['id'] = i
        lsss.append(lss)
    lsss = pd.concat(lsss)
    lsss['length'] = lsss.length
    splitedline = lsss
    return splitedline


def merge_polygon(data, col):
    '''
    The input is the GeoDataFrame of polygon geometry, and the col
    name. This function will merge the polygon based on the category
    in the mentioned column

    Parameters
    -------
    data : GeoDataFrame
        The polygon geometry
    col : str
        The column name for indicating category

    Returns
    -------
    data1 : GeoDataFrame
        The merged polygon
    '''
    groupnames = []
    geometries = []
    for i in data[col].drop_duplicates():
        groupnames.append(i)
        geometries.append(data[data[col] == i].unary_union)
    data1 = gpd.GeoDataFrame()
    data1['geometry'] = geometries
    data1[col] = groupnames
    return data1


def polyon_exterior(data, minarea=0):
    '''
    The input is the GeoDataFrame of the polygon geometry. The method
    will construct new polygon by extending the outer boundary of the
    ploygon

    Parameters
    -------
    data : GeoDataFrame
        The polygon geometry
    minarea : number
        The minimum area. Polygon of less area will be removed

    Returns
    -------
    data1 : GeoDataFrame
        The processed polygon
    '''
    data1 = data.copy()

    def polyexterior(p):
        from shapely.geometry import Polygon, MultiPolygon
        if type(p) == MultiPolygon:
            geometries = []
            for i in p:
                poly = Polygon(i.exterior)
                if minarea > 0:
                    if poly.area > minarea:
                        geometries.append(poly)
                else:
                    geometries.append(poly)
            return MultiPolygon(geometries)
        if type(p) == Polygon:
            return Polygon(p.exterior)
    data1['geometry'] = data1['geometry'].apply(lambda r: polyexterior(r))
    data1 = data1[-data1['geometry'].is_empty]
    return data1


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
        nstd = 9.210**0.5
    if confidence == 95:
        nstd = 5.991**0.5
    if confidence == 90:
        nstd = 4.605**0.5
    points = data.copy()
    points = gpd.GeoDataFrame(points)
    points['geometry'] = gpd.points_from_xy(points[lon], points[lat])
    if epsg:
        points.crs = {'init': 'epsg:4326'}
        points = points.to_crs(epsg=epsg)
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
