import numpy as np
from scipy import interpolate
import scipy.constants as sc
from pymeasure.instruments import Instrument
from qsource3.qsource3driver import QSource3Driver
from qsource3.qsource3 import QSource3


def interp_fnc(xy):
    """
    Create function f(x) interpolaing points (x\ :sub:`0`, y\ :sub:`0`), (x\ :sub:`1`, y\ :sub:`1`), ... .

    - f(x) = y\ :sub:`0` for xy = [[x0, y0]]
    - f(x) = y\ :sub:`0` + (y\ :sub:`1` - y\ :sub:`0`) / (x\ :sub:`1` - x\ :sub:`0`) * x
      for xy = [[x\ :sub:`0`, y\ :sub:`0`], [x\ :sub:`1`, y\ :sub:`1`]]
    - f(x) is  `quadratic spline interpolation function
      <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html#scipy.interpolate.interp1d>`_
      for higher number of xy points
    - f(x) = 0 otherwise

    :param xy: 2D array [[x\ :sub:`0`, y\ :sub:`0`], [x\ :sub:`1`, y\ :sub:`1`], ...]
    :returns: 1D function
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
    """
    Represents quadrupole mass filter high-level class.

    Owns instance of :class:`qsource3.qsource3driver.QSource3Driver`.
    
    :param frequency: RF frequency of the quadrupole in Hertz
    :param r0: characteristic radius of the quadrupole in meters
    :param driver: instance of :class:`qsource3.qsource3driver.QSource3Driver`
    :param calib_pnts_rf: calibration points for RF amplitude (m/z calibration), optional
    :param calib_pnts_dc: calibration points for DC difference (resolution), optional
    """
    def __init__(
        self,
        frequency: float,
        r0: float,
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

        # RF_amp = _rfFactor * (m/z)
        # _rfFactor = q0 * pi**2 * (r0 * frequency)**2
        # q0 = 0.706
        self._rfFactor = (
            0.706
            * sc.pi**2
            * sc.atomic_mass
            / sc.elementary_charge
            * (r0 * frequency) ** 2
        )

        # 1/2 * a0/q0 = 0.16784 - theoretical value for infinity resolution
        self._dcFactor = 0.16784 * self._rfFactor

    @property
    def calib_pnts_rf(self):
        """
        Calibration points for RF amplitude (m/z calibration). 
        
        :getter: Get copy of calibration points as 2D numpy array
        :setter: Set calibration points and create a new :attr:`interp_fnc_calib_pnts_rf` method
        :type: 2D array [[(m/z)\ :sub:`0`, y\ :sub:`0`], [(m/z)\ :sub:`1`, y\ :sub:`1`], ...]
        
        The points are interpolated using :attr:`interp_fnc`.
        """
        return np.copy(self._calib_pnts_rf)

    @calib_pnts_rf.setter
    def calib_pnts_rf(self, xy):
        self._calib_pnts_rf = np.array(xy)
        self._interp_fnc_calib_pnts_rf = interp_fnc(self._calib_pnts_rf)

    def interp_fnc_calib_pnts_rf(self, mz:float)->float:
        """
        Calculate a correction factor to RF amplitude for given m/z.
        
        :param mz: m/z
        """
        return self._interp_fnc_calib_pnts_rf(mz)

    @property
    def calib_pnts_dc(self):
        """
        Calibration points for DC difference (resolution). 
        
        :getter: Get copy of calibration points as 2D numpy array
        :setter: Set calibration points and create a new :attr:`interp_fnc_calib_pnts_dc` method
        :type: 2D array [[(m/z)\ :sub:`0`, y\ :sub:`0`], [(m/z)\ :sub:`1`, y\ :sub:`1`], ...]
        
        The points are interpolated using :attr:`interp_fnc`.
        """
        return np.copy(self._calib_pnts_dc)

    @calib_pnts_dc.setter
    def calib_pnts_dc(self, xy):
        self._calib_pnts_dc = np.array(xy)
        self._interp_fnc_calib_pnts_dc = interp_fnc(self._calib_pnts_dc)

    def interp_fnc_calib_pnts_dc(self, mz):
        """
        Calculate a correction factor to DC difference for given m/z.
        
        :param mz: m/z
        """
        return self._interp_fnc_calib_pnts_dc(mz)

    @property
    def mz(self)->float:
        """
        m/z
        
        :getter: Last value of m/z
        :setter: Set RF amplitude and DC difference according to given m/z and internal state (
                 :attr:`is_dc_on`,
                 :attr:`is_rod_polarity_positive`,
                 :attr:`calib_pnts_dc`,
                 :attr:`interp_fnc_calib_pnts_rf`
                 )
        """
        return self._mz

    @mz.setter
    def mz(self, mz:float):
        if mz < 0:
            mz = 0
        V = self.calc_rf(mz)
        U = self.calc_dc(mz)
        self.set_uv(U, V)
        _mz = mz

    @property
    def is_rod_polarity_positive(self)->bool:
        """
        Polarity of DC difference applied to rods.
        
        DC offset, RF amplitude and absolute value of DC difference is preserved.
        """
        return self._is_rod_polarity_positive

    @is_rod_polarity_positive.setter
    def is_rod_polarity_positive(self, v):
        if v != self._is_rod_polarity_positive:
            self._is_rod_polarity_positive = v
            self.dc_diff = -self.dc_diff

    @property
    def is_dc_on(self):
        """
        Flag if DC difference is applied to rods.
        
        - True - mass filter
        - False - ion guide
        
        DC offset and RF amplitude is preserved.
        """
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

    @property
    def max_mz(self):
        return self._driver.MAX_RF_AMP_PP / 2 / self._rfFactor
    
