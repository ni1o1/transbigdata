公交GPS的到离站信息匹配
=======================

::

    import transbigdata as tbd
    import pandas as pd
    import geopandas as gpd

读取数据
--------

读取GPS数据

::

    BUS_GPS= pd.read_csv(r'busgps.csv',header = None)
    BUS_GPS.columns = ['GPSDateTime', 'LineId', 'LineName', 'NextLevel', 'PrevLevel',
           'Strlatlon', 'ToDir', 'VehicleId', 'VehicleNo', 'unknow']
    #时间转换为datetime格式
    BUS_GPS['GPSDateTime'] = pd.to_datetime(BUS_GPS['GPSDateTime'])




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>GPSDateTime</th>
          <th>LineId</th>
          <th>LineName</th>
          <th>NextLevel</th>
          <th>PrevLevel</th>
          <th>Strlatlon</th>
          <th>ToDir</th>
          <th>VehicleId</th>
          <th>VehicleNo</th>
          <th>unknow</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>2019-01-16 23:59:59</td>
          <td>7100</td>
          <td>71</td>
          <td>2</td>
          <td>1</td>
          <td>121.335413,31.173188</td>
          <td>1</td>
          <td>沪D-R7103</td>
          <td>Z5A-0021</td>
          <td>1</td>
        </tr>
        <tr>
          <th>1</th>
          <td>2019-01-17 00:00:00</td>
          <td>7100</td>
          <td>71</td>
          <td>2</td>
          <td>1</td>
          <td>121.334616,31.172271</td>
          <td>1</td>
          <td>沪D-R1273</td>
          <td>Z5A-0002</td>
          <td>1</td>
        </tr>
        <tr>
          <th>2</th>
          <td>2019-01-17 00:00:00</td>
          <td>7100</td>
          <td>71</td>
          <td>24</td>
          <td>23</td>
          <td>121.339955,31.173025</td>
          <td>0</td>
          <td>沪D-R5257</td>
          <td>Z5A-0020</td>
          <td>1</td>
        </tr>
        <tr>
          <th>3</th>
          <td>2019-01-17 00:00:01</td>
          <td>7100</td>
          <td>71</td>
          <td>14</td>
          <td>13</td>
          <td>121.409491,31.20433</td>
          <td>0</td>
          <td>沪D-R5192</td>
          <td>Z5A-0013</td>
          <td>1</td>
        </tr>
        <tr>
          <th>4</th>
          <td>2019-01-17 00:00:03</td>
          <td>7100</td>
          <td>71</td>
          <td>15</td>
          <td>14</td>
          <td>121.398615,31.200253</td>
          <td>0</td>
          <td>沪D-T0951</td>
          <td>Z5A-0022</td>
          <td>1</td>
        </tr>
      </tbody>
    </table>
    </div>



经纬度坐标转换

::

    #切分经纬度的字符串
    BUS_GPS['lon'] = BUS_GPS['Strlatlon'].apply(lambda r:r.split(',')[0])
    BUS_GPS['lat'] = BUS_GPS['Strlatlon'].apply(lambda r:r.split(',')[1])
    #坐标系转换
    BUS_GPS['lon'],BUS_GPS['lat'] = tbd.gcj02towgs84(BUS_GPS['lon'].astype(float),BUS_GPS['lat'].astype(float))
    BUS_GPS.head(5)

读取公交线数据

::

    shp = r'busline.json'
    linegdf = gpd.GeoDataFrame.from_file(shp,encoding = 'gbk')
    line = linegdf.iloc[:1].copy()
    line.plot()









.. image:: output_8_1.png


读取公交站点数据

::

    shp = r'busstop.json'
    stop = gpd.GeoDataFrame.from_file(shp,encoding = 'gbk')
    stop.plot()









.. image:: output_10_1.png


到离站信息匹配
--------------

::

    tbd.busgps_arriveinfo(BUS_GPS,line,stop)


数据清洗中...  
数据投影中......  
匹配到离站信息...........................................  



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>arrivetime</th>
          <th>leavetime</th>
          <th>stopname</th>
          <th>VehicleId</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>2019-01-17 07:19:42</td>
          <td>2019-01-17 07:31:14</td>
          <td>延安东路外滩</td>
          <td>沪D-R0725</td>
        </tr>
        <tr>
          <th>1</th>
          <td>2019-01-17 09:53:08</td>
          <td>2019-01-17 10:09:34</td>
          <td>延安东路外滩</td>
          <td>沪D-R0725</td>
        </tr>
        <tr>
          <th>2</th>
          <td>2019-01-17 12:54:34</td>
          <td>2019-01-17 13:11:43</td>
          <td>延安东路外滩</td>
          <td>沪D-R0725</td>
        </tr>
        <tr>
          <th>3</th>
          <td>2019-01-17 15:37:36</td>
          <td>2019-01-17 15:42:28</td>
          <td>延安东路外滩</td>
          <td>沪D-R0725</td>
        </tr>
        <tr>
          <th>4</th>
          <td>2019-01-17 18:35:52</td>
          <td>2019-01-17 18:46:11</td>
          <td>延安东路外滩</td>
          <td>沪D-R0725</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>3</th>
          <td>2019-01-17 12:05:55</td>
          <td>2019-01-17 12:08:02</td>
          <td>河南中路</td>
          <td>沪D-T9651</td>
        </tr>
        <tr>
          <th>4</th>
          <td>2019-01-17 14:42:54</td>
          <td>2019-01-17 14:44:06</td>
          <td>河南中路</td>
          <td>沪D-T9651</td>
        </tr>
        <tr>
          <th>5</th>
          <td>2019-01-17 14:55:33</td>
          <td>2019-01-17 14:58:36</td>
          <td>河南中路</td>
          <td>沪D-T9651</td>
        </tr>
        <tr>
          <th>6</th>
          <td>2019-01-17 17:30:15</td>
          <td>2019-01-17 17:31:38</td>
          <td>河南中路</td>
          <td>沪D-T9651</td>
        </tr>
        <tr>
          <th>7</th>
          <td>2019-01-17 18:02:19</td>
          <td>2019-01-17 18:12:45</td>
          <td>河南中路</td>
          <td>沪D-T9651</td>
        </tr>
      </tbody>
    </table>
    <p>9406 rows × 4 columns</p>
    </div>


