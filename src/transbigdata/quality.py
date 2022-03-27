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


def sample_duration(data, col=['Vehicleid', 'Time']):
    '''
    Calculate the data sampling interval.

    Parameters
    -------
    data : DataFrame
        Data
    col : List
        The column name, in the order of [‘Vehicleid’, ‘Time’]

    Returns
    -------
    sample_duration : DataFrame
        A Series with the column name duration, the content is the sampling
        interval of the data, in seconds
    '''
    [Vehicleid, Time] = col
    data1 = data.copy()
    data1[Time] = pd.to_datetime(data1[Time])
    data1 = data1.sort_values(by=[Vehicleid, Time])
    data1[Vehicleid+'1'] = data1[Vehicleid].shift(-1)
    data1[Time+'1'] = data1[Time].shift(-1)
    data1['duration'] = (data1[Time+'1']-data1[Time]).dt.total_seconds()
    data1 = data1[data1[Vehicleid+'1'] == data1[Vehicleid]]
    sample_duration = data1[['duration']]
    return sample_duration


def data_summary(data, col=['Vehicleid', 'Time'], show_sample_duration=False,
                 roundnum=4):
    '''
    Output the general information of the dataset.

    Parameters
    -------
    data : DataFrame
        The trajectory points data
    col : List
        The column name, in the order of [‘Vehicleid’, ‘Time’]
    show_sample_duration : bool
        Whether to output individual sampling interval
    roundnum : number
        Number of decimal places
    '''
    [Vehicleid, Time] = col
    print('Amount of data')
    print('-----------------')
    print('Total number of data items: ', len(data))
    Vehicleid_count = data[Vehicleid].value_counts()
    print('Total number of individuals: ', len(Vehicleid_count))
    print('Data volume of individuals(Mean): ',
          round(Vehicleid_count.mean(), roundnum))
    print('Data volume of individuals(Upper quartile): ',
          round(Vehicleid_count.quantile(0.75), roundnum))
    print('Data volume of individuals(Median): ', round(
        Vehicleid_count.quantile(0.5), roundnum))
    print('Data volume of individuals(Lower quartile): ',
          round(Vehicleid_count.quantile(0.25), roundnum))
    print('')
    print('Data time period')
    print('-----------------')
    print('Start time: ', data[Time].min())
    print('End time: ', data[Time].max())
    print('')
    if show_sample_duration:
        sd = sample_duration(data, col=[Vehicleid, Time])
        print('Sampling interval')
        print('-----------------')
        print('Mean: ', round(sd['duration'].mean(), roundnum), 's')
        print('Upper quartile: ', round(
            sd['duration'].quantile(0.75), roundnum), 's')
        print('Median: ', round(sd['duration'].quantile(0.5), roundnum), 's')
        print('Lower quartile: ', round(
            sd['duration'].quantile(0.25), roundnum), 's')
