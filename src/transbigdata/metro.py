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
from shapely.geometry import LineString


def split_subwayline(line, stop):
    '''
    To slice the metro line with metro stations to obtain metro section
    information (This step is useful in subway passenger flow visualization)

    Parameters
    -------
    line : GeoDataFrame
        Bus/metro lines
    stop : GeoDataFrame
        Bus/metro stations

    Returns
    -------
    metro_line_splited : GeoDataFrame
        Generated section line shape
    '''
    def getline(r2, line_geometry):
        ls = []
        if r2['o_project'] <= r2['d_project']:
            tmp1 = np.linspace(r2['o_project'], r2['d_project'], 10)
        if r2['o_project'] > r2['d_project']:
            tmp1 = np.linspace( # pragma: no cover
                r2['o_project']-line_geometry.length, r2['d_project'], 10)
            tmp1[tmp1 < 0] = tmp1[tmp1 < 0]+line_geometry.length # pragma: no cover
        for j in tmp1:
            ls.append(line_geometry.interpolate(j))
        return LineString(ls)
    lss = []
    for k in range(len(line)):
        r = line.iloc[k]
        line_geometry = r['geometry']
        tmp = stop[stop['linename'] == r['linename']].copy()
        for i in tmp.columns:
            tmp[i+'1'] = tmp[i].shift(-1)
        tmp = tmp.iloc[:-1]
        tmp = tmp[['stationnames', 'stationnames1',
                   'geometry', 'geometry1', 'linename', 'line']]
        tmp['o_project'] = tmp['geometry'].apply(
            r['geometry'].project)
        tmp['d_project'] = tmp['geometry1'].apply(
            r['geometry'].project)
        tmp['geometry'] = tmp.apply(
            lambda r2: getline(r2, line_geometry), axis=1)
        lss.append(tmp)
    metro_line_splited = pd.concat(lss).drop('geometry1', axis=1)
    metro_line_splited.crs = 'epsg:4326'
    metro_line_splited['length'] = metro_line_splited.to_crs(epsg=3857).length
    metro_line_splited = metro_line_splited.drop(
        ['o_project', 'd_project'], axis=1)
    return metro_line_splited


