.. _taxigps:


******************************
出租车GPS数据处理
******************************

.. function:: transbigdata.taxigps_to_od(data,col = ['VehicleNum','Stime','Lng','Lat','OpenStatus'])

出租车OD提取算法，输入出租车GPS数据,提取OD

**输入**

data : DataFrame
	出租车GPS数据（清洗好的）
col : List            
	数据中各列列名，需要按顺序[车辆id，时间，经度，纬度，载客状态]

.. function:: transbigdata.taxigps_traj_point(data,oddata,col=['Vehicleid', 'Time', 'Lng', 'Lat', 'OpenStatus'])

输入出租车数据与OD数据，提取载客与空载的行驶路径点

**输入**

data : DataFrame
    出租车GPS数据，字段名由col变量指定
oddata : DataFrame
    出租车OD数据
col : List
    列名，按[车辆ID,时间,经度,纬度,载客状态]的顺序

**输出**

data_deliver : DataFrame
    载客轨迹点
data_idle : DataFrame
    空载轨迹点
