import transbigdata as tbd
import numpy as np

class TestGetbusdata:
    def test_getbusdata(self):

        data, stop = tbd.getbusdata('深圳市', ['地铁1号线'])
        assert '地铁1号线' in data['linename'].sum()
        assert '世界之窗' in tbd.split_subwayline(data, stop)['stationnames'].sum()

        data['speed'] = 36 #operation speed 36km/h
        data['stoptime'] = 0.5 #stop time at each stations 30s
        G = tbd.metro_network(data,stop, transfertime=10)
        path = tbd.get_shortest_path(G,stop,'罗湖','竹子林')
        assert len(path) == 12
        traveltime = tbd.get_path_traveltime(G,path)
        assert np.allclose(traveltime,28.3142682125485)
        paths = tbd.get_k_shortest_paths(G,stop,'罗湖','竹子林',20)
        assert len(paths) == 1

    def test_getadmin(self):
        admin, _ = tbd.getadmin(
            '深圳市', ak='2305ee7c82c147f11aac58fcc5bb7f19',jscode = '694338a096c6c50b74e5d74f411c9ab5', subdistricts=True)
        assert '深圳市' in admin['name'].sum()

    def test_getisochrone(self):
        tbd.get_isochrone_mapbox(
            120, 30, 20,
            access_token='pk.eyJ1IjoibHByMTIxNDc5IiwiYSI6ImNrd2c0YXVydTBremQyb3V0cHVhMml5anAifQ.Y-q937VgT0diVxukUqwofw',
            mode='walking')
        tbd.get_isochrone_amap(
            121.212403, 31.282477, 60, ak='2305ee7c82c147f11aac58fcc5bb7f19', jscode = '694338a096c6c50b74e5d74f411c9ab5',
            mode=0)
