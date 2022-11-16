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
import numpy as np
from .grids import GPS_to_grid
import warnings


def mobile_stay_move(data, params,
                     col=['ID', 'dataTime', 'longitude', 'latitude'],
                     activitytime=1800):
    '''
    Input trajectory data and gridding parameters, identify stay and move

    Parameters
    ----------------
    data : DataFrame
        trajectory data
    params : List
        gridding parameters
    col : List
        The column name, in the order of ['ID','dataTime','longitude',
        'latitude']
    activitytime : Number
        How much time to regard as activity

    Returns
    ----------------
    stay : DataFrame
        stay information
    move : DataFrame
        move information
    '''
    uid, timecol, lon, lat = col
    # Identify stay
    data = data.sort_values(by=col[:2])
    stay = data.copy()
    stay = stay.rename(columns={lon: 'lon', lat: 'lat', timecol: 'stime'})
    stay['stime'] = pd.to_datetime(stay['stime'])
    stay['LONCOL'], stay['LATCOL'] = GPS_to_grid(
        stay['lon'], stay['lat'], params)
    # Number the status
    stay['status_id'] = ((stay['LONCOL'] != stay['LONCOL'].shift()) |
                         (stay['LATCOL'] != stay['LATCOL'].shift()) |
                         (stay[uid] != stay[uid].shift())).astype(int)
    stay['status_id'] = stay.groupby([uid])['status_id'].cumsum()
    stay = stay.drop_duplicates(
        subset=[uid, 'status_id'], keep='first').copy()
    stay['etime'] = stay['stime'].shift(-1)
    stay = stay[stay[uid] == stay[uid].shift(-1)].copy()
    # Remove the duration shorter than given activitytime
    stay['duration'] = (pd.to_datetime(stay['etime']) -
                        pd.to_datetime(stay['stime'])).dt.total_seconds()
    stay = stay[stay['duration'] >= activitytime].copy()
    stay = stay[[uid, 'stime', 'LONCOL', 'LATCOL',
                 'etime', 'lon', 'lat', 'duration']]

    # Identify move
    move = stay.copy()
    move['stime_next'] = move['stime'].shift(-1)
    move['elon'] = move['lon'].shift(-1)
    move['elat'] = move['lat'].shift(-1)
    move['ELONCOL'] = move['LONCOL'].shift(-1)
    move['ELATCOL'] = move['LATCOL'].shift(-1)
    move[uid+'_next'] = move[uid].shift(-1)
    move = move[move[uid+'_next'] == move[uid]
                ].drop(['stime', 'duration', uid+'_next'], axis=1)
    move = move.rename(columns={'lon': 'slon',
                                'lat': 'slat',
                                'etime': 'stime',
                                'stime_next': 'etime',
                                'LONCOL': 'SLONCOL',
                                'LATCOL': 'SLATCOL',
                                })
    move['duration'] = (
        move['etime'] - move['stime']).dt.total_seconds()
    return stay, move


def mobile_stay_duration(staydata, col=['stime', 'etime'], start_hour=8, end_hour=20):
    '''
    Input the stay point data to identify the duration during night and day time.

    Parameters
    ----------------
    staydata : DataFrame
        Stay data
    col : List
        The column name, in the order of ['starttime','endtime']
    start_hour : Number
        Start hour of day time
    end_hour : Number
        End hour of day time

    Returns
    ----------------
    duration_night : Series
        Duration at night time
    duration_day : Series
        Duration at day time
    '''

    if (start_hour > end_hour) | (start_hour < 0) | (start_hour > 24) | (end_hour < 0) | (end_hour > 24):
        raise ValueError(  # pragma: no cover
            'end_hour or start_hour error, it should be: 0 <= start_hour <= end_hour <= 24')

    night_hour = start_hour+24-end_hour
    day_hour = end_hour-start_hour
    stay = staydata.copy()
    stime, etime = col
    stay[stime] = pd.to_datetime(stay[stime])
    stay[etime] = pd.to_datetime(stay[etime])

    stay['preday'] = pd.to_datetime(
        stay[stime].dt.date)-pd.Timedelta(1, unit='days')+pd.Timedelta(end_hour, unit='hours')

    tmp = (stay[stime]-stay['preday']).dt.total_seconds()
    days = tmp//(24*3600)
    remain = tmp % (24*3600)
    duration_night_stime = days*night_hour*3600 + \
        np.min([remain, np.ones(len(tmp))*night_hour*3600], axis=0)
    duration_day_stime = days*day_hour*3600 + \
        np.max([remain-(night_hour*3600), np.zeros(len(tmp))], axis=0)

    tmp = (stay[etime]-stay['preday']).dt.total_seconds()
    days = tmp//(24*3600)
    remain = tmp % (24*3600)
    duration_night_etime = days*night_hour*3600 + \
        np.min([remain, np.ones(len(tmp))*night_hour*3600], axis=0)
    duration_day_etime = days*day_hour*3600 + \
        np.max([remain-(night_hour*3600), np.zeros(len(tmp))], axis=0)

    duration_night = duration_night_etime-duration_night_stime
    duration_day = duration_day_etime-duration_day_stime

    return duration_night, duration_day


