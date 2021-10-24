.. _grids:


***************
栅格化
***************

方形栅格渔网的生成与对应
=============================

.. function:: transbigdata.rect_grids(bounds,accuracy = 500)

生成研究范围内的方形栅格

**输入**

bounds : List
    生成范围的边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 
accuracy : number
    栅格大小（米）
                                           

**输出**

grid : GeoDataFrame
    栅格的GeoDataFrame，其中LONCOL与LATCOL为栅格的编号，HBLON与HBLAT为栅格的中心点坐标 
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽


::

    #设定范围
    bounds = [lon1,lat1,lon2,lat2]
    grid,params = tbd.rect_grids(bounds,accuracy = 500)


.. function:: transbigdata.grid_params(bounds,accuracy = 500)

栅格参数获取

**输入**

bounds : List
    生成范围的边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 
accuracy : number
    栅格大小（米）
                                           

**输出**

params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽


::

    bounds = [113.75194,22.447837,114.624187,22.864748]
    tbd.grid_params(bounds,accuracy = 500)

.. function:: transbigdata.GPS_to_grids(lon,lat,params)

GPS数据对应栅格编号。输入数据的经纬度列与栅格参数，输出对应的栅格编号

**输入**

lon : Series
    经度列
lat : Series
    纬度列
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽
                                           
**输出**

LONCOL : Series
    经度栅格编号列
LATCOL : Series
    纬度栅格编号列

::

    data['LONCOL'],data['LATCOL'] = tbd.GPS_to_grids(data['Lng'],data['Lat'],params)

.. function:: transbigdata.grids_centre(loncol,latcol,params)

栅格编号对应栅格中心点经纬度。输入数据的栅格编号与栅格参数，输出对应的栅格中心点

**输入**

LONCOL : Series
    经度栅格编号列
LATCOL : Series
    纬度栅格编号列
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽
                                           
**输出**

HBLON : Series
    栅格中心点经度列
HBLAT : Series
    栅格中心点纬度列


::

    data['HBLON'],data['HBLAT'] = tbd.grids_centre(data['LONCOL'],data['LATCOL'],params)

.. function:: transbigdata.gridid_to_polygon(loncol,latcol,params)

栅格编号生成栅格的地理信息列。输入数据的栅格编号与栅格参数，输出对应的地理信息列

**输入**

LONCOL : Series
    经度栅格编号列
LATCOL : Series
    纬度栅格编号列
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽
                                           
**输出**

geometry : Series
    栅格的矢量图形列

::

    data['geometry'] = tbd.gridid_to_polygon(data['LONCOL'],data['LATCOL'],params)

.. function:: transbigdata.gridid_sjoin_shape(data,shape,params,col = ['LONCOL','LATCOL'])

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


六边形渔网生成
=============================

.. function:: transbigdata.hexagon_grids(bounds,accuracy = 500)

生成研究范围内的六边形渔网。

**输入**

bounds : List
    生成范围的边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 
accuracy : number
    六边形的边长（米）
                                           
**输出**

hexagon : GeoDataFrame
    六边形渔网的矢量图形

::

    
    #设定范围
    bounds = [113.6,22.4,114.8,22.9]
    hexagon = tbd.hexagon_grids(bounds,accuracy = 5000)
    hexagon.plot()

.. image:: _static/WX20211021-201747@2x.png
   :height: 200
