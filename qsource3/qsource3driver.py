from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


class QSource3Driver(Instrument):
    MAX_RF_AMP = 650.0  # Volts peak-to-peak
    MAX_DC = 75.0  # Volts
    
    def __init__(self, adapter, name="QSource3Driver", **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={
                "baud_rate": 1000000,
                "read_termination": "\r",
                "write_termination": "\r",
            },
            **kwargs,
        )

    def _ask_ok(self, s):
        response = self.ask(s)
        if response != "OK":
            raise ConnectionError(f"Invalid response: {response}")

    def test_communication(self):
        """
        Communication test
        """
        self._ask_ok("#Q")

    serial_number = Instrument.measurement(
        "#N",
        """Get serial number, returns three character string""",
    )

    def set_rs485_mode(self):
        """
        Set RS485 communication mode.
        """
        self._ask_ok("#R 1")

    def set_dc_voltage(self, output, voltage):
        """
        Set DC voltage in Volts (float from -75 to +75).

        :param voltage: voltage in Volts (float from -75 to +75).
        :param output: Output channel - 1 or 2.

        Resolution: 16 bits => real resolution is 2.3 mV.
        The values out of range are truncated.
        """
        v = int(round(truncated_range(voltage, [-self.MAX_DC, self.MAX_DC]) * 1000.0))  # convert to mV
        self._ask_ok(f"#DC{output} {v}")

    dc1 = property(
        fget=None,
        fset=lambda self, v: self.set_dc_voltage(1, v),
        doc="""
        Set DC voltage of channel 1 in Volts (float from -75 to +75).
        """,
    )

    dc2 = property(
        fget=None,
        fset=lambda self, v: self.set_dc_voltage(2, v),
        doc="""
        Set DC voltage of channel 2 in Volts (float from -75 to +75).
        """,
    )

    def set_ac_voltage(self, ac):
        """
        Set AC voltage with peak to peak value in Volts (float from 0 to +650).

        Resolution: 16 bits => real resolution is 9.4 mV.
        The values out of range are truncated.
        """
        v = int(round(truncated_range(ac, [0, self.MAX_RF_AMP]) * 1000.0))  # convert to mV
        self._ask_ok(f"#AC {v}")

    ac = property(
        fget=None,
        fset=lambda self, v: self.set_ac_voltage(v),
        doc="""
        Set AC voltage with peak to peak value in Volts (float from 0 to +650).
        """,
    )

    def set_voltages(self, dc1, dc2, ac):
        """
        Set DC and AC voltages.

        param dc1: DC voltage of channel 1 in Volts (float from -75 to +75).
        param dc2: DC voltage of channel 2 in Volts (float from -75 to +75).
        param ac: AC voltage with peak to peak value in Volts (float from 0 to +650).
        """
        _dc1 = int(round(truncated_range(dc1, [-self.MAX_DC, self.MAX_DC]) * 1000.0))  # convert to mV
        _dc2 = int(round(truncated_range(dc2, [-self.MAX_DC, self.MAX_DC]) * 1000.0))  # convert to mV
        _ac = int(round(truncated_range(ac, [0, self.MAX_RF_AMP]) * 1000.0))  # convert to mV
        self._ask_ok(f"#C {_dc1} {_dc2} {_ac}")

    voltages = property(
        fget=None,
        fset=lambda self, v: self.set_voltages(v[0], v[1], v[2]),
        doc="""
        Set DC and AC voltages.

        param dc1: DC voltage of channel 1 in Volts (float from -75 to +75).
        param dc2: DC voltage of channel 2 in Volts (float from -75 to +75).
        param ac: AC voltage with peak to peak value in Volts (float from 0 to +650).
        """,
    )

    def set_frequency(self, frequency):
        self._ask_ok(f"#F {int(round(frequency / 100.0))}")

    def get_frequency(self):
        response = self.ask("#G")
        return float(response) * 100

    frequency = property(
        fget=lambda self: self.get_frequency(),
        fset=lambda self, v: self.set_frequency(v),
        doc="""
        Set frequency of the generator at the actual range in Hz.
        """,
    )

    current = Instrument.measurement(
        "#U",
        """Get excitation current in mA""",
        get_process=lambda v: v / 10.0,  # convert to mA
    )

    def set_range(self, range):
        _range = strict_discrete_set(range, [0, 1, 2])
        self._ask_ok(f"#B {_range}")

    range = property(
        fget=None,
        fset=lambda self, v: self.set_range(v),
        doc="""
        Changes resonant frequency and corresponding mass measurement range of the
        quadrupole. 
        Property has range 0-2, where 0 is the highest range typically 1050 kHz, 
        1 – 480 kHz, 2 – 240 kHz.
        """,
    )

    def store_frequency(self):
        """
        Store actual value of frequency at the actual range given by
        :attr:`QSource3.range` into Flash memory. This value is read after power on.
        """
        self._ask_ok("#S")
