
******************************
可视化
******************************

| TransBigData包也依托于kepler.gl提供的可视化插件提供了一键数据整理与可视化的方法
| 使用此功能请先安装python的keplergl包
::

    pip install keplergl


.. function:: transbigdata.visualization_trip(trajdata,col = ['Lng','Lat','ID','Time'],zoom = 10,height=500)

输入轨迹数据与列名，生成kepler的可视化

**输入**

trajdata : DataFrame
    轨迹点数据
col : List
    列名，按[经度,纬度,轨迹编号,时间]的顺序
zoom : number
    地图缩放等级
height : number
    地图图框高度

**输出**

traj : keplergl.keplergl.KeplerGl
    keplergl提供的可视化
