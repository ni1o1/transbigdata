import transbigdata as tbd
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon


class TestODprocess:
    def setup_method(self):
        self.data = pd.DataFrame([[34745, '20:27:43', 113.80684699999999, 22.623248999999998, 1, 27],
                                  [34745, '20:24:07', 113.809898, 22.627399, 0, 0],
                                  [34745, '20:24:27', 113.809898, 22.627399, 1, 0],
                                  [34745, '20:22:07', 113.811348, 22.628067, 1, 0],
                                  [34745, '20:10:06', 113.81988500000001,
                                      22.6478, 1, 54],
                                  [34745, '19:59:48', 113.820213,
                                      22.674967000000002, 0, 23],
                                  [34745, '20:11:06', 113.82048, 22.6423, 0, 57],
                                  [34745, '20:13:46', 113.82676699999999,
                                      22.630899, 0, 66],
                                  [34745, '19:43:18', 114.828217, 22.7069, 0, 62],
                                  [34745, '19:42:18', 113.83161899999999,
                                      22.716998999999998, 0, 69],
                                  [22233, '14:41:40', 113.878571, 22.571199, 0, 0],
                                  [22233, '14:42:00', 113.879135, 22.571617, 0, 7],
                                  [22233, '14:45:40', 113.886253, 22.573217, 0, 25],
                                  [22233, '14:49:00', 113.8899,
                                      22.56956700000001, 0, 0],
                                  [22233, '14:55:15', 113.91093400000001,
                                      22.552383, 1, 60],
                                  [22233, '19:02:12', 113.927116,
                                      22.543948999999998, 1, 41],
                                  [22233, '14:32:47', 113.92831399999999,
                                      22.556867999999998, 1, 57],
                                  [22233, '14:57:35', 113.934036, 22.555267, 1, 65],
                                  [22233, '20:54:11', 113.942467, 22.507566, 0, 21],
                                  [22233, '18:51:30', 113.964569, 22.541849, 0, 0]], columns=['VehicleNum', 'time', 'slon', 'slat', 'OpenStatus', 'Speed'])
        self.sz = gpd.GeoDataFrame([Polygon([[113.74627986426263, 22.39928709355355], [113.74627986426263, 22.864719035968925], [
            114.62397036947118, 22.864719035968925], [114.62397036947118, 22.39928709355355]])], columns=['geometry'])

    def test_odprocess(self):
        
        assert len(tbd.clean_drift(self.data,col = ['VehicleNum','time','slon','slat']))==19
        assert len(tbd.clean_taxi_status(self.data,['VehicleNum','time','OpenStatus']))==19
        assert len(tbd.clean_traj(self.data,col = ['VehicleNum','time','slon','slat']))==18
        data = tbd.clean_outofshape(self.data, self.sz, col=['slon', 'slat'])
        data['time'] = pd.to_datetime(data['time'])
        assert len(tbd.traj_sparsify(data,col=['VehicleNum', 'time', 'slon', 'slat']))==19
        assert len(tbd.traj_sparsify(data,col = ['VehicleNum','time', 'slon', 'slat'],method = 'interpolate'))==1707
        assert len(tbd.traj_densify(data,col=['VehicleNum', 'time', 'slon', 'slat']))==1725
        assert len(tbd.points_to_traj(data,col=[ 'slon', 'slat','VehicleNum']))==2
        assert len(data) == 19
        assert len(tbd.clean_same(data,col = ['VehicleNum','time', 'slon', 'slat']))==19
        bounds = [113.75, 22.4, 114.62, 22.86]
        data = tbd.clean_outofbounds(data, bounds, col=['slon', 'slat'])
        assert len(data) == 19
        params = tbd.grid_params(bounds, accuracy=1000)
        stay,move = tbd.traj_stay_move(data,params,col = ['VehicleNum','time','slon','slat'],activitytime = 1800)
        assert len(stay)==2
        tbd.plot_activity(stay)
        data['LONCOL'], data['LATCOL'] = tbd.GPS_to_grids(
            data['slon'], data['slat'], params)
        res = data[['LONCOL', 'LATCOL']].values
        truth = [[6, 25],
                 [6, 25],
                 [6, 25],
                 [6, 25],
                 [7, 28],
                 [7, 31],
                 [7, 27],
                 [8, 26],
                 [8, 35],
                 [13, 19],
                 [13, 19],
                 [14, 19],
                 [14, 19],
                 [17, 17],
                 [18, 16],
                 [18, 17],
                 [19, 17],
                 [20, 12],
                 [22, 16]]
        assert np.allclose(res, truth)
        oddata = tbd.taxigps_to_od(
            data, col=['VehicleNum', 'time', 'slon', 'slat', 'OpenStatus'])
        assert len(oddata) == 4
        res2 = tbd.odagg_grid(oddata, params,arrow = True)[['SLONCOL', 'SLATCOL']].values
        truth = [[6, 25],
                 [7, 28],
                 [17, 17],
                 [18, 16]]
        assert np.allclose(res2, truth)
        assert len(tbd.odagg_shape(oddata, self.sz,params=params)) == 1
        assert len(tbd.odagg_shape(oddata, self.sz)) == 1
        data['count'] = 1
        assert tbd.dataagg(data,self.sz,col = ['slon','slat','count'],accuracy=500)[0]['count'].iloc[0]==19
