from qsource3.qsource3 import QSource3
from qsource3.massfilter import Quadrupole

qs = QSource3("COM1")
q1 = Quadrupole(frequency=200e3, r0=3e-3, adapter="COM1", name="Q1", )
q2 = Quadrupole(frequency=500e3, r0=3e-3, adapter="COM1", name="Q2", )
q3 = Quadrupole(frequency=1000e3, r0=3e-3, adapter="COM1", name="Q3", )


# qs.dc1 = 0

qs.voltages = (0, 0, 0)
