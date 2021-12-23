pNEUMA轨迹数据处理
====================================

| 这个案例的Jupyter notebook: `点击这里 <https://github.com/ni1o1/transbigdata/blob/main/example/Example%204-pNEUMA%20trajectory%20dataset%20processing.ipynb>`__.
| 在这个例子中，我们将示例如何将``TransBigData``融入到雅典pNEUMA轨迹数据集的处理与可视化中。
| 请注意，样本数据已经被经过了一定的处理。原始版本的数据集可以在这里下载。
  `website <https://open-traffic.epfl.ch/>`__

::

    import transbigdata as tbd
    import pandas as pd
    import geopandas as gpd
    import matplotlib.pyplot as plt

读取数据
-------------

轨迹数据
~~~~~~~~~~~~~~~~~~~

::

    # 读取数据
    data = pd.read_csv('data/pNEUMA_tbd_sample.csv')
    # 将时间戳转换为时间格式
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data.head()




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>track_id</th>
          <th>lon</th>
          <th>lat</th>
          <th>speed</th>
          <th>time</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>128</td>
          <td>23.730362</td>
          <td>37.990046</td>
          <td>12.5845</td>
          <td>1970-01-01 00:00:00.000</td>
        </tr>
        <tr>
          <th>1</th>
          <td>128</td>
          <td>23.730364</td>
          <td>37.990045</td>
          <td>12.4935</td>
          <td>1970-01-01 00:00:00.040</td>
        </tr>
        <tr>
          <th>2</th>
          <td>128</td>
          <td>23.730366</td>
          <td>37.990045</td>
          <td>12.3965</td>
          <td>1970-01-01 00:00:00.080</td>
        </tr>
        <tr>
          <th>3</th>
          <td>128</td>
          <td>23.730367</td>
          <td>37.990045</td>
          <td>12.2949</td>
          <td>1970-01-01 00:00:00.120</td>
        </tr>
        <tr>
          <th>4</th>
          <td>128</td>
          <td>23.730369</td>
          <td>37.990044</td>
          <td>12.1910</td>
          <td>1970-01-01 00:00:00.160</td>
        </tr>
      </tbody>
    </table>
    </div>





::

    # 输出数据大小信息
    data.info()


.. parsed-literal::

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 581244 entries, 0 to 581243
    Data columns (total 5 columns):
     #   Column    Non-Null Count   Dtype         
    ---  ------    --------------   -----         
     0   track_id  581244 non-null  int64         
     1   lon       581244 non-null  float64       
     2   lat       581244 non-null  float64       
     3   speed     581244 non-null  float64       
     4   time      581244 non-null  datetime64[ns]
    dtypes: datetime64[ns](1), float64(3), int64(1)
    memory usage: 22.2 MB


OSM路网数据获取
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

你可以直接从``data``文件夹加载道路数据，或者使用OSMNX下载路网 `OSMNX <https://osmnx.readthedocs.io/en/stable/>`__

::

    # 从OSMNX中获取路网数据
    # OSM Graph
    import osmnx as ox
    bounds = [23.723577, 37.975462, 23.738471, 37.993053]
    north, south, east, west = bounds[3], bounds[1], bounds[2], bounds[0]
    G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
    
    # 获取点和边
    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
    
    # 存储路网数据
    filepath = "data/pNEUMA_network.graphml"
    ox.save_graphml(G, filepath)

如果你没有OSMNX,可以运行下面代码读取已经现成的数据

::

    # 读取OSM数据
    import osmnx as ox
    filepath = "data/pNEUMA_network.graphml"
    G = ox.load_graphml(filepath)
    # 获取点和边
    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

地图底图加载
~~~~~~~~~~~~~~~~~~~~~

将地图底图加载并可视化

