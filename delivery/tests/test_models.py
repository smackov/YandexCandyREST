"""
The tests of models.
"""

from datetime import datetime, time

from django.test import TestCase
from django.core.exceptions import FieldError

from ..models import (
    Courier, Region, WorkingHours, Order, DeliveryHours, AssignedOrderSet
)


class CourierTestCase(TestCase):
    """
    The test case for Courier model.
    """

    def setUp(self):
        # Create regions: 1, 2, 3, 4, 5
        for region_number in range(1, 6):
            region = Region.objects.create(id=region_number)
            setattr(self, f'region_{region_number}', region)

        # Create courier
        self.courier = Courier.objects.create(
            courier_id=1, courier_type='foot')
        self.courier.regions.set([1, 2, 3])

        # Create working hours
        self.working_hours_1 = WorkingHours.objects.create(
            start=time(hour=9), end=time(hour=12), courier=self.courier)
        self.working_hours_2 = WorkingHours.objects.create(
            start=time(hour=18), end=time(hour=20), courier=self.courier)

    def test_regions(self):
        courier_regions = list(self.courier.regions.all())
        expected_regions = [self.region_1, self.region_2, self.region_3]
        self.assertEqual(courier_regions, expected_regions)

    def test_access_from_region_by_related_name(self):
        courier = self.region_1.couriers.all()[0]
        self.assertEqual(courier, self.courier)

    def test_str_function(self):
        excpected_str = 'Courier(id=1, type=foot, regions=[1, 2, 3])'
        self.assertEqual(str(self.courier), excpected_str)

    def test_load_capacity_when_foot_type(self):
        self.assertEqual(self.courier.load_capacity, 10)

    def test_load_capacity_when_bike_type(self):
        self.courier.courier_type = 'bike'
        self.assertEqual(self.courier.load_capacity, 15)

    def test_load_capacity_when_car_type(self):
        self.courier.courier_type = 'car'
        self.assertEqual(self.courier.load_capacity, 50)

    def test_load_capacity_when_unknown_type(self):
        self.courier.courier_type = 'not'
        excpected_msg = ("The 'courier_type' field of Courier with courier_id=1 contains "
                         "the unresolved value='not' that absents in COURIER_LOAD_CAPACITY")
        with self.assertRaisesMessage(FieldError, excpected_msg):
            self.courier.load_capacity


