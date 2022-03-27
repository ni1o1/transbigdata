import transbigdata as tbd
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon


class TestGrids:
    def setup_method(self):
        self.bounds = [113.6, 22.4, 113.605, 22.405]
        self.params = (113.6, 22.4, 0.004863669213934598, 0.004496605206422906)

    def test_rect_grids(self):
        result = tbd.rect_grids(self.bounds, accuracy=500)
        res1 = result[0]['geometry'].iloc[0]
        res2 = result[1]
        assert np.allclose(
            np.array(res1.exterior.coords), [
                [113.59756817,  22.3977517],
                [113.60243183, 22.3977517],
                [113.60243183, 22.4022483],
                [113.59756817, 22.4022483],
                [113.59756817,  22.3977517]])
        truth = (113.6, 22.4, 0.004863669213934598, 0.004496605206422906)
        assert np.allclose(res2, truth)

    def test_grid_params(self):
        result = tbd.grid_params(self.bounds, accuracy=500)
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
            [[113.6, 22.4], [113.61, 22.41], [113.6, 22.42]])
        ], columns=['geometry'])
        result = tbd.gridid_sjoin_shape(data, shape, self.params, col=[
                                        'LONCOL', 'LATCOL'])['geometry'].iloc[0]
        truth = [[113.60243183,  22.4022483],
                 [113.6072955,  22.4022483],
                 [113.6072955,  22.40674491],
                 [113.60243183,  22.40674491],
                 [113.60243183,  22.4022483]]
        assert np.allclose(np.array(result.exterior.coords), truth)

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
        truth = (113.60000000000001,
                 22.400000000000002,
                 0.004863669213932553,
                 0.004496605206423254)
        assert np.allclose(result, truth)

    def test_grid_from_params(self):
        result = list(tbd.rect_grids(self.bounds, params=self.params)[
                      0]['geometry'].iloc[3].exterior.coords)
        truth = [(113.60243183460696, 22.402248302603212),
                 (113.6072955038209, 22.402248302603212),
                 (113.6072955038209, 22.406744907809635),
                 (113.60243183460696, 22.406744907809635),
                 (113.60243183460696, 22.402248302603212)]
        assert np.allclose(result, truth)

    def test_tri_hexa_grids(self):
        params = [113.75, 22.4, 0.04871681446449111, 0.044966052064229066, 25]
        assert tbd.GPS_to_grids_tri(120, 31.3, params)[0] == '32,-186,-219'
        assert tbd.GPS_to_grids_hexa(120, 31.3, params)[0] == '32,-186,-218'

        hexagon = np.array(tbd.gridid_to_polygon_hexa(
            '32,-186,-218', params)[0].exterior.coords)
        truth = np.array([[119.909123,  31.293],
                          [119.932897,  31.340058],
                          [119.988936,  31.344583],
                          [120.021201,  31.302051],
                          [119.997428,  31.254993],
                          [119.941388,  31.250468],
                          [119.909123,  31.293]])
        assert np.allclose(hexagon.shape, truth.shape)

        triangle = np.array(tbd.gridid_to_polygon_tri(
            '32,-186,-219', params)[0].exterior.coords)
        truth = np.array([[120.021201,  31.302051],
                          [119.965162,  31.297525],
                          [119.997428,  31.254993],
                          [120.021201,  31.302051]])
        assert np.allclose(triangle.shape, truth.shape)
