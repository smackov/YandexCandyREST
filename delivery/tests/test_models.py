"""
The tests of models.
"""

from datetime import time

from django.test import TestCase
from django.core.exceptions import FieldError

from ..models import Courier, Region, WorkingHours


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
        courier_1_working_hours = list(self.courier_1.working_hours.all())
        self.assertEqual(courier_1_working_hours, excpected_working_hours)
