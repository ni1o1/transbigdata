.. transbigdata documentation master file, created by
   sphinx-quickstart on Thu Oct 21 14:41:25 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TransBigData 为交通时空大数据而生
========================================

TransBigData工具针对时空大数据处理而开发，集成了交通时空大数据处理过程中常用的方法，例如：

* 栅格渔网划分
* 地图底图与指北针添加
* 经纬度坐标转换与距离换算
* 点与点、点与线的最近邻匹配
* 各类常见数据的快速清洗与挖掘（开发中）

使用
==================
下面例子展示如何使用TransBigData工具快速地从出租车GPS数据中提取出行OD::

    #导入TransBigData包
    import transbigdata
    #读取数据    
    import pandas as pd
    data = pd.read_csv('TaxiData-Sample.csv',header = None) 
    data.columns = ['VehicleNum','time','slon','slat','OpenStatus','Speed'] 
    data

.. image:: _static/WX20211021-192131@2x.png
   :height: 300

使用transbigdata.taxigps_to_od方法，传入对应的列名，即可提取出行OD::

    #从GPS数据提取OD
    oddata = transbigdata.taxigps_to_od(data,col = ['VehicleNum','time','slon','slat','OpenStatus'])
    oddata

.. image:: _static/WX20211021-190104@2x.png
   :height: 300

对提取出的OD进行OD的栅格集计::

    #定义研究范围
   bounds = [113.6,22.4,114.8,22.9]
   #输入研究范围边界bounds与栅格宽度accuracy，获取栅格化参数
   params = transbigdata.grid_params(bounds = bounds,accuracy = 1500)
   #栅格化OD并集计
   od_gdf = transbigdata.odagg_grid(oddata,params)
   od_gdf.plot(column = 'count')

.. image:: _static/WX20211021-190524@2x.png
   :height: 300

文档目录
==================

.. toctree::
   :maxdepth: 2

   getting_started.rst
   example.rst
   grids.rst
   odprocess.rst
   ckdnearest.rst
   plot_map.rst
   CoordinatesConverter.rst
   taxigps.rst


