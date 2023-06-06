.. currentmodule:: transbigdata

******************************
数据可视化
******************************

.. autosummary::
   
    visualization_data
    visualization_trip
    visualization_od


在jupyter中显示可视化的设置
--------------------------------------


| TransBigData包也依托于kepler.gl提供的可视化插件提供了一键数据整理与可视化的方法
| 使用此功能请先安装python的keplergl包

::

    pip install keplergl

如果要在jupyter notebook中显示可视化，则需要勾选jupyter-js-widgets（可能需要另外安装）和keplergl-jupyter两个插件

.. image:: _static/jupytersettings.png

数据点分布可视化
-------------------

.. autofunction:: visualization_data

轨迹可视化
-------------------

.. autofunction:: visualization_trip


OD可视化
--------------------

.. autofunction:: visualization_od
