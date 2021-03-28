"""
Test api.
"""

from datetime import time, datetime, timezone
import json

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rich import inspect

from ..models import (
    Courier, Region, WorkingHours, Order, DeliveryHours, AssignedOrderSet)


class CourierListAPITestCase(APITestCase):
    """
    The test case for CourierListAPI class.
    """

    def setUp(self):

        # Input data
        self.input_data = {'data': []}
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

    def test_post_one_valid_courier(self):
        url = reverse('couriers')
        self.input_data['data'].append(self.input_data_foot)
        response = self.client.post(url, self.input_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'couriers': [{'id': 1}]})

        # Test courier instance
        self.assertEqual(Courier.objects.count(), 1)
        courier = Courier.objects.get()
        self.assertEqual(courier.courier_id, 1)
        self.assertEqual(courier.courier_type, 'foot')

    def test_post_two_valid_couriers(self):
        url = reverse('couriers')
        self.input_data['data'].append(self.input_data_foot)
        self.input_data['data'].append(self.input_data_bike)
        response = self.client.post(url, self.input_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'couriers': [{'id': 1}, {'id': 2}]})

        # Test courier instances
        courier_foot = Courier.objects.get(courier_id=1)
        courier_bike = Courier.objects.get(courier_id=2)
        self.assertEqual(Courier.objects.count(), 2)
        self.assertEqual(courier_foot.courier_id, 1)
        self.assertEqual(courier_bike.courier_id, 2)
        self.assertEqual(courier_foot.courier_type, 'foot')
        self.assertEqual(courier_bike.courier_type, 'bike')

    def test_post_two_invalid_couriers(self):

        self.input_data_foot['courier_type'] = 'none'
        self.input_data_bike['courier_type'] = 'none'

        self.input_data['data'].append(self.input_data_foot)
        self.input_data['data'].append(self.input_data_bike)
        url = reverse('couriers')
        response = self.client.post(url, self.input_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Courier.objects.count(), 0)
        self.assertEqual(Region.objects.count(), 0)
        self.assertEqual(WorkingHours.objects.count(), 0)


class CourierItemAPITestCase(APITestCase):
    """
    The test case for CourierItemAPI class.
    """

    def setUp(self):

        # Input data
        self.input_data = {'data': []}
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

        # Create regions: 1, 2, 3, 4, 5
        for region_number in range(1, 6):
            region = Region.objects.create(id=region_number)
            setattr(self, f'region_{region_number}', region)

        # Create courier
        self.courier = Courier.objects.create(
            courier_id=1, courier_type='car')
        self.courier.regions.set([1, 2, 3])

        # Create working hours
        self.working_hours_1 = WorkingHours.objects.create(
            start=time(hour=9), end=time(hour=12), courier=self.courier)
        self.working_hours_2 = WorkingHours.objects.create(
            start=time(hour=18), end=time(hour=20), courier=self.courier)

    def test_changed_all_courier_fields(self):
        url = reverse('courier-item', args=[1])
        response = self.client.patch(url, self.input_data_foot, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.input_data_foot)

    def test_request_with_invalid_courier_type(self):
        url = reverse('courier-item', args=[1])
        self.input_data_foot['courier_type'] = 'zuzu'
        response = self.client.patch(url, self.input_data_foot, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderListAPITestCase(APITestCase):
    """
    The test case for OrderListAPI class.
    """

    def setUp(self):
        # Input data
        self.input_data = {'data': []}
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

    def test_post_one_valid_order(self):
        url = reverse('orders')
        self.input_data['data'].append(self.input_data_1)
        response = self.client.post(url, self.input_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'orders': [{'id': 1}]})

        # Test order instance
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.order_id, self.input_data_1['order_id'])
        self.assertEqual(str(order.weight), str(self.input_data_1['weight']))
        self.assertEqual(Region.objects.count(), 1)
        self.assertEqual(DeliveryHours.objects.count(), 1)

    def test_post_two_valid_couriers(self):
        url = reverse('orders')
        self.input_data['data'].append(self.input_data_1)
        self.input_data['data'].append(self.input_data_2)
        response = self.client.post(url, self.input_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'orders': [{'id': 1}, {'id': 2}]})

        # Test order instances
        self.assertEqual(Order.objects.count(), 2)
        order_1 = Order.objects.get(order_id=1)
        order_2 = Order.objects.get(order_id=2)
        self.assertEqual(order_1.order_id, self.input_data_1['order_id'])
        self.assertEqual(order_2.order_id, self.input_data_2['order_id'])
        self.assertEqual(str(order_1.weight), str(self.input_data_1['weight']))
        self.assertEqual(str(order_2.weight), str(self.input_data_2['weight']))
        self.assertEqual(Region.objects.count(), 2)
        self.assertEqual(DeliveryHours.objects.count(), 3)

    def test_post_two_invalid_couriers(self):

        self.input_data_1['weight'] = 10.001
        self.input_data_2['order_id'] = 'none'

        self.input_data['data'].append(self.input_data_1)
        self.input_data['data'].append(self.input_data_2)
        url = reverse('orders')
        response = self.client.post(url, self.input_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Region.objects.count(), 0)
        self.assertEqual(DeliveryHours.objects.count(), 0)


