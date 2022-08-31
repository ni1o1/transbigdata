import transbigdata as tbd
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon


class TestGrids:
    def setup_method(self):
        self.bounds = [113.6, 22.4, 113.605, 22.405]
        self.params = [113.6, 22.4, 0.004863669213934598, 0.004496605206422906]
        self.shape = gpd.GeoDataFrame([Polygon([[113.59, 22.39], [113.61, 22.39], [113.61, 22.41], [113.6, 22.42]])],columns = ['geometry'])
        self.shape.crs = 'epsg:4326'
    def test_rect_grids(self):
        result = tbd.rect_grids(self.bounds, accuracy=500)
        res1 = result[0]['geometry'].iloc[0]
        res2 = result[1]
        res2 = [res2['slon'], res2['slat'], res2['deltalon'], res2['deltalat']]
        assert np.allclose(
            np.array(res1.exterior.coords), [[113.5927045,  22.39325509],
                                             [113.59756817,  22.39325509],
                                             [113.59756817,  22.3977517],
                                             [113.5927045,  22.3977517],
                                             [113.5927045,  22.39325509]])

        truth = [113.6, 22.4, 0.004863669213934598, 0.004496605206422906]
        assert np.allclose(res2, truth)

    def test_grid_params(self):
        result = tbd.grid_params(self.bounds, accuracy=500)
        result = [result['slon'], result['slat'],
                  result['deltalon'], result['deltalat']]
        truth = (113.6, 22.4, 0.004863669213934598, 0.004496605206422906)
        assert np.allclose(result, truth)

    def test_GPS_to_grids(self):
        result = tbd.GPS_to_grids(113.7, 22.7, self.params)
        truth = [21, 67]
        assert np.allclose(result, truth)

    def test_grids_centre(self):
        result = tbd.grids_centre(21, 67, self.params)
        truth = (113.70213705349262, 22.70127254883033)
        assert np.allclose(result, truth)

    def test_gridid_to_polygon(self):
        result = tbd.gridid_to_polygon(
            pd.Series(21), pd.Series(67), self.params)[0]
        truth = [[113.69970522,  22.69902425],
                 [113.70456889,  22.69902425],
                 [113.70456889,  22.70352085],
                 [113.69970522,  22.70352085],
                 [113.69970522,  22.69902425]]
        assert np.allclose(np.array(result.exterior.coords), truth)

    def test_gridid_sjoin_shape(self):
        data = pd.DataFrame([[1, 1], [10, 10], [100, 100]],
                            columns=['LONCOL', 'LATCOL'])
        shape = gpd.GeoDataFrame([Polygon([[1, 1], [10, 10], [100, 100]]),
                                  Polygon(
            [[113.59, 22.39], [113.61, 22.39], [113.61, 22.41], [113.6, 22.42]])
        ], columns=['geometry'])
        result = tbd.gridid_sjoin_shape(data, shape, self.params, col=[
                                        'LONCOL', 'LATCOL'])['geometry'].iloc[0]
        truth = [(113.60486366921393, 22.404496605206422)]
        assert np.allclose(list(result.coords), truth)

    def test_geohash(self):
        d = pd.DataFrame([[113.59550842,  22.4],
                          [113.59775421,  22.40359627],
                          [113.60224579,  22.40359627],
                          [113.60449158,  22.4],
                          [113.60224579,  22.39640364],
                          [113.59775421,  22.39640364],
                          [113.59550842,  22.4]], columns=['lon', 'lat'])
        c = tbd.geohash_encode(d['lon'], d['lat'], precision=12)
        assert c.sum() == 'webz2vv9rnwkwebz2yrq7t0cwebz3n6wkjn1webz3ju32w8swebz3j4ss0npwebz2vpke80zwebz2vv9rnwk'
        result = np.array(tbd.geohash_togrid(c).iloc[0].exterior.coords)
        truth = [[113.59550837,  22.39999987],
                 [113.59550837,  22.40000004],
                 [113.59550871,  22.40000004],
                 [113.59550871,  22.39999987],
                 [113.59550837,  22.39999987]]
        assert np.allclose(result, truth)
        c = tbd.geohash_decode(c)[0].astype('float').values
        assert np.allclose(c,
                           [113.595509, 113.597754,
                            113.602246, 113.604492,
                            113.602246, 113.597754, 113.595509])

    def test_regenerate_params(self):
        grid, params = tbd.rect_grids(self.bounds, 500)
        result = tbd.regenerate_params(grid)
        result = [result['slon'], result['slat'],
                  result['deltalon'], result['deltalat']]
        truth = (113.60000000000001,
                 22.400000000000002,
                 0.004863669213932553,
                 0.004496605206423254)
        assert np.allclose(result, truth)

    def test_grid_from_params(self):
        result = list(tbd.rect_grids(self.bounds, params=self.params)[
                      0]['geometry'].iloc[3].exterior.coords)
        truth = [(113.6072955038209, 22.393255092190365),
                 (113.61215917303483, 22.393255092190365),
                 (113.61215917303483, 22.39775169739679),
                 (113.6072955038209, 22.39775169739679),
                 (113.6072955038209, 22.393255092190365)]
        assert np.allclose(result, truth)

    def test_tri_hexa_grids(self):
        #三角形
        params = {'slon': 113.75,
                  'slat':  22.4,
                  'deltalon': 0.04871681446449111,
                  'deltalat': 0.044966052064229066,
                  'theta': 25,
                  'method': 'tri'}
        #测试栅格编号
        assert tbd.GPS_to_grid(120, 31.3, params)[-1] == -219

        #测试栅格polygon
        triangle = np.array(tbd.grid_to_polygon(
            [32, -186, -219], params)[0].exterior.coords)
        truth = np.array([[120.021201,  31.302051],
                          [119.965162,  31.297525],
                          [119.997428,  31.254993],
                          [120.021201,  31.302051]])
        assert np.allclose(triangle.shape, truth.shape)

        #测试栅格中心点
        result = tbd.grid_to_centre( [32, -186, -219], params)
        truth = [[119.994597],[31.28485633]]
        assert np.allclose(result,truth)

        #六边形
        params['method'] = 'hexa'
        #测试栅格编号
        assert tbd.GPS_to_grid(120, 31.3, params)[-1] == -218

        #测试栅格polygon
        hexagon = np.array(tbd.grid_to_polygon(
            [32, -186, -218], params)[0].exterior.coords)
        truth = np.array([[119.909123,  31.293],
                          [119.932897,  31.340058],
                          [119.988936,  31.344583],
                          [120.021201,  31.302051],
                          [119.997428,  31.254993],
                          [119.941388,  31.250468],
                          [119.909123,  31.293]])
        assert np.allclose(hexagon.shape, truth.shape)

        #测试栅格中心点
        result = tbd.grid_to_centre( [32, -186, -218], params)
        truth = [[119.96516214],[31.29752543]]
        assert np.allclose(result,truth)

    def test_params_optimize(self):
        data = pd.DataFrame([
            [34745, '20:27:43', 113.80684699999999, 22.623248999999998, 1, 27],
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
            [22233, '18:51:30', 113.964569, 22.541849, 0, 0]],
            columns=['Vehicleid',
                     'Time',
                     'slon',
                     'slat',
                     'OpenStatus',
                     'Speed'])
        initialparams = {'slon': 113.75,
                    'slat':  22.4,
                    'deltalon': 0.04871681446449111,
                    'deltalat': 0.044966052064229066,
                    'theta': 25,
                    'method': 'hexa'}
        #Optimize gridding params
        params_optimized = tbd.grid_params_optimize(data,
                                                    initialparams,
                                                    col=['Vehicleid','slon','slat'],
                                                    optmethod='centerdist',
                                                    sample=0, #not sampling
                                                    printlog=True,
                                                    max_iter=1)
        #Optimize gridding params
        params_optimized = tbd.grid_params_optimize(data,
                                                    initialparams,
                                                    col=['Vehicleid','slon','slat'],
                                                    optmethod='gini',
                                                    sample=0, #not sampling
                                                    printlog=True,
                                                    max_iter=1)

        params_optimized = tbd.grid_params_optimize(data,
                                                    initialparams,
                                                    col=['Vehicleid','slon','slat'],
                                                    optmethod='gridscount',
                                                    sample=10, #not sampling
                                                    printlog=True,
                                                    max_iter=1)
        #Optimize gridding params
        initialparams = {'slon': 113.75,
                    'slat':  22.4,
                    'deltalon': 0.04871681446449111,
                    'deltalat': 0.044966052064229066,
                    'theta': 25,
                    'method': 'rect'}
        #Optimize gridding params
        params_optimized = tbd.grid_params_optimize(data,
                                                    initialparams,
                                                    col=['Vehicleid','slon','slat'],
                                                    optmethod='centerdist',
                                                    sample=0, #not sampling
                                                    printlog=True,
                                                    max_iter=1)
        #Optimize gridding params
        params_optimized = tbd.grid_params_optimize(data,
                                                    initialparams,
                                                    col=['Vehicleid','slon','slat'],
                                                    optmethod='gini',
                                                    sample=0, #not sampling
                                                    printlog=True,
                                                    max_iter=1)

        params_optimized = tbd.grid_params_optimize(data,
                                                    initialparams,
                                                    col=['Vehicleid','slon','slat'],
                                                    optmethod='gridscount',
                                                    sample=10, #not sampling
                                                    printlog=True,
                                                    max_iter=1)
                                                    
    def test_area_to_grid(self):

        assert len(tbd.area_to_grid(self.shape)[0]) == 30
        assert len(tbd.area_to_grid(self.shape,method = 'tri')[0]) == 41
        assert len(tbd.area_to_grid(self.shape,method = 'hexa')[0]) == 10
    def test_area_to_params(self):
        assert np.allclose(tbd.area_to_params(self.shape)['deltalat'], 0.004496605206422906)

    def test_grid_to_centre(self):

        params = tbd.area_to_grid(self.shape,method = 'hexa')[1]
        assert np.allclose(tbd.grid_to_centre([1,2,3], params),[[113.59486376],[22.38221165]])

    def test_grid_to_area(self):
        data = pd.DataFrame([[0, -1, -1], [2,-3,-5], [100, 100, 0]],
                        columns=['loncol_1', 'loncol_2', 'loncol_3'])
        shape = gpd.GeoDataFrame([Polygon(
            [[113.59, 22.39], [113.61, 22.39], [113.61, 22.41], [113.6, 22.42]])
        ], columns=['geometry'])
        _,params = tbd.area_to_grid(shape, method='hexa')

        result = tbd.grid_to_area(data, shape, params, col=[
            'loncol_1', 'loncol_2', 'loncol_3'])['geometry'].iloc[0]
        truth = [113.59972751340152, 22.410768929810946]

        assert np.allclose([result.x,result.y],truth)
    
    def test_grid_to_params(self):

        shape = gpd.GeoDataFrame([Polygon(
            [[113.59, 22.39], [113.61, 22.39], [113.61, 22.41], [113.6, 22.42]])
        ], columns=['geometry'])
        grids,_ = tbd.area_to_grid(shape,params = {'slon': 113.59,
        'slat': 22.390000000000004,
        'deltalon': 0.004863756700757449,
        'deltalat': 0.0044966052064197015,
        'theta': 10,
        'method': 'rect'})
        assert np.allclose(tbd.grid_to_params(grids)['theta'],10)

