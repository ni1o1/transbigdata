地铁网络拓扑建模
================

这个案例的Jupyter notebook: `点击这里 <https://github.com/ni1o1/transbigdata/blob/main/example/Example%203-Modeling%20for%20subway%20network%20topology.ipynb>`__.

| 可以点击 `这个链接 <https://mybinder.org/v2/gh/ni1o1/transbigdata/9507de936806c34a4befd74aa9227b012569a6aa?urlpath=lab%2Ftree%2Fexample%2FExample%203-Modeling%20for%20subway%20network%20topology.ipynb>`__ 在线编辑器中尝试

下面的案例展示如何用TransBigData包抓取地铁线路，并构建地铁线网的拓扑网络模型

爬取地铁线路
------------

首先爬取地铁线路使用tbd.getbusdata方法，输入城市跟公交或地铁线路名称的关键词，即可获取到线路数据，坐标系为wgs84。

::

    import pandas as pd
    import transbigdata as tbd
    line,stop = tbd.getbusdata('厦门',['1号线','2号线','3号线'])



Obtaining city id: 厦门success
1号线
地铁1号线(镇海路-岩内) success
地铁1号线(岩内-镇海路) success
2号线
地铁2号线(五缘湾-天竺山) success
地铁2号线(天竺山-五缘湾) success
3号线
地铁3号线(厦门火车站-蔡厝) success
地铁3号线(蔡厝-厦门火车站) success
地铁3号线南延段(厦门火车站-沙坡尾) success
地铁3号线南延段(沙坡尾-厦门火车站) success


::

    line.plot()








.. image:: output_5_1.png


::

    stop.plot()








.. image:: output_6_1.png


轨道断面信息获取
----------------

tbd.split_subwayline方法可以用轨道站点切分轨道线路，得到轨道断面信息（这一步骤主要在地铁客流可视化中有用）

::

    metroline_splited = tbd.split_subwayline(line,stop)
    metroline_splited.plot(column = pd.Series(metroline_splited.index))





.. image:: output_9_1.png


轨道网络拓扑模型构建
--------------------

同时我们也可以直接使用站点数据，构建地铁网络的拓扑结构模型，方便后续地铁出行路径的识别。这一功能依赖于networkx包。

::

    #构建拓扑模型
    line['speed'] = 36 #每条线路运营车速 36km/h
    line['stoptime'] = 0.5 #每条线路停站时间 30s
    import networkx as nx
    G = tbd.metro_network(line,stop, transfertime=5)
    nx.draw(G,node_size=20)


.. image:: output_12_0.png

给定起终点，即可获取最短路径和前k个最短路径

::

    path = tbd.get_shortest_path(G,stop,'镇海路','蔡厝')
    path

::

    ['地铁1号线镇海路',
    '地铁1号线中山公园',
    '地铁1号线将军祠',
    '地铁1号线文灶',
    '地铁1号线湖滨东路',
    '地铁3号线湖滨东路',
    '地铁3号线体育中心',
    '地铁3号线人才中心',
    '地铁3号线湖里公园',
    '地铁3号线华荣路',
    '地铁3号线火炬园',
    '地铁3号线小东山',
    '地铁3号线安兜',
    '地铁3号线坂尚',
    '地铁3号线湖里创新园',
    '地铁3号线五缘湾',
    '地铁3号线林前',
    '地铁3号线鼓锣',
    '地铁3号线后村',
    '地铁3号线蔡厝']

::

    # 前k最短路径
    paths =  tbd.get_k_shortest_paths(G,stop,'镇海路','蔡厝',2)
    paths

::

    [['地铁1号线镇海路',
    '地铁1号线中山公园',
    '地铁1号线将军祠',
    '地铁1号线文灶',
    '地铁1号线湖滨东路',
    '地铁3号线湖滨东路',
    '地铁3号线体育中心',
    '地铁3号线人才中心',
    '地铁3号线湖里公园',
    '地铁3号线华荣路',
    '地铁3号线火炬园',
    '地铁3号线小东山',
    '地铁3号线安兜',
    '地铁3号线坂尚',
    '地铁3号线湖里创新园',
    '地铁3号线五缘湾',
    '地铁3号线林前',
    '地铁3号线鼓锣',
    '地铁3号线后村',
    '地铁3号线蔡厝'],
    ['地铁1号线镇海路',
    '地铁1号线中山公园',
    '地铁1号线将军祠',
    '地铁1号线文灶',
    '地铁1号线湖滨东路',
    '地铁1号线莲坂',
    '地铁1号线莲花路口',
    '地铁1号线吕厝',
    '地铁1号线乌石浦',
    '地铁1号线塘边',
    '地铁1号线火炬园',
    '地铁3号线火炬园',
    '地铁3号线小东山',
    '地铁3号线安兜',
    '地铁3号线坂尚',
    '地铁3号线湖里创新园',
    '地铁3号线五缘湾',
    '地铁3号线林前',
    '地铁3号线鼓锣',
    '地铁3号线后村',
    '地铁3号线蔡厝']]

获取路径出行时长

::

    tbd.get_path_traveltime(G,path)

::

    68.00206888083389