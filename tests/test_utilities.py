'''
This module tests the utilities module.
'''
#pylint: disable=invalid-name
#pylint: disable=line-too-long

import unittest

import numpy as np

from model.utilities import is_not_negative, is_positive, is_range, exponential_function, unit_sigmoid_function, expected_value, ReimannMethod, reimann_sum

class TestIsNotNegative(unittest.TestCase):
    '''Tests the is_not_negative function.'''
    def test_is_not_negative_returns_true_for_zero_value(self):
        '''Tests is_not_negative returns true for zero value.'''
        self.assertTrue(is_not_negative(0))

    def test_is_not_negative_returns_true_for_positive_value(self):
        '''Tests is_not_negative returns true for positive value.'''
        self.assertTrue(is_not_negative(1))

    def test_is_not_negative_returns_false_for_negative_value(self):
        '''Tests is_not_negative returns false for negative value.'''
        self.assertFalse(is_not_negative(-1))

class TestIsPositive(unittest.TestCase):
    '''Tests the is_positive function.'''
    def test_is_positive_returns_true_for_positive_value(self):
        '''Tests is_positive returns true for positive value.'''
        self.assertTrue(is_positive(1))

    def test_is_positive_returns_false_for_zero_value(self):
        '''Tests is_positive returns false for zero value.'''
        self.assertFalse(is_positive(0))

    def test_is_positive_returns_false_for_negative_value(self):
        '''Tests is_positive returns false for negative value.'''
        self.assertFalse(is_positive(-1))

class TestIsRange(unittest.TestCase):
    '''Tests the is_range function.'''
    def test_is_range_reverse_order_returns_false(self):
        '''Tests is range returns False for reverse order.'''
        self.assertFalse(is_range((1, 0)))

    def test_is_range_equal_values_returns_false(self):
        '''Tests is range retuns false for equal values.'''
        self.assertFalse(is_range((0, 0)))

    def test_is_range_single_value_returns_false(self):
        '''Tests is range returns false for single value.'''
        self.assertFalse(is_range((0,)))

    def test_is_range_0to1_returns_true(self):
        '''Tests is range returns true for [0,1].'''
        self.assertTrue(is_range((0, 1)))

    def test_is_range_more_than_2_values_returns_false(self):
        '''Tests is range returns false for more than 2 values.'''
        self.assertFalse(is_range((0, 0.5, 1)))

class TestExponential(unittest.TestCase):
    '''
    Tests the exponential function.
    '''
    def test_base_case_no_growth(self):
        '''
        Tests the exponential function with no growth.
        '''
        fx = exponential_function(base=1, rate_of_change=0)    #pylint: disable=invalid-name
        self.assertEqual(fx(10), 1)

    def test_base_case_with_growth(self):
        '''
        Tests the exponential function with growth.
        '''
        fx = exponential_function(base=1, rate_of_change=0.1)  #pylint: disable=invalid-name
        self.assertEqual(fx(10), 2.5937424601000023)

    def test_non_base_case_no_growth(self):
        '''
        Tests the exponential function with no growth.
        '''
        fx = exponential_function(base=2, rate_of_change=0)    #pylint: disable=invalid-name
        self.assertEqual(fx(10), 2)

    def test_non_base_case_with_growth(self):
        '''
        Tests the exponential function with growth.
        '''
        fx = exponential_function(base=2, rate_of_change=0.1)  #pylint: disable=invalid-name
        self.assertEqual(fx(10), 5.1874849202000046)

