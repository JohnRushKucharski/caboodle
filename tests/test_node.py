'''
Unit tests for the node module.
'''
# pylint: disable=line-too-long
import unittest
#from pathlib import Path

from model.node import Tag, Inflow, Storage, Outlet, DataNode

class TestDataInflow(unittest.TestCase):
    '''
    Unit tests for the Inflow class.
    '''
    def test_tag(self):
        '''Test that the inflow tag is Tag.INFLOW.'''
        self.assertEqual(Tag.INFLOW, Inflow(data=[1, 2, 3]).tag)

    def test_default_name(self):
        '''Test that the inflow name is Tag.INFLOW.value.'''
        self.assertEqual(Tag.INFLOW.value, Inflow(data=[1, 2, 3]).name)

    def test_senders(self):
        '''Test that inflow has no senders are correct.'''
        self.assertEqual({}, Inflow(data=[1, 2, 3]).senders())

    def test_receive(self):
        '''Test that inflow receives first value in data.'''
        self.assertEqual(1, Inflow(data=[1, 2, 3]).receive())

    def test_receive_2(self):
        '''Test that inflow receives second value in data.'''
        inflow = Inflow(data=[1, 2, 3])
        inflow.receive()  # first inflow recieved
        self.assertEqual(2, inflow.receive())  # second inflow recieved

    def test_send(self):
        '''Test that inflow sends the first value in data.'''
        self.assertEqual(1, Inflow([1, 2, 3]).send())

    def test_send_2(self):
        '''Test that inflow sends the second value in data.'''
        inflow = Inflow([1, 2, 3])
        inflow.receive()  # first inflow recieved
        self.assertEqual(2, inflow.send())  # second inflow sent (send calls recieve).  # noqa: E501

class TestStorage(unittest.TestCase):
    '''Tests the Storage class.'''
    def test_tag(self):
        '''Test that the default storage node tag is Tag.STORAGE.'''
        self.assertEqual(Tag.STORAGE, Storage().tag)

    def test_default_name(self):
        '''Test that the default storage node name is Tag.STORAGE.value.'''
        self.assertEqual(Tag.STORAGE.value, Storage().name)

    def test_default_senders(self):
        '''Test that the default storage node has no senders.'''
        self.assertEqual(set(), Storage().senders)

    def test_add_sender(self):
        '''Test that the storage node can add a sender.'''
        storage = Storage()
        sender = Inflow(data=[1, 2, 3])
        storage.add_sender(sender)
        self.assertEqual({sender}, storage.senders)

    def test_add_sender_twice_raises_value_error(self):
        '''Test that the storage node can add a specific sender twice and only has one sender.'''
        sender = Inflow(data=[1, 2, 3])
        storage = Storage(senders={sender})
        with self.assertRaises(ValueError):
            storage.add_sender(sender)

    def test_remove_sender(self):
        '''Test that the storage node can remove a sender.'''
        sender = Inflow(data=[1, 2, 3])
        storage = Storage(senders={sender})
        storage.remove_sender(sender)
        self.assertEqual(set(), storage.senders)

    def test_remove_sender_twice_raises_key_error(self):
        '''Test that the storage node cannot remove the same sender twice.'''
        sender = Inflow(data=[1, 2, 3])
        storage = Storage(senders={sender})
        storage.remove_sender(sender)
        with self.assertRaises(KeyError):
            storage.remove_sender(sender)

    def test_remove_absent_sender_raises_key_error(self):
        '''Test that the storage node cannot remove an absent sender.'''
        storage = Storage(senders={Inflow(data=[1, 2, 3])})
        with self.assertRaises(KeyError):
            storage.remove_sender(Inflow(data=[1, 2, 3]))

    def test_receive_no_senders_returns_0(self):
        '''Test that the storage node receives 0 from no senders.'''
        self.assertEqual(0, Storage().receive())

    def test_receive_1_sender_returns_first_inflow(self):
        '''Test that the storage node receives the first inflow from a sender.'''
        self.assertEqual(1, Storage(senders={Inflow(data=[1, 2, 3])}).receive())

    def test_receive_2_senders_returns_summed_first_inflows(self):
        '''Test that the storage node receives the sum of first inflows from senders.'''
        self.assertEqual(2.0, Storage(senders={Inflow(data=[1, 2, 3]), Inflow(data=[1, 2, 3])}).receive())

    def test_send_no_senders_returns_0(self):
        '''Test that the storage node sends 0 to no senders.'''
        self.assertEqual(0.0, Storage().send())

    def test_send_sender_first_inflow_lt_outlet_location_sender_returns_0(self):
        '''Test that the storage node first inflow less than outlet location returns 0.'''
        self.assertEqual(0.0, Storage(senders={Inflow(data=[1, 2, 3])}).send())

    def test_send_2_senders_returns_summed_first_inflows_gt_outlet_location_returns_volume_over_outlet(self):
        '''Test that the storage node sum of first inflows from senders over outlet location returns volume over location.'''
        self.assertEqual(1.0, Storage(senders={Inflow(data=[1, 2, 3]), Inflow(data=[1, 2, 3])}).send())

    def test_storage(self):
        '''Test that the storage node stores the first output.'''
        self.assertEqual(1, Storage().storage((1,)))