class CourierAssignOrdersTestCase(TestCase):
    """
    The test case for some methods of Courier model:

    - assign_orders(),
    - find_matching_orders().
    """

    def setUp(self):
        # Create regions: 1, 2, 3, 4, 5
        for region_number in range(1, 6):
            region = Region.objects.create(id=region_number)
            setattr(self, f'region_{region_number}', region)

        # Create courier
        self.courier = Courier.objects.create(
            courier_id=1, courier_type='foot')
        self.courier.regions.set([1])

        # Create working hours
        self.working_hours_1 = WorkingHours.objects.create(
            start=time(hour=9), end=time(hour=12), courier=self.courier)
        self.working_hours_2 = WorkingHours.objects.create(
            start=time(hour=18), end=time(hour=20), courier=self.courier)

        # Order data
        self.order_data_1 = {
            'order_id': 1,
            'weight': 4,
            'region': self.region_1,
        }
        self.order_data_2 = {
            'order_id': 2,
            'weight': 3,
            'region': self.region_2,
        }
        self.order_1 = Order.objects.create(**self.order_data_1)
        self.order_2 = Order.objects.create(**self.order_data_2)

        # Create delivery hours
        self.delivery_hours_1 = DeliveryHours.objects.create(
            start=time(hour=9), end=time(hour=12), order=self.order_1)
        self.delivery_hours_2 = DeliveryHours.objects.create(
            start=time(hour=15), end=time(hour=20), order=self.order_2)

        # Create order set
        self.order_set = AssignedOrderSet.objects.create(
            courier=self.courier, courier_type=self.courier.courier_type)

    def test_assign_orders_when_current_set_of_orders_isnt_empty(self):
        self.order_set.notstarted_orders.set([self.order_1, self.order_2])
        self.courier.current_set_of_orders = self.order_set
        self.courier.save()
        order_set = self.courier.assign_orders()
        self.assertEqual(order_set, self.order_set)

    def test_assign_orders_when_current_set_of_orders_is_empty(self):
        self.courier.current_set_of_orders = self.order_set
        self.courier.save()
        order_set = self.courier.assign_orders()
        self.assertNotEqual(order_set.id, self.order_set.id)
        self.assertEqual(order_set.courier, self.courier)
        self.assertEqual(order_set.courier_type, self.courier.courier_type)
        self.assertCountEqual(order_set.notstarted_orders.all(), [self.order_1])
        self.order_1.refresh_from_db()
        self.assertEqual(self.courier.current_set_of_orders, self.order_1.set_of_orders)

    def test_assign_orders_when_current_set_of_orders_not_exist(self):
        order_set = self.courier.assign_orders()
        self.assertNotEqual(order_set.id, self.order_set.id)
        self.assertEqual(AssignedOrderSet.objects.count(), 2)
        self.courier.save()
        self.assertEqual(self.courier.current_set_of_orders, order_set)
        self.order_1.refresh_from_db()
        self.assertEqual(self.courier.current_set_of_orders, self.order_1.set_of_orders)

    def test_assign_orders_when_current_set_of_orders_not_exist_and_not_matched_orders(self):
        self.order_1.weight = 40
        self.order_1.save()
        order_set = self.courier.assign_orders()
        self.assertIsNone(order_set)
        self.assertIsNone(self.courier.current_set_of_orders)

    def test_find_orders(self):
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0], self.order_1)

    def test_find_orders_weight_filter(self):
        self.order_1.weight = 10.01
        self.order_1.save()
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 0)

    def test_find_orders_weight_filter_when_equal(self):
        self.order_1.weight = 10
        self.order_1.save()
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0], self.order_1)

    def test_find_orders_region_filter(self):
        self.order_1.region = self.region_2
        self.order_1.save()
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 0)

    def test_find_orders_compete_time_filter(self):
        self.order_1.complete_time = datetime.now()
        self.order_1.save()
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 0)

    def test_find_orders_set_of_orders_filter(self):
        self.order_1.set_of_orders = self.order_set
        self.order_1.save()
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 0)

    def test_find_orders_delivery_hours_filter_lower_side(self):
        self.delivery_hours_1.delete()
        DeliveryHours.objects.create(
            start=time(hour=8), end=time(hour=9), order=self.order_1)
        DeliveryHours.objects.create(
            start=time(hour=17), end=time(hour=18), order=self.order_1)
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 0)
        DeliveryHours.objects.create(
            start=time(hour=8), end=time(hour=9, minute=1), order=self.order_1)
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 1)

    def test_find_orders_delivery_hours_filter_upper_side(self):
        self.delivery_hours_1.delete()
        DeliveryHours.objects.create(
            start=time(hour=12), end=time(hour=14), order=self.order_1)
        DeliveryHours.objects.create(
            start=time(hour=20), end=time(hour=21), order=self.order_1)
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 0)
        DeliveryHours.objects.create(
            start=time(hour=11, minute=59), end=time(hour=13), order=self.order_1)
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 1)

    def test_find_orders_delivery_hours_filter_outer_side(self):
        self.delivery_hours_1.delete()
        DeliveryHours.objects.create(
            start=time(hour=13), end=time(hour=14), order=self.order_1)
        DeliveryHours.objects.create(
            start=time(hour=21), end=time(hour=22), order=self.order_1)
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 0)

    def test_find_orders_delivery_hours_filter_inner_side(self):
        self.delivery_hours_1.delete()
        DeliveryHours.objects.create(
            start=time(hour=10), end=time(hour=11), order=self.order_1)
        DeliveryHours.objects.create(
            start=time(hour=19), end=time(hour=20), order=self.order_1)
        orders = self.courier.find_matching_orders()
        self.assertEqual(len(orders), 1)