def mobile_stay_dutation(*args, **kwargs):
    '''
    This method is renamed as transbigdata.mobile_stay_duration
    '''
    warnings.warn(
        "This method is renamed as transbigdata.mobile_stay_duration")     # pragma: no cover
    return mobile_stay_duration(*args, **kwargs)     # pragma: no cover


def mobile_identify_home(staydata, col=['uid', 'stime', 'etime', 'LONCOL', 'LATCOL'], start_hour=8, end_hour=20):
    '''
    Identify home location from mobile phone stay data. The rule is to identify the locations with longest 
    duration in night time. 

    Parameters
    ----------------
    staydata : DataFrame
        Stay data
    col : List
        The column name, in the order of ['uid','stime', 'etime', 'locationtag1', 'locationtag2', ...].
        There can be multiple 'locationtag' columns to specify the location.
    start_hour, end_hour : Number
        Start hour and end hour of day time

    Returns
    ----------------
    home : DataFrame
        Home location of mobile phone users
    '''
    uid = col[0]
    stime = col[1]
    etime = col[2]
    stay = staydata.copy()
    if ('duration_night' not in stay.columns) | ('duration_day' not in stay.columns):
        stay['duration_night'], stay['duration_day'] = mobile_stay_duration(
            stay, col=[stime, etime], start_hour=start_hour, end_hour=end_hour)
    # 夜晚最常停留地
    home = stay.groupby(
        [col[0], *col[3:]])['duration_night'].sum().reset_index()
    home = home.sort_values(by=[uid, 'duration_night'], ascending=False).drop_duplicates(
        subset=[uid], keep='first')
    home = home.drop(['duration_night'], axis=1)
    return home


def mobile_identify_work(staydata, col=['uid', 'stime', 'etime', 'LONCOL', 'LATCOL'], minhour=3, start_hour=8, end_hour=20, workdaystart=0, workdayend=4):
    '''
    Identify work location from mobile phone stay data. The rule is to identify the locations with longest 
    duration in day time on weekdays(Average duration should over `minhour`). 

    Parameters
    ----------------
    staydata : DataFrame
        Stay data
    col : List
        The column name, in the order of ['uid','stime','etime', 'locationtag1', 'locationtag2', ...].
        There can be multiple 'locationtag' columns to specify the location.
    minhour : Number
        Minimun duration in work days (hours).
    workdaystart,workdayend : Number
        Start and end of work days in the week. 0 - Monday, 4 - Friday
    start_hour, end_hour : Number
        Start hour and end hour of day time


    Returns
    ----------------
    work : DataFrame
        work location of mobile phone users
    '''
    uid = col[0]
    stime = col[1]
    etime = col[2]
    stay = staydata.copy()

    stay[stime] = pd.to_datetime(stay[stime])
    stay[etime] = pd.to_datetime(stay[etime])

    # 在工作日出现的日期数
    stay_workdays = stay[(stay[stime].dt.weekday >= workdaystart) &
                         (stay[stime].dt.weekday <= workdayend)].copy()

    # 将跨日的活动缩短为当日，以便计算日均持续时间
    stay_workdays['nextday'] = pd.to_datetime(
        stay_workdays[stime].dt.date+pd.Timedelta(1, unit='days'))
    stay_workdays[etime] = stay_workdays[[etime, 'nextday']].min(axis=1)
    stay_workdays['duration_night'], stay_workdays['duration_day'] = mobile_stay_duration(
        stay_workdays, col=[stime, etime], start_hour=start_hour, end_hour=end_hour)

    # 白天最常活动地
    work = stay_workdays.groupby(
        [col[0], *col[3:]])['duration_day'].sum().reset_index()
    work = work.sort_values(by=[uid, 'duration_day'], ascending=False).drop_duplicates(
        subset=[uid], keep='first')

    # 人出现在多少个工作日
    stay_workdays['date'] = stay_workdays[stime].dt.date
    uid_workdays = stay_workdays[[uid, 'date']].drop_duplicates().groupby([uid])[
        'date'].count().reset_index()

    # 要求工作日每天平均minhour小时以上
    work = pd.merge(work, uid_workdays)
    work = work[(work['duration_day']/work['date']) >= minhour*3600].copy()
    work = work.drop(['duration_day', 'date'], axis=1)

    return work

'''Old namespace'''

traj_stay_move = mobile_stay_move
