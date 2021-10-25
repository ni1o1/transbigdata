.. _getting_started:


***************
安装与依赖
***************

安装
=============================

这个包依赖geopandas：https://geopandas.org/index.html
如果你已经安装了geopandas，则直接在命令提示符中运行下面代码即可安装::

  pip install -U transbigdata

在Python中运行下面代码::

  import transbigdata as tbd

依赖包
=============================
TransBigData依赖如下包

* scipy
* pandas
* geopandas
* matplotlib

版本更新
=============================

0.1.6 (2021-10-25)
------------------------
修正taxigps_traj_point的Bug

0.1.5 (2021-10-25)
------------------------
增加轨迹处理部分：

* taxigps_traj_point  输入出租车数据与OD数据，提取载客与空载的行驶路径点
* points_to_traj 输入轨迹点，生成轨迹线型的GeoDataFrame


0.1.4 (2021-10-24)
------------------------
增加栅格化的gridid_sjoin_shape方法，输入数据（带有栅格经纬度编号两列），矢量图形与栅格化参数，输出数据栅格并对应矢量图形。


0.1.3 (2021-10-23)
------------------------
增加预处理的clean_same,clean_drift,clean_taxi_status方法
为预处理的id_reindex方法加入sample参数

0.1.2 (2021-10-23)
------------------------
更新数据预处理的clean_outofshape方法
增加共享单车数据处理功能，bikedata_to_od提取骑行订单数据与停车数据

0.1.1 (2021-10-22)
------------------------
加入数据预处理的clean_outofbounds，dataagg，id_reindex方法

0.1.0 (2021-10-21)
------------------------
最初版本发布