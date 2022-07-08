.. _mobile:


******************************
手机GPS/轨迹/话单/信令数据处理
******************************

.. function:: transbigdata.mobile_stay_move(data, params,col=['ID', 'dataTime', 'longitude', 'latitude'],activitytime=1800)

输入轨迹数据与栅格参数，识别停留和出行

**输入**

data : DataFrame
    轨迹数据，连续追踪的个体GPS
params : List
    栅格化参数
col : List
    列名，顺序为 ['ID','dataTime','longitude','latitude']
activitytime : Number
    停留点的最短持续时间

**输出**

stay : DataFrame
    停留数据
move : DataFrame
    出行数据


.. function:: transbigdata.mobile_stay_dutation(staydata, col=['stime', 'etime'], start_hour=8, end_hour=20)

输入停留点数据，识别白天与夜晚的持续时间

**输入**

staydata : DataFrame
    停留点数据
col : List
    列名，顺序为 ['starttime','endtime']
start_hour,end_hour : Number
    白天开始与白天结束时间（小时）

**输出**

duration_night : Series
    夜晚停留时间列（时长总和）
duration_day : Series
    白天停留时间列（时长总和）

.. function:: transbigdata.mobile_identify_home(staydata, col=['uid','stime', 'etime','LONCOL', 'LATCOL'], start_hour=8, end_hour=20 )

输入停留点数据识别居住地。规则为夜晚时段停留最长地点。

**输入**

staydata : DataFrame
    停留点数据
col : List
    列名，顺序为 ['uid','stime', 'etime', 'locationtag1', 'locationtag2', ...].
    可由多个'locationtag'列指定一个地点
start_hour, end_hour : Number
    白天开始与白天结束时间（小时）

**输出**

home : DataFrame
    居住地位置

.. function:: transbigdata.mobile_identify_work(staydata, col=['uid', 'stime', 'etime', 'LONCOL', 'LATCOL'], minhour=3, start_hour=8, end_hour=20,workdaystart=0, workdayend=4)

输入停留点数据识别工作地。规则为工作日白天时段停留最长地点（每日平均时长大于`minhour`）。

**Parameters**

staydata : DataFrame
    停留点数据
col : List
    列名，顺序为 ['uid','stime', 'etime', 'locationtag1', 'locationtag2', ...].
    可由多个'locationtag'列指定一个地点
minhour : Number
    每日平均时长大于`minhour`(小时).
workdaystart,workdayend : Number
    一周中工作日. 0 - Monday, 4 - Friday
start_hour, end_hour : Number
    白天开始与白天结束时间（小时）


**Returns**

work : DataFrame
    工作地位置

.. function:: transbigdata.mobile_plot_activity(data, col=['stime', 'etime', 'LONCOL', 'LATCOL'],figsize=(10, 5), dpi=250)

输入个体的活动数据（单一个体），绘制活动图

**输入**

data : DataFrame
    活动数据集
col : List
    列名，分别为[活动开始时间，活动结束时间，活动所在栅格经度编号，活动所在栅格纬度编号]


