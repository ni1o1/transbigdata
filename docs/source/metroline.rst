
******************************
公交地铁网络拓扑建模
******************************

.. function:: transbigdata.metro_network(line, stop, transfertime=5, nxgraph=True)

输入站点信息，输出网络信息，可用于最短路径与最短k路径生成。该方法依赖于NetworkX。
地铁出行时间由以下部分构成：地铁运行时间（距离/速度）+停站时间（一般取固定值）+换乘时间（步行时间+等车时间）

**输入**

line : GeoDataFrame
    地铁线路，`line`列存储地铁线路名称，`speed`存储每条地铁线路运行车速，`stoptime`每条线路停站时间
stop : GeoDataFrame
    公交站点
transfertime : number
    每个轨道换乘的时长
nxgraph : bool
    默认True，如果True则直接输出由NetworkX构建的网络G，如果为False，则输出网络的边edge1,edge2和
    节点node，以便用于精确定义边权
    
**输出**

*nxgraph为True时*
G : networkx.classes.graph.Graph
    networkx构建的网络G

*nxgraph为False时*
edge1 : DataFrame
    轨道断面的边
edge2 : DataFrame
    轨道换乘的边
node : List
    网络节点

.. function:: transbigdata.get_shortest_path(G, stop, ostation, dstation)

获取最短路径

**输入**

G : networkx.classes.graph.Graph
    networkx构建的地铁网络G
stop : DataFrame
    地铁站点信息表
ostation : str
    O站点名称
dstation : str
    D站点名称

**输出**

path : list
    路径，一个包含路径经过节点名称的list

.. function:: transbigdata.get_k_shortest_paths(G, stop, ostation, dstation, k)

获取前k个最短路径

**输入**

G : networkx.classes.graph.Graph
    networkx构建的地铁网络G
stop : DataFrame
    地铁站点信息表
ostation : str
    O站点名称
dstation : str
    D站点名称
k : int
    获取前k个路径

**输出**

paths : list
    包含前k个路径的list

.. function:: transbigdata.get_path_traveltime(G, path)

通过路径获得出行时间

**输入**

G : networkx.classes.graph.Graph
    networkx构建的地铁网络G
path : list
    路径，一个包含路径经过节点名称的list

**输出**

traveltime : float
    该路径的出行时间

.. function:: transbigdata.split_subwayline(line,stop)

用公交/地铁站点对公交/地铁线进行切分，得到断面，可用于可视化

**输入**

line : GeoDataFrame
    公交/地铁线路
stop : GeoDataFrame
    公交/地铁站点

**输出**

metro_line_splited : GeoDataFrame
    生成的断面线型