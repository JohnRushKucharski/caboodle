'''Tests for the reservoir module.'''
# pylint: disable=line-too-long
import unittest

from model.asset import Asset
import model.reservoir as res

class TestBasicGate(unittest.TestCase):
    '''Tests for the basic_gate function.'''
    def test_basic_gate_volume_lt_location_returns_0(self):
        '''Test that the basic_gate function returns 0 when volume < location.'''
        self.assertEqual(res.ReleaseRange(0.0, 0.0), res.basic_gate(res.BasicOutlet(), 0.0))

    def test_basic_gate_volume_eq_location_returns_0(self):
        '''Test that the basic_gate function returns 0 when volume = location.'''
        self.assertEqual(res.ReleaseRange(0.0, 0.0), res.basic_gate(res.BasicOutlet(location=1.0), 1.0))

    def test_basic_gate_volume_gt_location_returns_min_max(self):
        '''Test that the basic_gate function returns min and max when volume > location.'''
        self.assertEqual(res.ReleaseRange(0.0, 1.0), res.basic_gate(res.BasicOutlet(), 1.0))

class TestBasicOutlet(unittest.TestCase):
    '''Tests for the BasicOutlet class.'''
    def test_location_default(self):
        '''Test that the default location is 0.0.'''
        self.assertEqual(0.0, res.BasicOutlet().location)

    def test_design_range_default(self):
        '''Test that the default release range is (0.0, inf).'''
        self.assertEqual((0.0, float('inf')), res.BasicOutlet().design_range)

    def test_release_range_functional_range_constrained_by_volume(self):
        '''Test that the release range is constrained by the reservoir volume.'''
        self.assertEqual((0.0, 10.0), res.BasicOutlet().release_range(10.0))

    def test_release_range_functional_range_constrained_neg_volume_over(self):
        '''Test that the release range is constrained by the reservoir volume < location.'''
        self.assertEqual((0.0, 0.0), res.BasicOutlet(location=5.0).release_range(4.0))

class TestBasicGateWithFailure(unittest.TestCase):
    '''Tests for the basic_gate_with_failure function.'''
    def test_basic_gate_with_failure_volume_lt_location_returns_0(self):
        '''Test that the basic_gate_with_failure function returns 0 when volume < location.'''
        self.assertEqual(res.ReleaseRange(0.0, 0.0), res.basic_gate_with_failure(res.OutletAsset(Asset()), 0.0))

    def test_basic_gate_with_failure_volume_eq_location_returns_0(self):
        '''Test that the basic_gate_with_failure function returns 0 when volume = location.'''
        self.assertEqual(res.ReleaseRange(0.0, 0.0), res.basic_gate_with_failure(res.OutletAsset(Asset(), location=1.0), 1.0))

    def test_basic_gate_with_failure_volume_gt_location_returns_min_max(self):
        '''Test that the basic_gate_with_failure function returns min and max when volume > location.'''
        self.assertEqual(res.ReleaseRange(0.0, 1.0), res.basic_gate_with_failure(res.OutletAsset(Asset()), 1.0))