::

    # 可视化地图底图 tbd.plot_map
    bounds = [23.723577, 37.975462, 23.738471, 37.993053]
    
    fig = plt.figure(1, (12, 8), dpi=100)
    ax = plt.subplot(121)
    plt.sca(ax)
    tbd.plot_map(plt, bounds, zoom=18, style=1) # the map
    edges.plot(ax=ax, lw=1, color='grey') # edges
    nodes.plot(ax=ax, markersize = 8, color='red') # nodes
    plt.axis('off');
    
    ax = plt.subplot(122)
    plt.sca(ax)
    tbd.plot_map(plt, bounds, zoom=18, style=5) # the map
    edges.plot(ax=ax, lw=1, color='grey') # edges
    nodes.plot(ax=ax, markersize = 8, color='red') # nodes
    plt.axis('off');



.. image:: output_11_0.png


数据清洗
-------------

数据稀疏化
~~~~~~~~~~~~~~

| 数据集的采样间隔为 :math:`0.04` 秒, 非常小，不便于处理。
| 然而，一些宏观层面的研究不需要如此高的采样间隔。在这种情况下，数据可以使用``tbd.traj_sparsify``进行稀疏化。

::

    # 原始数据
    data.info()


.. parsed-literal::

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 581244 entries, 0 to 581243
    Data columns (total 5 columns):
     #   Column    Non-Null Count   Dtype         
    ---  ------    --------------   -----         
     0   track_id  581244 non-null  int64         
     1   lon       581244 non-null  float64       
     2   lat       581244 non-null  float64       
     3   speed     581244 non-null  float64       
     4   time      581244 non-null  datetime64[ns]
    dtypes: datetime64[ns](1), float64(3), int64(1)
    memory usage: 22.2 MB


::

    #轨迹稀疏化
    data_sparsify = tbd.traj_sparsify(data, col=['track_id', 'time', 'lon', 'lat'],timegap=0.4,method='subsample')
    data_sparsify.info()


.. parsed-literal::

    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 23293 entries, 0 to 581229
    Data columns (total 5 columns):
     #   Column    Non-Null Count  Dtype         
    ---  ------    --------------  -----         
     0   track_id  23293 non-null  int64         
     1   lon       23293 non-null  float64       
     2   lat       23293 non-null  float64       
     3   speed     23293 non-null  float64       
     4   time      23293 non-null  datetime64[ns]
    dtypes: datetime64[ns](1), float64(3), int64(1)
    memory usage: 1.1 MB


冗余数据剔除
~~~~~~~~~~~~~

在车辆停止运行时，位置没有发生移动，但仍然会产生大量GPS点，这些静止的GPS点除第一和最后一个点外的都可以删除。

::

    #用 tbd.clean_same 删除冗余数据
    data_sparsify_clean = tbd.clean_same(data_sparsify, col=['track_id', 'time', 'lon', 'lat'])
    data_sparsify_clean.info()


.. parsed-literal::

    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 10674 entries, 0 to 581229
    Data columns (total 5 columns):
     #   Column    Non-Null Count  Dtype         
    ---  ------    --------------  -----         
     0   track_id  10674 non-null  int64         
     1   lon       10674 non-null  float64       
     2   lat       10674 non-null  float64       
     3   speed     10674 non-null  float64       
     4   time      10674 non-null  datetime64[ns]
    dtypes: datetime64[ns](1), float64(3), int64(1)
    memory usage: 500.3 KB


::

    data_sparsify_clean.head()




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>track_id</th>
          <th>lon</th>
          <th>lat</th>
          <th>speed</th>
          <th>time</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>128</td>
          <td>23.730362</td>
          <td>37.990046</td>
          <td>12.5845</td>
          <td>1970-01-01 00:00:00</td>
        </tr>
        <tr>
          <th>25</th>
          <td>128</td>
          <td>23.730399</td>
          <td>37.990040</td>
          <td>10.6835</td>
          <td>1970-01-01 00:00:01</td>
        </tr>
        <tr>
          <th>50</th>
          <td>128</td>
          <td>23.730429</td>
          <td>37.990036</td>
          <td>7.8580</td>
          <td>1970-01-01 00:00:02</td>
        </tr>
        <tr>
          <th>75</th>
          <td>128</td>
          <td>23.730443</td>
          <td>37.990033</td>
          <td>1.2661</td>
          <td>1970-01-01 00:00:03</td>
        </tr>
        <tr>
          <th>1775</th>
          <td>128</td>
          <td>23.730443</td>
          <td>37.990033</td>
          <td>0.0027</td>
          <td>1970-01-01 00:01:11</td>
        </tr>
      </tbody>
    </table>
    </div>



