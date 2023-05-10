import pytest

from pymeasure.test import expected_protocol

from qsource3.qsource3 import QSource3Driver
from qsource3.massfilter import Quadrupole

with expected_protocol(
    QSource3Driver,
    [
        (r"#C 0 0 0", r"OK"),
        (
            r"#C 10909 -10909 129992",
            r"OK",
        ),  # 1 ... q.mz = 100 => DC1 = 10.909 V, DC2 = -10.909 V, RF = 129.992 Vp-p
        (r"#DC1 909", r"OK"),
        (r"#DC2 -20909", r"OK"),  # 2 ... q.dc_offst = -10
        (r"#DC1 -20909", r"OK"),
        (r"#DC2 909", r"OK"),  # 3 ... q.is_rod_polarity_positive = False
        (r"#C -10000 -10000 129992", r"OK"),  # 4 ... q.is_dc_on = False
        (r"#DC1 -10000", r"OK"),
        (r"#DC2 -10000", r"OK"),  # 5 ... q.is_rod_polarity_positive = False
        (r"#C 909 -20909 129992", r"OK"),  # 6 ... q.is_dc_on = True
    ],
) as driver:

    r0 = 3e-3
    f = 1e6

    q = Quadrupole(
        frequency=f,
        r0=r0,
        driver=driver,
        name="Q1",
    )

    # 1 ...
    q.mz = 100
    assert 100.0 == pytest.approx(q.mz)
    assert 64.99585477169073 == pytest.approx(q.rf)
    assert 10.909360892982084 == pytest.approx(q.dc_diff)
    assert 0.0 == pytest.approx(q.dc_offst)

    # 2 ...
    q.dc_offst = -10
    assert 100.0 == pytest.approx(q.mz)
    assert 64.99585477169073 == pytest.approx(q.rf)
    assert 10.909360892982084 == pytest.approx(q.dc_diff)
    assert -10.0 == pytest.approx(q.dc_offst)

    # 3 ...
    q.is_rod_polarity_positive = False
    assert 100.0 == pytest.approx(q.mz)
    assert 64.99585477169073 == pytest.approx(q.rf)
    assert -10.909360892982084 == pytest.approx(q.dc_diff)
    assert -10.0 == pytest.approx(q.dc_offst)

    # 4 ...
    q.is_dc_on = False
    assert 100.0 == pytest.approx(q.mz)
    assert 64.99585477169073 == pytest.approx(q.rf)
    assert 0.0 == pytest.approx(q.dc_diff)
    assert -10.0 == pytest.approx(q.dc_offst)

    # 5 ...
    q.is_rod_polarity_positive = True
    assert 100.0 == pytest.approx(q.mz)
    assert 64.99585477169073 == pytest.approx(q.rf)
    assert 0.0 == pytest.approx(q.dc_diff)
    assert -10.0 == pytest.approx(q.dc_offst)

    # 6 ...
    q.is_dc_on = True
    assert 100.0 == pytest.approx(q.mz)
    assert 64.99585477169073 == pytest.approx(q.rf)
    assert 10.909360892982084 == pytest.approx(q.dc_diff)
    assert -10.0 == pytest.approx(q.dc_offst)
