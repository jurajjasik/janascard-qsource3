import numpy as np
from scipy import interpolate
from pymeasure.instruments import Instrument
from qsource3.qsource3 import QSource3


def interp_fnc(xy):
    array = np.array(xy)

    if array.shape[0] == 1:
        return lambda v: array[0, 1] * np.ones_like(v)

    if array.shape[0] == 2:
        return interpolate.interp1d(
            array[:, 0], array[:, 1], fill_value="extrapolate", kind="slinear"
        )

    if array.shape[0] > 2:
        return interpolate.interp1d(
            array[:, 0], array[:, 1], fill_value="extrapolate", kind="quadratic"
        )

    return lambda v: np.zeros_like(v)


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

        self._mz = None
        self._dc1 = None
        self._dc2 = None
        self._rfAmp = None
        self._polarity = True  # rods polarity
        self._dcOn = True  #  True => mass filter, False => ion guide

        """
         RF_amp = _rfFactor * (m/z)
        _rfFactor = q0 * pi**2 * (r0 * frequency)**2
         q0 = 0.706
        """
        self._rfFactor = 7.22176e-8 * (r0 * frequency) ** 2

        """
        1/2 * a0/q0 - theoretical value for infinity resolution
        """
        self._dcFactor = 0.16784 * self._rfFactor

    @property
    def mz(self):
        return self._mz

    @mz.setter
    def mz(self, mz):
        """
        Set m/z
        """
        if mz < 0:
            mz = 0
        V = self.calc_rf(mz)
        U = self.calc_dc(mz)
        self.set_uv(U, V)
        _mz = mz

    def calc_rf(self, mz):
        return self._rfFactor * (1.0 + interp(mz, self._calib_pnts_rf)) * mz

    def calc_dc(self, mz):
        return self._dcFactor * (1.0 + interp(mz, self._calib_pnts_dc)) * mz
