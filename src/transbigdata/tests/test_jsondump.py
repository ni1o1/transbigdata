import transbigdata as tbd
import os
import numpy as np


class TestDump:
    def test_dump(self):
        tbd.dumpjson([np.int64(1),
                      np.float64(1),
                      np.array([1])
                      ], 'test.json')
        os.remove('test.json')