def metro_network(line, stop, transfertime=5, nxgraph=True):
    '''
    Inputting the metro station data and outputting the network topology
    model. The graph generated relies on NetworkX. The travel time is consist of:
    operation time between stations + stop time at each station + transfer time

    Parameters
    -------

    line : GeoDataFrame
        Lines. Should have `line` column to store line name `speed` column to
        store metro speed and `stoptime` column to store stop time at each
        station.
    stop : GeoDataFrame
        Bus/metro stations
    transfertime : number
        Travel time per transfer
    nxgraph : bool
        Default True, if True then output the network G constructed by
        NetworkX, if False then output the edges1(line section),
        edge2(station transfer), and the node of the network

    Returns
    -------

    When the nxgraph parameter is True
    ================================================================
    G : networkx.classes.graph.Graph
        Network G built by networkx.

    When the nxgraph parameter is False (This is for detail design of the network)
    ================================================================
    edge1 : DataFrame
        Network edge for line section.
    edge2 : DataFrame
        Network edge for transfering.
    node : List
        Network nodes.
    '''
    # Obtain edge1: Network edge for line section.
    linestop = stop.copy()
    if ('speed' not in line.columns) | ('stoptime' not in line.columns):
        raise ValueError( # pragma: no cover
            'Lines should have `line` column to store line name,'
            '`speed` column to store metro speed and'
            '`stoptime` column to store stop time at each station'
        )
    for i in linestop.columns:
        linestop[i+'1'] = linestop[i].shift(-1)
    linestop = linestop[linestop['linename'] == linestop['linename1']].copy()
    linestop = linestop.rename(
        columns={'stationnames': 'ostop', 'stationnames1': 'dstop'})
    linestop['ostation'] = linestop['line']+linestop['ostop']
    linestop['dstation'] = linestop['line']+linestop['dstop']
    edge1 = linestop[['ostation', 'dstation']].copy()

    # calculate travel time for edge1
    # calculate distance
    metrolinesplit = split_subwayline(line, stop)
    metrolinesplit['ostation'] = metrolinesplit['line'] + \
        metrolinesplit['stationnames']
    metrolinesplit['dstation'] = metrolinesplit['line'] + \
        metrolinesplit['stationnames1']
    metrolinesplit = metrolinesplit[['ostation', 'dstation', 'line', 'length']]
    edge1 = pd.merge(edge1, metrolinesplit, how='left')
    edge1 = pd.merge(edge1, line[['line', 'speed', 'stoptime']])

    # calculate duration
    edge1['duration'] = 60*(edge1['length']/1000) / \
        edge1['speed']+edge1['stoptime']
    edge1 = edge1[['ostation', 'dstation', 'duration']].drop_duplicates(
        subset=['ostation', 'dstation'])

    # Obtain edge2: Network edge for transfering.
    linestop = stop.copy()
    linestop['station'] = linestop['line'] + linestop['stationnames']
    tmp = linestop.groupby(['stationnames'])[
        'linename'].count().rename('count').reset_index()
    tmp = pd.merge(linestop, tmp[tmp['count'] > 2]
                   ['stationnames'], on='stationnames')
    tmp = tmp[['stationnames', 'line', 'station']].drop_duplicates()
    tmp = pd.merge(tmp, tmp, on='stationnames')

    edge2 = tmp[tmp['line_x'] != tmp['line_y']][['station_x', 'station_y']]
    # All transfer time are set as the same, export `edge2` for further degign
    edge2['duration'] = transfertime
    edge2.columns = edge1.columns
    edge = edge1.append(edge2)
    node = list(edge['ostation'].drop_duplicates())
    if nxgraph:
        import networkx as nx
        G = nx.Graph()
        G.add_nodes_from(node)
        G.add_weighted_edges_from(edge.values)
        return G
    else:
        return edge1, edge2, node # pragma: no cover


def get_shortest_path(G, stop, ostation, dstation):
    '''
    Obtain the travel path of shortest path from the metro nextwork

    Parameters
    -------

    G : networkx.classes.graph.Graph
        metro network
    stop : DataFrame
        metro stop dataframe
    ostation : str
        O station name
    dstation : str
        D station name


    Returns
    -------
    path : list
        travel path: list of station names
    '''
    import networkx as nx
    o = stop[stop['stationnames'] == ostation]['line'].iloc[0]+ostation
    d = stop[stop['stationnames'] == dstation]['line'].iloc[0]+dstation
    return nx.shortest_path(G, source=o, target=d, weight='weight')


def get_k_shortest_paths(G, stop, ostation, dstation, k):
    '''
    Obtain the k th shortest paths from the metro nextwork

    Parameters
    -------

    G : networkx.classes.graph.Graph
        metro network
    stop : DataFrame
        metro stop dataframe
    ostation : str
        O station name
    dstation : str
        D station name
    k : int
        the k th shortest paths


    Returns
    -------
    paths : list
        travel path: list of travel paths
    '''
    from itertools import islice
    import networkx as nx
    o = stop[stop['stationnames'] == ostation]['line'].iloc[0]+ostation
    d = stop[stop['stationnames'] == dstation]['line'].iloc[0]+dstation
    return list(
        islice(nx.shortest_simple_paths(G, o, d, weight='weight'), k)
    )


def get_path_traveltime(G, path):
    '''
    Obtain the travel time of the path

    Parameters
    -------

    G : networkx.classes.graph.Graph
        metro network
    path : list
        list of stationnames

    Returns
    -------
    traveltime : float
        travel time of the path
    '''
    traveltime = 0
    for i in range(len(path)-1):
        traveltime += G.get_edge_data(path[i], path[i+1])['weight']
    return traveltime
