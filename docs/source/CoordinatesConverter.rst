.. _CoordinatesConverter:


******************************
坐标与距离
******************************

火星坐标系互转
=============================

GCJ02,BD09,WGS94坐标系互转

.. function:: transbigdata.gcj02tobd09(lng, lat)

.. function:: transbigdata.bd09togcj02(bd_lon, bd_lat)

.. function:: transbigdata.wgs84togcj02(lng, lat)

.. function:: transbigdata.gcj02towgs84(lng, lat)

.. function:: transbigdata.wgs84tobd09(lon,lat)

.. function:: transbigdata.bd09towgs84(lon,lat)


坐标互转，基于numpy列运算::

  data['Lng'],data['Lat'] = tbd.wgs84tobd09(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = tbd.wgs84togcj02(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = tbd.gcj02tobd09(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = tbd.gcj02towgs84(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = tbd.bd09togcj02(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = tbd.bd09towgs84(data['Lng'],data['Lat'])  

经纬度计算距离
=============================

.. function:: transbigdata.getdistance(lon1, lat1, lon2, lat2)

按经度1，纬度1，经度2，纬度2 （十进制度数）顺序输入起终点经纬度，为DataFrame的列，获取距离（米），基于numpy列运算::
    
  data['distance'] = tbd.getdistance(data['Lng1'],data['Lat1'], data['Lng2'],data['Lat2'])  

