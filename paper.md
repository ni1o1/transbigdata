---
title: 'TransBigData: A Python package for transportation spatio-temporal big data processing, analysis and visualization'
tags:
  - Python
  - transportation
  - spatio-temporal data
  - geospatial data
  - GIS
  - data quality analysis
  - data pre-processing
  - data visualization
  - taxi GPS data
  - bus GPS data
  - bike sharing data
authors:
  - name: Qing Yu
    orcid: 0000-0003-2513-2969
    affiliation: 1
  - name: Jian Yuan^[corresponding author]
    orcid: 0000-0002-7202-0946
    affiliation: 1
affiliations:
 - name: Key Laboratory of Road and Traffic Engineering of the Ministry of Education, Tongji University, 4800 Cao’an Road, Shanghai 201804, People’s Republic of China
   index: 1
date: 30 November 2021
bibliography: paper.bib
---
# Summary

In recent years, data generated in the field of transportation has begun to explode. Individual continuous tracking data, such as mobile phone data, IC smart card data, taxi GPS data, bus GPS data and bicycle sharing order data, also known as "spatio-temporal big data" or "Track &Trace data" [@harrison:2020], has great potential for applications in data-driven transportation research. These spatio-temporal big data typically require three aspects of information [@zhang:2021]: Who? When? Where? They are characterized by high data quality, large collection scope, and fine-grained spatio-temporal information, which can fully capture the daily activities of individuals and their travel behavior in the city in both temporal and spatial dimensions. The emergence of these data provides new ways and opportunities for potential transportation demand analysis and travel mechanism understanding in supporting urban transportation planning and management [@chen:2021; @zhang:2020]. However, processing with these multi-source spatial temporal big data usually requires a series of similar processing procedure (e.g., data quality accessment, data preprocessing, data cleaning, data gridding, data aggregation, and data visualization). There is an urgent need for a one-size-fits-all tool that can adapt to the various processing demand of different transportation data in this field.

# **Similar software packages**

Several tools exist which allow process and visualization of spatio-temporal mobility data. moveVis [@2020moveVis] providing tools to visualize movement data and temporal changes of environmental data by creating video animations. TraViA [@Siebinga2021] provides tools to visualize and annotate movement data in an interactive approach. MovingPandas [@0x003aba2b] is a comprehensive tool that could both provide trajectory data structures and functions for data exploration and visualization. PySAL [@rey_pysal_2010] is a family of packages allows for advanced geospatial data science, which supports the development of high-level applications. The traffic library [@Olive2019] is a toolbox for processing and analyzing air traffic data.

However, there is a lot of work before transforming raw spatio-temporal data into valuable insights. For example, transformation of coordinate systems, trip map-matching, origin-destination calculation. Thus, a tool that integrates multiple data processing functions, GIS analysis tools, and various visualization features through one language could effectively facilitate the research progress.

# Statement of need

`TransBigData` is a Python package developed for transportation spatio-temporal big data processing, analysis, and visualization that provides fast and concise methods for processing taxi GPS data, bicycle sharing data, and bus GPS data, for example. Further, a variety of processing methods for each stage of transportation spatio-temporal big data analysis are included in the code base. `TransBigData` provides clean, efficient, flexible, and easy to use API, allowing complex data tasks to be achieved with concise code, and it has already been used in a number of scientific publications [@yu:2020-1; @yu:2020; @li2021taxi; @yu2021partitioning].

For some types of data, `TransBigData` also provides targeted tools for specific needs, such as extraction of origins and destinations (OD) of taxi trips from taxi GPS data and identification of arrival and departure information from bus GPS data.

Currently, `TransBigData` mainly provides the following methods:

- *Data Quality*: Provides methods to quickly obtain the general information of the dataset, including the data amount, the time period, and the sampling interval.
- *Data Preprocess*: Provides methods to fix multiple types of data error.
- *Data Gridding*: Provides methods to generate multiple types of geographic grids (rectangular and hexagonal) in the research area. Provides fast algorithms to map GPS data to the generated grids (\autoref{fig:fig1}).
- *Data Aggregating*: Provides methods to aggregate GPS and OD data into geographic polygons.
- *Trajectory Processing*: Provides quick methods to re-organize the data structure and implement data augmentation from various data formats, including generating trajectory linestrings from GPS points, and trajectory densification, etc.
- *Data Visualization*: Built-in visualization capabilities leverage the visualization package `keplergl` to interactively visualize data in Jupyter notebooks with simple code.
- *Basemap Loading*: Provides methods to display Mapbox basemaps in `matplotlib` figures (\autoref{fig:fig2}).

The latest stable release of the software can be installed via `pip` and full documentation
can be found at https://transbigdata.readthedocs.io/en/latest/.

![TransBigData</code></code> generates rectangular grids and aggregates GPS data to the grids.\label{fig:fig1}](images/figure1.png){ width=100% }

![TransBigData</code></code> visualizes taxi trip ODs and displays basemaps with matplotlib</code></code>.\label{fig:fig2}](images/figure2.png){ width=100% }

# References
