.. _quality:


******************************
数据质量
******************************


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