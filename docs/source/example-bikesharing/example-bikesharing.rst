共享单车数据社区发现
========================================

| 这个案例的Jupyter notebook: `点击这里 <https://github.com/ni1o1/transbigdata/blob/main/example/Example%205-community%20detection%20for%20bikesharing%20data.ipynb>`__.
| 对于共享单车的出行，每一次出行都可以被看作是一个从起点行动到终点的出行过程。当我们把起点和终点视为节点，把它们之间的出行视为边时，就可以构建一个网络。通过分析这个网络，我们可以得到关于城市的空间结构、共享单车需求的宏观出行特征等信息。
| 社区发现，也可以叫图分割，帮助我们揭示网络中节点之间的隐藏关系。在这个例子中，我们将介绍如何将TransBigData整合到共享单车数据的社区发现分析过程中。


::

    import pandas as pd
    import numpy as np
    import geopandas as gpd
    import transbigdata as tbd

数据预处理
-------------------------

在社区发现之前，我们首先需要对数据进行预处理。从共享单车订单中提取出行OD并剔除异常出行，并以清洗好的数据作为研究对象。

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


读取研究区域的边界，并用tbd.clean_outofshape方法剔除研究区域以外的数据

::

    #读取上海行政区划边界
    shanghai_admin = gpd.read_file(r'data/shanghai.json')
    #剔除研究范围外的数据
    bikedata = tbd.clean_outofshape(bikedata, shanghai_admin, col=['LONGITUDE', 'LATITUDE'], accuracy=500)

用tbd.bikedata_to_od方法从单车数据中识别出行OD信息

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

我们需要剔除过长与过短的共享单车出行。用tbd.getdistance获取起终点之间的直线距离，并筛选删除直线距离小于100米与大于10千米的出行

::

    #计算骑行直线距离
    move_data['distance'] = tbd.getdistance(move_data['slon'],move_data['slat'],move_data['elon'],move_data['elat'])
    #清洗骑行数据，删除过长与过短的出行
    move_data = move_data[(move_data['distance']>100)&(move_data['distance']<10000)]

接下来，我们以500米×500米的栅格为最小分析单元，用tbd.grid_params方法获取栅格划分参数，再将参数输入tbd.odagg_grid方法，对OD进行栅格集计

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

对OD集计的结果在地图上可视化，用tbd.plot_map加载地图底图，并用tbd.plotscale添加比例尺与指北针

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


提取节点信息
------------------------

使用igraph包构建网络。在Python中，igraph与networkx功能类似，都提供了网络分析的功能，仅在部分算法的支持上有所区别。
构建网络时，我们需要向igraph提供网络的节点与边的信息。以OD数据中出现过的每个栅格作为节点，构建节点的信息时，需要为节点创建从0开始的数字编号，代码如下

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
----------------

将新的编号连接到OD信息表上，以提取新ID之间的出行量构成边

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

导入igraph包，创建网络，添加节点，并将边数据输入网络。同时，为每一条边添加相应的权重

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

在构建好的网络上应用社区发现算法。其中，我们使用igraph包自带的g.community_multilevel方法实现Fast unfolding社区发现算法。前面我们介绍过，Fast unfolding算法将社区逐层迭代合并直至模块度最优，而在g.community_multilevel方法中可以设定return_levels返回迭代的中间结果。这里我们设定return_levels为False，只返回最终结果进行分析

::

    #社区发现
    g_clustered = g.community_multilevel(weights = edge_weights, return_levels=False)


社区发现的结果存储在g_clustered变量中，可以用内置方法直接计算模块度

::

    #模块度
    g_clustered.modularity




.. parsed-literal::

    0.8496561130926571

一般来说，模块度在0.5以上已经属于较高值。而这一结果的模块度达到0.84，表明网络的社区结构非常明显，社区划分结果也能够很好地划分网络。接下来，我们将社区划分结果赋值到节点信息表上，为后面的可视化做准备。代码如下

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

在社区发现的结果中，可能会存在部分社区中只存在少量的节点，无法形成规模较大的社区。这些社区为离群点，在可视化之前应该删去，这里我们保留包含10个栅格以上的社区

::

    #统计每个社区的栅格数量
    group = node['group'].value_counts()
    #提取大于10个栅格的社区
    group = group[group>10]
    #只保留这些社区的栅格
    node = node[node['group'].apply(lambda r:r in group.index)]

将栅格编号复原，再用tbd.gridid_to_polygon方法从栅格编号生成栅格的地理几何图形

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

在这一步中，我们将每一个节点复原为栅格，标记上节点所属的社区编号，生成了每个栅格的地理信息，并将其转换为GeoDataFrame，可以用如下代码绘制栅格，测试是否生成成功

::

    node.plot('group')




.. image:: output_22_1.png


这里我们将group字段的分组编号映射到颜色上进行初步可视化，不同分组的颜色不同。从结果的图中可以看到，相同颜色的栅格在地理空间上大多聚集在一起，表明共享单车的空间联系可以将地理空间上接近的区域紧密地联系在一起

前面的结果可视化的效果并不明显，我们并不能从图中清晰地看出分区的情况。接下来，我们可以对分区结果进行一定的调整与可视化。可视化的调整主要有以下思路:

* 比较合适的分区结果应该是每个区域都为空间上连续的区域，在初步的可视化结果中，有不少的栅格在空间上为孤立存在，这些点应该予以剔除。
* 在可视化结果中，我们可以将同一个组别的栅格合并，为每个分区形成面要素，这样在下一步可视化中就可以绘制出分区的边界。
* 在分区结果中，有些区域的内部可能会存在其他区域的“飞地”，即隶属于本分区，却被其他分区所包围，只能“飞”过其他分区的属地，才能到达自己的飞地。这种分区在共享单车的实际运营中也是难以管理的，应该避免这种情况的出现。

解决上述问题，我们可以使用TransBigData所提供的两个GIS处理方法，tbd.merge_polygon和tbd.polyon_exterior。其中tbd.merge_polygon能够将同一个组别的面要素进行合并，而tbd.polyon_exterior则可以对多边形取外边界后再构成新的多边形，以此剔除飞地。同时，也可以设定最小面积，对小于此面积的面要素进行剔除。代码如下


::

    #以group字段为分组，将同一组别的面要素合并
    node_community = tbd.merge_polygon(node,'group')
    #输入多边形GeoDataFrame数据，对多边形取外边界构成新多边形
    #设定最小面积minarea，小于该面积的面全部剔除，避免大量离群点出现
    node_community = tbd.polyon_exterior(node_community,minarea = 0.000100)


处理好社区的面要素后，接下来需要对面要素进行可视化。我们希望对不同的面赋予不同的颜色。在可视化章节中我们提到，在显示的要素没有数值上的大小区别时，颜色的选择上需要保持它们各自的颜色具有相同的亮度与饱和度。而用seaborn的调色盘方法即可快速地生成同一亮度与饱和度下的多种颜色

::

    #生成调色盘
    import seaborn as sns
    ## l: 亮度
    ## s: 饱和度
    cmap = sns.hls_palette(n_colors=len(node_community), l=.7, s=0.8)
    sns.palplot(cmap)



.. image:: output_24_0.png

对社区结果进行可视化

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

至此，我们就已经成功地可视化出共享单车社区，并绘制出每一个社区的边界。在用社区发现模型进行分区时，并没有往模型中输入任何地理空间信息，模型对研究区域的分割也仅仅依靠共享单车出行需求所构成的网络联系。
