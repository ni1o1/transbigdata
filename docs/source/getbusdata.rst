
******************************
数据获取
******************************

获取公交线路
=============================

.. function:: transbigdata.getbusdata(city,keywords,accurate=True)

通过输入城市与关键词，获取公交线路的线型与站点

**输入**

city : str
    城市
keywords : str或List
    关键词，线路名称，支持单个关键词或多个关键词
accurate : bool
    是否精确匹配，默认True

**输出**

data : GeoDataFrame
    生成的公交线路
stop : GeoDataFrame
    生成的公交站点

获取行政区划
=============================

.. function:: transbigdata.getadmin(keyword,ak,jscode='',subdistricts = False)

输入关键词与高德ak，抓取行政区划gis

**输入**

keywords : str
    关键词，可以是名称，如"深圳市"，或行政区划编号，如440500
ak : str
    高德ak
jscode : str
    安全密钥，自2021年12月02日升级，升级之后所申请的 key 必须配备安全密钥 jscode 一起使用
subdistricts : bool
    是否输出子行政区划的信息

**输出**

admin : GeoDataFrame
    行政区划信息
districts : DataFrame
    子行政区划的信息，利用这个可以进一步抓下一级的行政区划

获取等时圈
=============================

.. function:: transbigdata.get_isochrone_amap(lon,lat,reachtime,ak,jscode='',mode=2)

获取高德地图等时圈，支持`公交`、`地铁`、`公交+地铁`三种模式

**输入**

lon : float
    起点经度(WGS84)
lat : float
    起点纬度(WGS84)
reachtime : number
    等时圈时间
ak : str
    高德地图ak
jscode : str
    安全密钥，自2021年12月02日升级，升级之后所申请的 key 必须配备安全密钥 jscode 一起使用
mode : int or str
    出行方式，0`公交`、1`地铁`、2`公交+地铁`

**输出**

isochrone : GeoDataFrame
    等时圈的GeoDataFrame(WGS84)

.. function:: transbigdata.get_isochrone_mapbox(lon,lat,reachtime,access_token='auto',mode = 'driving')

获取mapbox地图等时圈，支持驾车、步行、骑行

**输入**

lon : float
    起点经度(WGS84)
lat : float
    起点纬度(WGS84)
reachtime : number
    等时圈时间
access_token : str
    Mapbox的access token，如果设置为 `auto`则会自动读取已经保存的access token
mode : bool
    出行方式，取值为 `driving`， `walking` 或 `cycling`

**输出**

isochrone : GeoDataFrame
    等时圈的GeoDataFrame(WGS84)