.. _CoordinatesConverter:
.. currentmodule:: transbigdata

******************************
Coordinates and Distances
******************************


.. autosummary::
   :toctree: api/
   
    gcj02tobd09
    gcj02towgs84
    wgs84togcj02
    wgs84tobd09
    bd09togcj02
    bd09towgs84
    bd09mctobd09
    transform_shape
    getdistance

Coordinate convertering method
---------------------------------------

TransBigData package provides quick converting of coordinates such as GCJ02, BD09, BD09mc, WGS94

.. autofunction:: gcj02tobd09

.. autofunction:: bd09togcj02

.. autofunction:: wgs84togcj02

.. autofunction:: gcj02towgs84

.. autofunction:: wgs84tobd09

.. autofunction:: bd09towgs84

.. autofunction:: bd09mctobd09

Coordinates reciprocal converting, based on numpy column computation::

  >>> data['Lng'],data['Lat'] = tbd.wgs84tobd09(data['Lng'],data['Lat'])  
  >>> data['Lng'],data['Lat'] = tbd.wgs84togcj02(data['Lng'],data['Lat'])  
  >>> data['Lng'],data['Lat'] = tbd.gcj02tobd09(data['Lng'],data['Lat'])  
  >>> data['Lng'],data['Lat'] = tbd.gcj02towgs84(data['Lng'],data['Lat'])  
  >>> data['Lng'],data['Lat'] = tbd.bd09togcj02(data['Lng'],data['Lat'])  
  >>> data['Lng'],data['Lat'] = tbd.bd09towgs84(data['Lng'],data['Lat'])  
  >>> data['Lng'],data['Lat'] = tbd.bd09mctobd09(data['Lng'],data['Lat']) 

Convert coordinates of the geographic elements
==========================================================

.. autofunction:: transform_shape


Distance measurment
--------------------------

.. autofunction:: getdistance