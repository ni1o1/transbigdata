.. _preprocess:


******************************
数据预处理
******************************


各类数据通用的预处理
============================

.. function:: transbigdata.clean_same(data,col = ['VehicleNum','Time','Lng','Lat'])

删除信息与前后数据相同的数据以减少数据量
如：某个体连续n条数据除了时间以外其他信息都相同，则可以只保留首末两条数据

**输入**

data : DataFrame
    数据
col : List
    列名，按[个体ID,时间,经度,纬度]的顺序，可以传入更多列。会以时间排序，再判断除了时间以外其他列的信息

**输出**

data1 : DataFrame
    清洗后的数据

.. function:: transbigdata.clean_drift(data,col = ['VehicleNum','Time','Lng','Lat'],speedlimit = 80)

删除漂移数据。条件是，此数据与前后的速度都大于speedlimit，但前后数据之间的速度却小于speedlimit。
传入的数据中时间列如果为datetime格式则计算效率更快

**输入**

data : DataFrame
    数据
col : List
    列名，按[个体ID,时间,经度,纬度]的顺序

**输出**

data1 : DataFrame
    研究范围内的数据


.. function:: transbigdata.clean_outofbounds(data,bounds,col = ['Lng','Lat'])

输入研究范围的左下右上经纬度坐标，剔除超出研究范围的数据

**输入**

data : DataFrame
    数据
bounds : List    
    研究范围的左下右上经纬度坐标，顺序为[lon1,lat1,lon2,lat2]
col : List
    经纬度列名

**输出**

data1 : DataFrame
    研究范围内的数据


.. function:: transbigdata.clean_outofshape(data,shape,col = ['Lng','Lat'],accuracy=500)

输入研究范围的GeoDataFrame，剔除超出研究区域的数据

**输入**

data : DataFrame
    数据
shape : GeoDataFrame    
    研究范围的GeoDataFrame
col : List
    经纬度列名
accuracy : number
    计算原理是先栅格化后剔除，这里定义栅格大小，越小精度越高

**输出**

data1 : DataFrame
    研究范围内的数据

.. function:: transbigdata.id_reindex(data,col,new = False,timegap = None,timecol = None,suffix = '_new',sample = None)

对数据的ID列重新编号

**输入**

data : DataFrame
    数据 
col : str
    要重新编号的ID列名
new : bool
    False，相同ID的新编号相同；True，依据表中的顺序，ID再次出现则编号不同
timegap : number
    如果个体在一段时间内没出现（timegap为时间阈值），则编号为新的个体。此参数与timecol同时设定才有效果。
timecol : str
    时间字段名称，此参数与timegap同时设定才有效果。
suffix : str
    新编号列名的后缀，设置为False时替代原有列名
sample : int
    传入数值，对重新编号的个体进行抽样
    
**输出**

data1 : DataFrame
    重新编号的数据

.. function:: transbigdata.id_reindex_disgap(data,col = ['uid','lon','lat'],disgap=1000,suffix = '_new')

对数据的ID列重新编号，如果相邻两条记录超过距离，则编号为新id

**输入**

data : DataFrame
    数据 
col : str
    要重新编号的ID列名
disgap : number
    如果个体轨迹超过一定距离，则编号为新的个体。
suffix : str
    新编号列名的后缀
    
**输出**

data1 : DataFrame
    重新编号的数据

轨迹清洗
==================
.. function:: transbigdata.clean_traj(data,col = ['uid','str_time','lon','lat'],tripgap = 1800,disgap = 50000,speedlimit = 80)

轨迹数据清洗组合拳

**输入**

data : DataFrame
    轨迹数据
col : List
    列名，以[个体id,时间,经度,纬度]排列
tripgap : number
    多长的时间视为新的出行
disgap : number
    多长距离视为新的出行
speedlimit : number
    车速限制

**输出**

data1 : DataFrame
    清洗后的数据


出租车数据的预处理
==================

.. function:: transbigdata.clean_taxi_status(data,col = ['VehicleNum','Time','OpenStatus'],timelimit = None)

删除出租车数据中载客状态瞬间变化的记录，这些记录的存在会影响出行订单判断。
判断条件为:如果对同一辆车，上一条记录与下一条记录的载客状态都与本条记录不同，则本条记录应该删去

**输入**

data : DataFrame
    数据
col : List
    列名，按[车辆ID,时间,载客状态]的顺序
timelimit : number
    可选，单位为秒，上一条记录与下一条记录的时间小于该时间阈值才予以删除

**输出**

data1 : DataFrame
    清洗后的数据