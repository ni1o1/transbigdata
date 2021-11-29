.. _quality:


******************************
数据质量分析
******************************



.. function:: transbigdata.data_summary(data,col = ['Vehicleid','Time'],show_sample_duration = False)

输入数据，打印数据概况

**输入**

data : DataFrame
    轨迹点数据
col : List
    列名，按[个体ID，时间]的顺序
show_sample_duration : bool
    是否输出个体采样间隔信息
roundnum : number
    小数点取位数
    
使用方法

::

    import transbigdata as tbd
    import pandas as pd
    #读取数据    
    data = pd.read_csv('TaxiData-Sample.csv',header = None) 
    data.columns = ['Vehicleid','Time','Lng','Lat','OpenStatus','Speed']      
    data['Time'] = pd.to_datetime(data['Time'])
    #轨迹增密前的采样间隔
    tbd.data_summary(data,col = ['Vehicleid','Time','Lng','Lat'],show_sample_duration=True)

::

    数据量
    -----------------
    数据总量 : 544999 条
    个体总量 : 180 个
    个体数据量均值 : 3027.77 条
    个体数据量上四分位 : 4056.25 条
    个体数据量中位数 : 2600.5 条
    个体数据量下四分位 : 1595.75 条

    数据时间段
    -----------------
    开始时间 : 2021-11-12 00:00:00
    结束时间 : 2021-11-12 23:59:59

    个体采样间隔
    -----------------
    均值 : 28.0 秒
    上四分位 : 30.0 秒
    中位数 : 20.0 秒
    下四分位 : 15.0 秒

.. function:: transbigdata.sample_duration(data,col = ['Vehicleid','Time']):

统计数据采样间隔

**输入**

data : DataFrame
    数据
col : List
    列名，按[个体ID,时间]的顺序

**输出**

sample_duration : DataFrame
    一列的数据表，列名为duration，内容是数据的采样间隔，单位秒