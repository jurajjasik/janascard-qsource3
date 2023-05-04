import numpy as np
from scipy import interpolate
from pymeasure.instruments import Instrument
from qsource3.qsource3driver import QSource3Driver
from qsource3.qsource3 import QSource3


def interp_fnc(xy):
    """
    Create function interpolaing points

    :param xy: 2D array [[x0, y0], [x1, y1], ...]
    """
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


class Quadrupole(QSource3):
    def __init__(
        self,
        frequency,
        r0,
        driver: QSource3Driver,
        calib_pnts_rf=[],
        calib_pnts_dc=[],
        name="Quadrupole",
        **kwargs
    ):
        super().__init__(driver=driver, name=name, **kwargs)

        self.calib_pnts_rf = calib_pnts_rf
        self.calib_pnts_dc = calib_pnts_dc

        self._mz = None

        self._is_rod_polarity_positive = True  # rods polarity
        self._is_dc_on = True  #  True => mass filter, False => ion guide

        """
         RF_amp = _rfFactor * (m/z)
        _rfFactor = q0 * pi**2 * (r0 * frequency)**2
         q0 = 0.706
        """
        self._rfFactor = 7.22176e-8 * (r0 * frequency) ** 2

        """
        1/2 * a0/q0 = 0.16784 - theoretical value for infinity resolution
        """
        self._dcFactor = 0.16784 * self._rfFactor

    @property
    def calib_pnts_rf(self):
        return np.copy(self._calib_pnts_rf)

    @calib_pnts_rf.setter
    def calib_pnts_rf(self, xy):
        self._calib_pnts_rf = np.array(xy)
        self._interp_fnc_calib_pnts_rf = interp_fnc(self._calib_pnts_rf)

    def interp_fnc_calib_pnts_rf(self, mz):
        return self._interp_fnc_calib_pnts_rf(mz)

    @property
    def calib_pnts_dc(self):
        return np.copy(self._calib_pnts_dc)

    @calib_pnts_dc.setter
    def calib_pnts_dc(self, xy):
        self._calib_pnts_dc = np.array(xy)
        self._interp_fnc_calib_pnts_dc = interp_fnc(self._calib_pnts_dc)

    def interp_fnc_calib_pnts_dc(self, mz):
        return self._interp_fnc_calib_pnts_dc(mz)

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

    @property
    def is_rod_polarity_positive(self):
        return self._is_rod_polarity_positive

    @is_rod_polarity_positive.setter
    def is_rod_polarity_positive(self, v):
        if v != self._is_rod_polarity_positive:
            self._is_rod_polarity_positive = v
            self.dc_diff = -self.dc_diff

    @property
    def is_dc_on(self):
        return self._is_dc_on

    @is_dc_on.setter
    def is_dc_on(self, v):
        if v != self._is_dc_on:
            self._is_dc_on = v
            self.mz = self.mz  # reset mz => set correct DC voltages

    def calc_rf(self, mz):
        return self._rfFactor * (1.0 + interp(mz, self._calib_pnts_rf)) * mz

    def calc_dc(self, mz):
        return self._dcFactor * (1.0 + interp(mz, self._calib_pnts_dc)) * mz

    def set_uv(self, u, v):
        dc1 = self.dc_offst
        dc2 = self.dc_offst
        
        if self.is_dc_on:
            if self.is_rod_polarity_positive:
                dc1 += u
                dc2 -= u
            else:
                dc1 -= u
                dc2 += u
        
        self.set_voltages(dc1, dc2, v)
    