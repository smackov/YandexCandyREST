"""
Test serializers.
"""

from datetime import time

from django.test import TestCase

from ..serializers import (CourierItemPostSerializer, OrderSerializer)
from ..models import Courier, Region, WorkingHours, Order, DeliveryHours


class CourierItemPostSerializerTestCase(TestCase):
    """
    The test case for CourierItemPostSerializer class.
    """

    def setUp(self):

        # Input data
        self.input_data_foot = {
            'courier_id': 1,
            'courier_type': 'foot',
            'regions': [1, 2],
            'working_hours': ["09:00-18:00", "20:00-22:10"]
        }
        self.input_data_bike = {
            'courier_id': 2,
            'courier_type': 'bike',
            'regions': [2, 3],
            'working_hours': ["10:00-14:00"]
        }
        self.input_many_data = [self.input_data_foot, self.input_data_bike]

    def test_valid_to_true_if_get_valid_data(self):
        serializer = CourierItemPostSerializer(
            data=self.input_many_data, many=True)
        self.assertTrue(serializer.is_valid())

    def test_create_function(self):
        serializer = CourierItemPostSerializer(
            data=self.input_many_data, many=True)
        self.assertTrue(serializer.is_valid())
        couriers = serializer.save()
        expected_couriers = Courier.objects.filter(courier_id__in=[1, 2])
        self.assertCountEqual(couriers, expected_couriers)

    def test_save_one_valide_courier(self):
        serializer = CourierItemPostSerializer(
            data=[self.input_data_foot], many=True)
        self.assertTrue(serializer.is_valid())
        couriers = serializer.save()

        # Test courier instance
        self.assertEqual(Courier.objects.count(), 1)
        courier = Courier.objects.get()
        self.assertEqual(courier.courier_id, 1)
        self.assertEqual(courier.courier_type, 'foot')

        # Test region instances
        self.assertCountEqual(courier.regions.all(), Region.objects.all())
        self.assertEqual(Region.objects.all()[0].id, 1)
        self.assertEqual(Region.objects.all()[1].id, 2)

        # Test working_hours instances
        self.assertCountEqual(courier.working_hours.all(),
                              WorkingHours.objects.all())
        self.assertEqual(str(WorkingHours.objects.all()[0]), "09:00-18:00")
        self.assertEqual(str(WorkingHours.objects.all()[1]), "20:00-22:10")

    def test_save_two_valide_courier(self):
        serializer = CourierItemPostSerializer(
            data=self.input_many_data, many=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Test courier instances
        courier_foot = Courier.objects.get(courier_id=1)
        courier_bike = Courier.objects.get(courier_id=2)
        self.assertEqual(Courier.objects.count(), 2)
        self.assertEqual(courier_foot.courier_id, 1)
        self.assertEqual(courier_bike.courier_id, 2)
        self.assertEqual(courier_foot.courier_type, 'foot')
        self.assertEqual(courier_bike.courier_type, 'bike')

        # Test region instances
        self.assertCountEqual(courier_foot.regions.all(),
                              Region.objects.filter(id__in=[1, 2]))
        self.assertCountEqual(courier_bike.regions.all(),
                              Region.objects.filter(id__in=[2, 3]))
        self.assertEqual(Region.objects.all()[0].id, 1)
        self.assertEqual(Region.objects.all()[1].id, 2)
        self.assertEqual(Region.objects.all()[2].id, 3)

        # Test working_hours instances
        self.assertEqual(WorkingHours.objects.count(), 3)
        self.assertEqual(str(WorkingHours.objects.all()[0]), "09:00-18:00")
        self.assertEqual(WorkingHours.objects.all()[0].courier, courier_foot)
        self.assertEqual(str(WorkingHours.objects.all()[1]), "20:00-22:10")
        self.assertEqual(WorkingHours.objects.all()[1].courier, courier_foot)
        self.assertEqual(str(WorkingHours.objects.all()[2]), "10:00-14:00")
        self.assertEqual(WorkingHours.objects.all()[2].courier, courier_bike)


class OrderSerializerTestCase(TestCase):
    """
    The test case for OrderSerializer class.
    """

    def setUp(self):

        # Input data
        self.input_data_1 = {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        }
        self.input_data_2 = {
            "order_id": 2,
            "weight": 0.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        }
        self.input_many_data = [self.input_data_1, self.input_data_2]

    def test_valid_to_true_if_get_valid_data(self):
        serializer = OrderSerializer(
            data=self.input_many_data, many=True)
        self.assertTrue(serializer.is_valid())

    def test_weight_upper_limit_data(self):
        self.input_data_1['weight'] = 50
        serializer = OrderSerializer(data=self.input_data_1)
        self.assertTrue(serializer.is_valid())

    def test_weight_over_upper_limit_data(self):
        self.input_data_1['weight'] = 50.01
        serializer = OrderSerializer(data=self.input_data_1)
        self.assertFalse(serializer.is_valid())

    def test_weight_lower_limit_data(self):
        self.input_data_1['weight'] = 0.01
        serializer = OrderSerializer(data=self.input_data_1)
        self.assertTrue(serializer.is_valid())

    def test_weight_over_lower_limit_data(self):
        self.input_data_1['weight'] = 0.00
        serializer = OrderSerializer(data=self.input_data_1)
        self.assertFalse(serializer.is_valid())

    def test_weight_2_decimal_places(self):
        self.input_data_1['weight'] = 0.123
        serializer = OrderSerializer(data=self.input_data_1)
        self.assertFalse(serializer.is_valid())
        
    def test_create_function(self):
        serializer = OrderSerializer(
            data=self.input_many_data, many=True)
        self.assertTrue(serializer.is_valid())
        orders = serializer.save()
        expected_orders = Order.objects.filter(order_id__in=[1, 2])
        self.assertCountEqual(orders, expected_orders)

    def test_save_one_valide_order(self):
        data = self.input_data_2
        serializer = OrderSerializer(data=self.input_data_2)
        self.assertTrue(serializer.is_valid())
        order = serializer.save()

        # Test order instance
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.order_id, data['order_id'])
        self.assertEqual(str(order.weight), str(data['weight']))

        # Test region instances
        self.assertEqual(order.region, Region.objects.get())
        self.assertEqual(order.region.id, data['region'])

        # Test working_hours instances
        self.assertCountEqual(order.delivery_hours.all(),
                              DeliveryHours.objects.all())
        self.assertEqual(str(DeliveryHours.objects.all()[0]), data['delivery_hours'][0])
        self.assertEqual(str(DeliveryHours.objects.all()[1]), data['delivery_hours'][1])
