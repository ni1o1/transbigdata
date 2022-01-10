import transbigdata as tbd
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon


class TestBikedata:
    def setup_method(self):
        self.data =pd.DataFrame([['713ED7A4B5EA3233E0533C0BA8C09291', '2018-08-27 8:41:46', 0,
        121.432966, 31.130154],
       ['713ED7A4B5EA3233E0533C0BA8C09291', '2018-08-27 8:58:46', 1,
        121.435436, 31.135094],
       ['713ED7A4B5EA3233E0533C0BA8C09291', '2018-08-27 17:27:11', 0,
        121.442523, 31.128701],
       ['713ED7A4B5EA3233E0533C0BA8C09291', '2018-08-27 17:55:01', 0,
        121.441443, 31.128867],
       ['713ED7A4B5EA3233E0533C0BA8C09291', '2018-08-27 17:48:11', 1,
        121.445683, 31.135021],
       ['713ED7A4B5EA3233E0533C0BA8C09291', '2018-08-27 17:59:45', 1,
        121.445293, 31.136567],
       ['713ED7A4B5EA3233E0533C0BA8C09291', '2018-08-27 20:02:16', 0,
        121.406615, 31.13313],
       ['713ED7A4B5EA3233E0533C0BA8C09291', '2018-08-27 20:08:02', 1,
        121.413019, 31.128553000000004],
       ['713ED790D6AE3233E0533C0BA8C09291', '2018-08-27 6:55:14', 0,
        121.355498346732, 31.233843474138],
       ['713ED790D6AE3233E0533C0BA8C09291', '2018-08-27 7:01:51', 1,
        121.362343645231, 31.2392523563195]], columns=['BIKE_ID', 'DATA_TIME', 'LOCK_STATUS', 'LONGITUDE', 'LATITUDE'])

    def test_bikedata(self):
        assert len(tbd.bikedata_to_od(self.data,startend = ['2018-08-27 00:00:00','2018-08-28 00:00:00'])[0])==5
        assert len(tbd.bikedata_to_od(self.data)[1])==3
    
