import geopandas as gpd  
import pandas as pd
from .grids import GPS_to_grids,grids_centre
def odagg_grid(oddata,params,col = ['slon','slat','elon','elat'],arrow = False,**kwargs):
    '''
    Aggregate the OD matrix and generate the grid geometry. The input is the OD matrix (each row represents a trip). The OD will assigned to grids and then aggregated in the form of GeoDataFrame.

    Parameters
    -------
    oddata : DataFrame
        OD data
    col : List
        The column of the origin/destination location,[‘slon’,’slat’,’elon’,’elat’]. The default weight is 1 for each column. You can also add the weight parameter, for example, [‘slon’,’slat’,’elon’,’elat’,’count’].
    params : List
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat), lonStart and latStart are the lower-left coordinates, deltaLon, deltaLat are the length and width of a single grid
    arrow : bool
        Whether the generated OD geographic line contains arrows

    Returns
    -------
    oddata1 : GeoDataFrame
        GeoDataFrame of OD after aggregation
    '''
    if len(col)==4:
        [slon,slat,elon,elat]=col
        count = 'count'
    if len(col)==5:
        [slon,slat,elon,elat,count]=col
    oddata['SLONCOL'],oddata['SLATCOL'] = GPS_to_grids(oddata[slon],oddata[slat],params)
    oddata['ELONCOL'],oddata['ELATCOL'] = GPS_to_grids(oddata[elon],oddata[elat],params)
    if len(col)==4:
        oddata[count] = 1
    oddata_agg = oddata.groupby(['SLONCOL','SLATCOL','ELONCOL','ELATCOL'])[count].sum().reset_index()
    oddata_agg['SHBLON'],oddata_agg['SHBLAT'] = grids_centre(oddata_agg['SLONCOL'],oddata_agg['SLATCOL'],params)
    oddata_agg['EHBLON'],oddata_agg['EHBLAT'] = grids_centre(oddata_agg['ELONCOL'],oddata_agg['ELATCOL'],params)
    from shapely.geometry import LineString    
    if arrow:
        oddata_agg['geometry'] = oddata_agg.apply(lambda r:tolinewitharrow(r['SHBLON'],r['SHBLAT'],r['EHBLON'],r['EHBLAT'],**kwargs),axis = 1)    
    else:
        oddata_agg['geometry'] = oddata_agg.apply(lambda r:LineString([[r['SHBLON'],r['SHBLAT']],[r['EHBLON'],r['EHBLAT']]]),axis = 1)    
    oddata_agg = gpd.GeoDataFrame(oddata_agg)    
    oddata_agg = oddata_agg.sort_values(by = count)
    return oddata_agg

