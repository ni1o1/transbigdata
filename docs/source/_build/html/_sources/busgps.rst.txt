.. _busgps:


******************************
公交车GPS数据处理
******************************

.. function:: transbigdata.busgps_arriveinfo(data,line,stop,col = ['VehicleId','GPSDateTime','lon','lat','stopname'],stopbuffer = 200,mintime = 300,project_epsg = 2416,timegap = 1800,method = 'project',projectoutput = False)

输入公交GPS数据、公交线路与站点的GeoDataFrame，该方法能够识别公交的到离站信息

**输入**

data : DataFrame
    公交GPS数据，单一公交线路，且需要含有车辆ID、GPS时间、经纬度（wgs84）
line : GeoDataFrame
    公交线型的GeoDataFrame数据，单一公交线路
stop : GeoDataFrame
    公交站点的GeoDataFrame数据
col : List
    列名，按[车辆ID,时间,经度,纬度，站点名称字段]的顺序
stopbuffer : number
    米，站点的一定距离范围，车辆进入这一范围视为到站，离开则视为离站
mintime : number
    秒，短时间内公交再次到站则需要与前一次的到站数据结合一起计算到离站时间，该参数设置阈值
project_epsg : number
    匹配时会将数据转换为投影坐标系以计算距离，这里需要给定投影坐标系的epsg代号
timegap : number
    秒，清洗数据用，多长时间车辆不出现，就视为新的车辆
method : str
    公交运行图匹配方法，可选'project'或'dislimit'；
    project为直接匹配线路上最近点，匹配速度快；
    dislimit则需要考虑前面点位置，加上距离限制，匹配速度慢。
projectoutput : bool
    是否输出投影后的数据

**输出**

arrive_info : DataFrame
    公交到离站信息

.. function:: transbigdata.busgps_onewaytime(arrive_info,stop,start,end,col = ['VehicleId','stopname'])

输入到离站信息表arrive_info与站点信息表stop，计算单程耗时

**输入**

arrive_info : DataFrame
    公交到离站数据
stop : GeoDataFrame
    公交站点的GeoDataFrame数据
start : Str
    起点站名字
end : Str
    终点站名字
col : List
    字段列名[车辆ID,站点名称]


**输出**

onewaytime : DataFrame
    公交单程耗时