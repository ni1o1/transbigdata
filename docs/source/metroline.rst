
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


.. function:: transbigdata.metro_network(stop,traveltime = 3,transfertime = 5,nxgraph = True)

输入站点信息，输出网络信息，该方法依赖于NetworkX

**输入**

stop : GeoDataFrame
    公交站点
traveltime : number
    每个轨道断面的出行时长
transfertime : number
    每个轨道换乘的时长
nxgraph : bool
    默认True，如果True则直接输出由NetworkX构建的网络G，如果为False，则输出网络的边edge1,edge2,和节点node
    
**输出**

G : networkx.classes.graph.Graph
    networkx构建的网络G，nxgraph参数为True时只输出这个
edge1 : DataFrame
    轨道断面的边，nxgraph参数为False时输出这个
edge2 : DataFrame
    轨道换乘的边，nxgraph参数为False时输出这个
node : List
    网络节点，nxgraph参数为False时输出这个