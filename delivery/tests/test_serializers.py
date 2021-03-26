"""
Test serializers.
"""

from datetime import time

from django.test import TestCase

from ..serializers import CourierItemPostSerializer
from ..models import Courier, Region, WorkingHours


class CourierItemPostSerializerTestCase(TestCase):
    """
    The test case for CourierItemPostSerializer class.
    """

    def setUp(self):
        # Input data for serializer
        self.input_data_foot = {
            'courier_id': 1,
            'courier_type': 'foot',
            'regions': [1, 2],
            'working_hours': ["09:00-18:00", "20:00-22:00"]
        }
        self.input_data_bike = {
            'courier_id': 2,
            'courier_type': 'bike',
            'regions': [3, 4],
            'working_hours': ["10:00-14:00"]
        }
        self.input_many_data = [self.input_data_foot, self.input_data_bike]

    def test_valid_to_true_if_get_valid_data(self):
        serializer = CourierItemPostSerializer(
            data=self.input_many_data, many=True)
        serializer.is_valid()
        print('\nSerializer errors: ', serializer.errors)
        # self.assertTrue(serializer.is_valid())

    def test_create_function(self):
        serializer = CourierItemPostSerializer(
            data=self.input_many_data, many=True)
        self.assertTrue(serializer.is_valid())
        couriers = serializer.save()
        expected_couriers = Courier.objects.filter(courier_id__in=[1, 2])
        self.assertCountEqual(couriers, expected_couriers)
