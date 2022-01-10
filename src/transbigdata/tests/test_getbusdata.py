import transbigdata as tbd
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import networkx as nx

class TestGetbusdata:
    def test_getbusdata(self):
        data,stop = tbd.getbusdata('深圳市',['地铁1号线'])
        assert '地铁1号线' in data['linename'].sum()
        assert '世界之窗' in tbd.split_subwayline(data,stop)['stationnames'].sum()
        G = tbd.metro_network(stop)
        assert type(G) == nx.classes.graph.Graph
        
    def test_getadmin(self):
        admin,districts = tbd.getadmin('深圳市','f35aa69595d3fd9527dfe9033a640b9c',subdistricts = True)
        assert '深圳市' in admin['name'].sum()
    