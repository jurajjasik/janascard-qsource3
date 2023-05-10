from pymeasure.instruments import Instrument
from qsource3.qsource3driver import QSource3Driver


class QSource3(Instrument):
    r"""
    High-level class representing QSource3 RF generator.
    
    Outputs of the generator: 
    
    .. math::
        {\phi}_{\text{A}} = U_1 + V \cos(2 {\pi} f)
        
        {\phi}_{\text{A}} = U_2 - V \cos(2 {\pi} f)
        
    where :math:`f` is frequency (in Hertz) given by actual frequency range of the ``driver``
    (see :attr:`QSource3Driver.set_range()`).
    Keeps track with DC voltages (:math:`U_1`, :math:`U_2`) and RF amplitude (:math:`V`).
    Provides manipulation 
    with DC offset (:math:`U_{\text{ofst}} = (U_1 + U_2) / 2`)
    and DC difference (:math:`U_{\text{diff}} = (U_1 - U_2) / 2`).

    :param driver: driver class for communication with QSource3 device.
    """
    def __init__(self, driver: QSource3Driver, name="QSource3", **kwargs):
        super().__init__(adapter=None, name=name, **kwargs)
        self._driver = driver

        self._dc1 = None
        self._dc2 = None
        self._rf = None

    def set_voltages(self, dc1: float, dc2: float, rf: float):
        r"""
        Set DC voltages and RF amplitude simultaneosly.

        :param dc1: DC voltage :math:`U_1`  (in Volts)
        :param dc2: DC voltage :math:`U_2`  (in Volts)
        :param rf: RF amplitude :math:`V` (in Volts, 0-to-peak)
        """
        self._driver.set_voltages(dc1, dc2, 2.0 * rf)
        self._dc1 = dc1
        self._dc2 = dc2
        self._rf = rf

    @property
    def rf(self)->float:
        r"""RF amplitude :math:`V` (in Volts, 0-to-peak)
        """
        return self._rf

    @rf.setter
    def rf(self, v):
        self._driver.ac = 2.0 * v  # amp 0-P to amp P-P
        self._rf = v

    @property
    def dc1(self)->float:
        r"""DC voltage :math:`U_1`  (in Volts)
        """
        return self._dc1

    @dc1.setter
    def dc1(self, v):
        self._driver.dc1 = v
        self._dc1 = v

    @property
    def dc2(self)->float:
        r"""DC voltage :math:`U_2`  (in Volts)
        """
        return self._dc2

    @dc2.setter
    def dc2(self, v):
        self._driver.dc2 = v
        self._dc2 = v

    @property
    def dc_offst(self)->float:
        r"""DC offset :math:`U_{\text{ofst}}` (in Volts)

        :getter: return :math:`U_{\text{ofst}} = (U_1 + U_2) / 2`
        :setter:
            :math:`U_1 := U_{\text{ofst}} + U_{\text{diff}}`,
            :math:`U_2 := U_{\text{ofst}} - U_{\text{diff}}`.
        """
        return (self.dc1 + self.dc2) / 2.0

    @dc_offst.setter
    def dc_offst(self, v):
        self.dc1 = v + self.dc_diff
        self.dc2 = v - self.dc_diff

    @property
    def dc_diff(self)->float:
        r"""DC difference :math:`U_{\text{diff}}` (in Volts)

        :getter: return :math:`U_{\text{diff}} = (U_1 - U_2) / 2`
        :setter:
            :math:`U_1 := U_{\text{ofst}} + U_{\text{diff}}`,
            :math:`U_2 := U_{\text{ofst}} - U_{\text{diff}}`.
        """
        return (self.dc1 - self.dc2) / 2.0

    @dc_diff.setter
    def dc_diff(self, v):
        self.dc1 = self.dc_offst + v
        self.dc2 = self.dc_offst - v
