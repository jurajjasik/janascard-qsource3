import time
import numpy as np
from qsource3.qsource3driver import QSource3Driver
from qsource3.massfilter import Quadrupole


def make_full_scan(q: Quadrupole):
    # calculate maximum m/z
    max_mz = q.max_mz

    # create vector of m/z values from 0 to max_mz with step 0.1
    mz_vec = np.arange(0, max_mz, 0.1)

    #  scan over mz_vec
    for mz in mz_vec:
        q.mz = mz
        time.sleep(0.1)


# characteristic radius of the quadrupole
r0 = 3e-3

# create driver connected to COM1 port
driver = QSource3Driver("COM1")

###################
# switch to range 0
driver.set_range(0)

# read operating frequency from EEPROM
freq0 = driver.frequency

# create Quadrupole instance
q0 = Quadrupole(
    frequency=freq0,
    r0=r0,
    driver=driver,
    name="Q1",
)

###################
# switch to range 1
driver.set_range(1)

# read operating frequency from EEPROM
freq1 = driver.frequency

# create Quadrupole instance
q1 = Quadrupole(
    frequency=freq1,
    r0=r0,
    driver=driver,
    name="Q1",
)

###################
# switch to range 2
driver.set_range(2)

# read operating frequency from EEPROM
freq2 = driver.frequency

# create Quadrupole instance
q2 = Quadrupole(
    frequency=freq2,
    r0=r0,
    driver=driver,
    name="Q1",
)

# scan over range 0
driver.set_range(0)
make_full_scan(q0)

# scan over range 1
driver.set_range(1)
make_full_scan(q1)

# scan over range 2
driver.set_range(2)
make_full_scan(q2)
