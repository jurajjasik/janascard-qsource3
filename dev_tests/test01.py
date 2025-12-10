from qsource3.qsource3 import QSource3Driver
from qsource3.massfilter import Quadrupole

qs = QSource3Driver("COM1")

r0 = 3e-3  # m

q1 = Quadrupole(
    frequency=240e3,
    r0=r0,
    driver=qs,
    name="Q1",
)
q2 = Quadrupole(
    frequency=480e3,
    r0=r0,
    driver=qs,
    name="Q2",
)
q3 = Quadrupole(
    frequency=1050e3,
    r0=r0,
    driver=qs,
    name="Q3",
)

print(f"q1.max_mz = {q1.max_mz}")
print(f"q2.max_mz = {q2.max_mz}")
print(f"q3.max_mz = {q3.max_mz}")
