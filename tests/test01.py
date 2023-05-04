from qsource3.qsource3 import QSource3Driver
from qsource3.massfilter import Quadrupole

qs = QSource3Driver("COM1")

q1 = Quadrupole(
    frequency=200e3,
    r0=3e-3,
    driver=qs,
    name="Q1",
)
q2 = Quadrupole(
    frequency=500e3,
    r0=3e-3,
    driver=qs,
    name="Q2",
)
q3 = Quadrupole(
    frequency=1000e3,
    r0=3e-3,
    driver=qs,
    name="Q3",
)
