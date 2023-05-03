import numpy as np
from pymeasure.instruments import Instrument
from qsource3.qsource3 import QSource3


class Quadrupole(Instrument):
    def __init__(
        self,
        rf_generator: QSource3,
        frequency,
        r0,
        calib_pnts_rf=[],
        calib_pnts_dc=[],
        name="",
        **kwargs
    ):
        super().__init__(adapter=None, name=name, **kwargs)
        self._gen = rf_generator
        self._calib_pnts_rf = np.array(calib_pnts_rf)
        self._calib_pnts_dc = np.array(calib_pnts_dc)

        #  RF_amp = _rfFactor * (m/z)
        # _rfFactor = q0 * pi**2 * (r0 * frequency)**2
        #  q0 = 0.706
        self._rfFactor = 7.22176e-8 * (r0 * frequency) ** 2

        #  1/2 * a0/q0 - theoretical value for infinity resolution
        self._dcFactor = 0.16784 * self._rfFactor
