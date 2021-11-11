.. _traj:


******************************
轨迹处理
******************************


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

.. function:: transbigdata.points_to_traj(traj_points,col = ['Lng','Lat','ID'],timecol = None)

输入轨迹点，生成轨迹线型的GeoDataFrame

**输入**

traj_points : DataFrame
    轨迹点数据
col : List
    列名，按[经度,纬度,轨迹编号]的顺序
timecol : str
    可选，时间列的列名，如果给了则输出带有[经度,纬度,高度,时间]的geojson，可放入kepler中可视化轨迹

**输出**

traj : GeoDataFrame或json
    生成的轨迹数据，如果timecol没定义则为GeoDataFrame，否则为json

.. function:: transbigdata.dumpjson(data,path)

输入json数据，存储为文件。这个方法主要是解决numpy数值型无法兼容json包报错的问题

**输入**

data : json
    要储存的json数据
path : str
    保存的路径