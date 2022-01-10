import transbigdata as tbd
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Polygon


class TestGisprocess:
    def setup_method(self):
        self.Centerline = gpd.read_file('{"type": "FeatureCollection", "features": [{"id": "0", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68570740160918, 44.0787457866043], [87.68645046729048, 44.076232872455286]]}}, {"id": "1", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68264271353992, 44.075612961425655], [87.68375615646332, 44.07414940028094]]}}, {"id": "2", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68645046729048, 44.076232872455286], [87.68708471544996, 44.07365060928234]]}}, {"id": "3", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68645046729048, 44.076232872455286], [87.6875136241044, 44.07504676107092], [87.68851961299117, 44.0746480974192]]}}, {"id": "4", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68645046729048, 44.076232872455286], [87.68621557677827, 44.07507660904865], [87.6856695946903, 44.0744984489369]]}}, {"id": "5", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68375615646332, 44.07414940028094], [87.68443421646374, 44.07310623751142], [87.68516775880424, 44.072626945592525], [87.68612967919796, 44.07240268063775], [87.68760135753165, 44.07243204581898]]}}, {"id": "6", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68375615646332, 44.07414940028094], [87.6856695946903, 44.0744984489369]]}}, {"id": "7", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68733133758964, 44.07337902470143], [87.68760135753165, 44.07243204581898]]}}, {"id": "8", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68708471544996, 44.07365060928234], [87.68733133758964, 44.07337902470143]]}}, {"id": "9", "type": "Feature", "properties": {"Id": 0}, "geometry": {"type": "LineString", "coordinates": [[87.68733133758964, 44.07337902470143], [87.68778577868343, 44.07424246258923], [87.68851961299117, 44.0746480974192]]}}]}')
        self.dfA = gpd.GeoDataFrame([[1, 2], [2, 4], [2, 6],
                                     [2, 10], [24, 6], [21, 6],
                                     [22, 6]], columns=['lon1', 'lat1'])
        self.dfB = gpd.GeoDataFrame(
            [[1, 3], [2, 5], [2, 2]], columns=['lon', 'lat'])

    def test_splitline_with_length(self):
        splitedline = tbd.splitline_with_length(self.Centerline, maxlength=100)
        result = splitedline['length'].max()
        assert np.allclose(result, 0.0045634806283561345)

    def test_ckdnearest(self):

        result = tbd.ckdnearest(self.dfA, self.dfB, Aname=['lon1', 'lat1'], Bname=[
                                'lon', 'lat'])[['lon1', 'lat1', 'lon', 'lat']].values
        truth = [[1,  2,  1,  3],
                 [2,  4,  2,  5],
                 [2,  6,  2,  5],
                 [2, 10,  2,  5],
                 [24,  6,  2,  5],
                 [21,  6,  2,  5],
                 [22,  6,  2,  5]]
        assert np.allclose(result, truth)

    def test_ckdnearest_point(self):
        dfA = self.dfA
        dfB = self.dfB
        dfA['geometry'] = gpd.points_from_xy(dfA['lon1'], dfA['lat1'])
        dfB['geometry'] = gpd.points_from_xy(dfB['lon'], dfB['lat'])
        tbd.ckdnearest_point(dfA, dfB)
        result = tbd.ckdnearest_point(
            dfA, dfB)[['lon1', 'lat1', 'lon', 'lat']].values
        truth = [[1,  2,  1,  3],
                 [2,  4,  2,  5],
                 [2,  6,  2,  5],
                 [2, 10,  2,  5],
                 [24,  6,  2,  5],
                 [21,  6,  2,  5],
                 [22,  6,  2,  5]]
        assert np.allclose(result, truth)

    def test_ckdnearest_line(self):
        dfA = self.dfA
        dfB = self.dfB
        dfA['geometry'] = gpd.points_from_xy(
            self.dfA['lon1'], self.dfA['lat1'])
        dfB['geometry'] = [LineString([[1, 1], [1.5, 2.5], [3.2, 4]]),
                           LineString([[1, 0], [1.5, 0], [4, 0]]),
                           LineString([[1, -1], [1.5, -2], [4, -4]])]
        result = tbd.ckdnearest_line(
            dfA, dfB)[['lon1', 'lat1', 'lon', 'lat']].values
        truth = [[1,  2,  1,  3],
                 [2,  4,  1,  3],
                 [2,  6,  1,  3],
                 [2, 10,  1,  3],
                 [21,  6,  1,  3],
                 [22,  6,  1,  3],
                 [24,  6,  2,  5]]
        assert np.allclose(result, truth)

    def test_merge_polygon(self):
        dfB = gpd.GeoDataFrame([[1, 2], [2, 4], [2, 6]],
                               columns=['lon1', 'lat1'])
        dfB['geometry'] = [Polygon([[1, 1], [1.5, 2.5], [3.2, 4]]),
                           Polygon([[1, 0], [1.5, 0], [4, 10]]),
                           Polygon([[1, -1], [1.5, -2], [4, 10]])]
        res = tbd.merge_polygon(dfB, 'lon1')
        result = res[res['lon1'] == 2]['geometry'].iloc[0]
        result = np.array(result.exterior.coords)
        truth = [[1.5, -2.],
                 [1., -1.],
                 [1.27272727,  0.],
                 [1.,  0.],
                 [4., 10.],
                 [1.5, -2.]]
        assert np.allclose(result, truth)
        result2 = tbd.polyon_exterior(res, minarea=1)
        result2 = result2[result2['lon1'] == 1]['geometry'].iloc[0]
        result2 = np.array(result2.exterior.coords)
        truth2 = [[1., 1.],
                  [1.5, 2.5],
                  [3.2, 4.],
                  [1., 1.]]
        assert np.allclose(result2, truth2)
    def test_ellipse_params(self):
        np.random.seed(1)
        data = np.random.uniform(1,10,(100,2))
        data[:,1:] = 0.5*data[:,0:1]+np.random.uniform(-2,2,(100,1))
        data = pd.DataFrame(data,columns = ['x','y'])
        ellip_params = tbd.ellipse_params(data,confidence=95,col = ['x','y'])
        assert np.allclose(ellip_params[0],[5.0412876 , 2.73948777])
        assert np.allclose(ellip_params[1:], [
        4.862704682680083,
        15.338646317379267,
        -62.20080325474961,
        58.580734145363145,
        0.6829769340746545])