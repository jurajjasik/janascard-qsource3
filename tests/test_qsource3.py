import pytest

from pymeasure.test import expected_protocol
from qsource3.qsource3 import QSource3


def test_test_communication():
    with expected_protocol(
        QSource3,
        [("#Q", "OK")],
    ) as inst:
        inst.test_communication()


def test_set_rs485_mode():
    with expected_protocol(
        QSource3,
        [("#R 1", "OK")],
    ) as inst:
        inst.set_rs485_mode()


def test_dc1():
    with expected_protocol(
        QSource3,
        [("#DC1 1000", "OK")],
    ) as inst:
        inst.dc1 = 1.0


def test_dc2():
    with expected_protocol(
        QSource3,
        [("#DC2 -75000", "OK")],
    ) as inst:
        inst.dc2 = -100.0


def test_ac():
    with expected_protocol(
        QSource3,
        [("#AC 1000", "OK")],
    ) as inst:
        inst.ac = 1.0


def test_voltages():
    with expected_protocol(
        QSource3,
        [("#C 1000 1000 1000", "OK")],
    ) as inst:
        inst.voltages = (1.0, 1.0, 1.0)


def test_frequency():
    with expected_protocol(
        QSource3,
        [("#F 10000", "OK"), ("#G", "10000")],
    ) as inst:
        inst.frequency = 1e6
        assert inst.frequency == 1e6


def test_current():
    with expected_protocol(
        QSource3,
        [("#U", "1234")],
    ) as inst:
        assert inst.current == 1234 / 10.0


def test_range():
    with expected_protocol(
        QSource3,
        [("#B 1", "OK")],
    ) as inst:
        inst.range = 1


def test_store_frequency():
    with expected_protocol(
        QSource3,
        [("#S", "OK")],
    ) as inst:
        inst.store_frequency()
