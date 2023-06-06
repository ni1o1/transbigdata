.. transbigdata documentation master file, created by
   sphinx-quickstart on Thu Oct 21 14:41:25 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TransBigData 为交通时空大数据而生
========================================

.. image:: _static/logo-wordmark-dark.png



**Main Functions**

TransBigData is a Python package developed for transportation spatio-temporal big data processing and analysis. TransBigData provides fast and concise methods for processing common traffic spatio-temporal big data such as Taxi GPS data, bicycle sharing data and bus GPS data. It includes general methods such as rasterization, data quality analysis, data pre-processing, data set counting, trajectory analysis, GIS processing, map base map loading, coordinate and distance calculation, and data visualization.

**Technical Features**

* Provides different processing methods for different stages of traffic spatio-temporal big data analysis.
* The code with TransBigData is clean, efficient, flexible, and easy to use, allowing complex data tasks to be achieved with concise code.


Introduction
---------------


Quick Start
==============================

| Before installing TransBigData, make sure that you have installed the geopandas package: https://geopandas.org/index.html
| If you already have geopandas installed, run the following code directly from the command prompt to install it

::

    pip install -U transbigdata

The following example shows how to use the TransBigData to quickly extract trip OD from taxi GPS data

::

    import transbigdata as tbd
    import pandas as pd
    data = pd.read_csv('TaxiData-Sample.csv',header = None) 
    data.columns = ['VehicleNum','time','slon','slat','OpenStatus','Speed'] 
    data

.. image:: _static/WX20211021-192131@2x.png
   :height: 300


Use the `tbd.taxigps_to_od` method and pass in the corresponding column name to extract the trip OD:
::

    #Extract OD from GPS data
    oddata = tbd.taxigps_to_od(data,col = ['VehicleNum','time','slon','slat','OpenStatus'])
    oddata

.. image:: _static/WX20211021-190104@2x.png
   :height: 300

Aggregate OD into grids::

   #define bounds
   bounds = [113.6,22.4,114.8,22.9]
   #obtain the gridding parameters
   params = tbd.grid_params(bounds = bounds,accuracy = 1500)
   #gridding OD data and aggregate
   od_gdf = tbd.odagg_grid(oddata,params)
   od_gdf.plot(column = 'count')

.. image:: _static/WX20211021-190524@2x.png
   :height: 300


Installation
==============================

.. toctree::
   :caption: Installation
   :maxdepth: 2
   
   getting_started.rst

Example gallery
==============================

.. toctree::
   :caption: Example
   :maxdepth: 2

   gallery/index.rst

Core Methods
==============================

.. toctree::
   :caption: Core Methods
   :maxdepth: 2

   grids.rst
   traj.rst

General Methods
==============================

.. toctree::
   :caption: General Methods
   :maxdepth: 2
   
   quality.rst
   preprocess.rst
   getbusdata.rst
   gisprocess.rst
   plot_map.rst
   CoordinatesConverter.rst
   visualization.rst
   activity.rst
   odprocess.rst
   utils.rst

Methods for specific data
==============================

.. toctree::
   :caption: Methods for specific data
   :maxdepth: 2

   mobile.rst
   taxigps.rst
   bikedata.rst
   busgps.rst
   metroline.rst



