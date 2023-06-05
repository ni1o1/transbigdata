.. _getting_started:


******************************
Installation
******************************

安装
=============================

TransBigData support Python >= 3.6.

TransBigData depends on geopandas, Before installing TransBigData, you need to install geopandas based on `this link <https://geopandas.org/en/stable/getting_started.html#installation>`_  If you already have geopandas installed, run the following code directly from the command prompt to install it::

  pip install -U transbigdata

You can also install TransBigData by conda-forge, this will automaticaly solve the dependency, it can be installed with::
  
  conda install -c conda-forge transbigdata

To import TransBigData, run the following code in Python::

  import transbigdata as tbd

Dependency
=============================
TransBigData depends on the following packages

* `pandas`
* `shapely`
* `rtree`
* `geopandas`
* `scipy`
* `matplotlib`
* `networkx` (optional)
* `igraph` (optional)
* `osmnx` (optional)
* `seaborn` (optional)
* `keplergl` (optional)
