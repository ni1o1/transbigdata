import transbigdata as tbd
import numpy as np

class TestActivity:
    def test_entropy(self):
        result = tbd.cal_entropy([1,2,3])
        truth = 1.584962500721156
        assert np.allclose(result,truth)

    def test_entropy_rate(self):
        result = tbd.cal_entropy_rate([1,2,3,1,2,1])
        truth = 0.5283208335737187
        assert np.allclose(result,truth)