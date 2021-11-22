.. _odprocess:


***************
数据聚合集计
***************

数据集计
==========

.. function:: transbigdata.dataagg(data,shape,col = ['Lng','Lat','count'],accuracy=500)

数据集计至小区

**输入**

data : DataFrame
    数据
shape : GeoDataFrame
	小区
col : List
    可传入经纬度两列，如['Lng','Lat']，此时每一列权重为1。也可以传入经纬度和计数列三列，如['Lng','Lat','count']
accuracy : number
    计算原理是先栅格化后集计，这里定义栅格大小，越小精度越高

**输出**

aggresult : GeoDataFrame
    小区，其中count列为统计结果
data1 : DataFrame
    数据，对应上了小区

OD集计
==========

.. function:: transbigdata.odagg_grid(oddata,params,col = ['slon','slat','elon','elat'],arrow = False,**kwargs)


OD集计与地理信息生成（栅格）。输入OD数据（每一行数据是一个出行），栅格化OD并集计后生成OD的GeoDataFrame

**输入**

oddata : DataFrame 
    OD数据
col : List
    起终点列名,['slon','slat','elon','elat']，此时每一列权重为1。
    也可以传入权重列，如['slon','slat','elon','elat','count']
params : List
    栅格参数(lonStart,latStart,deltaLon,deltaLat)，分别为栅格左下角坐标与单个栅格的经纬度长宽
arrow : bool
    生成的OD地理线型是否包含箭头

**输出**

oddata1 : GeoDataFrame 
    集计后生成OD的GeoDataFrame

.. function:: transbigdata.odagg_shape(oddata,shape,col = ['slon','slat','elon','elat'],params = None,round_accuracy = 6,arrow = False,**kwargs)

OD集计与地理信息生成（小区集计）。输入OD数据（每一行数据是一个出行），栅格化OD并集计后生成OD的GeoDataFrame

**输入**

oddata : DataFrame 
    OD数据
shape : GeoDataFrame
    集计小区的GeoDataFrame
col : List   
    起终点列名,['slon','slat','elon','elat']，此时每一列权重为1。
    也可以传入权重列，如['slon','slat','elon','elat','count']
params : List 
    栅格化参数，如果传入，则先栅格化后以栅格中心点匹配小区，如果不传入，则直接以经纬度匹配。在数据量大时，用栅格化进行匹配速度会极大提升
round_accuracy : number
    集计时经纬度取小数位数
arrow : bool       
    生成的OD地理线型是否包含箭头

**输出**

oddata1 : GeoDataFrame 
    集计后生成OD的GeoDataFrame


