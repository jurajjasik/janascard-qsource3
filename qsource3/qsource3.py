from pymeasure.instruments import Instrument
from qsource3.qsource3driver import QSource3Driver


class QSource3(Instrument):
    def __init__(self, driver: QSource3Driver, name="QSource3", **kwargs):
        super().__init__(adapter=None, name=name, **kwargs)
        self._driver = driver

        self._dc1 = None
        self._dc2 = None
        self._rf = None

    def set_voltages(dc1, dc2, rf):
        self._driver.set_voltages(dc1, dc2, rf)
        self._dc1 = dc1
        self._dc2 = dc2
        self._rf = rf

    @property
    def rf(self):
        return self._rf

    @rf.setter
    def rf(self, v):
        self._driver.ac = 2.0 * v  # amp 0-P to amp P-P
        self._rf = v

    @property
    def dc1(self):
        return self._dc1

    @dc1.setter
    def dc1(self, v):
        self._driver.dc1 = v
        self._dc1 = v

    @property
    def dc2(self):
        return self._dc2

    @dc2.setter
    def dc2(self, v):
        self._driver.dc2 = v
        self._dc2 = v

    @property
    def dc_offst(self):
        return (self.dc1 + self.dc2) / 2.0

    @dc_offst.setter
    def dc_offst(self, v):
        self.dc1 = v + self.dc_diff
        self.dc2 = v - self.dc_diff

    @property
    def dc_diff(self):
        return (self.dc1 - self.dc2) / 2.0

    @dc_diff.setter
    def dc_diff(self, v):
        self.dc1 = self.dc_offst + v
        self.dc2 = self.dc_offst - v