数据可视化
------------------

::

    gdf_data = gpd.GeoDataFrame(data_sparsify_clean, 
                                geometry=gpd.points_from_xy(data_sparsify_clean['lon'], 
                                                            data_sparsify_clean['lat']), 
                                crs=4326)
    gdf_data.head()




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>track_id</th>
          <th>lon</th>
          <th>lat</th>
          <th>speed</th>
          <th>time</th>
          <th>geometry</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>128</td>
          <td>23.730362</td>
          <td>37.990046</td>
          <td>12.5845</td>
          <td>1970-01-01 00:00:00</td>
          <td>POINT (23.73036 37.99005)</td>
        </tr>
        <tr>
          <th>25</th>
          <td>128</td>
          <td>23.730399</td>
          <td>37.990040</td>
          <td>10.6835</td>
          <td>1970-01-01 00:00:01</td>
          <td>POINT (23.73040 37.99004)</td>
        </tr>
        <tr>
          <th>50</th>
          <td>128</td>
          <td>23.730429</td>
          <td>37.990036</td>
          <td>7.8580</td>
          <td>1970-01-01 00:00:02</td>
          <td>POINT (23.73043 37.99004)</td>
        </tr>
        <tr>
          <th>75</th>
          <td>128</td>
          <td>23.730443</td>
          <td>37.990033</td>
          <td>1.2661</td>
          <td>1970-01-01 00:00:03</td>
          <td>POINT (23.73044 37.99003)</td>
        </tr>
        <tr>
          <th>1775</th>
          <td>128</td>
          <td>23.730443</td>
          <td>37.990033</td>
          <td>0.0027</td>
          <td>1970-01-01 00:01:11</td>
          <td>POINT (23.73044 37.99003)</td>
        </tr>
      </tbody>
    </table>
    </div>



::

    # 获取有最多数据点的车辆
    gdf_count = gdf_data.groupby('track_id')['lon'].count().rename('count').sort_values(ascending=False).reset_index()
    print(list(gdf_count.iloc[:20]['track_id']))


.. parsed-literal::

    [2138, 3290, 1442, 3197, 4408, 1767, 5002, 5022, 2140, 347, 2584, 4750, 4542, 2431, 4905, 4997, 1329, 4263, 1215, 3400]


可视化车辆

::

    fig = plt.figure(1, (6, 8), dpi=100)
    
    ax = plt.subplot(111)
    plt.sca(ax)
    
    # map
    tbd.plot_map(plt, bounds, zoom=18, style=4) # the map
    edges.plot(ax=ax, lw=1, color='grey') # edges
    # nodes.plot(ax=ax, markersize = 6, color='red') # nodes
    
    # trajectory
    gdf_data.plot(column='speed', ax=ax, markersize=0.5)
    
    plt.axis('off');



.. image:: output_22_0.png


可视化单辆车，并显示最短路径

::

    # select a vehicle
    tmpgdf_data = gdf_data[gdf_data['track_id']==2138]
    
    # the origin / destination location
    # o_point = [tmpgdf_data.iloc[0]['lon'], tmpgdf_data.iloc[0]['lat']]
    # d_point = [tmpgdf_data.iloc[-1]['lon'], tmpgdf_data.iloc[-1]['lat']]
    
    # get the nearest node of each point on the map
    tmpgdf_data = tbd.ckdnearest_point(tmpgdf_data, nodes)
    
    # extract the o/d node
    o_index, d_index = tmpgdf_data.iloc[0]['index'], tmpgdf_data.iloc[-1]['index']
    o_node_id, d_node_id = list(nodes[nodes['index']==o_index].index)[0], \
                           list(nodes[nodes['index']==d_index].index)[0]
    print(o_node_id, d_node_id)
    
    tmpgdf_data.head()


