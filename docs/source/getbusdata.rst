
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