class TestUpdateCondition(unittest.TestCase):
    '''Tests for the update_condition function.'''
    def test_update_condition_none_asset_value_gt_salvage_value_returns_same_outlet(self):
        '''Test that the update_condition function returns same outlet when asset value > salvage value.'''
        outlet = res.OutletAsset(Asset())
        self.assertEqual(outlet, res.update_condition(outlet, 100.0, 1.0))

    def test_update_condition_previous_state_neq_none_returns_same_outlet(self):
        '''Test that the update_condition function returns same outlet when failure_state is not NONE.'''
        outlet = res.OutletAsset(Asset(), failure_state=res.FailureState.OPEN)
        self.assertEqual(outlet, res.update_condition(outlet, 100.0, 1.0))

    def test_update_condition_asset_value_eq_salvage_value_and_volume_gt_location_returns_outlet_with_state_eq_open(self):
        '''Test that the update_condition function returns outlet with failure_state eq OPEN when asset value = salvage value and volume > location.'''
        self.assertEqual(res.FailureState.OPEN, res.update_condition(res.OutletAsset(Asset()), 0.0, 1.0).failure_state)

    def test_update_condition_asset_value_eq_salvage_value_and_volume_eq_location_returns_outlet_with_state_eq_closed(self):
        '''Test that the update_condition function returns outlet with failure_state eq CLOSED when asset value = salvage value and volume = location.'''
        self.assertEqual(res.FailureState.CLOSED, res.update_condition(res.OutletAsset(Asset()), 0.0, 0.0).failure_state)

    def test_update_condition_asset_value_eq_salvage_value_and_volume_lt_location_returns_outlet_with_state_eq_closed(self):
        '''Test that the update_condition function returns outlet with failure_state eq CLOSED when asset value = salvage value and volume < location.'''
        self.assertEqual(res.FailureState.CLOSED, res.update_condition(res.OutletAsset(Asset(), location=1.0), 0.0, 0.5).failure_state)

class TestOutletAsset(unittest.TestCase):
    '''Tests for the OutletAsset class.'''
    def test_location_default(self):
        '''Test that the default location is 0.0.'''
        self.assertEqual(0.0, res.OutletAsset(asset=Asset()).location)

    def test_failure_state_default(self):
        '''Test that the default failure state is NONE.'''
        self.assertEqual(res.FailureState.NONE, res.OutletAsset(asset=Asset()).failure_state)

    def test_design_range_default(self):
        '''Test that the default release range is (0.0, inf).'''
        self.assertEqual((0.0, float('inf')), res.OutletAsset(asset=Asset()).design_range)

    def test_release_range_functional_range_constrained_by_volume(self):
        '''Test that the release range is constrained by the reservoir volume.'''
        self.assertEqual((0.0, 10.0), res.OutletAsset(asset=Asset()).release_range(10.0))

    def test_release_range_functional_range_constrained_by_closed_failure_state(self):
        '''Test that the release range is constrained for outlet in failed closed state.'''
        self.assertEqual((0.0, 0.0), res.OutletAsset(asset=Asset(), failure_state=res.FailureState.CLOSED).release_range(10.0))

    def test_release_range_functional_range_constrained_by_open_failure_state(self):
        '''Test that the release range is constrained for outlet in failed open state.'''
        self.assertEqual((10.0, 10.0), res.OutletAsset(asset=Asset(), failure_state=res.FailureState.OPEN).release_range(10.0))

class TestFormatOutlets(unittest.TestCase):
    '''Tests for the format_outlets function.'''
    def test_format_outlets_empty_returns_empty(self):
        '''Test that the format_outlets function returns an empty tuple when given an empty list.'''
        self.assertEqual((), res.format_outlets([]))

    def test_format_outlets_one_outlet_no_name_returns_outlet_with_expected_name(self):
        '''Test that the format_outlets function returns a tuple with one outlet with expected name when given an outlet with no name.'''
        self.assertEqual((res.BasicOutlet(name='outlet@0'),), res.format_outlets((res.BasicOutlet(),)))

    def test_format_outlets_one_outlet_with_name_returns_same_name_outlet(self):
        '''Test that the format_outlets function returns a tuple with one outlet with input when given an outlet with that name.'''
        self.assertEqual((res.BasicOutlet(name='spillway@0'),), res.format_outlets((res.BasicOutlet(name='spillway'),)))

    def test_format_outlets_two_outlets_same_name_returns_outlets_with_expected_names(self):
        '''Test that the format_outlets function returns a tuple with two outlets with expected names when given two outlets with the same name.'''
        expected = (res.BasicOutlet(name='spillway@0'), res.BasicOutlet(name='spillway2@0'))
        actual = res.format_outlets((res.BasicOutlet(name='spillway'), res.BasicOutlet(name='spillway')))
        self.assertEqual(expected, actual)

    def test_format_outlets_returns_new_tuple_with_input_unchanged(self):
        '''Test that the format_outlets function returns a new tuple with input unchanged.'''
        input_outlets = (res.BasicOutlet(name='spillway'),)
        self.assertEqual((res.BasicOutlet(name='spillway@0'),), res.format_outlets(input_outlets))
        self.assertEqual((res.BasicOutlet(name='spillway'),), input_outlets)

