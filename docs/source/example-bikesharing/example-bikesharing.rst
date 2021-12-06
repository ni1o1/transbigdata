共享单车数据社区发现
========================================

| 这个案例的Jupyter notebook: `点击这里 <https://github.com/ni1o1/transbigdata/blob/main/example/Example%205-community%20detection%20for%20bikesharing%20data.ipynb>`__.

::

    import pandas as pd
    import numpy as np
    import geopandas as gpd
    import transbigdata as tbd

数据预处理
-------------------------

::

    #读取共享单车数据
    bikedata = pd.read_csv(r'data/bikedata-sample.csv')
    bikedata.head(5)




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
          <th>BIKE_ID</th>
          <th>DATA_TIME</th>
          <th>LOCK_STATUS</th>
          <th>LONGITUDE</th>
          <th>LATITUDE</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>5</td>
          <td>2018-09-01 0:00:36</td>
          <td>1</td>
          <td>121.363566</td>
          <td>31.259615</td>
        </tr>
        <tr>
          <th>1</th>
          <td>6</td>
          <td>2018-09-01 0:00:50</td>
          <td>0</td>
          <td>121.406226</td>
          <td>31.214436</td>
        </tr>
        <tr>
          <th>2</th>
          <td>6</td>
          <td>2018-09-01 0:03:01</td>
          <td>1</td>
          <td>121.409402</td>
          <td>31.215259</td>
        </tr>
        <tr>
          <th>3</th>
          <td>6</td>
          <td>2018-09-01 0:24:53</td>
          <td>0</td>
          <td>121.409228</td>
          <td>31.214427</td>
        </tr>
        <tr>
          <th>4</th>
          <td>6</td>
          <td>2018-09-01 0:26:38</td>
          <td>1</td>
          <td>121.409771</td>
          <td>31.214406</td>
        </tr>
      </tbody>
    </table>
    </div>



::

    #读取上海行政区划边界
    shanghai_admin = gpd.read_file(r'data/shanghai.json')
    #剔除研究范围外的数据
    bikedata = tbd.clean_outofshape(bikedata, shanghai_admin, col=['LONGITUDE', 'LATITUDE'], accuracy=500)

::

    #识别单车出行OD
    move_data,stop_data = tbd.bikedata_to_od(bikedata,
                       col = ['BIKE_ID','DATA_TIME','LONGITUDE','LATITUDE','LOCK_STATUS'])
    move_data.head(5)




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
          <th>BIKE_ID</th>
          <th>stime</th>
          <th>slon</th>
          <th>slat</th>
          <th>etime</th>
          <th>elon</th>
          <th>elat</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>96</th>
          <td>6</td>
          <td>2018-09-01 0:00:50</td>
          <td>121.406226</td>
          <td>31.214436</td>
          <td>2018-09-01 0:03:01</td>
          <td>121.409402</td>
          <td>31.215259</td>
        </tr>
        <tr>
          <th>561</th>
          <td>6</td>
          <td>2018-09-01 0:24:53</td>
          <td>121.409228</td>
          <td>31.214427</td>
          <td>2018-09-01 0:26:38</td>
          <td>121.409771</td>
          <td>31.214406</td>
        </tr>
        <tr>
          <th>564</th>
          <td>6</td>
          <td>2018-09-01 0:50:16</td>
          <td>121.409727</td>
          <td>31.214403</td>
          <td>2018-09-01 0:52:14</td>
          <td>121.412610</td>
          <td>31.214905</td>
        </tr>
        <tr>
          <th>784</th>
          <td>6</td>
          <td>2018-09-01 0:53:38</td>
          <td>121.413333</td>
          <td>31.214951</td>
          <td>2018-09-01 0:55:38</td>
          <td>121.412656</td>
          <td>31.217051</td>
        </tr>
        <tr>
          <th>1028</th>
          <td>6</td>
          <td>2018-09-01 11:35:01</td>
          <td>121.419261</td>
          <td>31.213414</td>
          <td>2018-09-01 11:35:13</td>
          <td>121.419518</td>
          <td>31.213657</td>
        </tr>
      </tbody>
    </table>
    </div>



::

    #计算骑行直线距离
    move_data['distance'] = tbd.getdistance(move_data['slon'],move_data['slat'],move_data['elon'],move_data['elat'])
    #清洗骑行数据，删除过长与过短的出行
    move_data = move_data[(move_data['distance']>100)&(move_data['distance']<10000)]

