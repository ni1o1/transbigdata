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


def cal_entropy(sequence):
    '''
    Calculate entropy.

    Parameters
    ----------------
    sequence : List,DataFrame,Series
        sequence data

    Returns
    ----------------
    entropy : Number
    '''
    if not isinstance(sequence,list)|\
        isinstance(sequence,pd.DataFrame)|\
        isinstance(sequence,pd.Series):
        raise TypeError('Sequence must be List,DataFrame,Series') # pragma: no cover
    sequence = pd.DataFrame(sequence)
    r_1 = sequence[0].value_counts().reset_index()
    r_1[0] /= r_1[0].sum()
    entropy = -(r_1[0]*np.log(r_1[0])/np.log(2)).sum()
    return entropy

def cal_entropy_rate(sequence):
    '''
    Calculate entropy rate.
    Reference: Goulet-Langlois, G., Koutsopoulos, H. N., Zhao, Z., & Zhao, J. (2017). Measuring regularity of individual travel patterns. IEEE Transactions on Intelligent Transportation Systems, 19(5), 1583-1592.
    
    Parameters
    ----------------
    sequence : List,DataFrame,Series
        sequence data

    Returns
    ----------------
    entropy_rate : Number
    '''
    if not isinstance(sequence,list)|\
        isinstance(sequence,pd.DataFrame)|\
        isinstance(sequence,pd.Series):
        raise TypeError('Sequence must be List,DataFrame,Series') # pragma: no cover
    sequence = pd.DataFrame(sequence,columns = ['key'])
    #对item编号排序
    sequence = sequence.reindex().reset_index()
    sequence_item = sequence['key'].drop_duplicates().reset_index().rename(columns = {'index':'Id'})
    sequence = pd.merge(sequence,sequence_item).sort_values('index')
    #序列
    sequence = list(sequence['Id'].astype(str))
    #BWT
    sequences = []
    for i in range(len(sequence)):
        sequence_new_1 = sequence[0:i]
        sequence_new_2 = sequence[i:]
        sequence_new = ','.join(sequence_new_2+sequence_new_1)
        sequences.append(sequence_new)
    sequences = sorted(sequences)
    sorted_rotations = [i.split(',')[-1] for i in sequences]

    #对序列分割为多个n**0.5长度的段
    sorted_rotations = pd.DataFrame(sorted_rotations)
    n = len(sorted_rotations)
    sorted_rotations['group'] = range(n)
    sorted_rotations['group'] /= n**0.5
    sorted_rotations['group'] = sorted_rotations['group'].astype(int)
    entropy_rate = sorted_rotations.groupby(['group']).apply(lambda r:cal_entropy(r[0])).mean()
    return entropy_rate
    