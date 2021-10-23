.. _preprocess:


******************************
数据预处理
******************************

.. function:: transbigdata.clean_outofbounds(data,bounds,col = ['Lng','Lat'])

输入研究范围的左下右上经纬度坐标，剔除超出研究范围的数据

输入

data : DataFrame
    数据
bounds : List    
    研究范围的左下右上经纬度坐标，顺序为[lon1,lat1,lon2,lat2]
col : List
    经纬度列名

输出

data1 : DataFrame
    研究范围内的数据


.. function:: transbigdata.clean_outofshape(data,shape,col = ['Lng','Lat'],accuracy=500)

输入研究范围的GeoDataFrame，剔除超出研究区域的数据

输入

data : DataFrame
    数据
shape : GeoDataFrame    
    研究范围的GeoDataFrame
col : List
    经纬度列名
accuracy : number
    计算原理是先栅格化后剔除，这里定义栅格大小，越小精度越高

输出

data1 : DataFrame
    研究范围内的数据

.. function:: transbigdata.id_reindex(data,col,new = False,suffix = '_new')

对数据的ID列重新编号

输入

data : DataFrame
    数据 
col : str
    要重新编号的ID列名
new : bool
    False，相同ID的新编号相同；True，依据表中的顺序，ID再次出现则编号不同
suffix : str
    新编号列名的后缀，设置为False时替代原有列名

输出

data1 : DataFrame
    重新编号的数据