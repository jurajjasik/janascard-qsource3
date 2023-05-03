from qsource3.qsource3 import QSource3

class Quadrupole(QSource3):
    def __init__(self, frequency, r0, adapter, name, **kwargs):
        super().__init__(adapter, name, **kwargs)
        self._f = frequency
        self._r0 = r0
    