def odagg_shape(oddata,shape,col = ['slon','slat','elon','elat'],params = None,round_accuracy = 6,arrow = False,**kwargs):
    '''
    Generate the OD aggregation results and the corresponding geometry. The input is the OD data (each row represents a trip). The OD will assigned to grids and then aggregated in the form of GeoDataFrame.

    Parameters
    -------
    oddata : DataFrame
        OD data
    shape : GeoDataFrame
        GeoDataFrame of the target traffic zone
    col : List
        The column of the origin/destination location,[‘slon’,’slat’,’elon’,’elat’]. The default weight is 1 for each column. You can also add the weight parameter, for example, [‘slon’,’slat’,’elon’,’elat’,’count’].
    params : List (optional)
        Gridding parameters (lonStart,latStart,deltaLon,deltaLat), lonStart and latStart are the lower-left coordinates, deltaLon, deltaLat are the length and width of a single grid
        If availabel, After the data gridding, the traffic zone will be matched based on the grid center. If not available, then the matching will be processed based on longitude and latitude. When the number of data items is large, the matching efficiency will be improved greatly thanks to data gridding.
    round_accuracy : number
        The number of decimal for latitude and longitude when implementing aggregation
    arrow : bool
        Whether the generated OD geographic line contains arrows

    Returns
    -------
    oddata1 : GeoDataFrame
        GeoDataFrame of OD after aggregation
    '''
    if len(col)==4:
        [slon,slat,elon,elat]=col
        count = 'count'
    if len(col)==5:
        [slon,slat,elon,elat,count]=col
    shape_1 = shape.copy()
    shape['x'] = shape.centroid.x
    shape['y'] = shape.centroid.y
    shape = shape[['x','y','geometry']]
    if params:
        oddata['SLONCOL'],oddata['SLATCOL'] = GPS_to_grids(oddata[slon],oddata[slat],params)
        oddata['ELONCOL'],oddata['ELATCOL'] = GPS_to_grids(oddata[elon],oddata[elat],params)
        if len(col)==4:
            oddata[count] = 1
        oddata_agg = oddata.groupby(['SLONCOL','SLATCOL','ELONCOL','ELATCOL'])[count].sum().reset_index()
        oddata_agg['SHBLON'],oddata_agg['SHBLAT'] = grids_centre(oddata_agg['SLONCOL'],oddata_agg['SLATCOL'],params)
        oddata_agg['EHBLON'],oddata_agg['EHBLAT'] = grids_centre(oddata_agg['ELONCOL'],oddata_agg['ELATCOL'],params)
        a = oddata_agg[['SHBLON','SHBLAT']]
        b = oddata_agg[['EHBLON','EHBLAT']]
        a.columns = ['lon','lat']
        b.columns = ['lon','lat']
        c = pd.concat([a,b]).drop_duplicates()
        d = c[['lon','lat']].drop_duplicates()
        d['geometry'] = gpd.points_from_xy(d['lon'],d['lat'])
        d = gpd.GeoDataFrame(d)
        d = gpd.sjoin(d,shape)
        c = pd.merge(c,d)
        c = c[['lon','lat','index_right','x','y']]
        c.columns = ['SHBLON','SHBLAT','sindex','sx','sy']
        oddata_agg = pd.merge(oddata_agg,c)
        c.columns = ['EHBLON','EHBLAT','eindex','ex','ey']
        oddata_agg = pd.merge(oddata_agg,c)
        oddata_agg = oddata_agg.groupby(['sindex','sx','sy','eindex','ex','ey'])[count].sum().reset_index()
    else:
        a = oddata[[slon,slat]]
        b = oddata[[elon,elat]]
        a.columns = ['lon','lat']
        b.columns = ['lon','lat']
        c = pd.concat([a,b]).drop_duplicates()
        c['lon_simple'] = c['lon'].round(round_accuracy)
        c['lat_simple'] = c['lat'].round(round_accuracy)
        d = c[['lon_simple','lat_simple']].drop_duplicates()
        d['geometry'] = gpd.points_from_xy(d['lon_simple'],d['lat_simple'])
        d = gpd.GeoDataFrame(d)
        d = gpd.sjoin(d,shape)
        c = pd.merge(c,d)
        c = c[['lon','lat','index_right','x','y']]
        c.columns = ['slon','slat','sindex','sx','sy']
        oddata = pd.merge(oddata,c)
        c.columns = ['elon','elat','eindex','ex','ey']
        oddata = pd.merge(oddata,c)
        if len(col)==4:
            oddata[count] = 1
        oddata_agg = oddata.groupby(['sindex','sx','sy','eindex','ex','ey'])[count].sum().reset_index()
    from shapely.geometry import LineString    
    if arrow:
        oddata_agg['geometry'] = oddata_agg.apply(lambda r:tolinewitharrow(r['sx'],r['sy'],r['ex'],r['ey'],**kwargs),axis = 1)    
    else:
        oddata_agg['geometry'] = oddata_agg.apply(lambda r:LineString([[r['sx'],r['sy']],[r['ex'],r['ey']]]),axis = 1)    
    oddata_agg = gpd.GeoDataFrame(oddata_agg)    
    oddata_agg = oddata_agg[['sindex','eindex',count,'geometry']]
    oddata_agg = pd.merge(oddata_agg,shape_1.reset_index().rename(columns = {'index':'sindex'}).drop('geometry',axis = 1),on = 'sindex')
    oddata_agg = pd.merge(oddata_agg,shape_1.reset_index().rename(columns = {'index':'eindex'}).drop('geometry',axis = 1),on = 'eindex')
    oddata_agg = oddata_agg.sort_values(by = count)
    return oddata_agg

def tolinewitharrow(x1,y1,x2,y2,theta = 20,length = 0.1,pos = 0.8):
    '''
    Input start and end coords，Returns LineString with arrow

    Parameters
    -------
    x1,y1,x2,y2 : float
        xy coords of start and end coords
    theta : float
        Angle of arrow
    length : float
        The length ratio of the arrow to the original line. For example, if the length of the original line is 1 and the length is set to 0.3, the arrow size is 0.3
    pos : float
        Position of arrow, 0 at the start point, 1 at the end point

    Returns
    -------
    Line : MultiLineString
        OD LineString with arrow
    '''
    import numpy as np
    from shapely.geometry import MultiLineString
    l_main = [[x1,y1],[x2,y2]]
    p1,p2 = (1-pos)*x1+pos*x2,(1-pos)*y1+pos*y2
    R = np.array([[np.cos(np.radians(theta)),-np.sin(np.radians(theta))],
                  [np.sin(np.radians(theta)),np.cos(np.radians(theta))]])
    l1 = np.dot(R,np.array([[x1-x2,y1-y2]]).T).T[0]*length+np.array([p1,p2]).T
    l1 = [list(l1),[p1,p2]]
    R = np.array([[np.cos(np.radians(-theta)),-np.sin(np.radians(-theta))],
                  [np.sin(np.radians(-theta)),np.cos(np.radians(-theta))]])
    l2 = np.dot(R,np.array([[x1-x2,y1-y2]]).T).T[0]*length+np.array([p1,p2]).T
    l2 = [list(l2),[p1,p2]]
    return MultiLineString([l_main,l1,l2])