class OrderTestCase(TestCase):
    """
    The test case for Order model.
    """

    def setUp(self):

        # Create regions with id=1, id=2
        self.region_1 = Region.objects.create(id=1)
        self.region_2 = Region.objects.create(id=2)

        # Order data
        self.order_data = {
            'order_id': 1,
            'weight': 11.11,
            'region': self.region_1,
        }
        self.order = Order.objects.create(**self.order_data)

        # Create delivery hours
        self.delivery_hours_1 = DeliveryHours.objects.create(
            start=time(hour=9), end=time(hour=12), order=self.order)
        self.delivery_hours_2 = DeliveryHours.objects.create(
            start=time(hour=15), end=time(hour=20), order=self.order)

    def test_str_function(self):
        excpected_str = 'Order (order_id=1, weight=11.11, region=1)'
        self.assertEqual(str(self.order), excpected_str)

    def test_order_id(self):
        self.assertEqual(self.order.order_id, self.order_data['order_id'])

    def test_regions(self):
        self.assertEqual(self.order.region, self.order_data['region'])
        self.assertEqual(Region.objects.count(), 2)

    def test_weight(self):
        self.assertEqual(self.order.weight, self.order_data['weight'])
        self.assertEqual(str(self.order.weight),
                         str(self.order_data['weight']))

    def test_int_weight(self):
        self.order.weight = 50
        self.order.save()
        self.assertEqual(self.order.weight, 50)
        self.assertEqual(str(self.order.weight), str(50))

    def test_delivery_hours_access_by_related_name(self):
        expected_delivery_hours = [
            self.delivery_hours_1, self.delivery_hours_2]
        self.assertCountEqual(
            self.order.delivery_hours.all(), expected_delivery_hours)
        self.assertEqual(self.order.delivery_hours.count(), 2)

    def test_access_from_region_by_related_name(self):
        order = self.region_1.orders.all()[0]
        self.assertEqual(order, self.order)


class RegionTestCase(TestCase):
    """
    The test case for Region model.
    """

    def setUp(self):
        self.region = Region.objects.create(id=1)

    def test_str_function(self):
        excpected_str = 'Region (1)'
        self.assertEqual(str(self.region), excpected_str)

    def test_repr_function(self):
        excpected_repr = str(self.region.id)
        self.assertEqual(repr(self.region), excpected_repr)


class WorkingHoursTestCase(TestCase):
    """
    The test case for WorkingHours model.

    It's the 'working_hours' field for Courier model.
    """

    def setUp(self):
        # Create courier
        self.courier_1 = Courier.objects.create(
            courier_id=1, courier_type='foot')
        self.courier_2 = Courier.objects.create(
            courier_id=2, courier_type='foot')

        # Create working hours
        self.working_hours_1 = WorkingHours.objects.create(
            start=time(hour=9), end=time(hour=12, minute=20), courier=self.courier_1)
        self.working_hours_2 = WorkingHours.objects.create(
            start=time(hour=18), end=time(hour=20), courier=self.courier_1)
        self.working_hours_3 = WorkingHours.objects.create(
            start=time(hour=18), end=time(hour=20), courier=self.courier_2)

    def test_str_function(self):
        excpected_str = '09:00-12:20'
        self.assertEqual(str(self.working_hours_1), excpected_str)

    def test_access_to_working_hours_from_courier_by_related_name(self):
        excpected_working_hours = [self.working_hours_1, self.working_hours_2]
        self.assertCountEqual(
            self.courier_1.working_hours.all(), excpected_working_hours)


class DeliveryHoursTestCase(TestCase):
    """
    The test case for DeliveryHours model.

    It's the 'delivery_hours' field for Order model.
    """

    def setUp(self):

        # Order data
        self.region_1 = Region.objects.create(id=1)
        self.order_data = {
            'order_id': 1,
            'weight': 11.11,
            'region': self.region_1,
        }
        self.order = Order.objects.create(**self.order_data)

        # Create delivery hours
        self.delivery_hours_1 = DeliveryHours.objects.create(
            start=time(hour=9), end=time(hour=12, minute=20), order=self.order)
        self.delivery_hours_2 = DeliveryHours.objects.create(
            start=time(hour=15), end=time(hour=20), order=self.order)

    def test_str_function(self):
        excpected_str = '09:00-12:20'
        self.assertEqual(str(self.delivery_hours_1), excpected_str)

    def test_access_to_delivery_hours_from_order_by_related_name(self):
        excpected_delivery_hours = [
            self.delivery_hours_1, self.delivery_hours_2]
        self.assertCountEqual(
            self.order.delivery_hours.all(), excpected_delivery_hours)


class AssignedOrderSetTestCase(TestCase):
    """
    The test case for AssignOrderSet model.
    """

    def setUp(self):
        # Create courier
        self.courier = Courier.objects.create(
            courier_id=1, courier_type='foot')

        # Create region and order
        self.region = Region.objects.create(id=1)
        self.order_data = {
            'order_id': 1,
            'weight': 10,
            'region': self.region,
        }
        self.order = Order.objects.create(**self.order_data)

        # Create order set
        self.order_set = AssignedOrderSet.objects.create(
            courier=self.courier, courier_type=self.courier.courier_type)
        self.order_set.notstarted_orders.add(self.order)

    def test_str_function(self):
        excpected_str = 'Order set (id=1, courier_id=1)'
        self.assertEqual(str(self.order_set), excpected_str)
