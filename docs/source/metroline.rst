
******************************
公交地铁网络拓扑建模
******************************

.. function:: transbigdata.split_subwayline(line,stop)

用公交/地铁站点对公交/地铁线进行切分，得到断面

**输入**

line : GeoDataFrame
    公交/地铁线路
stop : GeoDataFrame
    公交/地铁站点

**输出**

metro_line_splited : GeoDataFrame
    生成的断面线型