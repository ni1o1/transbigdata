.. _grids:


***************
数据栅格化
***************

栅格时空数据处理框架
=============================

.. function:: transbigdata.area_to_grid(location, accuracy=500, method='rect', params='auto')

从研究范围生成栅格

**输入**

location : bounds(List) or shape(GeoDataFrame)
    在哪生成栅格 如果是生成范围的边界bounds，则内容为[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 如果是面要素，则必须是GeoDataFrame
accuracy : number
    栅格大小（米）
method : str
    `rect`方形, `tri`三角形或`hexa`六边形
params : list or dict
    栅格参数。如果给定了栅格参数，`accuracy`参数将不起作用

**输出**

grid : GeoDataFrame
    栅格的GeoDataFrame
params : list or dict
    栅格参数

.. function:: transbigdata.area_to_params(location, accuracy=500, method='rect')

从研究范围生成栅格参数

**输入**

locationbounds(List) or shape(GeoDataFrame)
    在哪生成栅格 如果是生成范围的边界bounds，则内容为[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 如果是面要素，则必须是GeoDataFrame
accuracy : number
    栅格大小（米）
method : str
    `rect`方形, `tri`三角形或`hexa`六边形


**输出**

params : list or dict
    栅格参数

.. function:: transbigdata.GPS_to_grid(lon, lat, params)

GPS数据对应栅格编号。输入数据的经纬度列与栅格参数，输出对应的栅格编号

**输入**

lon : Series
    经度列
lat : Series
    纬度列
params : list or dict
    栅格参数

**输出**

方形栅格输出:
[LONCOL,LATCOL] : list
    栅格编号两列

三角形、六边形栅格输出:
[loncol_1,loncol_2,loncol_3] : list
    栅格编号三列

.. function:: transbigdata.grid_to_centre(gridid, params)

栅格编号对应栅格中心点经纬度。输入数据的栅格编号与栅格参数，输出对应的栅格中心点

**输入**

gridid : list
    方形栅格:
    [LONCOL,LATCOL] : list
        栅格编号两列
    三角形、六边形栅格:
    [loncol_1,loncol_2,loncol_3] : list
        栅格编号三列

params : list or dict
    栅格参数

**输出**

HBLON : Series
    栅格中心点经度列
HBLAT : Series
    栅格中心点纬度列

.. function:: transbigdata.grid_to_polygon(gridid, params)

栅格编号生成栅格的地理信息列。输入数据的栅格编号与栅格参数，输出对应的地理信息列

**输入**

gridid : list
    方形栅格:
    [LONCOL,LATCOL] : list
        栅格编号两列
    三角形、六边形栅格:
    [loncol_1,loncol_2,loncol_3] : list
        栅格编号三列

params : list or dict
    栅格参数

**输出**

geometry : Series
    栅格的矢量图形列

.. function:: transbigdata.grid_to_area(data, shape, params, col=['LONCOL', 'LATCOL'])

输入数据（带有栅格经纬度编号两列），矢量图形与栅格化参数，输出数据栅格并对应矢量图形。

**输入**

data : DataFrame
    数据,（带有栅格经纬度编号列）
shape : GeoDataFrame
    矢量图形
params : list or dict
    栅格参数
col : List
    列名，方型栅格下为[LONCOL,LATCOL]
    三角形、六边形栅格为[loncol_1,loncol_2,loncol_3]

**输出**

data1 : DataFrame
    数据，对应至矢量图形
    
.. function:: transbigdata.grid_to_params(grid)

从栅格数据重新生成栅格参数，目前仅支持方形栅格

**输入**

grid : GeoDataFrame
    transbigdata中生成的方形栅格


**输出**

params : list or dict
    栅格参数

栅格参数的优化
=====================

.. function:: transbigdata.grid_params_optimize(data,initialparams,col=['uid','lon','lat'],optmethod='centerdist',printlog=False,sample=0,pop=15,max_iter=50,w=0.1,c1=0.5,c2=0.5)

提供了三种优化栅格化参数的方法

**输入**

data : DataFrame
    轨迹数据
initialparams : List
    初始栅格化参数
col : List
    列名 [uid,lon,lat]
optmethod : str
    优化方法: centerdist, gini, gridscount
printlog : bool
    是否打印日志
sample : int
    抽样数据量，设置为0则不抽样
pop,max_iter,w,c1,c2:
    scikit-opt中PSO的参数设置，详情看：https://scikit-opt.github.io/scikit-opt/#/zh/README
    
**输出**

params_optimized : List
    优化后的栅格化参数

geohash编码
==============

geohash是一种公共域地理编码系统，它的作用是将经纬度地理位置编码为字母和数字组成的字符串，字符串也可解码为经纬度。每个字符串代表一个网格编号，字符串的长度越长则精度越高。根据\ `wiki <https://en.wikipedia.org/wiki/Geohash>`__\ ，geohash字符串长度对应精度表格如下：

========================= ======== ======== ========= ========= ========
geohash length(precision) lat bits lng bits lat error lng error km error
========================= ======== ======== ========= ========= ========
1                         2        3        ±23       ±23       ±2500
2                         5        5        ±2.8      ±5.6      ±630
3                         7        8        ±0.70     ±0.70     ±78
4                         10       10       ±0.087    ±0.18     ±20
5                         12       13       ±0.022    ±0.022    ±2.4
6                         15       15       ±0.0027   ±0.0055   ±0.61
7                         17       18       ±0.00068  ±0.00068  ±0.076
8                         20       20       ±0.000085 ±0.00017  ±0.019
========================= ======== ======== ========= ========= ========

TransBigData包中也提供了geohash的处理功能，主要包括三个函数：


.. function:: transbigdata.geohash_encode(lon,lat,precision=12)

输入经纬度与精度，输出geohash编码

**输入**

lon : Series
    经度列
lat : Series
    纬度列
precision : number
    geohash精度                       

**输出**

geohash : Series
    geohash编码列 


.. function:: transbigdata.geohash_decode(geohash)

输入geohash，输出经纬度

**输入**

geohash : Series
    geohash编码列                    

**输出**

lon : Series
    经度列
lat : Series
    纬度列

.. function:: transbigdata.geohash_togrid(geohash)

输入geohash编码，输出geohash网格的地理信息图形Series列

**输入**

geohash : Series
    geohash编码列                    

**输出**

poly : Series
    geohash的栅格列

相比TransBigData包中提供的方形栅格处理方法，geohash更慢，也无法提供自由定义的栅格大小。下面的示例展示如何利用这三个函数对数据进行geohash编码集计，并可视化

::

    import transbigdata as tbd
    import pandas as pd
    import geopandas as gpd
    #读取数据    
    data = pd.read_csv('TaxiData-Sample.csv',header = None) 
    data.columns = ['VehicleNum','time','slon','slat','OpenStatus','Speed'] 

::

    #依据经纬度geohash编码，精确度选6时，栅格大小约为±0.61km
    data['geohash'] = tbd.geohash_encode(data['slon'],data['slat'],precision=6)
    data['geohash']




.. parsed-literal::

    0         ws0btw
    1         ws0btz
    2         ws0btz
    3         ws0btz
    4         ws0by4
               ...  
    544994    ws131q
    544995    ws1313
    544996    ws131f
    544997    ws1361
    544998    ws10tq
    Name: geohash, Length: 544999, dtype: object



::

    #基于geohash编码集计
    dataagg = data.groupby(['geohash'])['VehicleNum'].count().reset_index()
    #geohash编码解码为经纬度
    dataagg['lon_geohash'],dataagg['lat_geohash'] = tbd.geohash_decode(dataagg['geohash'])
    #geohash编码生成栅格矢量图形
    dataagg['geometry'] = tbd.geohash_togrid(dataagg['geohash'])
    #转换为GeoDataFrame
    dataagg = gpd.GeoDataFrame(dataagg)
    dataagg




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
          <th>geohash</th>
          <th>VehicleNum</th>
          <th>lon_geohash</th>
          <th>lat_geohash</th>
          <th>geometry</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>w3uf3x</td>
          <td>1</td>
          <td>108.</td>
          <td>10.28</td>
          <td>POLYGON ((107.99561 10.27771, 107.99561 10.283...</td>
        </tr>
        <tr>
          <th>1</th>
          <td>webzz6</td>
          <td>12</td>
          <td>113.9</td>
          <td>22.47</td>
          <td>POLYGON ((113.87329 22.46704, 113.87329 22.472...</td>
        </tr>
        <tr>
          <th>2</th>
          <td>webzz7</td>
          <td>21</td>
          <td>113.9</td>
          <td>22.48</td>
          <td>POLYGON ((113.87329 22.47253, 113.87329 22.478...</td>
        </tr>
        <tr>
          <th>3</th>
          <td>webzzd</td>
          <td>1</td>
          <td>113.9</td>
          <td>22.47</td>
          <td>POLYGON ((113.88428 22.46704, 113.88428 22.472...</td>
        </tr>
        <tr>
          <th>4</th>
          <td>webzzf</td>
          <td>2</td>
          <td>113.9</td>
          <td>22.47</td>
          <td>POLYGON ((113.89526 22.46704, 113.89526 22.472...</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>2022</th>
          <td>ws1d9u</td>
          <td>1</td>
          <td>114.7</td>
          <td>22.96</td>
          <td>POLYGON ((114.68628 22.96143, 114.68628 22.966...</td>
        </tr>
        <tr>
          <th>2023</th>
          <td>ws1ddh</td>
          <td>6</td>
          <td>114.7</td>
          <td>22.96</td>
          <td>POLYGON ((114.69727 22.96143, 114.69727 22.966...</td>
        </tr>
        <tr>
          <th>2024</th>
          <td>ws1ddj</td>
          <td>2</td>
          <td>114.7</td>
          <td>22.97</td>
          <td>POLYGON ((114.69727 22.96692, 114.69727 22.972...</td>
        </tr>
        <tr>
          <th>2025</th>
          <td>ws1ddm</td>
          <td>4</td>
          <td>114.7</td>
          <td>22.97</td>
          <td>POLYGON ((114.70825 22.96692, 114.70825 22.972...</td>
        </tr>
        <tr>
          <th>2026</th>
          <td>ws1ddq</td>
          <td>7</td>
          <td>114.7</td>
          <td>22.98</td>
          <td>POLYGON ((114.70825 22.97241, 114.70825 22.977...</td>
        </tr>
      </tbody>
    </table>
    <p>2027 rows × 5 columns</p>
    </div>



::

    #设定绘图边界
    bounds = [113.6,22.4,114.8,22.9]
    #创建图框
    import matplotlib.pyplot as plt
    import plot_map
    fig =plt.figure(1,(8,8),dpi=280)
    ax =plt.subplot(111)
    plt.sca(ax)
    #添加地图底图
    tbd.plot_map(plt,bounds,zoom = 12,style = 4)
    #绘制colorbar
    cax = plt.axes([0.05, 0.33, 0.02, 0.3])
    plt.title('count')
    plt.sca(ax)
    #绘制geohash的栅格集计
    dataagg.plot(ax = ax,column = 'VehicleNum',cax = cax,legend = True)
    #添加比例尺和指北针
    tbd.plotscale(ax,bounds = bounds,textsize = 10,compasssize = 1,accuracy = 2000,rect = [0.06,0.03],zorder = 10)
    plt.axis('off')
    plt.xlim(bounds[0],bounds[2])
    plt.ylim(bounds[1],bounds[3])
    plt.show()



.. image:: geohash/output_9_0.png


旧方法
=============================

.. function:: transbigdata.rect_grids(location,accuracy = 500,params='auto')

该方法已经更名为`area_to_grid <https://transbigdata.readthedocs.io/en/latest/grids.html#transbigdata.area_to_grid>`_
生成研究范围内的方形栅格

**输入**

location : bounds(List) or shape(GeoDataFrame)
    在哪生成栅格
    如果是生成范围的边界bounds，则内容为[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 
    如果是面要素，则必须是GeoDataFrame
accuracy : number
    栅格大小（米）
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0
    默认值为auto自动生成，当给定栅格参数时，栅格大小将从栅格参数中计算得到                   
    

**输出**

grid : GeoDataFrame
    栅格的GeoDataFrame，其中LONCOL与LATCOL为栅格的编号，HBLON与HBLAT为栅格的中心点坐标 
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0


::

    #设定范围
    bounds = [lon1,lat1,lon2,lat2]
    grid,params = tbd.rect_grids(bounds,accuracy = 500)


.. function:: transbigdata.grid_params(bounds,accuracy = 500)

该方法已经更名为`area_to_params <https://transbigdata.readthedocs.io/en/latest/grids.html#transbigdata.area_to_params>`_
栅格参数获取

**输入**

bounds : List
    生成范围的边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 
accuracy : number
    栅格大小（米）
                                           

**输出**

params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0


::

    bounds = [113.75194,22.447837,114.624187,22.864748]
    tbd.grid_params(bounds,accuracy = 500)




.. function:: transbigdata.GPS_to_grids(lon,lat,params)

该方法已经更名为`GPS_to_grid <https://transbigdata.readthedocs.io/en/latest/grids.html#transbigdata.GPS_to_grid>`_
GPS数据对应栅格编号。输入数据的经纬度列与栅格参数，输出对应的栅格编号

**输入**

lon : Series
    经度列
lat : Series
    纬度列
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0
                                           
**输出**

LONCOL : Series
    经度栅格编号列
LATCOL : Series
    纬度栅格编号列

::

    data['LONCOL'],data['LATCOL'] = tbd.GPS_to_grids(data['Lng'],data['Lat'],params)

.. function:: transbigdata.grids_centre(loncol,latcol,params)

该方法已经更名为`grid_to_centre <https://transbigdata.readthedocs.io/en/latest/grids.html#transbigdata.grid_to_centre>`_
栅格编号对应栅格中心点经纬度。输入数据的栅格编号与栅格参数，输出对应的栅格中心点

**输入**

LONCOL : Series
    经度栅格编号列
LATCOL : Series
    纬度栅格编号列
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0
                                           
**输出**

HBLON : Series
    栅格中心点经度列
HBLAT : Series
    栅格中心点纬度列


::

    data['HBLON'],data['HBLAT'] = tbd.grids_centre(data['LONCOL'],data['LATCOL'],params)

.. function:: transbigdata.gridid_to_polygon(loncol,latcol,params)

该方法已经更名为`grid_to_polygon <https://transbigdata.readthedocs.io/en/latest/grids.html#transbigdata.grid_to_polygon>`_
栅格编号生成栅格的地理信息列。输入数据的栅格编号与栅格参数，输出对应的地理信息列

**输入**

LONCOL : Series
    经度栅格编号列
LATCOL : Series
    纬度栅格编号列
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0
                                           
**输出**

geometry : Series
    栅格的矢量图形列

::

    data['geometry'] = tbd.gridid_to_polygon(data['LONCOL'],data['LATCOL'],params)

.. function:: transbigdata.gridid_sjoin_shape(data,shape,params,col = ['LONCOL','LATCOL'])

该方法已经更名为`grid_to_area <https://transbigdata.readthedocs.io/en/latest/grids.html#transbigdata.grid_to_area>`_
输入数据（带有栅格经纬度编号两列），矢量图形与栅格化参数，输出数据栅格并对应矢量图形。

**输入**

data : DataFrame
    数据,（带有栅格经纬度编号两列）
shape : GeoDataFrame
    矢量图形
params : List
    栅格化参数
col : List
    列名，[经度栅格编号，纬度栅格编号]

**输出**

data1 : DataFrame
    数据栅格并对应矢量图形


.. function:: transbigdata.regenerate_params(grid):

该方法已经更名为`grid_to_params <https://transbigdata.readthedocs.io/en/latest/grids.html#transbigdata.grid_to_params>`_
从栅格数据重新生成栅格参数 

**输入**  
grid : GeoDataFrame  
    transbigdata中生成的grid                 

**输出**  
params : List  
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0  


.. function:: transbigdata.GPS_to_grids_tri(lon, lat, params)

GPS数据对应栅格编号。输入数据的经纬度列与栅格参数，输出对应的三角边形栅格编号

**输入**

lon : Series
    经度列
lat : Series
    纬度列
params : List
    栅格参数与方形栅格一致，生成栅格参数指定的距离将成为三角形的边长
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0
    

**输出**

gridid : Series
    三角边形栅格编号


.. function:: transbigdata.gridid_to_polygon_tri(gridid, params)

栅格编号生成栅格的地理信息列。输入数据的栅格编号与栅格参数，输出对应的地理信息列

**输入**

gridid : Series
    栅格编号列
params : List
    栅格参数与方形栅格一致，生成栅格参数指定的距离将成为三角形的边长
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0
   

**输出**

geometry : Series
    栅格的矢量图形列

::

    
    #将GPS数据匹配至三角形栅格
    data['gridid'] = tbd.GPS_to_grids_tri(data['lon'],data['lat'],params)
    #生成几何图形
    grid_agg['geometry'] = tbd.gridid_to_polygon_tri(grid_agg['gridid'],params)

.. image:: _static/WechatIMG2459.jpeg
   :height: 200


.. function:: transbigdata.GPS_to_grids_hexa(lon, lat, params)

GPS数据对应栅格编号。输入数据的经纬度列与栅格参数，输出对应的六边形栅格编号

**输入**

lon : Series
    经度列
lat : Series
    纬度列
params : List
    栅格参数与方形栅格一致，生成栅格参数指定的距离将成为六边形的边长
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0
   
**输出**

gridid : Series
    六边形栅格编号

.. function:: transbigdata.gridid_to_polygon_hexa(gridid, params)

栅格编号生成栅格的地理信息列。输入数据的栅格编号与栅格参数，输出对应的地理信息列

**输入**

gridid : Series
    六边形栅格编号
params : List
    栅格参数与方形栅格一致，生成栅格参数指定的距离将成为六边形的边长
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，或(lonStart,latStart,deltaLon,deltaLat,theta)，其中，lonStart,latStart分别为栅格左下角坐标，deltaLon,deltaLat为单个栅格的经纬度长宽，theta为栅格的角度，不给则默认为0

**输出**

geometry : Series
    栅格的矢量图形列

::

    
    #将GPS数据匹配至六边形栅格
    data['gridid'] = tbd.GPS_to_grids_hexa(data['lon'],data['lat'],params)
    #生成几何图形
    grid_agg['geometry'] = tbd.gridid_to_polygon_hexa(grid_agg['gridid'],params)

.. image:: _static/WechatIMG2470.jpeg
   :height: 200