class TestOutlet(unittest.TestCase):
    '''
    Unit tests for the Outlet class.
    '''
    def test_tag(self):
        '''Test that the outlet tag is Tag.OUTLET.'''
        self.assertEqual(Tag.OUTLET, Outlet().tag)

    def test_default_name(self):
        '''Test that the outlet name is Tag.OUTLET.value.'''
        self.assertEqual(Tag.OUTLET.value, Outlet().name)

    def test_default_senders(self):
        '''Test that the outlet has no senders.'''
        self.assertEqual(set(), Outlet().senders)

    def test_add_sender(self):
        '''Test that the outlet can add a sender.'''
        outlet = Outlet()
        sender = Inflow(data=[1, 2, 3])
        outlet.add_sender(sender)
        self.assertEqual({sender}, outlet.senders)

    def test_add_sender_twice_raises_value_error(self):
        '''Test that the outlet can add a sender twice and only has one sender.'''
        sender = Inflow(data=[1, 2, 3])
        outlet = Outlet(senders={sender})
        with self.assertRaises(ValueError):
            outlet.add_sender(sender)

    def test_remove_sender(self):
        '''Test that the outlet can remove a sender.'''
        sender = Inflow(data=[1, 2, 3])
        outlet = Outlet(senders={sender})
        outlet.remove_sender(sender)
        self.assertEqual(set(), outlet.senders)

    def test_remove_sender_twice_raises_key_error(self):
        '''Test that the outlet can remove a sender twice.'''
        sender = Inflow(data=[1, 2, 3])
        outlet = Outlet(senders={sender})
        outlet.remove_sender(sender)
        with self.assertRaises(KeyError):
            outlet.remove_sender(sender)

    def test_remove_absent_sender_raises_key_error(self):
        '''Test that the outlet can remove a sender twice.'''
        outlet = Outlet(senders={Inflow(data=[1, 2, 3])})
        sender = Inflow(data=[1, 2, 3])
        with self.assertRaises(KeyError):
            outlet.remove_sender(sender)

    def test_receive_no_senders_returns_0(self):
        '''Test that the outlet receives the sum of inflows.'''
        self.assertEqual(0, Outlet().receive())

    def test_receive_1_sender_returns_first_inflow(self):
        '''Test that the outlet receives the sum of inflows.'''
        self.assertEqual(1, Outlet(senders={Inflow(data=[1, 2, 3])}).receive())

    def test_receive_2_senders_returns_summed_first_inflows(self):
        '''Test that the outlet receives the sum of inflows.'''
        self.assertEqual(2.0, Outlet(senders={Inflow(data=[1, 2, 3]), Inflow(data=[1, 2, 3])}).receive())

    def test_send_no_senders_returns_0(self):
        '''Test that the outlet sends the sum of inflows.'''
        self.assertEqual(0, Outlet().send())

    def test_send_1_sender_returns_first_inflow(self):
        '''Test that the outlet sends the sum of inflows.'''
        self.assertEqual(1, Outlet(senders={Inflow(data=[1, 2, 3])}).send())

    def test_send_2_senders_returns_summed_first_inflows(self):
        '''Test that the outlet sends the sum of inflows.'''
        self.assertEqual(2.0, Outlet(senders={Inflow(data=[1, 2, 3]), Inflow(data=[1, 2, 3])}).send())

class TestDataNode(unittest.TestCase):
    '''Tests the DataNode class.'''
    # def __init__(self):
    #     super().__init__()
    #     Path.mkdir(Path.cwd() / 'tests' / 'data', exist_ok=True)

    def test_send_simple_inflow_node_records_first_inflow(self):
        '''Test that the DataNode class can be instantiated, and inflow node records data.'''
        node = DataNode(node=Inflow(data=[1,2,3]), logpath='')
        node.send()
        self.assertEqual([1], node.log.data)

    def test_send_default_storage_node_records_data_from_first_timestep(self):
        '''Test that the DataNode class can be instantiated, and storage node records data from first timestep.'''
        node = DataNode(node=Storage(senders={Inflow([1, 2, 3])}), logpath='')
        node.send()
        # [(inflow, outlets..., spill, storage)]
        self.assertEqual([(1.0, 0.0, 0.0, 1.0)], node.log.data)
