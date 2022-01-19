import pandas as pd

def bikedata_to_od(data,col = ['BIKE_ID','DATA_TIME','LONGITUDE','LATITUDE','LOCK_STATUS'],startend = None):
    '''
    Input bike-sharing order data (with data only generated when the lock is switched on and off), specify the column name, and extract the ride and parking information from it

    Parameters
    -------
    data : DataFrame
        Bike-sharing order data
    col : List
        Column names, the order cannot be changed.[‘BIKE_ID’,’DATA_TIME’,’LONGITUDE’,’LATITUDE’,’LOCK_STATUS’]
    startend : List
        The start time and end time of the observation period, for example [‘2018-08-27 00:00:00’,’2018-08-28 00:00:00’]. If it is passed in, the riding and parking situations (from the beginning of the observation period to the first appearance of the bicycle) and (from the last appearance of the bicycle to the end of the observation period) are considered.
        
    Returns
    -------
    move_data : DataFrame
        Riding data
    stop_data : DataFrame
        Parking data
    '''
    [BIKE_ID,DATA_TIME,LONGITUDE,LATITUDE,LOCK_STATUS] = col
    oddata = data.copy()
    oddata = oddata.sort_values(by = [BIKE_ID,DATA_TIME])
    if startend:
        oddata['tmp_index'] = range(len(oddata))
        #Add records at the beginning of the time period
        data_1 = oddata.copy()  
        #After grouping the single vehicle ID, sort it in ascending order according to time to get the rank id
        data_1['rank'] = data_1.groupby(BIKE_ID)['tmp_index'].rank(method = 'first')  
        data_1 = data_1[data_1['rank']==1]  
        #Modify time to the start time of the observation period
        data_1[DATA_TIME] = startend[0]
        data_1[LOCK_STATUS] = 1
        #Add records at the end of the time period
        data_2 = oddata.copy()  
        data_2['rank'] = data_2.groupby(BIKE_ID)['tmp_index'].rank(ascending = False,method = 'first')  
        data_2 = data_2[data_2['rank']==1]  
        data_2[DATA_TIME] = startend[1]
        data_2[LOCK_STATUS] = 0
        oddata = pd.concat([oddata,data_1,data_2]).sort_values(by = [BIKE_ID,DATA_TIME])
    for i in col:
        oddata[i+'_'] = oddata[i].shift(-1)
    oddata = oddata[oddata[BIKE_ID] == oddata[BIKE_ID+'_']]
    move_data = oddata[(oddata[LOCK_STATUS]==0)&(oddata[LOCK_STATUS+'_']==1)][[BIKE_ID,DATA_TIME,LONGITUDE,LATITUDE,DATA_TIME+'_',LONGITUDE+'_',LATITUDE+'_']]
    move_data.columns = [BIKE_ID,'stime','slon','slat','etime','elon','elat']
    stop_data = oddata[(oddata[LOCK_STATUS]==1)&(oddata[LOCK_STATUS+'_']==0)][[BIKE_ID,DATA_TIME,LONGITUDE,LATITUDE,DATA_TIME+'_',LONGITUDE+'_',LATITUDE+'_']]
    stop_data.columns = [BIKE_ID,'stime','slon','slat','etime','elon','elat']
    return move_data,stop_data