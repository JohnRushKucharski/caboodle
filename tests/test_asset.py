'''Tests for the asset module.'''
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest

from model.asset import Asset

class TestAsset(unittest.TestCase):
    '''Tests for the Asset class.'''
    def test_initial_value_default(self):
        '''Test that the default initial value is 100.0.'''
        self.assertEqual(100.0, Asset().initial_value)

    def test_salvage_value_default(self):
        '''Test that the default salvage value is 0.0.'''
        self.assertEqual(0.0, Asset().salvage_value)

    def test_periods_in_schedule_default(self):
        '''Test that the default periods in schedule is 100.0.'''
        self.assertEqual(100.0, Asset().periods_in_schedule)

    def test_maintenance_requirement_default(self):
        '''Test that the default maintenance requirement is 1.0.'''
        self.assertEqual(1.0, Asset().maintenance_requirement)

    def test_shape_parameter_default(self):
        '''Test that the default shape parameter is 1.0.'''
        self.assertEqual(1.0, Asset().shape_parameter)

    def test_acceleration_factor_default(self):
        '''Test that the default acceleration factor is 1.0.'''
        self.assertEqual(1.0, Asset().acceleration_factor)

    def test_ft_t_eq_0_returns_1(self):
        '''Test that the ft function returns 1 when t = 0.'''
        self.assertEqual(1.0, Asset().ft(0.0))

    def test_ft_t_eq_periods_in_schedule_returns_0(self):
        '''Test that the ft function returns 0 when t = periods_in_schedule.'''
        self.assertEqual(0.0, Asset().ft(Asset().periods_in_schedule))

    def test_ft_t_gt_periods_in_schedule_returns_0(self):
        '''Test that the ft function returns 0 when t > periods_in_schedule.'''
        self.assertEqual(0.0, Asset().ft(Asset().periods_in_schedule + 1.0))

    def test_default_ft_t_eq_periods_in_schedule_div_2_returns_0dot5(self):
        '''Test that the default ft function returns 1/2 when t = periods_in_schedule / 2.'''
        self.assertEqual(0.5, Asset().ft(Asset().periods_in_schedule / 2.0))

    def test_inverse_ft_y_eq_0_returns_periods_in_schedule(self):
        '''Test that the inverse_ft function returns periods_in_schedule when y = 0.'''
        self.assertEqual(Asset().periods_in_schedule, Asset().inverse_ft(0.0))

    def test_inverse_ft_y_eq_1_returns_0(self):
        '''Test that the inverse_ft function returns 0 when y = 1.'''
        self.assertEqual(0.0, Asset().inverse_ft(1.0))

    def test_inverse_ft_y_gt_1_raises_value_error(self):
        '''Test that the inverse_ft function raises a ValueError when y > 1.'''
        with self.assertRaises(ValueError):
            Asset().inverse_ft(1.1)

    def test_inverse_ft_y_lt_0_raises_value_error(self):
        '''Test that the inverse_ft function raises a ValueError when y < 0.'''
        with self.assertRaises(ValueError):
            Asset().inverse_ft(-0.1)

    def test_inverse_ft_y_eq_0dot5_returns_periods_in_schedule_div_2(self):
        '''Test that the inverse_ft function returns periods_in_schedule / 2 when y = 1/2.'''
        self.assertEqual(Asset().periods_in_schedule / 2.0, Asset().inverse_ft(0.5))

    def test_scheduler_maintenance_eq_0_acceleration_eq_1_returns_2(self):
        '''Test that the scheduler returns the initial value when there is no maintenance.'''
        self.assertEqual(2.0, Asset().scheduler(0.0))

    def test_scheduler_mainenance_eq_1_acceleration_eq_1_returns_1(self):
        '''Test that the scheduler returns 1 when maintenance equals the maintenance requirement.'''
        self.assertEqual(1.0, Asset().scheduler(1.0))

    def test_scheduler_maintenance_eq_2_raises_value_error(self):
        '''Test that the scheduler raises a ValueError when maintenance exceeds the maintenance requirement.'''
        with self.assertRaises(ValueError):
            Asset().scheduler(2.0)

    def test_scheduler_maintenance_eq_0_acceleration_eq_2_returns_3(self):
        '''Test that the scheduler returns (scheuded depreciation = 1) + (unfunded portion = 1.0) * 2 = 3.0 when there is no maintenance and acceleration equals 2.'''
        self.assertEqual(3.0, Asset(acceleration_factor=2.0).scheduler(0.0))

    def test_scheduler_maintenance_eq_1_acceleration_eq_2_returns_2(self):
        '''Test that the scheduler returns scheduled depreciation = 1 when there is maintenance and acceleration equals 2.'''
        self.assertEqual(1.0, Asset(acceleration_factor=2.0).scheduler(1.0))

    def test_scheduler_maintenance_eq_0_acceleration_eq_0dot5_returns_1dot5(self):
        '''Test that the scheduler returns (scheuded depreciation = 1) + (unfunded portion = 1.0) * 0.5 = 1.5 when there is no maintenance and acceleration equals 0.5.'''
        self.assertEqual(1.5, Asset(acceleration_factor=0.5).scheduler(0.0))

    def test_scheduler_maintenance_eq_1_acceleration_eq_0dot5_returns_1dot5(self):
        '''Test that the scheduler returns scheduled depreciation = 1 when there is maintenance and acceleration equals 0.5.'''
        self.assertEqual(1.0, Asset(acceleration_factor=0.5).scheduler(1.0))

    def test_depreciate_default_fx_maintenance_eq_required_maintenance_returns_scheduled_value(self):
        '''Test that the default depreciation function with required maintenance returns 1 year of depreciation on default schedule.'''
        self.assertEqual(99.0, Asset().depreciate(asset_value=100.0, maintenance=1.0))

    def test_depreciate_default_fx_maintenance_lt_required_maintenance_returns_accelerated_value(self):
        '''Test that the default depreciation function with maintenance < required maintenance returns 1.1 year of depreciation on default schedule.'''
        self.assertEqual(98.9, Asset().depreciate(asset_value=100.0, maintenance=0.9))

    def test_depreciate_default_fx_maintenance_eq_0_returns_max_accelerated_value(self):
        '''Test that the default depreciation function with no maintenance returns 2 year of depreciation on default schedule.'''
        self.assertEqual(98.0, Asset().depreciate(asset_value=100.0, maintenance=0.0))

    def test_depreciate_default_fx_maintenance_gt_required_maintenance_returns_recap_value(self):
        '''Test that the default depreciation function with maintenance > required_maintenance return 1 year of depreciation on default schedule with recapitalization.'''
        self.assertEqual(99.1, Asset().depreciate(asset_value=100.0, maintenance=1.1))

    def test_depreciate_default_fx_maintenance_gt_required_maintenance_and_max_recap_returns_initial_value(self):
        '''Test that the default depreciation function with maintenance > required_maintenance and max recap returns intial value.'''
        self.assertEqual(Asset().initial_value, Asset().depreciate(asset_value=100.0, maintenance=2.0))

    def test_depreciate_default_fx_maintenance_gt_required_maintenance_and_gt_max_recap_returns_initial_value(self):
        '''Test that the default depreciation function with maintenance > required_maintenance and more than max recap returns intial value.'''
        self.assertEqual(Asset().initial_value, Asset().depreciate(asset_value=100.0, maintenance=2.1))

    def test_depreciate_default_fx_at_last_scheduled_value_maintenance_eq_required_maintenance_returns_salvage_value(self):
        '''Test that the default depreciation function asset value scheduled to equal salavage value returns salvage value.'''
        self.assertEqual(Asset().salvage_value, Asset().depreciate(asset_value=1.0, maintenance=1.0))

    def test_depreciate_default_fx_at_last_scheduled_value_maintenance_lt_required_maintenance_returns_salvage_value(self):
        '''Test that the default depreciation function asset value scheduled to equal salavage value returns salvage value.'''
        self.assertEqual(Asset().salvage_value, Asset().depreciate(asset_value=1.0, maintenance=0.9))

    def test_depreciate_default_fx_at_last_scheduled_value_maintenance_gt_required_maintenance_returns_salvage_value(self):
        '''Test that the default depreciation function asset value scheduled to equal salavage value returns salvage value.'''
        self.assertAlmostEqual(0.1, Asset().depreciate(asset_value=1.0, maintenance=1.1))

    def test_shadow_value_max_portion_lt_0_raises_value_error(self):
        '''Test that the shadow_value function raises a ValueError when max_portion_error < 0.'''
        with self.assertRaises(ValueError):
            Asset().shadow_value(1.0, 1.0, 0.0, max_portion_error=-0.1)

    def test_shadow_value_max_portion_gt_1_raises_value_error(self):
        '''Test that the shadow_value function raises a ValueError when max_portion_error > 1.'''
        with self.assertRaises(ValueError):
            Asset().shadow_value(1.0, 1.0, 0.0, max_portion_error=1.1)

    def test_shadow_value_maintenance_eq_0_returns_last_estimate_eq_initial_value_returns_ge_90_le_intial_value(self):
        '''Test that the shadow_value function returns a value between 90% and 100% of the initial value when maintenance = 0 and last_estimate = initial_value.'''
        self.assertTrue(90.0 <= Asset().shadow_value(100.0, 100.0, 0.0) <= 100.0)

    def test_shadow_value_maintenance_eq_0_returns_last_estimate_eq_50_returns_ge_40_le_60(self):
        '''Test that the shadow_value function returns a value between 40% and 60% of the last estimate when maintenance = 0 and last_estimate = 50.'''
        self.assertTrue(40.0 <= Asset().shadow_value(50.0, 50.0, 0.0) <= 60.0)

    def test_shadow_value_maintenance_eq_0_returns_last_estimate_eq_0_returns_ge_0_le_10(self):
        '''Test that the shadow_value function returns a value between 0% and 10% of the last estimate when maintenance = 0 and last_estimate = 0.'''
        self.assertTrue(0.0 <= Asset().shadow_value(0.0, 0.0, 0.0) <= 10.0)

    def test_shadow_value_maintenance_eq_1_returns_last_estimate(self):
        '''Test that the shadow_value function returns the last estimate when maintenance = 1.'''
        self.assertEqual(50.0, Asset().shadow_value(50.0, 50.0, 1.0))

    def test_shadow_value_maintenance_eq_50percent_required_maintenance_returns_last_estimate_plus_or_minus_5percent(self):
        '''Test that the shadow_value function returns the last estimate plus or minus 5% when maintenance = 50% of required maintenance.'''
        self.assertTrue(45.0 <= Asset().shadow_value(50.0, 50.0, 0.5) <= 55.0)

    def test_shadow_value_maintenance_recap_gt_error_returns_actual_value(self):
        '''Test that the shadow_value function returns the actual value when recapitalization > error.'''
        self.assertEqual(40.0, Asset().shadow_value(50.0, 40.0, 11.0))

    def test_shadow_value_maintenance_recap_ls_error_narrows_overestimate_by_recap(self):
        '''Test that the shadow_value function narrows the value overestimate by the recapitalization amount when recapitalization < error.'''
        self.assertEqual(49.0, Asset().shadow_value(50.0, 40.0, 2.0))

    def test_shadow_value_maintenance_recap_ls_error_narraows_underestimate_by_recap(self):
        '''Test that the shadow_value function narrows the value underestimate by the recapitalization amount when recapitalization < error.'''
        self.assertEqual(51.0, Asset().shadow_value(50.0, 60.0, 2.0))

    def test_portion_remaining_asset_value_eq_initial_value_returns_1(self):
        '''Test that the portion_remaining function returns 1 when asset_value = initial_value.'''
        self.assertEqual(1.0, Asset().portion_remaining(Asset().initial_value))

    def test_portion_remaining_asset_value_eq_salvage_value_returns_0(self):
        '''Test that the portion_remaining function returns 0 when asset_value = salvage_value.'''
        self.assertEqual(0.0, Asset().portion_remaining(Asset().salvage_value))

    def test_portion_remaining_asset_value_gt_initial_value_raises_value_error(self):
        '''Test that the portion_remaining function raises a ValueError when asset_value > initial_value.'''
        with self.assertRaises(ValueError):
            Asset().portion_remaining(Asset().initial_value + 1.0)

    def test_portion_remaining_asset_value_lt_salvage_value_raises_value_error(self):
        '''Test that the portion_remaining function raises a ValueError when asset_value < salvage_value.'''
        with self.assertRaises(ValueError):
            Asset().portion_remaining(Asset().salvage_value - 1.0)

    def test_portion_remaining_default_asset_with_value_eq_half_initial_value_returns_0dot5(self):
        '''Test that the portion_remaining function returns 1/2 when asset_value = 1/2 * initial_value.'''
        self.assertEqual(0.5, Asset().portion_remaining(Asset().initial_value / 2.0))
