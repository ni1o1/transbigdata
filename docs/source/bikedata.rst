.. _bikedata:


******************************
共享单车数据处理
******************************

.. function:: transbigdata.bikedata_to_od(data,col = ['BIKE_ID','DATA_TIME','LONGITUDE','LATITUDE','LOCK_STATUS'],startend = None)

输入共享单车订单数据（只在开关锁时产生数据），指定列名，提取其中的骑行与停车信息

**输入**

data : DataFrame
    共享单车订单数据，只在开关锁时产生数据
col : List
    列名，顺序不能变，分别为[单车ID,时间,经度,纬度,锁状态]，例如['BIKE_ID','DATA_TIME','LONGITUDE','LATITUDE','LOCK_STATUS']
startend : List
    传入的为[开始时间,结束时间]，如['2018-08-27 00:00:00','2018-08-28 00:00:00']。
    如传入，则考虑（观测时段开始时到单车第一次出现）与（单车最后一次出现到观测时段结束）的骑行与停车情况。
    
**输出**

move_data : DataFrame
    骑行订单数据
stop_data : DataFrame
    停车数据