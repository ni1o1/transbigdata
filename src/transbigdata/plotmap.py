'''
BSD 3-Clause License

Copyright (c) 2021, Qing Yu
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import numpy as np
import math
import io
from PIL import Image
import os
import warnings
from configparser import ConfigParser


def set_mapboxtoken(mapboxtoken):
    config_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'config.ini')
    config = ConfigParser()
    config.read(config_path)
    if not config.has_section('MAPBOX'):
        config.add_section('MAPBOX')   # pragma: no cover

    config.set('MAPBOX', 'mapboxtoken', mapboxtoken)
    with open(config_path, 'w') as configfile:
        config.write(configfile)
        print('Set mapboxtoken success')


def read_mapboxtoken():
    '''
    Read mapboxtoken
    '''
    try:
        config_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'config.ini')
        config = ConfigParser()
        config.read(config_path)
        mapboxtoken = config['MAPBOX']['mapboxtoken']
    except Exception:  # pragma: no cover
        warnings.warn("Mapboxtoken not found, "   # pragma: no cover
                      "The basemap is set as OpenStreetMap"
                      "please use tbd.set_mapboxtoken() to set the access token, see: "
                      "https://transbigdata.readthedocs.io/en/latest/plot_map.html"
                      )
        mapboxtoken = ''  # pragma: no cover
    return mapboxtoken


def set_imgsavepath(imgsavepath):
    '''
    Set savepath for maps

    Parameters
    -------
    imgsavepath : str
        savepath
    '''
    if not os.path.exists(imgsavepath):
        raise ValueError('Path do not exist')  # pragma: no cover
    config_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'config.ini')
    config = ConfigParser()
    config.read(config_path)
    if not config.has_section('MAPBOX'):
        config.add_section('MAPBOX')   # pragma: no cover

    config.set('MAPBOX', 'imgsavepath', imgsavepath)
    with open(config_path, 'w') as configfile:
        config.write(configfile)
        print('Set imgsavepath success')


def read_imgsavepath():
    '''
    Read map savepath
    '''
    try:
        config_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'config.ini')
        config = ConfigParser()
        config.read(config_path)
        imgsavepath = config['MAPBOX']['imgsavepath']
    except Exception:  # pragma: no cover
        warnings.warn('Map base map storage path not found, \
        please use tbd.set_imgsavepath() to set it first, \
        see: https://transbigdata.readthedocs.io/en/latest/plot_map.html')  # pragma: no cover
        imgsavepath = ''  # pragma: no cover
    return imgsavepath


def deg2num(lat_deg, lon_deg, zoom):
    '''
    Calculate xy tiles from coordinates

    Parameters
    -------
    lon_deg : number
        Longitude
    lat_deg : number
        Latitude
    zoom : Int
        Zoom level of the map
    '''
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) +
                (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
    '''
    Calculate coordinates from xy tiles

    Parameters
    -------
    xtile : Int
        x tile
    ytile : Int
        y tile
    zoom : Int
        Zoom level of the map
    '''
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


def getImageCluster(lon_deg, lat_deg, delta_long, delta_lat, zoom,
                    printlog, imgsavepath, style=4, access_token=''):
    '''
    Get map image
    '''
    smurl = ''
    if (style == 1) | (style == 'streets'):
        styleid = 'ckwinzgw581od14mpyfhka6nk'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 2) | (style == 'outdoors'):
        styleid = 'ckwinx7aj4y4a15p7ftfwq9dn'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 3) | (style == 'satellite'):
        styleid = 'cjv36cj9u4h1q1ftemjed4f2y'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 4) | (style == 'light'):
        styleid = 'ckwfx658z4dpb14ocnz6tky9d'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 5) | (style == 'dark'):
        styleid = 'cjetnd20i1vbi2qqxbh0by7p8'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 6) | (style == 'light-ch'):
        styleid = 'ckj9bhq7s9mvj19mq3e3fye35'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 7) | (style == 'ice creem'):
        styleid = 'cjv36iiz9243t1fo8mweb4z6r'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 8) | (style == 'night'):
        styleid = 'ck2o3fyvy0dch1cp6j2pkz2dv'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 9) | (style == 'terrain'):
        styleid = 'cjv36gyklf43q1fnuwibiuetl'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 10) | (style == 'basic blue'):
        styleid = 'ckwio2ze12fgk15p2alr5a4xj'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 11):
        styleid = 'cl39hgul1000514llp3yj7yh3'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 12):
        styleid = 'cl38pljx0006r14qp7ioy7gcc'  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/ni1o1/'+styleid + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if (style == 0) | (style == 'OSM'):
        styleid = 'osm'  # pragma: no cover
        smurl = r'https://tile.openstreetmap.org/{0}/{1}/{2}.png'  # pragma: no cover
    if (str(style)[:16] == 'mapbox://styles/'):
        styleid = style.split('/')[-1]  # pragma: no cover
        smurl = r'https://api.mapbox.com/styles/v1/'+style[16:] + \
            r'/tiles/256/{0}/{1}/{2}?&access_token=' + \
                access_token  # pragma: no cover
    if smurl == '':
        raise ValueError('Style error')  # pragma: no cover

    xmin, ymax = deg2num(lat_deg, lon_deg, zoom)
    xmax, ymin = deg2num(lat_deg + delta_lat, lon_deg + delta_long, zoom)

    def get_img(smurl, zoom, xtile, ytile, imgsize, imgsavepath):
        import os

        filename = str(style)+str(styleid)+'-'+str(zoom)+'-' + \
            str(xtile)+'-'+str(ytile)+'-'+str(imgsize)+'.png'

        def savefig(filename, tile):
            try:
                if 'tileimg' in os.listdir(imgsavepath):
                    if filename in os.listdir(imgsavepath+'tileimg'):  # pragma: no cover
                        pass  # pragma: no cover
                    else:

                        tile.save(os.path.join(imgsavepath+'tileimg',
                                  filename))  # pragma: no cover
                        if printlog:  # pragma: no cover
                            print('figsaved:'+os.path.join(imgsavepath+'tileimg',
                                  filename))  # pragma: no cover
                else:
                    os.mkdir(imgsavepath+'tileimg')
            except Exception as e:
                print(e)

        def loadfig(filename):
            try:
                if 'tileimg' in os.listdir(imgsavepath):
                    if filename in os.listdir(imgsavepath+'tileimg'):  # pragma: no cover
                        tile = Image.open(
                            os.path.join(os.path.join(imgsavepath, 'tileimg'), filename))  # pragma: no cover
                        return tile  # pragma: no cover
                    else:
                        return None  # pragma: no cover
                else:
                    os.mkdir(imgsavepath+'tileimg')
                    return None  # pragma: no cover
            except Exception as e:
                if printlog:  # pragma: no cover
                    print(e) # pragma: no cover
                return None # pragma: no cover

        tile = loadfig(filename)
        if tile is None:
            try:
                t = 0
                while t < 10:
                    try:
                        imgurl = smurl.format(zoom, xtile, ytile)
                        header = {}
                        header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                        header['Accept-Language'] = 'zh-CN,zh;q=0.8'
                        header['Upgrade-Insecure-Requests'] = '1'
                        header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'

                        import requests
                        response1 = requests.get(
                            imgurl, headers=header, timeout=6)
                        imgstr = response1.content
                        tile = Image.open(io.BytesIO(imgstr))
                        savefig(filename, tile)
                        Cluster.paste(tile, box=(
                            (xtile-xmin)*imgsize,  (ytile-ymin)*imgsize))
                        t = 10
                    except Exception:  # pragma: no cover
                        if printlog:  # pragma: no cover
                            print('Get map tile failed, retry ',
                                  t)  # pragma: no cover
                        t += 1  # pragma: no cover
            except Exception:  # pragma: no cover
                print("Couldn't download image")  # pragma: no cover
                tile = None  # pragma: no cover
        else:  # pragma: no cover
            Cluster.paste(tile, box=(
                (xtile-xmin)*imgsize,  (ytile-ymin)*imgsize))  # pragma: no cover

    imgsize = 256
    import threading
    threads = []
    Cluster = Image.new(
        'RGB', ((xmax-xmin+1)*imgsize-1, (ymax-ymin+1)*imgsize-1))
    for xtile in range(xmin, xmax+1):
        for ytile in range(ymin,  ymax+1):
            threads.append(threading.Thread(target=get_img, args=(
                smurl, zoom, xtile, ytile, imgsize, imgsavepath)))
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
    threads.clear()
    return Cluster


def plot_map(plt, bounds, zoom='auto', style=0, printlog=False):
    '''
    Plot the basemap

    Parameters
    -------
    plt : matplotlib.pyplot
        Where to plot
    bounds : List
        The drawing boundary of the base map, [lon1,lat1,lon2,lat2]
        (WGS84 coordinate system), where lon1 and lat1 are the coordinates
        of the lower left corner and lon2 and lat2 are the coordinates of
        the upper right corner
    zoom : number
        The larger the magnification level of the base map, the longer the
        loading time. Generally, the range for a single city is between 12
        and 16
    printlog : bool
        Show log
    style : number
        The style of map basemap can be 1-10, as follows
    '''
    access_token = read_mapboxtoken()
    if access_token == '':
        style = 0  # pragma: no cover
    imgsavepath = read_imgsavepath()
    if imgsavepath != '':
        try:
            import os
            os.listdir(imgsavepath)
        except Exception:  # pragma: no cover
            warnings.warn(  # pragma: no cover
                'imgsavepath do not exist, your tile map will not save')
    else:
        warnings.warn(
            'imgsavepath do not exist, your tile map will not save')  # pragma: no cover
    lon1 = bounds[0]
    lat1 = bounds[1]
    lon2 = bounds[2]
    lat2 = bounds[3]
    if zoom == 'auto':
        zoom = 11-np.log(lon2-lon1)/np.log(2)  # pragma: no cover
    zoom = min(18, int(zoom+0.5))
    a = getImageCluster(lon1, lat1, lon2-lon1,  lat2-lat1, zoom, style=style,
                        printlog=printlog, imgsavepath=imgsavepath,
                        access_token=access_token)
    x1, y1 = deg2num(lat1, lon1, zoom)
    x2, y2 = deg2num(lat2, lon2, zoom)
    x1, y1 = num2deg(x1, y1+1, zoom)
    x2, y2 = num2deg(x2+1, y2, zoom)
    plt.imshow(np.asarray(a), extent=(y1, y2, x1+0.00, x2+0.00))


def plotscale(ax, bounds, textcolor='k', textsize=8, compasssize=1,
              accuracy='auto', rect=[0.1, 0.1], unit="KM", style=1, **kwargs):
    '''
    Add compass and scale for a map

    Parameters
    -------
    bounds : List
        The drawing boundary of the base map, [lon1,lat1,lon2,lat2]
        (WGS84 coordinate system), where lon1 and lat1 are the coordinates
        of the lower left corner and lon2 and lat2 are the coordinates of
        the upper right corner
    textsize : number
        size of the text
    compasssize : number
        size of the compass
    accuracy : number
        Length of scale bar (m)
    unit : str
        ‘KM’,’km’,’M’,’m’, the scale units
    style : number
        1 or 2, the style of the scale
    rect : List
        The approximate position of the scale bar in the figure, such as
        [0.9,0.9], is in the upper right corner
    '''
    import math
    lon1 = bounds[0]
    lat1 = bounds[1]
    lon2 = bounds[2]
    lat2 = bounds[3]
    if accuracy == 'auto':
        accuracy = (int((lon2-lon1)/0.0003/1000+0.5)*1000)  # pragma: no cover
    a, c = rect
    b = 1-a
    d = 1-c
    alon, alat = (b*lon1+a*lon2)/(a+b), (d*lat1+c*lat2)/(c+d)
    deltaLon = accuracy * 360 / \
        (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360))
    # add scale
    from shapely.geometry import Polygon
    import geopandas as gpd
    if style == 1:
        scale = gpd.GeoDataFrame({
            'color': [(0, 0, 0), (1, 1, 1), (0, 0, 0), (1, 1, 1)],
            'geometry':
            [Polygon([
                (alon, alat),
                (alon+deltaLon, alat),
                (alon+deltaLon, alat+deltaLon*0.4),
                (alon, alat+deltaLon*0.4)]),
             Polygon([
                 (alon+deltaLon, alat),
                 (alon+2*deltaLon, alat),
                 (alon+2 * deltaLon, alat+deltaLon*0.4),
                 (alon+deltaLon, alat+deltaLon*0.4)]),
             Polygon([
                 (alon+2*deltaLon, alat),
                 (alon+4*deltaLon, alat),
                 (alon+4 * deltaLon, alat+deltaLon*0.4),
                 (alon+2*deltaLon, alat+deltaLon*0.4)]),
             Polygon([
                 (alon+4*deltaLon, alat),
                 (alon+8*deltaLon, alat),
                 (alon+8 * deltaLon, alat+deltaLon*0.4),
                 (alon+4*deltaLon, alat+deltaLon*0.4)])
             ]})
        scale.plot(ax=ax, edgecolor=textcolor,
                   facecolor=scale['color'], lw=0.6, **kwargs)
        if (unit == 'KM') | (unit == 'km'):
            ax.text(alon+1*deltaLon, alat+deltaLon*0.5,
                    str(int(1*accuracy/1000)), color=textcolor,
                    fontsize=textsize, ha='center', va='bottom')
            ax.text(alon+2*deltaLon, alat+deltaLon*0.5,
                    str(int(2*accuracy/1000)), color=textcolor,
                    fontsize=textsize, ha='center', va='bottom')
            ax.text(alon+4*deltaLon, alat+deltaLon*0.5,
                    str(int(4*accuracy/1000)), color=textcolor,
                    fontsize=textsize, ha='center', va='bottom')
            ax.text(alon+8*deltaLon, alat+deltaLon*0.5,
                    str(int(8*accuracy/1000)), color=textcolor,
                    fontsize=textsize, ha='center', va='bottom')
            ax.text(alon+8.5*deltaLon, alat+deltaLon*0.5, unit,
                    color=textcolor, fontsize=textsize, ha='left',
                    va='top')
        if (unit == 'M') | (unit == 'm'):
            ax.text(alon+1*deltaLon, alat+deltaLon*0.5, str(int(1*accuracy)),
                    color=textcolor, fontsize=textsize,
                    ha='center', va='bottom')
            ax.text(alon+2*deltaLon, alat+deltaLon*0.5, str(int(2*accuracy)),
                    color=textcolor, fontsize=textsize,
                    ha='center', va='bottom')
            ax.text(alon+4*deltaLon, alat+deltaLon*0.5, str(int(4*accuracy)),
                    color=textcolor, fontsize=textsize,
                    ha='center', va='bottom')
            ax.text(alon+8*deltaLon, alat+deltaLon*0.5, str(int(8*accuracy)),
                    color=textcolor, fontsize=textsize,
                    ha='center', va='bottom')
            ax.text(alon+8.5*deltaLon, alat+deltaLon*0.5, unit,
                    color=textcolor, fontsize=textsize,
                    ha='left', va='top')
    if style == 2:
        scale = gpd.GeoDataFrame({
            'color': [(0, 0, 0), (1, 1, 1)],
            'geometry':
            [Polygon([(alon+deltaLon, alat),
                      (alon+4*deltaLon, alat),
                      (alon+4*deltaLon, alat+deltaLon*0.4),
                      (alon+deltaLon, alat+deltaLon*0.4)]),
                Polygon([(alon+4*deltaLon, alat),
                         (alon+8*deltaLon, alat),
                         (alon+8 * deltaLon, alat+deltaLon*0.4),
                         (alon+4*deltaLon, alat+deltaLon*0.4)])
             ]})
        scale.plot(ax=ax, edgecolor=textcolor,
                   facecolor=scale['color'], lw=0.6, **kwargs)
        if (unit == 'KM') | (unit == 'km'):
            ax.text(alon+4*deltaLon, alat+deltaLon*0.5,
                    str(int(4*accuracy/1000)),
                    color=textcolor, fontsize=textsize,
                    ha='center', va='bottom')
            ax.text(alon+8*deltaLon, alat+deltaLon*0.5,
                    str(int(8*accuracy/1000)),
                    color=textcolor, fontsize=textsize,
                    ha='center', va='bottom')
            ax.text(alon+8.5*deltaLon, alat+deltaLon*0.5, unit,
                    color=textcolor, fontsize=textsize,
                    ha='left', va='top')
        if (unit == 'M') | (unit == 'm'):
            ax.text(alon+4*deltaLon, alat+deltaLon*0.5,
                    str(int(4*accuracy)),
                    color=textcolor, fontsize=textsize,
                    ha='center', va='bottom')
            ax.text(alon+8*deltaLon, alat+deltaLon*0.5,
                    str(int(8*accuracy)),
                    color=textcolor, fontsize=textsize,
                    ha='center', va='bottom')
            ax.text(alon+8.5*deltaLon, alat+deltaLon*0.5, unit,
                    color=textcolor, fontsize=textsize,
                    ha='left', va='top')
    # add compass
    deltaLon = compasssize*deltaLon
    alon = alon-deltaLon
    compass = gpd.GeoDataFrame({
        'color': [(0, 0, 0), (1, 1, 1)],
        'geometry': [
            Polygon([[alon, alat],
                     [alon, alat+deltaLon],
                     [alon+1/2*deltaLon, alat-1/2*deltaLon]]),
            Polygon([[alon, alat],
                     [alon, alat+deltaLon],
                     [alon-1/2*deltaLon, alat-1/2*deltaLon]])]})
    compass.plot(ax=ax, edgecolor=textcolor,
                 facecolor=compass['color'], lw=0.6, **kwargs)
    ax.text(alon, alat+deltaLon, 'N', color=textcolor,
            fontsize=textsize, ha='center', va='bottom')
