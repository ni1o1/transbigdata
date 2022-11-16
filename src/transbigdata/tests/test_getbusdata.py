import transbigdata as tbd

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
        #assert np.allclose(traveltime,28.3142682125485)
        paths = tbd.get_k_shortest_paths(G,stop,'罗湖','竹子林',20)
        assert len(paths) == 1

    def test_getadmin(self):

        admin = 0
        t = 0
        while (type(admin)==int)&(t<2):
            try:
                admin, _ = tbd.getadmin(
                    '深圳市', 
                    ak='169521e66b7a30adcaa36ae0a9c04c8d',
                    jscode = '2cdd826ad4099fae293dbabf3657c78d', 
                    subdistricts=True)
            except:     # pragma: no cover
                t+=1    # pragma: no cover
        #assert '深圳市' in list(admin['name'])

    def test_getisochrone(self):

        result = 0
        t = 0
        while (type(result)==int)&(t<2):
            try:
                result = tbd.get_isochrone_mapbox(
                    120, 30, 20,
                    access_token='pk.eyJ1IjoibHByMTIxNDc5IiwiYSI6ImNrd2c0YXVydTBremQyb3V0cHVhMml5anAifQ.Y-q937VgT0diVxukUqwofw',
                    mode='walking')
            except:     # pragma: no cover
                t+=1    # pragma: no cover
            
        import geopandas as gpd
        #assert type(result) == gpd.geodataframe.GeoDataFrame

        result = 0
        t = 0
        while (type(result)==int)&(t<2):
            try:
                result = tbd.get_isochrone_amap(
                    121.212403, 31.282477, 60,
                    ak='169521e66b7a30adcaa36ae0a9c04c8d',
                    jscode = '2cdd826ad4099fae293dbabf3657c78d', 
                    mode=0)
            except:     # pragma: no cover
                t+=1    # pragma: no cover

        import geopandas as gpd
        #assert type(result) == gpd.geodataframe.GeoDataFrame