class TestSigmoid(unittest.TestCase):
    '''
    Tests the sigmoid function.
    '''
    def test_base_case_is_linear(self):
        '''
        Tests that the base case sigmoid function is linear.
        '''
        fx = unit_sigmoid_function(k=1)  #pylint: disable=invalid-name
        self.assertEqual(fx(0.5), 0.5)

    def test_base_case_min_value(self):
        '''
        Tests that the base case sigmoid function has lower bound of 0.
        '''
        fx = unit_sigmoid_function(k=1) #pylint: disable=invalid-name
        self.assertEqual(fx(0), 0)

    def test_base_case_max_value(self):
        '''
        Tests that the base case sigmoid function has upper bound of 1.
        '''
        fx = unit_sigmoid_function(k=1) #pylint: disable=invalid-name
        self.assertEqual(fx(1), 1)

    def test_base_case_lower_bound(self):
        '''
        Tests that the base case sigmoid function has lower bound of 0.
        '''
        fx = unit_sigmoid_function(k=1) #pylint: disable=invalid-name
        self.assertEqual(fx(-1), 0)

    def test_base_case_upper_bound(self):
        '''
        Tests that the base case sigmoid function has upper bound of 1.
        '''
        fx = unit_sigmoid_function(k=1) #pylint: disable=invalid-name
        self.assertEqual(fx(2), 1)

    def test_k_equals_0_is_step_min_value(self):
        '''
        Tests that the k = 0 sigmoid function has minimum value 0.
        '''
        fx = unit_sigmoid_function(k=0) #pylint: disable=invalid-name
        self.assertEqual(fx(0), 0)

    def test_k_equals_0_is_step_max_value(self):
        '''
        Tests that the k = 0 sigmoid function has maximum value 1.
        '''
        fx = unit_sigmoid_function(k=0) #pylint: disable=invalid-name
        self.assertEqual(fx(1), 1)

    def test_k_equals_0_is_dot5_at_dot01(self):
        '''
        Tests that the k = 0 sigmoid function is 0.5 at 0.01.
        '''
        fx = unit_sigmoid_function(k=0) #pylint: disable=invalid-name
        self.assertEqual(fx(0.1), 0.5)

    def test_k_equals_0_is_dot5_at_dot99(self):
        '''
        Tests that the k = 0 sigmoid function is 0.5 at 0.99.
        '''
        fx = unit_sigmoid_function(k=0) #pylint: disable=invalid-name
        self.assertEqual(fx(0.99), 0.5)

    def test_lower_k_has_gt_value_for_x_gt_0_lt_dot5(self):
        '''
        Tests that the sigmoid function with lower k has higher slope for x in (0, 0.5).
        '''
        fx_lo_k = [unit_sigmoid_function(k=2)(x) for x in np.arange(0.1, 0.5, 0.1)]
        fx_hi_k = [unit_sigmoid_function(k=3)(x) for x in np.arange(0.1, 0.5, 0.1)]
        for i, _ in enumerate(fx_lo_k):
            with self.subTest(i=i):
                self.assertGreater(fx_lo_k[i], fx_hi_k[i])

    def test_lower_k_has_lt_value_for_x_gt_dot5_lt_1(self):
        '''
        Tests that the sigmoid function with lower k has lower slope for x in (0.5, 1).
        '''
        fx_lo_k = [unit_sigmoid_function(k=2)(x) for x in np.arange(0.6, 1, 0.1)]
        fx_hi_k = [unit_sigmoid_function(k=3)(x) for x in np.arange(0.6, 1, 0.1)]
        for i, _ in enumerate(fx_lo_k):
            with self.subTest(i=i):
                self.assertLess(fx_lo_k[i], fx_hi_k[i])

    def test_lower_k_has_eq_value_for_x_le0_dot5_ge1(self):
        '''
        Tests that the sigmoid function with lower k has equal slope for x in {0, 0.5, 1}.
        '''
        fx_lo_k = [unit_sigmoid_function(k=2)(x) for x in [-1, 0, 0.5, 1, 2]]
        fx_hi_k = [unit_sigmoid_function(k=3)(x) for x in [-1, 0, 0.5, 1, 2]]
        for i, _ in enumerate(fx_lo_k):
            with self.subTest(i=i):
                self.assertEqual(fx_lo_k[i], fx_hi_k[i])

class TestExpectedValue(unittest.TestCase):
    '''
    Tests the expected value function.
    '''
    def test_no_depreciation(self):
        '''
        Tests the expected value function with no depreciation.
        '''
        self.assertEqual(expected_value([1, 2, 3, 4, 5], rate_of_depreciation=0), 3)

    def test_full_depreciation(self):
        '''
        Tests the expected value function with full depreciation.
        '''
        self.assertEqual(expected_value([1, 2, 3, 4, 5], rate_of_depreciation=1), 5)

    def test_weights(self):
        '''
        Tests the expected value function with half depreciation.
        '''
        # expected value: 4.1612...
        expected = sum([1 * 0.03125, 2 * 0.0625, 3 * 0.125, 4 * 0.25, 5 * 0.5]) / sum([0.03125, 0.0625, 0.125, 0.25, 0.5])  #pylint: disable=line-too-long
        self.assertEqual(expected_value([1, 2, 3, 4, 5], rate_of_depreciation=0.5), expected)

class TestReimannSum(unittest.TestCase):
    '''Tests the reimann sum function.'''
    def test_left_0to1_n100(self):
        '''Tests the reimann sum function with left reimann sum method, n = 100.'''
        self.assertEqual(reimann_sum(lambda x: x, (0, 1), method=ReimannMethod.LEFT, n=100), 0.495)

    def test_left_0to1_n1(self):
        '''Tests the reimann sum function with left reimann sum method, n = 1.'''
        self.assertEqual(reimann_sum(lambda x: x, (0, 1), method=ReimannMethod.LEFT, n=1), 0.0)

    def test_right_0to1_n100(self):
        '''Tests the reimann sum function with right reimann sum method, n = 100.'''
        self.assertEqual(reimann_sum(lambda x: x, (0, 1), method=ReimannMethod.RIGHT, n=100), 0.505)

    def test_right_0to1_n1(self):
        '''Tests the reimann sum function with right reimann sum method, n = 1.'''
        self.assertEqual(reimann_sum(lambda x: x, (0, 1), method=ReimannMethod.RIGHT, n=1), 1.0)

    def test_midpoint_0to1_n100(self):
        '''Tests the reimann sum function with midpoint reimann sum method, n = 100.'''
        self.assertEqual(reimann_sum(lambda x: x, (0, 1), method=ReimannMethod.MIDPOINT, n=100), 0.5)

    def test_midpoint_0to1_n1(self):
        '''Tests the reimann sum function with midpoint reimann sum method, n = 1.'''
        self.assertEqual(reimann_sum(lambda x: x, (0, 1), method=ReimannMethod.MIDPOINT, n=1), 0.5)

    def test_trapezoid_0to1_n100(self):
        '''Tests the reimann sum function with trapezoid reimann sum method, n = 100.'''
        self.assertEqual(reimann_sum(lambda x: x, (0, 1), method=ReimannMethod.TRAPEZOID, n=100), 0.5)

    def test_trapezoid_0to1_n1(self):
        '''Tests the reimann sum function with trapezoid reimann sum method, n = 1.'''
        self.assertEqual(reimann_sum(lambda x: x, (0, 1), method=ReimannMethod.TRAPEZOID, n=1), 0.5)
