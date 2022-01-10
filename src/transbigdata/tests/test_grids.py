import transbigdata as tbd
import numpy as np

class TestGrids:
    def test_rect_grids(self):
        bounds = [113.6,22.4,114.8,22.9]
        result = tbd.grid_params(bounds,accuracy = 500)
        truth = (113.6, 22.4, 0.004872390756896538, 0.004496605206422906)
        assert np.allclose(result,truth)