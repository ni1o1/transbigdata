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

import pandas as pd


def clean_taxi_status(data, col=['VehicleNum', 'Time', 'OpenStatus'],
                      timelimit=None):
    '''
    Deletes records of instantaneous changes in passenger carrying status from
    taxi data. These abnormal records can affect travel order judgments.
    Judgement method: If the passenger status of the previous record and the
    next record are different from this record for the same vehicle, then this
    record should be deleted.

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        Column names, in the order of [‘VehicleNum’, ‘Time’, ‘OpenStatus’]
    timelimit : number
        Optional, in seconds. If the time between the previous record and the
        next record is less than the time threshold, then it will be deleted

    Returns
    -------
    data1 : DataFrame
        Cleaned data
    '''
    data1 = data.copy()
    [VehicleNum, Time, OpenStatus] = col
    if timelimit:
        data1[Time] = pd.to_datetime(data1[Time])
        data1 = data1[
            -((data1[OpenStatus].shift(-1) == data1[OpenStatus].shift()) &
              (data1[OpenStatus] != data1[OpenStatus].shift()) &
              (data1[VehicleNum].shift(-1) == data1[VehicleNum].shift()) &
              (data1[VehicleNum] == data1[VehicleNum].shift()) &
              ((data1[Time].shift(-1) - data1[Time].shift()
                ).dt.total_seconds() <= timelimit)
              )]
    else:
        data1 = data1[
            -((data1[OpenStatus].shift(-1) == data1[OpenStatus].shift()) &
              (data1[OpenStatus] != data1[OpenStatus].shift()) &
              (data1[VehicleNum].shift(-1) == data1[VehicleNum].shift()) &
              (data1[VehicleNum] == data1[VehicleNum].shift()))]
    return data1


def taxigps_to_od(data,
                  col=['VehicleNum', 'Stime', 'Lng', 'Lat', 'OpenStatus']):
    '''
    Input Taxi GPS data, extract OD information

    Parameters
    -------
    data : DataFrame
        Taxi GPS data
    col : List
        Column names in the data, need to be in order [vehicle id, time,
        longitude, latitude, passenger status]

    Returns
    -------
    oddata : DataFrame
        OD information
    '''
    [VehicleNum, Stime, Lng, Lat, OpenStatus] = col
    data1 = data[col]
    data1 = data1.sort_values(by=[VehicleNum, Stime])
    data1['StatusChange'] = data1[OpenStatus] - data1[OpenStatus].shift()
    oddata = data1[((data1['StatusChange'] == -1) |
                   (data1['StatusChange'] == 1)) &
                   (data1[VehicleNum].shift() == data1[VehicleNum])]
    oddata = oddata.drop([OpenStatus], axis=1)
    oddata.columns = [VehicleNum, 'stime', 'slon', 'slat', 'StatusChange']
    oddata['etime'] = oddata['stime'].shift(-1)
    oddata['elon'] = oddata['slon'].shift(-1)
    oddata['elat'] = oddata['slat'].shift(-1)
    oddata = oddata[(oddata['StatusChange'] == 1) &
                    (oddata[VehicleNum] == oddata[VehicleNum].shift(-1))]
    oddata = oddata.drop('StatusChange', axis=1)
    oddata['ID'] = range(len(oddata))
    return oddata


def taxigps_traj_point(data, oddata,
                       col=['Vehicleid', 'Time', 'Lng', 'Lat', 'OpenStatus']):
    '''
    Input Taxi data and OD data to extract the trajectory points for delivery
    and idle trips

    Parameters
    -------
    data : DataFrame
        Taxi GPS data, field name specified by col variable
    oddata : DataFrame
        Taxi OD data
    col : List
        Column names, need to be in order [vehicle id, time, longitude,
        latitude, passenger status]

    Returns
    -------
    data_deliver : DataFrame
        Trajectory points for delivery trips
    data_idle : DataFrame
        Trajectory points for idle trips
    '''
    VehicleNum, Time, Lng, Lat, OpenStatus = col
    oddata1 = oddata.copy()
    odata = oddata1[[VehicleNum, 'stime', 'slon', 'slat', 'ID']].copy()
    odata.columns = [VehicleNum, Time, Lng, Lat, 'ID']
    odata.loc[:, 'flag'] = 1
    odata.loc[:, OpenStatus] = -1
    ddata = oddata1[[VehicleNum, 'etime', 'elon', 'elat', 'ID']].copy()
    ddata.columns = [VehicleNum, Time, Lng, Lat, 'ID']
    ddata.loc[:, 'flag'] = -1
    ddata.loc[:, OpenStatus] = -1
    data1 = pd.concat([data, odata, ddata])
    data1 = data1.sort_values(by=[VehicleNum, Time, OpenStatus])
    data1['flag'] = data1['flag'].fillna(0)
    data1['flag'] = data1.groupby(VehicleNum)['flag'].cumsum()
    data1['ID'] = data1['ID'].ffill()
    data_deliver = data1[(data1['flag'] == 1) &
                         (-data1['ID'].isnull()) & (data1[OpenStatus] != -1)]
    data_idle = data1[(data1['flag'] == 0) &
                      (-data1['ID'].isnull()) & (data1[OpenStatus] != -1)]
    return data_deliver, data_idle
