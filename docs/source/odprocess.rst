.. _odprocess:


***************
OD处理
***************


.. function:: transbigdata.odagg_grid(oddata,params,col = ['slon','slat','elon','elat'],arrow = False,**kwargs)


OD集计与地理信息生成（栅格）。

=========== ===========
参数         描述                                                         
=========== ===========
oddata      OD数据
col         起终点列名
params      栅格化参数
arrow       生成的OD地理线型是否包含箭头
=========== ===========    

输入OD数据（每一行数据是一个出行），栅格化OD并集计后生成OD的GeoDataFrame


.. function:: transbigdata.odagg_shape(oddata,shape,col = ['slon','slat','elon','elat'],params = None,round_accuracy = 6,arrow = False,**kwargs)

OD集计与地理信息生成（小区集计）。

============== ===========
参数              描述                                                         
============== ===========
oddata          OD数据
shape           集计小区的GeoDataFrame
col             起终点列名
params          栅格化参数，如果传入，则先栅格化后以栅格中心点匹配小区，如果不传入，则直接以经纬度匹配。在数据量大时，用栅格化进行匹配速度会极大提升
round_accuracy  集计时经纬度取小数位数
arrow           生成的OD地理线型是否包含箭头
============== ===========

输入OD数据（每一行数据是一个出行），栅格化OD并集计后生成OD的GeoDataFrame
