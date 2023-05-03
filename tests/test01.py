from qsource3.qsource3 import QSource3
from qsource3.massfilter import Quadrupole

qs = QSource3("COM1")

q1 = Quadrupole(
    qs,
    frequency=200e3,
    r0=3e-3,
    name="Q1",
)
q2 = Quadrupole(
    qs,
    frequency=500e3,
    r0=3e-3,
    name="Q2",
)
q3 = Quadrupole(
    qs,
    frequency=1000e3,
    r0=3e-3,
    name="Q3",
)
