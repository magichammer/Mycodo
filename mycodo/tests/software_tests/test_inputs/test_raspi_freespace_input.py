# coding=utf-8
""" Tests for the RaspberryPiFreeSpace sensor class """
import mock
import pytest
from testfixtures import LogCapture

from collections import Iterator
from mycodo.inputs.raspi_freespace import InputModule as RaspberryPiFreeSpace


# ----------------------------
#   RaspberryPiFreeSpace tests
# ----------------------------
def test_raspi_freespace_iterates_using_in():
    """ Verify that a RaspberryPiFreeSpace object can use the 'in' operator """
    with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement') as mock_measure:
        mock_measure.side_effect = [67, 52, 37, 45]
        raspi_freespace = RaspberryPiFreeSpace(None, testing=True)
        expected_result_list = [dict(disk_space=67.00),
                                dict(disk_space=52.00),
                                dict(disk_space=37.00),
                                dict(disk_space=45.00)]
        assert expected_result_list == [temp for temp in raspi_freespace]


def test_raspi_freespace__iter__returns_iterator():
    """ The iter methods must return an iterator in order to work properly """
    with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement') as mock_measure:
        mock_measure.side_effect = [67, 52]
        raspi_freespace = RaspberryPiFreeSpace(None, testing=True)
        assert isinstance(raspi_freespace.__iter__(), Iterator)


def test_raspi_freespace_read_updates_temp():
    """  Verify that RaspberryPiFreeSpace(0x99, 1).read() gets the average temp """
    with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement') as mock_measure:
        mock_measure.side_effect = [67, 52]
        raspi_freespace = RaspberryPiFreeSpace(None, testing=True)
        assert raspi_freespace._disk_space is None
        assert not raspi_freespace.read()
        assert raspi_freespace._disk_space == 67.0
        assert not raspi_freespace.read()
        assert raspi_freespace._disk_space == 52.0


def test_raspi_freespace_next_returns_dict():
    """ next returns dict(disk_space=float) """
    with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement') as mock_measure:
        mock_measure.side_effect = [67, 52]
        raspi_freespace = RaspberryPiFreeSpace(None, testing=True)
        assert raspi_freespace.next() == dict(disk_space=67.00)


def test_raspi_freespace_condition_properties():
    """ verify disk_space property """
    with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement') as mock_measure:
        mock_measure.side_effect = [67, 52]
        raspi_freespace = RaspberryPiFreeSpace(None, testing=True)
        assert raspi_freespace._disk_space is None
        assert raspi_freespace.disk_space == 67.00
        assert raspi_freespace.disk_space == 67.00
        assert not raspi_freespace.read()
        assert raspi_freespace.disk_space == 52.00


def test_raspi_freespace_special_method_str():
    """ expect a __str__ format """
    with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement') as mock_measure:
        mock_measure.side_effect = [0.0]
        raspi_freespace = RaspberryPiFreeSpace(None, testing=True)
        raspi_freespace.read()
        assert "Free Space: 0.00" in str(raspi_freespace)


def test_raspi_freespace_special_method_repr():
    """ expect a __repr__ format """
    with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement') as mock_measure:
        mock_measure.side_effect = [0.0]
        raspi_freespace = RaspberryPiFreeSpace(None, testing=True)
        raspi_freespace.read()
        assert "<InputModule(disk_space=0.00)>" in repr(raspi_freespace)


def test_raspi_freespace_raises_exception():
    """ stops iteration on read() error """
    with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement', side_effect=IOError):
        with pytest.raises(StopIteration):
            RaspberryPiFreeSpace(None, testing=True).next()


def test_raspi_freespace_read_returns_1_on_exception():
    """ Verify the read() method returns true on error """
    with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement', side_effect=Exception):
        assert RaspberryPiFreeSpace(None, testing=True).read()


def test_raspi_freespace_read_logs_unknown_errors():
    """ verify that IOErrors are logged """
    with LogCapture() as log_cap:
        with mock.patch('mycodo.inputs.raspi_freespace.InputModule.get_measurement', side_effect=Exception('msg')):
            RaspberryPiFreeSpace(None, testing=True).read()
    expected_logs = ('mycodo.inputs.raspi_freespace', 'ERROR', 'InputModule raised an exception when taking a reading: msg')
    assert expected_logs in log_cap.actual()
