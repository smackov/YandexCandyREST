"""
Test api.
"""

from datetime import time

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from ..models import Courier, Region, WorkingHours


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