"""Unit tests for the safe_yaml module"""

import unittest
from collections import defaultdict, OrderedDict, Counter

import numpy as np

from pynba.safe_yaml import dump, load, _convert_to_native_types


class TestSafeYaml(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test case for safe_yaml"""

    def _check_data(self, data):
        self.assertEqual(data, load(dump(data)))

    def _check_conversion(self, data, expected):
        native_data = _convert_to_native_types(data)
        self.assertEqual(native_data, expected)

    def test_dict(self):
        """Test dict serializes correctly"""
        self._check_data({1: 2})

    def test_defaultdict(self):
        """Test defaultdict converts correctly"""
        self._check_conversion(defaultdict(int, one=2), {"one": 2})

    def test_ordereddict(self):
        """Test OrderedDict converts correctly"""
        self._check_conversion(OrderedDict(one=2), {"one": 2})

    def test_counter(self):
        """Test Counter serializes correctly"""
        self._check_conversion(Counter(one=2), {"one": 2})

    def test_list(self):
        """Test list serializes correctly"""
        self._check_data([1, 2])

    def test_set(self):
        """Test set converts correctly"""
        self._check_conversion({1, 2}, [1, 2])

    def test_frozen_set(self):
        """Test frozenset converts correctly"""
        self._check_conversion(frozenset([1, 2]), [1, 2])

    def test_tuple(self):
        """Test tuple converts correctly"""
        self._check_conversion((1, 2), [1, 2])

    def test_keys(self):
        """Test dict.keys() converts correctly"""
        self._check_conversion({1: 2}.keys(), [1])

    def test_values(self):
        """Test dict.values() converts correctly"""
        self._check_conversion({1: 2}.values(), [2])

    def test_items(self):
        """Test dict.items() converts correctly"""
        self._check_conversion({1: 2}.items(), [[1, 2]])

    def test_range(self):
        """Test range converts correctly"""
        self._check_conversion(range(2), [0, 1])

    def test_generator(self):
        """Test generator converts correctly"""
        self._check_conversion((val for val in [1, 2]), [1, 2])

    def test_bool(self):
        """Test bool serializes correctly"""
        self._check_data(True)

    def test_int(self):
        """Test int serializes correctly"""
        self._check_data(1)

    def test_float(self):
        """Test float serializes correctly"""
        self._check_data(1.2)

    def test_str(self):
        """Test str serializes correctly"""
        self._check_data("one")

    def test_np_bool(self):
        """Test numpy bool converts correctly"""
        self._check_conversion(np.bool_(True), True)

    def test_np_int(self):
        """Test numpy int converts correctly"""
        self._check_conversion(np.int8(1), 1)

    def test_np_float(self):
        """Test numpy float converts correctly"""
        self._check_conversion(np.float64(1.2), 1.2)

    def test_np_str(self):
        """Test numpy string converts correctly"""
        self._check_conversion(np.str_("one"), "one")

    def test_np_array_1d(self):
        """Test numpy 1d array converts correctly"""
        self._check_conversion(np.array([1]), [1])

    def test_np_array_2d(self):
        """Test numpy 2d array converts correctly"""
        self._check_conversion(np.array([[1], [2]]), [[1], [2]])

    def test_none(self):
        """Test None serializes correctly"""
        self._check_data(None)


if __name__ == "__main__":
    unittest.main()