class OrdersAssignAPITestCase(APITestCase):
    """
    The test case for OrdersAssignAPI class.
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

    def test_post_valid_courier_with_potential_orders(self):
        url = reverse('orders-assign')
        data = {'courier_id': self.courier.courier_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.courier.refresh_from_db()
        assign_time = self.courier.current_set_of_orders.assign_time
        expected_response_data = {
            'orders': [{'id': 1}],
            'assign_time': assign_time.isoformat().replace('+00:00', 'Z')
        }
        self.assertEqual(json.loads(response.content), expected_response_data)

    def test_post_valid_courier_without_potential_orders(self):
        self.order_1.weight = 40
        self.order_1.save()
        url = reverse('orders-assign')
        data = {'courier_id': self.courier.courier_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, [])

    def test_post_invalid_courier(self):
        url = reverse('orders-assign')
        data = {'courier_id': 999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'detail': "Courier doesn't exist"})

    def test_post_invalid_fields(self):
        url = reverse('orders-assign')
        data = {'courier_id2': 999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {
                         'courier_id': ["This field is required."]})

    def test_post_valid_courier_with_notstarted_and_finished_orders(self):
        self.order_set = AssignedOrderSet.objects.create(
            courier=self.courier, courier_type=self.courier.courier_type
        )
        self.order_set.notstarted_orders.set([self.order_1])
        self.order_set.finished_orders.set([self.order_2])
        self.courier.current_set_of_orders = self.order_set
        self.courier.save()

        url = reverse('orders-assign')
        data = {'courier_id': self.courier.courier_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response_data = {
            'orders': [{'id': 1}],
            'assign_time': self.order_set.assign_time.isoformat().replace('+00:00', 'Z')
        }
        self.assertEqual(json.loads(response.content), expected_response_data)

    def test_post_valid_courier_with_all_finished_orders(self):
        self.order_data_3 = {
            'order_id': 3,
            'weight': 3,
            'region': self.region_1,
        }
        self.order_3 = Order.objects.create(**self.order_data_3)
        self.delivery_hours_3 = DeliveryHours.objects.create(
            start=time(hour=9), end=time(hour=12), order=self.order_3)

        self.order_set = AssignedOrderSet.objects.create(
            courier=self.courier, courier_type=self.courier.courier_type
        )
        self.order_set.finished_orders.set([self.order_1, self.order_2])
        self.order_1.set_of_orders = self.order_set
        self.order_2.set_of_orders = self.order_set
        self.order_1.save()
        self.order_2.save()
        self.courier.current_set_of_orders = self.order_set
        self.courier.save()

        url = reverse('orders-assign')
        data = {'courier_id': self.courier.courier_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.courier.refresh_from_db()
        assign_time = self.courier.current_set_of_orders.assign_time
        expected_response_data = {
            'orders': [{'id': 3}],
            'assign_time': assign_time.isoformat().replace('+00:00', 'Z')
        }
        self.assertEqual(json.loads(response.content), expected_response_data)


class OrdersCompleteAPITestCase(APITestCase):
    """
    The test case for OrdersCompleteAPI class.
    """

    def setUp(self):
        # orders/complete request data
        self.complete_data = {
            'courier_id': 1,
            'order_id': 1,
            'complete_time': "2021-03-24T12:39:07.42Z",
        }
        self.complete_time = datetime(
            year=2021, month=3, day=24, hour=12, minute=39, second=7, 
            microsecond=420000, tzinfo=timezone.utc)

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
        self.order_set.notstarted_orders.set([self.order_1, self.order_2])

        # Set order_set to orders
        self.order_1.set_of_orders = self.order_set
        self.order_2.set_of_orders = self.order_set
        self.order_1.save()
        self.order_2.save()

    def test_if_data_invalid(self):
        self.complete_data['unresolved_field'] = self.complete_data.pop(
            'courier_id')
        url = reverse('orders-complete')
        response = self.client.post(url, self.complete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data)

    def test_if_courier_doesnot_exist(self):
        self.complete_data['courier_id'] = 999
        url = reverse('orders-complete')
        response = self.client.post(url, self.complete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data)

    def test_if_order_doesnot_exist(self):
        self.complete_data['order_id'] = 999
        url = reverse('orders-complete')
        response = self.client.post(url, self.complete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data)

    def test_if_order_and_courier_do_not_exist(self):
        self.complete_data['order_id'] = 999
        url = reverse('orders-complete')
        response = self.client.post(url, self.complete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data)

    def test_if_all_valid(self):
        url = reverse('orders-complete')
        response = self.client.post(url, self.complete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"order_id": 1})
        self.order_set.refresh_from_db()
        self.assertEqual(
            list(self.order_set.notstarted_orders.all()), [self.order_2])
        self.assertEqual(
            list(self.order_set.finished_orders.all()), [self.order_1])
        self.order_1.refresh_from_db()
        self.assertEqual(self.order_1.complete_time, self.complete_time)
        self.order_2.refresh_from_db()
        self.assertIsNone(self.order_2.complete_time)
        
        # Check if the same answer and it is
        response = self.client.post(url, self.complete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"order_id": 1})

    def test_if_order_have_another_executor(self):
        self.another_courier = Courier.objects.create(
            courier_id=10, courier_type='bike'
        )
        self.order_set.courier = self.another_courier
        self.order_set.save()
        url = reverse('orders-complete')
        response = self.client.post(url, self.complete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data)
        self.order_1.refresh_from_db()
        self.assertIsNone(self.order_1.complete_time)

    def test_if_order_hasnot_order_set(self):
        self.order_1.set_of_orders = None
        self.order_1.save()
        url = reverse('orders-complete')
        response = self.client.post(url, self.complete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(response.data)
        self.order_1.refresh_from_db()
        self.assertIsNone(self.order_1.complete_time)
