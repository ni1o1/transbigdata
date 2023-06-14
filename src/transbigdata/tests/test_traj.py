import transbigdata as tbd
import pandas as pd
import pytest
import os
import numpy as np
class TestMobile:

    def test_mobile(self):
        data = pd.DataFrame([['00466ab30de56db7efbd04991b680ae1', 201806010000, 121.43, 30.175,
                20180601],
            ['00466ab30de56db7efbd04991b680ae1', 201806010620, 121.43, 30.175,
                20180601],
            ['00466ab30de56db7efbd04991b680ae1', 201806010721, 121.417, 30.24,
                20180601],
            ['00466ab30de56db7efbd04991b680ae1', 201806011022,
            121.417, 30.24, 20180601],
            ['00466ab30de56db7efbd04991b680ae1', 201806012026,
                121.43, 30.175, 20180601],
            ['00466ab30de56db7efbd04991b680ae1', 201806012328,
            121.43, 30.175,20180601],
            ['00466ab30de56db7efbd04991b680ae1', 201806012329,
            121.42, 30.175,20180601],
            ['00466ab30de56db7efbd04991b680ae1', 201806020000, 121.43, 30.175,
                20180602],
            ['00466ab30de56db7efbd04991b680ae1', 201806020620, 121.43, 30.175,
                20180602],
            ['00466ab30de56db7efbd04991b680ae1', 201806020721, 121.417, 30.24,
                20180602],
            ['00466ab30de56db7efbd04991b680ae1', 201806021022,
            121.417, 30.24, 20180602],
            ['00466ab30de56db7efbd04991b680ae1', 201806022026,
                121.43, 30.175, 20180602],
            ['00466ab30de56db7efbd04991b680ae1', 201806022328,
            121.43, 30.175,20180602],
            ['00466ab30de56db7efbd04991b680ae1', 201806022329,
            121.42, 30.175,20180602]],columns=['user_id','stime','longitude','latitude','date'])
        data['stime'] = pd.to_datetime(data['stime'], format='%Y%m%d%H%M')
        result = tbd.traj_length(data,col = ['longitude','latitude','user_id'])
        assert np.allclose(result['length'].iloc[0],32223.16691673902)
        result = tbd.traj_length(data,col = ['longitude','latitude','user_id'],method='Project')
        assert np.allclose(result['length'].iloc[0],32143.68176512773)
        #Obtain gridding parameters
        params = tbd.area_to_params([121.860, 29.295, 121.862, 29.301], accuracy=500)
        #Identify stay and move infomation from mobile phone trajectory data
        stay,move = tbd.traj_stay_move(data,params,col = ['user_id','stime','longitude', 'latitude'])

        assert len(stay) == 7
        assert len(move) == 8

        #Slice trajectory data
        slicedata = tbd.traj_slice(data, move, traj_col=['user_id', 'stime'],slice_col=['user_id', 'stime', 'etime', 'moveid'])
        assert len(slicedata) == 8

        #Identify home location
        home = tbd.mobile_identify_home(stay, col=['user_id','stime', 'etime','LONCOL', 'LATCOL','lon','lat'], start_hour=8, end_hour=20 )
        assert home['LONCOL'].iloc[0] == -83
        #Identify work location
        work = tbd.mobile_identify_work(stay, col=['user_id', 'stime', 'etime', 'LONCOL', 'LATCOL','lon','lat'], minhour=3, start_hour=8, end_hour=20,workdaystart=0, workdayend=4)
        assert work['LONCOL'].iloc[0] == -86

        #Plot activity
        stay['group'] = stay['LONCOL'].astype(str)+','+stay['LATCOL'].astype(str)
        tbd.plot_activity(stay,col=['stime', 'etime', 'group'])

        # Smooth trajectory
        smoothed = tbd.traj_smooth(data,col = ['user_id','stime','longitude', 'latitude'],proj = False,process_noise_std = 0.5, measurement_noise_std = 1)
        smoothed = tbd.traj_smooth(data,col = ['user_id','stime','longitude', 'latitude'],proj = True,process_noise_std = 0.5, measurement_noise_std = 1)
        assert len(smoothed) == 14

        #Segment trajectory
        segmented = tbd.traj_segment(slicedata,groupby_col=['user_id'],retain_col=['stime', 'longitude', 'latitude', 'date','moveid'])
        assert len(segmented) == 1

        import osmnx as ox
        traj = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', 'traj2.csv'))
        G = ox.load_graphml(os.path.join(os.path.dirname(__file__), 'data', 'G.graphml'))
        assert len(tbd.traj_mapmatch(traj,G,col=['lon','lat']))==14