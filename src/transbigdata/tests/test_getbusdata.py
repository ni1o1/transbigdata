import transbigdata as tbd
import networkx as nx


class TestGetbusdata:
    def test_getbusdata(self):

        data, stop = tbd.getbusdata('深圳市', ['地铁1号线'])
        assert '地铁1号线' in data['linename'].sum()
        assert '世界之窗' in tbd.split_subwayline(data, stop)['stationnames'].sum()
        G = tbd.metro_network(stop)
        assert type(G) == nx.classes.graph.Graph

    def test_getadmin(self):
        admin, _ = tbd.getadmin(
            '深圳市', 'f35aa69595d3fd9527dfe9033a640b9c', subdistricts=True)
        assert '深圳市' in admin['name'].sum()

    def test_getisochrone(self):
        tbd.get_isochrone_mapbox(
            120, 30, 20,
            access_token='pk.eyJ1IjoibHByMTIxNDc5IiwiYSI6ImNrd2c0YXVydTBremQyb3V0cHVhMml5anAifQ.Y-q937VgT0diVxukUqwofw',
            mode='walking')
        tbd.get_isochrone_amap(
            121.212403, 31.282477, 60, ak='f35aa69595d3fd9527dfe9033a640b9c',
            mode=0)
