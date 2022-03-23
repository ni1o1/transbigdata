import transbigdata as tbd
import numpy as np
import pandas as pd


class TestCoordinatesConverter:
    def setup_method(self):
        self.data = pd.DataFrame(
            [['713ED7A4B5EA3233E0533C0BA8C09291', '2018-08-27 8:41:46', 0,
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
              121.362343645231, 31.2392523563195]],
            columns=['BIKE_ID',
                     'DATA_TIME',
                     'LOCK_STATUS',
                     'LONGITUDE',
                     'LATITUDE'])

    def test_CoordinatesConverter(self):
        lon, lat = tbd.wgs84tobd09(
            self.data['LONGITUDE'], self.data['LATITUDE'])
        assert np.allclose([lon.iloc[0], lat.iloc[0]], [
                           121.44400198,  31.13461178])
        lon, lat = tbd.bd09towgs84(
            self.data['LONGITUDE'], self.data['LATITUDE'])
        assert np.allclose([lon.iloc[0], lat.iloc[0]], [
                           121.42189628157456, 31.125775772415125])
        lon, lat = tbd.bd09mctobd09(
            self.data['LONGITUDE'], self.data['LATITUDE'])
        assert np.allclose([lon.iloc[0], lat.iloc[0]], [
                           0.0010908419148962093, 0.00028151894107858114])
        assert tbd.getdistance(121.432966, 31.130154,
                               121.442523, 31.128701) == 923.9008993249727
