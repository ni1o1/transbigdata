from .traj import points_to_traj
import pandas as pd

def visualization_trip(trajdata,col = ['Lng','Lat','ID','Time'],zoom = 10,height=500):
    '''
    输入轨迹数据与列名，生成kepler的可视化
    
    输入
    -------
    trajdata : DataFrame
        轨迹点数据
    col : List
        列名，按[经度,纬度,轨迹编号,时间]的顺序
    zoom : number
        地图缩放等级
    height : number
        地图图框高度

    输出
    -------
    traj : keplergl.keplergl.KeplerGl
        keplergl提供的可视化
    '''
    try:
        from keplergl import KeplerGl
    except:
        raise Exception('请安装keplergl，在终端或命令提示符中运行pip install keplergl，然后重启Python') 
    print('整理轨迹数据...')
    [Lng,Lat,ID,timecol] = col
    trajdata[timecol] = pd.to_datetime(trajdata[timecol])
    trajdata = trajdata.sort_values(by = [ID,timecol])
    traj = points_to_traj(trajdata,col = [Lng,Lat,ID],timecol = timecol)
    #获取基本参数
    ls = []
    for i in range(len(traj['features'])):
        ls.append(traj['features'][i]['geometry']['coordinates'][0])
    ls = pd.DataFrame(ls)
    lon_center,lat_center,starttime = ls[0].mean(),ls[1].mean(),ls[3].min()
    print('生成可视化...')
    #创建一个KeplerGl对象
    vmap = KeplerGl(config = {
        "version": "v1",
        "config":
        {        "visState":
            {
                "filters": [],
                "layers": [
                {
                    "id": "hizm36i",
                    "type": "trip",
                    "config":
                    {
                        "dataId": "trajectory",
                        "label": "trajectory",
                        "color": [255,255,255],
                        "highlightColor": [255, 255, 0, 255],
                        "columns":
                        {
                            "geojson": "_geojson"
                        },
                        "isVisible": True,
                    },
                }],
                "layerBlending": "additive",
                "animationConfig":
                {
                    "currentTime": starttime,
                    "speed": 0.1
                }
            },
            "mapState":
            {
                "bearing": 0,
                "latitude": lat_center,
                "longitude": lon_center,
                "pitch": 0,
                "zoom": zoom,
            },
        }},
    data = {'trajectory':traj},height=height)
    #激活KeplerGl对象到jupyter的窗口中
    return vmap
