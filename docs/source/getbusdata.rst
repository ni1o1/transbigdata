
******************************
爬虫
******************************

.. function:: transbigdata.getbusdata(city,keywords)

通过输入城市与关键词，获取公交线路的线型与站点

**输入**

city : str
    城市
keywords : List
    关键词，线路名称

**输出**

data : GeoDataFrame
    生成的公交线路
stop : GeoDataFrame
    生成的公交站点

.. function:: transbigdata.getadmin(keyword,ak,subdistricts = False)

输入关键词与高德ak，抓取行政区划gis

**输入**

keywords : str
    关键词，可以是名称，如"深圳市"，或行政区划编号，如440500
ak : str
    高德ak
subdistricts : bool
    是否输出子行政区划的信息

**输出**

admin : GeoDataFrame
    行政区划信息
districts : DataFrame
    子行政区划的信息，利用这个可以进一步抓下一级的行政区划