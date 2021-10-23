# TransBigData 针对交通时空大数据处理的Python包

<img src="https://github.com/ni1o1/transbigdata/raw/main/docs/source/_static/logo-wordmark-dark.png" style="width:550px">

[![Build Status](https://app.travis-ci.com/ni1o1/transbigdata.svg?branch=main)](https://app.travis-ci.com/ni1o1/transbigdata) [![Documentation Status](https://readthedocs.org/projects/transbigdata/badge/?version=latest)](https://transbigdata.readthedocs.io/en/latest/?badge=latest) ![PyPI](https://img.shields.io/pypi/v/transbigdata) [![bilibili](https://img.shields.io/badge/bilibili-%E5%90%8C%E6%B5%8E%E5%B0%8F%E6%97%AD%E5%AD%A6%E9%95%BF-green.svg)](https://space.bilibili.com/3051484)  

TransBigData工具针对时空大数据处理而开发，集成了交通时空大数据处理过程中常用的方法。例如：

* 栅格渔网划分，请看[这个示例](https://github.com/ni1o1/transbigdata/blob/master/example/example-grid.ipynb)
* 地图底图与指北针添加，请看[这个示例](https://github.com/ni1o1/transbigdata/blob/master/example/example-grid.ipynb)
* 经纬度坐标转换与距离换算
* 点与点、点与线的最近邻匹配，请看[这个示例](https://github.com/ni1o1/transbigdata/blob/master/example/example-ckdnearest.ipynb)
* 各类常见数据的快速清洗与挖掘：出租车数据请看[这个示例](https://github.com/ni1o1/transbigdata/blob/master/example/example-od.ipynb)

更多细节请查看：  
[TransBigData的说明文档](https://transbigdata.readthedocs.io/en/latest/)


## 安装

    pip install -U transbigdata


## 使用

下面例子展示如何使用TransBigData工具快速地从出租车GPS数据中提取出行OD:

    #导入TransBigData包
    import transbigdata as tbd
    #读取数据    
    import pandas as pd
    data = pd.read_csv('TaxiData-Sample.csv',header = None) 
    data.columns = ['VehicleNum','time','slon','slat','OpenStatus','Speed'] 
    data

<img src="https://github.com/ni1o1/transbigdata/raw/main/docs/source/_static/WX20211021-192131@2x.png" style="height:300px">

使用transbigdata.taxigps_to_od方法，传入对应的列名，即可提取出行OD:

    #从GPS数据提取OD
    oddata = tbd.taxigps_to_od(data,col = ['VehicleNum','time','slon','slat','OpenStatus'])
    oddata

<img src="https://github.com/ni1o1/transbigdata/raw/main/docs/source/_static/WX20211021-190104@2x.png" style="height:300px">

对提取出的OD进行OD的栅格集计:

    #定义研究范围
    bounds = [113.6,22.4,114.8,22.9]
    #输入研究范围边界bounds与栅格宽度accuracy，获取栅格化参数
    params = tbd.grid_params(bounds = bounds,accuracy = 1500)
    #栅格化OD并集计
    od_gdf = tbd.odagg_grid(oddata,params)
    od_gdf.plot(column = 'count')

<img src="https://github.com/ni1o1/transbigdata/raw/main/docs/source/_static/WX20211021-190524@2x.png" style="height:300px">
