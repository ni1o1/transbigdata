import transbigdata as tbd
import os

class TestDump:
    def test_dump(self):
        tbd.dumpjson([1], 'test.json')
        os.remove('test.json')