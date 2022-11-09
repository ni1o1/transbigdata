import transbigdata as tbd
import numpy as np
import pandas as pd

class TestActivity:
    def test_entropy(self):
        result = tbd.entropy([1,2,3])
        truth = 1.584962500721156
        assert np.allclose(result,truth)

    def test_entropy_rate(self):
        result = tbd.entropy_rate([1,2,3,1,2,1])
        truth = 0.5283208335737187
        assert np.allclose(result,truth)

    def test_ellipse_params(self):
        np.random.seed(1)
        data = np.random.uniform(1, 10, (100, 2))
        data[:, 1:] = 0.5*data[:, 0:1]+np.random.uniform(-2, 2, (100, 1))
        data = pd.DataFrame(data, columns=['x', 'y'])
        ellip_params = tbd.ellipse_params(data, confidence=95, col=['x', 'y'])
        
        assert np.allclose(ellip_params[0], [5.0412876, 2.73948777])
        assert np.allclose(ellip_params[1:], [
            4.862704682680083,
            15.338646317379267,
            -62.20080325474961,
            58.580734145363145,
            0.6829769340746545])
            
        import matplotlib.pyplot as plt
        plt.figure(1,(5,5))
        ax = plt.subplot(111)
        tbd.ellipse_plot(ellip_params,ax,fill = False,edgecolor = 'k',linewidth = 1)