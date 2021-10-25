.. _traj:


******************************
轨迹
******************************

.. function:: transbigdata.points_to_traj(traj_points,col = ['Lng','Lat','ID'])

输入轨迹点，生成轨迹线型的GeoDataFrame

**输入**

traj_points : DataFrame
    轨迹点数据
col : List
    列名，按[经度,纬度,轨迹编号]的顺序

**输出**

traj : GeoDataFrame
    生成的轨迹数据