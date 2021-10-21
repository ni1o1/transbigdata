.. _ckdnearest:


******************************
点与点、点与线近邻匹配
******************************

基于scipy包所提供的cKDTree算法进行点与点、点与线的最近邻匹配，算法复杂度为o(log(n))

.. function:: transbigdata.ckdnearest(dfA_origin,dfB_origin,Aname = ['lon','lat'],Bname = ['lon','lat'])

输入两个DataFrame，分别指定经纬度列名，为表A匹配表B中最近点，并计算距离

.. function:: transbigdata.ckdnearest_point(gdA, gdB):

输入两个geodataframe，gdfA、gdfB均为点，该方法会为gdfA表连接上gdfB中最近的点，并添加距离字段dsit

.. function:: transbigdata.ckdnearest_line(gdfA, gdfB)

输入两个geodataframe，其中gdfA为点，gdfB为线，该方法会为gdfA表连接上gdfB中最近的线，并添加距离字段dsit

