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