.. parsed-literal::

    250691723 358465943


.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>track_id</th>
          <th>lon</th>
          <th>lat</th>
          <th>speed</th>
          <th>time</th>
          <th>geometry_x</th>
          <th>dist</th>
          <th>index</th>
          <th>y</th>
          <th>x</th>
          <th>street_count</th>
          <th>highway</th>
          <th>geometry_y</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>2138</td>
          <td>23.735287</td>
          <td>37.977435</td>
          <td>42.1006</td>
          <td>1970-01-01 00:01:35.560</td>
          <td>POINT (23.73529 37.97743)</td>
          <td>0.000779</td>
          <td>145</td>
          <td>37.978086</td>
          <td>23.734859</td>
          <td>4</td>
          <td>NaN</td>
          <td>POINT (23.73486 37.97809)</td>
        </tr>
        <tr>
          <th>1</th>
          <td>2138</td>
          <td>23.735254</td>
          <td>37.977473</td>
          <td>41.8663</td>
          <td>1970-01-01 00:01:36.000</td>
          <td>POINT (23.73525 37.97747)</td>
          <td>0.000729</td>
          <td>145</td>
          <td>37.978086</td>
          <td>23.734859</td>
          <td>4</td>
          <td>NaN</td>
          <td>POINT (23.73486 37.97809)</td>
        </tr>
        <tr>
          <th>2</th>
          <td>2138</td>
          <td>23.735181</td>
          <td>37.977558</td>
          <td>39.9012</td>
          <td>1970-01-01 00:01:37.000</td>
          <td>POINT (23.73518 37.97756)</td>
          <td>0.000618</td>
          <td>145</td>
          <td>37.978086</td>
          <td>23.734859</td>
          <td>4</td>
          <td>NaN</td>
          <td>POINT (23.73486 37.97809)</td>
        </tr>
        <tr>
          <th>3</th>
          <td>2138</td>
          <td>23.735111</td>
          <td>37.977638</td>
          <td>37.7748</td>
          <td>1970-01-01 00:01:38.000</td>
          <td>POINT (23.73511 37.97764)</td>
          <td>0.000514</td>
          <td>145</td>
          <td>37.978086</td>
          <td>23.734859</td>
          <td>4</td>
          <td>NaN</td>
          <td>POINT (23.73486 37.97809)</td>
        </tr>
        <tr>
          <th>4</th>
          <td>2138</td>
          <td>23.735047</td>
          <td>37.977712</td>
          <td>33.8450</td>
          <td>1970-01-01 00:01:39.000</td>
          <td>POINT (23.73505 37.97771)</td>
          <td>0.000418</td>
          <td>145</td>
          <td>37.978086</td>
          <td>23.734859</td>
          <td>4</td>
          <td>NaN</td>
          <td>POINT (23.73486 37.97809)</td>
        </tr>
      </tbody>
    </table>
    </div>






.. parsed-literal::

    250691723 358465943


::

    fig = plt.figure(1, (6, 8), dpi=100)
    
    ax = plt.subplot(111)
    plt.sca(ax)
    
    # map
    tbd.plot_map(plt, bounds, zoom=18, style=4) # the map
    edges.plot(ax=ax, lw=1, color='grey') # edges
    # nodes.plot(ax=ax, markersize = 6, color='red') # nodes
    
    # trajectory
    gdf_data[gdf_data['track_id']==2138].plot(ax=ax, markersize=5, color='red')
    
    
    plt.axis('off');



.. image:: output_27_0.png


我们可以将轨迹数据与最短路径做比对.

::

    # the shortest path (optional)
    # ax = plt.subplot(122)
    # plt.sca(ax)
    route = ox.shortest_path(G, o_node_id, d_node_id, weight="length")
    plt, ax = ox.plot_graph_route(G, route, route_color="green", route_linewidth=8, node_size=0)



.. image:: output_29_0.png

