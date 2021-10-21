.. _CoordinatesConverter:


******************************
坐标转换与距离计算
******************************

火星坐标系互转
=============================
坐标互转，基于numpy列运算::

  data['Lng'],data['Lat'] = transbigdata.wgs84tobd09(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = transbigdata.wgs84togcj02(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = transbigdata.gcj02tobd09(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = transbigdata.gcj02towgs84(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = transbigdata.bd09togcj02(data['Lng'],data['Lat'])  
  data['Lng'],data['Lat'] = transbigdata.bd09towgs84(data['Lng'],data['Lat'])  

经纬度计算距离
=============================
输入起终点经纬度，获取距离（米），基于numpy列运算::
    
  data['distance'] = transbigdata.getdistance(data['Lng1'],data['Lat1'], data['Lng2'],data['Lat2'])  