::

    # 获取栅格划分参数
    bounds = (120.85, 30.67, 122.24, 31.87)
    params = tbd.grid_params(bounds,accuracy = 500)
    #集计OD
    od_gdf = tbd.odagg_grid(move_data, params, col=['slon', 'slat', 'elon', 'elat'])
    od_gdf.head(5)




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
          <th>SLONCOL</th>
          <th>SLATCOL</th>
          <th>ELONCOL</th>
          <th>ELATCOL</th>
          <th>count</th>
          <th>SHBLON</th>
          <th>SHBLAT</th>
          <th>EHBLON</th>
          <th>EHBLAT</th>
          <th>geometry</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>26</td>
          <td>95</td>
          <td>26</td>
          <td>96</td>
          <td>1</td>
          <td>120.986782</td>
          <td>31.097177</td>
          <td>120.986782</td>
          <td>31.101674</td>
          <td>LINESTRING (120.98678 31.09718, 120.98678 31.1...</td>
        </tr>
        <tr>
          <th>40803</th>
          <td>117</td>
          <td>129</td>
          <td>116</td>
          <td>127</td>
          <td>1</td>
          <td>121.465519</td>
          <td>31.250062</td>
          <td>121.460258</td>
          <td>31.241069</td>
          <td>LINESTRING (121.46552 31.25006, 121.46026 31.2...</td>
        </tr>
        <tr>
          <th>40807</th>
          <td>117</td>
          <td>129</td>
          <td>117</td>
          <td>128</td>
          <td>1</td>
          <td>121.465519</td>
          <td>31.250062</td>
          <td>121.465519</td>
          <td>31.245565</td>
          <td>LINESTRING (121.46552 31.25006, 121.46552 31.2...</td>
        </tr>
        <tr>
          <th>40810</th>
          <td>117</td>
          <td>129</td>
          <td>117</td>
          <td>131</td>
          <td>1</td>
          <td>121.465519</td>
          <td>31.250062</td>
          <td>121.465519</td>
          <td>31.259055</td>
          <td>LINESTRING (121.46552 31.25006, 121.46552 31.2...</td>
        </tr>
        <tr>
          <th>40811</th>
          <td>117</td>
          <td>129</td>
          <td>118</td>
          <td>126</td>
          <td>1</td>
          <td>121.465519</td>
          <td>31.250062</td>
          <td>121.470780</td>
          <td>31.236572</td>
          <td>LINESTRING (121.46552 31.25006, 121.47078 31.2...</td>
        </tr>
      </tbody>
    </table>
    </div>



::

    #创建图框
    import matplotlib.pyplot as plt
    import plot_map
    fig =plt.figure(1,(8,8),dpi=300)
    ax =plt.subplot(111)
    plt.sca(ax)
    #添加地图底图
    tbd.plot_map(plt,bounds,zoom = 11,style = 8)
    #绘制colorbar
    cax = plt.axes([0.05, 0.33, 0.02, 0.3])
    plt.title('Data count')
    plt.sca(ax)
    #绘制OD
    od_gdf.plot(ax = ax,column = 'count',cmap = 'Blues_r',linewidth = 0.5,vmax = 10,cax = cax,legend = True)
    #添加比例尺和指北针
    tbd.plotscale(ax,bounds = bounds,textsize = 10,compasssize = 1,textcolor = 'white',accuracy = 2000,rect = [0.06,0.03],zorder = 10)
    plt.axis('off')
    plt.xlim(bounds[0],bounds[2])
    plt.ylim(bounds[1],bounds[3])
    plt.show()



.. image:: output_7_0.png


网络构建
-------------------------

提取节点信息
~~~~~~~~~~~~~~~~~~~

::

    #把起终点的经纬度栅格编号变为一个字段
    od_gdf['S'] = od_gdf['SLONCOL'].astype(str) + ',' + od_gdf['SLATCOL'].astype(str)
    od_gdf['E'] = od_gdf['ELONCOL'].astype(str) + ',' + od_gdf['ELATCOL'].astype(str)
    #提取节点集合
    node = set(od_gdf['S'])|set(od_gdf['E'])
    #把节点集合变成DataFrame
    node = pd.DataFrame(node)
    #重新编号节点
    node['id'] = range(len(node))
    node




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
          <th>0</th>
          <th>id</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>118,134</td>
          <td>0</td>
        </tr>
        <tr>
          <th>1</th>
          <td>109,102</td>
          <td>1</td>
        </tr>
        <tr>
          <th>2</th>
          <td>59,71</td>
          <td>2</td>
        </tr>
        <tr>
          <th>3</th>
          <td>93,78</td>
          <td>3</td>
        </tr>
        <tr>
          <th>4</th>
          <td>96,17</td>
          <td>4</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>9806</th>
          <td>94,97</td>
          <td>9806</td>
        </tr>
        <tr>
          <th>9807</th>
          <td>106,152</td>
          <td>9807</td>
        </tr>
        <tr>
          <th>9808</th>
          <td>124,134</td>
          <td>9808</td>
        </tr>
        <tr>
          <th>9809</th>
          <td>98,158</td>
          <td>9809</td>
        </tr>
        <tr>
          <th>9810</th>
          <td>152,86</td>
          <td>9810</td>
        </tr>
      </tbody>
    </table>
    <p>9811 rows × 2 columns</p>
    </div>



提取边信息
~~~~~~~~~~~~~~~~~~~

::

    #把新编号连接到OD数据上
    node.columns = ['S','S_id']
    od_gdf = pd.merge(od_gdf,node,on = ['S'])
    node.columns = ['E','E_id']
    od_gdf = pd.merge(od_gdf,node,on = ['E'])
    #提取边信息
    edge = od_gdf[['S_id','E_id','count']]
    edge




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
          <th>S_id</th>
          <th>E_id</th>
          <th>count</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>8261</td>
          <td>7105</td>
          <td>1</td>
        </tr>
        <tr>
          <th>1</th>
          <td>9513</td>
          <td>2509</td>
          <td>1</td>
        </tr>
        <tr>
          <th>2</th>
          <td>118</td>
          <td>2509</td>
          <td>3</td>
        </tr>
        <tr>
          <th>3</th>
          <td>348</td>
          <td>2509</td>
          <td>1</td>
        </tr>
        <tr>
          <th>4</th>
          <td>1684</td>
          <td>2509</td>
          <td>1</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>68468</th>
          <td>8024</td>
          <td>4490</td>
          <td>2</td>
        </tr>
        <tr>
          <th>68469</th>
          <td>4216</td>
          <td>3802</td>
          <td>2</td>
        </tr>
        <tr>
          <th>68470</th>
          <td>4786</td>
          <td>6654</td>
          <td>2</td>
        </tr>
        <tr>
          <th>68471</th>
          <td>6484</td>
          <td>602</td>
          <td>3</td>
        </tr>
        <tr>
          <th>68472</th>
          <td>7867</td>
          <td>8270</td>
          <td>3</td>
        </tr>
      </tbody>
    </table>
    <p>68473 rows × 3 columns</p>
    </div>



构建网络
--------

::

    import igraph
    #创建网络
    g = igraph.Graph()
    #在网络中添加节点。
    g.add_vertices(len(node))
    #在网络中添加边。
    g.add_edges(edge[['S_id','E_id']].values)
    #提取边的权重。
    edge_weights = edge[['count']].values
    #给边添加权重。
    for i in range(len(edge_weights)):
        g.es[i]['weight'] = edge_weights[i]

社区发现
-------------

::

    #社区发现
    g_clustered = g.community_multilevel(weights = edge_weights, return_levels=False)

::

    #模块度
    g_clustered.modularity




.. parsed-literal::

    0.8496561130926571



::

    #将结果赋值到节点上
    node['group'] = g_clustered.membership
    #重命名列
    node.columns = ['grid','node_id','group']
    node




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
          <th>grid</th>
          <th>node_id</th>
          <th>group</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>118,134</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <th>1</th>
          <td>109,102</td>
          <td>1</td>
          <td>1</td>
        </tr>
        <tr>
          <th>2</th>
          <td>59,71</td>
          <td>2</td>
          <td>2</td>
        </tr>
        <tr>
          <th>3</th>
          <td>93,78</td>
          <td>3</td>
          <td>3</td>
        </tr>
        <tr>
          <th>4</th>
          <td>96,17</td>
          <td>4</td>
          <td>4</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>9806</th>
          <td>94,97</td>
          <td>9806</td>
          <td>8</td>
        </tr>
        <tr>
          <th>9807</th>
          <td>106,152</td>
          <td>9807</td>
          <td>36</td>
        </tr>
        <tr>
          <th>9808</th>
          <td>124,134</td>
          <td>9808</td>
          <td>37</td>
        </tr>
        <tr>
          <th>9809</th>
          <td>98,158</td>
          <td>9809</td>
          <td>9</td>
        </tr>
        <tr>
          <th>9810</th>
          <td>152,86</td>
          <td>9810</td>
          <td>26</td>
        </tr>
      </tbody>
    </table>
    <p>9811 rows × 3 columns</p>
    </div>



社区可视化
-------------

::

    #统计每个社区的栅格数量
    group = node['group'].value_counts()
    #提取大于10个栅格的社区
    group = group[group>10]
    #只保留这些社区的栅格
    node = node[node['group'].apply(lambda r:r in group.index)]

::

    #切分获取栅格编号
    node['LONCOL'] = node['grid'].apply(lambda r:r.split(',')[0]).astype(int)
    node['LATCOL'] = node['grid'].apply(lambda r:r.split(',')[1]).astype(int)
    #生成栅格地理图形
    node['geometry'] = tbd.gridid_to_polygon(node['LONCOL'],node['LATCOL'],params)
    #转为GeoDataFrame
    import geopandas as gpd
    node = gpd.GeoDataFrame(node)
    node




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
          <th>grid</th>
          <th>node_id</th>
          <th>group</th>
          <th>LONCOL</th>
          <th>LATCOL</th>
          <th>geometry</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>118,134</td>
          <td>0</td>
          <td>0</td>
          <td>118</td>
          <td>134</td>
          <td>POLYGON ((121.46815 31.27030, 121.47341 31.270...</td>
        </tr>
        <tr>
          <th>1</th>
          <td>109,102</td>
          <td>1</td>
          <td>1</td>
          <td>109</td>
          <td>102</td>
          <td>POLYGON ((121.42080 31.12641, 121.42606 31.126...</td>
        </tr>
        <tr>
          <th>3</th>
          <td>93,78</td>
          <td>3</td>
          <td>3</td>
          <td>93</td>
          <td>78</td>
          <td>POLYGON ((121.33663 31.01849, 121.34189 31.018...</td>
        </tr>
        <tr>
          <th>4</th>
          <td>96,17</td>
          <td>4</td>
          <td>4</td>
          <td>96</td>
          <td>17</td>
          <td>POLYGON ((121.35241 30.74419, 121.35767 30.744...</td>
        </tr>
        <tr>
          <th>5</th>
          <td>156,117</td>
          <td>5</td>
          <td>5</td>
          <td>156</td>
          <td>117</td>
          <td>POLYGON ((121.66806 31.19385, 121.67332 31.193...</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>9806</th>
          <td>94,97</td>
          <td>9806</td>
          <td>8</td>
          <td>94</td>
          <td>97</td>
          <td>POLYGON ((121.34189 31.10392, 121.34715 31.103...</td>
        </tr>
        <tr>
          <th>9807</th>
          <td>106,152</td>
          <td>9807</td>
          <td>36</td>
          <td>106</td>
          <td>152</td>
          <td>POLYGON ((121.40502 31.35124, 121.41028 31.351...</td>
        </tr>
        <tr>
          <th>9808</th>
          <td>124,134</td>
          <td>9808</td>
          <td>37</td>
          <td>124</td>
          <td>134</td>
          <td>POLYGON ((121.49971 31.27030, 121.50498 31.270...</td>
        </tr>
        <tr>
          <th>9809</th>
          <td>98,158</td>
          <td>9809</td>
          <td>9</td>
          <td>98</td>
          <td>158</td>
          <td>POLYGON ((121.36293 31.37822, 121.36819 31.378...</td>
        </tr>
        <tr>
          <th>9810</th>
          <td>152,86</td>
          <td>9810</td>
          <td>26</td>
          <td>152</td>
          <td>86</td>
          <td>POLYGON ((121.64702 31.05446, 121.65228 31.054...</td>
        </tr>
      </tbody>
    </table>
    <p>8527 rows × 6 columns</p>
    </div>



::

    node.plot('group')




.. image:: output_22_1.png


::

    #以group字段为分组，将同一组别的面要素合并
    node_community = tbd.merge_polygon(node,'group')
    #输入多边形GeoDataFrame数据，对多边形取外边界构成新多边形
    #设定最小面积minarea，小于该面积的面全部剔除，避免大量离群点出现
    node_community = tbd.polyon_exterior(node_community,minarea = 0.000100)



::

    #生成调色盘
    import seaborn as sns
    ## l: 亮度
    ## s: 饱和度
    cmap = sns.hls_palette(n_colors=len(node_community), l=.7, s=0.8)
    sns.palplot(cmap)



.. image:: output_24_0.png


::

    #创建图框
    import matplotlib.pyplot as plt
    import plot_map
    fig =plt.figure(1,(8,8),dpi=300)
    ax =plt.subplot(111)
    plt.sca(ax)
    #添加地图底图
    tbd.plot_map(plt,bounds,zoom = 10,style = 6)
    #设定colormap
    from matplotlib.colors import ListedColormap 
    #打乱社区的排列顺序
    node_community = node_community.sample(frac=1)
    #绘制社区
    node_community.plot(cmap = ListedColormap(cmap),ax = ax,edgecolor = '#333',alpha = 0.8)
    #添加比例尺和指北针
    tbd.plotscale(ax,bounds = bounds,textsize = 10,compasssize = 1,textcolor = 'k'
                  ,accuracy = 2000,rect = [0.06,0.03],zorder = 10)
    plt.axis('off')
    plt.xlim(bounds[0],bounds[2])
    plt.ylim(bounds[1],bounds[3])
    plt.show()



.. image:: output_25_0.png

