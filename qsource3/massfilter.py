import numpy as np
from scipy import interpolate
import scipy.constants as sc
from pymeasure.instruments import Instrument
from qsource3.qsource3driver import QSource3Driver
from qsource3.qsource3 import QSource3


def interp_fnc(xy):
    r"""
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
    r"""
    Quadrupole mass filter high-level class.

    Voltage applied to quadrupole poles A and B is:

    .. math::
        {\phi}_{\text{A}} = U_{\text{ofst}} + U_{\text{diff}} + V \cos(2{\pi} f)

        {\phi}_{\text{B}} = U_{\text{ofst}} - U_{\text{diff}} - V \cos(2{\pi} f)

    RF amplitude :math:`V` is given by:

    .. math::
        V = q_0 ({\pi} f r_0)^2 [1 + {\delta}(m/z)] (m/z)
        :label: eq_V

    where :math:`q_0 = 0.706`, :math:`f` is frequency (in Hertz),
    :math:`r_0` is characteristic radius of quadrupole,
    :math:`(m/z)` is mass over charge ratio (in u/e),
    and :math:`{\delta}(m/z)` is mass calibration function.

    In mass filtering mode, the DC difference :math:`U_{\text{diff}}` is given by:

    .. math::
        U_{\text{diff}} = \frac{1}{2} \frac{a_0}{q_0} [1 + {\rho}(m/z)] V(m/z)
        :label: eq_U

    where :math:`a_0 = 0.237`,
    and :math:`{\rho}(m/z) < 0` is resolution calibration function (the resolution is infinitive for :math:`{\rho}(m/z) = 0`).

    If :math:`U_{\text{diff}} = 0` then the quadrupole acts as an ion guide. This option can be switched by :attr:`is_dc_on`.

    The functions :math:`{\delta}(m/z)` and :math:`{\rho}(m/z)` are interpolated from 2D arrays
    [[:math:`(m/z)_0`, :math:`{\delta}_0`], [:math:`(m/z)_1`, :math:`{\delta}_1`], ...]
    and
    [[:math:`(m/z)_0`, :math:`{\rho}_0`], [:math:`(m/z)_1`, :math:`{\rho}_1`], ...].
    See :attr:`calib_pnts_rf`, :attr:`calib_pnts_dc`, :attr:`interp_fnc`.

    :param frequency: RF frequency of the quadrupole :math:`f` in Hertz
    :param r0: characteristic radius of the quadrupole :math:`r_0` in meters
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
        self._dcFactor = 0.5 * 0.237 / 0.706

    @property
    def calib_pnts_rf(self):
        r"""
        Calibration points for RF amplitude (m/z calibration) using which :math:`{\delta}(m/z)` is constructed.

        See :eq:`eq_V`.

        :getter: Get copy of calibration points as 2D numpy array
        :setter: Set calibration points and create a new :attr:`interp_fnc_calib_pnts_rf` method
        :type: 2D array [[:math:`(m/z)_0`, :math:`{\delta}_0`], [:math:`(m/z)_1`, :math:`{\delta}_1`], ...]

        The points are interpolated using :attr:`interp_fnc`.
        """
        return np.copy(self._calib_pnts_rf)

    @calib_pnts_rf.setter
    def calib_pnts_rf(self, xy):
        self._calib_pnts_rf = np.array(xy)
        self._interp_fnc_calib_pnts_rf = interp_fnc(self._calib_pnts_rf)

    def interp_fnc_calib_pnts_rf(self, mz:float)->float:
        r"""
        Mass calibration function :math:`{\delta}(m/z)`

        See :eq:`eq_V`.

        :param mz: :math:`m/z`
        """
        return self._interp_fnc_calib_pnts_rf(mz)

    @property
    def calib_pnts_dc(self):
        r"""
        Calibration points for DC difference (resolution) using which :math:`{\rho}(m/z)` is constructed.

        See :eq:`eq_U`.

        :getter: Get copy of calibration points as 2D numpy array
        :setter: Set calibration points and create a new :attr:`interp_fnc_calib_pnts_dc` method
        :type: 2D array [[:math:`(m/z)_0`, :math:`{\rho}_0`], [:math:`(m/z)_1`, :math:`{\rho}_1`], ...]

        The points are interpolated using :attr:`interp_fnc`.
        """
        return np.copy(self._calib_pnts_dc)

    @calib_pnts_dc.setter
    def calib_pnts_dc(self, xy):
        self._calib_pnts_dc = np.array(xy)
        self._interp_fnc_calib_pnts_dc = interp_fnc(self._calib_pnts_dc)

    def interp_fnc_calib_pnts_dc(self, mz: float) -> float:
        r"""
        Resolution calibration function :math:`{\rho}(m/z)`

        See :eq:`eq_U`.

        :param mz: :math:`m/z`
        """
        return self._interp_fnc_calib_pnts_dc(mz)

    @property
    def mz(self)->float:
        r"""
        :math:`m/z`

        :getter: Last value of :math:`m/z`
        :setter: Set RF amplitude and DC difference according to given :math:`m/z` and internal state (
                 :attr:`is_dc_on`,
                 :attr:`is_rod_polarity_positive`,
                 :attr:`calib_pnts_dc`,
                 :attr:`calib_pnts_rf`
                 )
        """
        return self._mz

    @mz.setter
    def mz(self, mz:float):
        if mz < 0:
            mz = 0
        U, V = self.calc_uv(mz)
        self.set_uv(U, V)
        _mz = mz

    @property
    def is_rod_polarity_positive(self)->bool:
        r"""
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
    def is_dc_on(self) -> bool:
        r"""
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

    def calc_uv(self, mz: float) -> (float, float):
        r"""
        Calculate RF amplitude :math:`V` and DC difference :math:`U_{\text{diff}}`.
        for given :math:`m/z` according to :eq:`eq_V` and :eq:`eq_U`

        :param mz: :math:`m/z`
        :returns: (:math:`U_{\text{diff}}`, :math:`V`)
        """
        v = self._rfFactor * (1.0 + interp(mz, self._calib_pnts_rf)) * mz
        u = self._dcFactor * (1.0 + interp(mz, self._calib_pnts_dc)) * v
        return u, v

    def set_uv(self, u: float, v: float):
        r"""
        Set RF amplitude :math:`V` and DC difference :math:`U_{\text{diff}}`.

        The DC difference is set according to :attr:`is_dc_on` and :attr:`is_rod_polarity_positive`.

        The DC offset :math:`U_{\text{ofst}}` is not affected.

        :param u: DC difference :math:`U_{\text{diff}}`
        :param v: RF amplitude :math:`V`
        """
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
    def max_mz(self) -> float:
        r"""
        Maximum :math:`m/z` of this quadrupole.

        :math:`{\delta}(m/z)` and :math:`{\rho}(m/z)` are not accounted.
        """
        return self._driver.MAX_RF_AMP_PP / 2 / self._rfFactor
