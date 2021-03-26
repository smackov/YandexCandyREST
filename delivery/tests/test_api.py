"""
Test api.
"""

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from ..models import Courier, Region, WorkingHours


class CourierTestAPITestCase(APITestCase):
    
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

    def test_post_one_valide_courier(self):
        url = reverse('couriers')
        self.input_data['data'].append(self.input_data_foot)
        response = self.client.post(url, self.input_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test courier instance
        courier = Courier.objects.get()
        self.assertEqual(Courier.objects.count(), 1)
        self.assertEqual(courier.courier_id, 1)
        self.assertEqual(courier.courier_type, 'foot')
        
        # Test region instances
        self.assertCountEqual(courier.regions.all(), Region.objects.all())
        self.assertEqual(Region.objects.all()[0].id, 1)
        self.assertEqual(Region.objects.all()[1].id, 2)
        
        # Test working_hours instances
        self.assertCountEqual(courier.working_hours.all(), WorkingHours.objects.all())
        self.assertEqual(str(WorkingHours.objects.all()[0]), "09:00-18:00")
        self.assertEqual(str(WorkingHours.objects.all()[1]), "20:00-22:10")

    def test_post_two_valide_courier(self):
        url = reverse('couriers')
        self.input_data['data'].append(self.input_data_foot)
        self.input_data['data'].append(self.input_data_bike)
        response = self.client.post(url, self.input_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test courier instances
        courier_foot = Courier.objects.get(courier_id=1)
        courier_bike = Courier.objects.get(courier_id=2)
        self.assertEqual(Courier.objects.count(), 2)
        self.assertEqual(courier_foot.courier_id, 1)
        self.assertEqual(courier_bike.courier_id, 2)
        self.assertEqual(courier_foot.courier_type, 'foot')
        self.assertEqual(courier_bike.courier_type, 'bike')
        
        # Test region instances
        self.assertCountEqual(courier_foot.regions.all(), Region.objects.filter(id__in=[1, 2]))
        self.assertCountEqual(courier_bike.regions.all(), Region.objects.filter(id__in=[2, 3]))
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
        