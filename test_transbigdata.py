def test_transbigdata():
	import transbigdata as tbd
	print('well done!')
	return 666


import pandas as pd


def de_sample_traj(df, sample_interval, col=['vehID','time']):
    '''
    轨迹数据采样间隔过高的时候，数据量太大，不便于分析。
    这个函数可以将采样间隔扩大，缩减数据量（保留首末行）。
    暂时需要原始数据为等间隔采样。
    '''
    veh_list = list(df[col[0]].drop_duplicates())
    compressed_list = []
    for each_veh in veh_list:
        df_each_veh = df[df[col[0]]==each_veh]
        
        # start_time, end_time
        start_time, end_time = df_car_1.iloc[0][col[1]], df_car_1.iloc[-1][col[1]]
        
        # compress
        df_each_veh_compress = df_each_veh[((df_each_veh[col[1]] - start_time) % sample_interval == 0) | 
                                           (df_each_veh[col[1]] == end_time)]
        
        compressed_list.append(df_each_veh_compress)

    # put all vehicles together
    df_compressed = pd.concat(compressed_list)
    print('origin data length:', len(df))
    print('compressed data length:', len(df_compressed))
    
    return df_compressed