class TestOutletSorter(unittest.TestCase):
    '''Tests for the outlet_sorter function.'''
    def test_outlet_sorter_empty_returns_empty(self):
        '''Test that the outlet_sorter function returns an empty tuple when given an empty list.'''
        self.assertEqual((), res.outlet_sorter([]))

    def test_outlet_sorter_default_returns_sorted_on_location(self):
        '''Test that the outlet_sorter function returns a tuple with outlets reverse sorted on location when given a list of outlets.'''
        self.assertEqual((res.BasicOutlet(location=1.0), res.BasicOutlet(location=0.0)),
                         res.outlet_sorter((res.BasicOutlet(location=0.0), res.BasicOutlet(location=1.0))))

    def test_outlet_sorter_duplicate_outlet_returns_tuple(self):
        '''Test that the outlet_sorter function returns a tuple with outlets reverse sorted on location when given a list of outlets.'''
        basic_outlet = res.BasicOutlet(location=0.0)
        self.assertEqual((basic_outlet, basic_outlet), res.outlet_sorter((basic_outlet, basic_outlet)))

class TestReservoir(unittest.TestCase):
    '''Tests for the Reservoir class.'''
    def test_capacity_default(self):
        '''Test that the default capacity is 0.0.'''
        self.assertEqual(1.0, res.Reservoir().capacity)

    def test_outlets_default(self):
        '''Test that the default outlets is basic outlet.'''
        self.assertEqual((res.BasicOutlet(name='outlet@1', location=1.0),), res.Reservoir().outlets)

    def test_format_outlets_sorts_by_location_then_name(self):
        '''Test that the format_outlets function returns a tuple with outlets sorted by location then name.'''
        expected = (res.BasicOutlet(name='a@0', location=0.0),
                    res.BasicOutlet(name='b@0', location=0.0),
                    res.BasicOutlet(name='a@1', location=1.0),
                    res.BasicOutlet(name='b@1', location=1.0))
        actual = res.Reservoir(outlets=
                               (res.BasicOutlet(name='b', location=1.0),
                                res.BasicOutlet(name='b', location=0.0),
                                res.BasicOutlet(name='a', location=1.0),
                                res.BasicOutlet(name='a', location=0.0))).outlets
        self.assertEqual(expected, actual)

    def test_operate_default_reservoir_volume_eq_0_returns_tuple_tuple_with_outlet_spill_and_storage_eq_0(self):
        '''Test that the operate function returns a tuple with one named tuple with storage eq 0 and outlet eq 0 when given a reservoir with storage eq 0.'''
        self.assertEqual((0,0,0), res.Reservoir().operate(0.0))

    def test_operate_default_reservoir_storage_eq_0_returns_tuple_named_tuple_with_storage_eq_0_and_outlet_eq_0(self):
        '''Test that the operate function returns a tuple with one named tuple with storage eq 0 and outlet eq 0 when given a reservoir with storage eq 0.'''
        self.assertEqual((0,0,0), res.Reservoir().operate(0.0))

    def test_operate_default_reservoir_storage_eq_1_returns_tuple_named_tuple_with_storage_eq_1_and_outlet_eq_0(self):
        '''Test that the operate function returns a tuple with one named tuple with storage eq 1 and outlet eq 0 when given a reservoir with storage eq 1.'''
        self.assertEqual((0,0,1), res.Reservoir().operate(1.0))

    def test_operate_default_reservoir_storage_eq_2_returns_tuple_named_tuple_with_storage_eq_1_and_outlet_eq_1(self):
        '''Test that the operate function returns a tuple with one named tuple with storage eq 1 and outlet eq 1 when given a reservoir with storage eq 2.'''
        self.assertEqual((1,0,1), res.Reservoir().operate(2.0))

    def test_operate_gate_max_release_eq_0dot5_reservoir_storage_eq_2_returns_tuple_named_tuple_with_storage_eq_1_and_outlet_eq_0dot5_spilled_release_eq_0dot5(self):
        '''Test that the operate function returns a tuple with one named tuple with storage eq 1 outlet eq 0.5 and spilled release eq 0.5 when given a reservoir with storage eq 2 and gate max release eq 0.5.'''
        self.assertEqual((0.5, 0.5, 1.0), res.Reservoir(outlets=(res.BasicOutlet(location=1.0, design_range=res.ReleaseRange(0.0, 0.5)),)).operate(2.0))

    def test_operate_outletasset_max_release_eq_0dot5_reservoir_storage_eq_2_returns_tuple_named_tuple_with_storage_eq_1_and_outlet_eq_0dot5_spilled_release_eq_0dot5(self):
        '''Test that the operate function returns a tuple with one named tuple with storage eq 1 outlet eq 0.5 and spilled release eq 0.5 when given a reservoir with storage eq 2 and outlet asset max release eq 0.5.'''
        self.assertEqual((0.5, 0.5, 1.0), res.Reservoir(outlets=(res.OutletAsset(asset=Asset(), location=1.0, design_range=res.ReleaseRange(0.0, 0.5)),)).operate(2.0))

    def test_operate_outletasset_failed_closed_storage_at_capacity_returns_no_release_only_storage(self):
        '''Test that the operate function returns a failed closed outlet, generates no release, only storage.'''
        self.assertEqual((0,0,1), res.Reservoir(outlets=(res.OutletAsset(asset=Asset(), location=0.0, failure_state=res.FailureState.CLOSED),)).operate(1.0))

    def test_operate_outletasset_failed_closed_storage_gt_capacity_returns_no_release_storage_eq_capacity_spill_eq_1(self):
        '''Test that the operate function returns a failed closed outlet, generates no release, only storage and spill.'''
        self.assertEqual((0, 1, 1), res.Reservoir(outlets=(res.OutletAsset(asset=Asset(), location=0.0, failure_state=res.FailureState.CLOSED),)).operate(2.0))

    def test_operate_multiple_outlets_returns_outputs_in_expected_order(self):
        '''Test that the operate function returns a tuple with named tuples with storage eq 1 outlet eq 0.5 and spilled release eq 0.5 when given a reservoir with storage eq 2 and gate max release eq 0.5.'''
        actual = res.Reservoir(outlets=
                               (res.BasicOutlet(name='b', location=1.0),
                                res.BasicOutlet(name='b', location=0.0),
                                res.BasicOutlet(name='a', location=1.0),
                                res.BasicOutlet(name='a', location=0.0))).operate(2.0)
        expected = (1.0, 0.0, 1.0, 0.0, 0.0, 0.0)
        self.assertEqual(expected, actual)

    def test_multiple_outlets_with_retriction_returns_outputs_in_expected_order(self):
        '''Complicated assortment of basic and asset outlets with flow restrictions returns expected outputs.'''
        actual = res.Reservoir(outlets=
                               (res.OutletAsset(Asset(), name='b', location=1.0, failure_state=res.FailureState.OPEN, design_range=res.ReleaseRange(0.0, 0.5)),
                                res.BasicOutlet(name='b', location=0.0, design_range=res.ReleaseRange(0.0, 0.5)),
                                res.OutletAsset(Asset(), name='a', location=1.0, failure_state=res.FailureState.CLOSED),
                                res.BasicOutlet(name='a', location=0.0, design_range=res.ReleaseRange(0, 0)))).operate(3.0)
        expected = (0.0, 0.5, 0.0, 0.5, 1.0, 1.0)
        self.assertEqual(expected, actual)
