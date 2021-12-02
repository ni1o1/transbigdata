[English](README.md) 中文版

# TransBigData 针对交通时空大数据处理的Python包

<img src="https://github.com/ni1o1/transbigdata/raw/main/docs/source/_static/logo-wordmark-dark.png" style="width:550px">

[![Documentation Status](https://readthedocs.org/projects/transbigdata/badge/?version=latest)](https://transbigdata.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/transbigdata.svg)](https://badge.fury.io/py/transbigdata) ![PyPI - Downloads](https://img.shields.io/pypi/dm/transbigdata) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/ni1o1/transbigdata) [![bilibili](https://img.shields.io/badge/bilibili-%E5%90%8C%E6%B5%8E%E5%B0%8F%E6%97%AD%E5%AD%A6%E9%95%BF-green.svg)](https://space.bilibili.com/3051484)  


`TransBigData`是一个为交通时空大数据处理、分析和可视化而开发的Python包。`TransBigData`为处理常见的交通时空大数据（如出租车GPS数据、共享单车数据和公交车GPS数据）提供了快速而简洁的方法。`TransBigData`为交通时空大数据分析的各个阶段提供了多种处理方法,代码简洁、高效、灵活、易用，可以用简洁的代码实现复杂的数据任务。

对于一些特定类型的数据，`TransBigData`还提供了针对特定需求的工具，如从出租车GPS数据中提取出租车行程的起点和终点信息（OD），从公交车GPS数据中识别到离站信息。该包的最新稳定版本可以通过pip安装，完整的文档可以查看：[TransBigData的说明文档](https://transbigdata.readthedocs.io/zh_CN/latest/)

**技术特点**

* 面向交通时空大数据分析不同阶段的处理需求提供不同处理功能。
* 代码简洁、高效、灵活、易用，通过简短的代码即可实现复杂的数据任务。


**主要功能**

目前，`TransBigData`主要提供以下方法。

* **数据质量分析**: 提供快速获取数据集一般信息的方法，包括数据量、时间段和采样间隔。
* **数据预处理**: 提供清洗多种类型的数据错误的方法。
* **数据栅格化**: 提供在研究区域内生成多种类型的地理网格（矩形网格、六角形网格）的方法。提供快速算法将GPS数据映射到生成的网格上。
* **数据聚合集计**: 提供将GPS数据和OD数据聚合到地理多边形的方法。
* **数据可视化**: 内置的可视化功能，利用可视化包keplergl，用简单的代码在Jupyter笔记本上交互式地可视化数据。
* **轨迹数据处理**: 提供处理轨迹数据的方法，包括从GPS点生成轨迹线型，轨迹增密等。
* **地图底图**: 提供在matplotlib上显示Mapbox地图底图的方法。

## 安装

在安装`TransBigData`之前，请确保已经安装了可用的geopandas包：https://geopandas.org/index.html  
如果你已经安装了geopandas，则直接在命令提示符中运行下面代码即可安装

    pip install -U transbigdata


## 使用

下面例子展示如何使用`TransBigData`工具快速地从出租车GPS数据中提取出行OD:

    #导入TransBigData包
    import transbigdata as tbd
    #读取数据    
    import pandas as pd
    data = pd.read_csv('TaxiData-Sample.csv',header = None) 
    data.columns = ['VehicleNum','time','slon','slat','OpenStatus','Speed'] 
    data

<img src="https://github.com/ni1o1/transbigdata/raw/main/docs/source/_static/WX20211021-192131@2x.png" style="height:300px">

使用`transbigdata.taxigps_to_od`方法，传入对应的列名，即可提取出行OD:

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

## 相关链接

* 小旭学长的b站： https://space.bilibili.com/3051484
* 小旭学长的七天入门交通时空大数据分析课程（零基础免费课）： https://www.lifangshuju.com/#/introduce/166  
* 小旭学长的交通时空大数据分析课程： https://www.lifangshuju.com/#/introduce/154  
* 小旭学长的数据可视化课程： https://www.lifangshuju.com/#/introduce/165  
* 本项目的github页面： https://github.com/ni1o1/transbigdata/  
* 有bug请在这个页面提交： https://github.com/ni1o1/transbigdata/issues  

## 引用

而如果你想要引用这个 GitHub 仓库，可以使用如下的 bibtex：

```
@misc{transbigdata,
  author = {Qing Yu},
  title = {TransBigData},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub Repository},
  howpublished = {\url{https://github.com/ni1o1/transbigdata}},
}
```
