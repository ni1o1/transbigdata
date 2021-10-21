# TransBigData 交通时空大数据处理

TransBigData工具针对时空大数据处理而开发，目前有下面几个功能：
1. 添加地图底图：请看[这个示例](https://github.com/ni1o1/transbigdata/blob/master/example/example-grid.ipynb)
2. 火星坐标转换
3. 经纬度换算距离
4. 栅格渔网划分：请看[这个示例](https://github.com/ni1o1/transbigdata/blob/master/example/example-grid.ipynb)
5. 用KDTree算法匹配点与点、点与线的最近邻：请看[这个示例](https://github.com/ni1o1/transbigdata/blob/master/example/example-ckdnearest.ipynb)
6. 出租车GPS数据的OD提取：请看[这个示例](https://github.com/ni1o1/transbigdata/blob/master/example/example-od.ipynb)

## 安装

    pip install transbigdata

## 底图加载功能

### 地图底图加载

只需要用以下代码：

    import transbigdata
    #设定显示范围
    bounds = [lon1,lat1,lon2,lat2]  
    transbigdata.plot_map(plt,bounds,zoom = 12,style = 4)  

参数

| 参数        | 描述                                                         |
| ----------- | ------------------------------------------------------------ |
| bounds      | 底图的绘图边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 |
| zoom        | 底图的放大等级，越大越精细，加载的时间也就越久，一般单个城市大小的范围，这个参数选取12到16之间 |
| style       | 地图底图的样式，可选1-7，1-6为openstreetmap，7是mapbox       |
| imgsavepath | 瓦片地图储存路径，设置路径后，会把地图下载到本地的文件夹下，使用时也会优先搜索是否有已经下载的瓦片，默认的存放路径是C:\\ |
| printlog    | 是否显示日志                                                 |

### 绘制指北针和比例尺的功能plotscale

为底图添加指北针和比例尺

    transbigdata.plotscale(ax,bounds = bounds,textsize = 10,compasssize = 1,accuracy = 2000,rect = [0.06,0.03])  

参数

| 参数        | 描述                                                         |
| ----------- | ------------------------------------------------------------ |
| bounds      | 底图的绘图边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 |
| textsize    | 标注文字大小                                                 |
| compasssize | 标注的指北针大小                                             |
| accuracy    | 标注比例尺的长度                                             |
| unit        | 'KM','km','M','m' 比例尺的单位                               |
| style       | 1或2，比例尺样式                                             |
| rect       | 比例尺在图中的大致位置，如[0.9,0.9]则在右上角                    |

## 栅格化功能
### 生成方形栅格渔网

生成研究范围内的方形栅格  

    #设定范围
    bounds = [lon1,lat1,lon2,lat2]
    grid,params = transbigdata.rect_grids(bounds,accuracy = 500)


输入参数

| 参数        | 描述                                                         |
| ----------- | ------------------------------------------------------------ |
| bounds      | 底图的绘图边界，[lon1,lat1,lon2,lat2] (WGS84坐标系) 其中，lon1,lat1是左下角坐标，lon2,lat2是右上角坐标 |
| accuracy    | 栅格大小                                                 |

输出

| 参数        | 描述                                                         |
| ----------- | ------------------------------------------------------------ |
| grid      | 栅格的GeoDataFrame，其中LONCOL与LATCOL为栅格的编号，HBLON与HBLAT为栅格的中心点坐标 |
| params    | 栅格参数，分布为(lonStart,latStart,deltaLon,deltaLat)栅格左下角坐标与单个栅格的经纬度长宽|

### 栅格参数获取

输入经纬度范围bounds，输出栅格参数

    bounds = [113.75194,22.447837,114.624187,22.864748]
    grid_params(bounds,accuracy = 500)

### GPS数据对应栅格编号

输入数据的经纬度列与栅格参数，输出对应的栅格编号

    data['LONCOL'],data['LATCOL'] = transbigdata.GPS_to_grids(data['Lng'],data['Lat'],params)

### 栅格编号对应栅格中心点经纬度

输入数据的栅格编号与栅格参数，输出对应的栅格中心点

    data['HBLON'],data['HBLAT'] = transbigdata.grids_centre(data['LONCOL'],data['LATCOL'],params)

### 栅格编号生成栅格的地理信息列

输入数据的栅格编号与栅格参数，输出对应的地理信息列

    data['geometry'] = transbigdata.gridid_to_polygon(data['LONCOL'],data['LATCOL'],params)

### 生成六边形渔网

生成研究范围内的六边形渔网  

    
    #设定范围
    bounds = [lon1,lat1,lon2,lat2]
    hexagon = transbigdata.hexagon_grids(bounds,accuracy = 5000)


## 坐标计算功能
### 火星坐标系互转

坐标互转，基于numpy列运算

    data['Lng'],data['Lat'] = transbigdata.wgs84tobd09(data['Lng'],data['Lat'])  
    data['Lng'],data['Lat'] = transbigdata.wgs84togcj02(data['Lng'],data['Lat'])  
    data['Lng'],data['Lat'] = transbigdata.gcj02tobd09(data['Lng'],data['Lat'])  
    data['Lng'],data['Lat'] = transbigdata.gcj02towgs84(data['Lng'],data['Lat'])  
    data['Lng'],data['Lat'] = transbigdata.bd09togcj02(data['Lng'],data['Lat'])  
    data['Lng'],data['Lat'] = transbigdata.bd09towgs84(data['Lng'],data['Lat'])  

### 经纬度计算距离

输入起终点经纬度，获取距离（米），基于numpy列运算
    
    data['distance'] = transbigdata.getdistance(data['Lng1'],data['Lat1'], data['Lng2'],data['Lat2'])  


## OD处理
### OD集计与地理信息生成（栅格）
输入OD数据，栅格化OD并集计后生成OD的GeoDataFrame

    odagg_grid(oddata,params,col = ['slon','slat','elon','elat'],arrow = False,**kwargs):
    oddata - OD数据
    col - 起终点列名
    params - 栅格化参数
    arrow - 生成的OD地理线型是否包含箭头

### OD集计与地理信息生成（小区集计）
输入OD数据，栅格化OD并集计后生成OD的GeoDataFrame

    odagg_shape(oddata,shape,col = ['slon','slat','elon','elat'],params = None,round_accuracy = 6,arrow = False,**kwargs):
    oddata - OD数据
    shape - 集计小区的GeoDataFrame
    col - 起终点列名
    params - 栅格化参数，如果传入，则先栅格化后以栅格中心点匹配小区，如果不传入，则直接以经纬度匹配。在数据量大时，用栅格化进行匹配速度会极大提升
    round_accuracy - 集计时经纬度取小数位数
    arrow - 生成的OD地理线型是否包含箭头

## 出租车GPS数据处理
### 出租车OD提取算法
输入出租车GPS数据,提取OD

    taxigps_to_od(data,col = ['VehicleNum','Stime','Lng','Lat','OpenStatus'])
    data - 出租车GPS数据（清洗好的）
    col - 数据中各列列名，需要按顺序[车辆id，时间，经度，纬度，载客状态]