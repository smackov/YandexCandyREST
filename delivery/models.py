"""
The models.
"""

from django.db import models
from django.core.exceptions import FieldError


COURIER_TYPES = [
    ('foot', 'Foot'),
    ('bike', 'Bike'),
    ('car', 'Car'),
]

COURIER_LOAD_CAPACITY = {
    'foot': 10,
    'bike': 15,
    'car': 50,
}


class Courier(models.Model):
    """
    The courier is the man delivering orders to customers.
    """
    courier_id = models.IntegerField(primary_key=True)
    courier_type = models.CharField(max_length=4, choices=COURIER_TYPES)
    regions = models.ManyToManyField('Region', related_name='couriers')

    class Meta:
        ordering = ['courier_id', 'courier_type']

    def __repr__(self):
        return 'Courier(id={}, type={}, regions={})'.format(
            self.courier_id, self.courier_type, list(self.regions.all()),
        )

    @property
    def load_capacity(self):
        """
        The load capacity is the maximum weight Courier is able to deliver.

        It matches the constants: COURIER_TYPES, COURIER_LOAD_CAPACITY
        """

        load = COURIER_LOAD_CAPACITY.get(self.courier_type)
        if load:
            return load
        raise FieldError("The 'courier_type' field of Courier with "
                         f"courier_id={self.courier_id} contains the unresolved "
                         f"value='{self.courier_type}' that absents in "
                         "COURIER_LOAD_CAPACITY")


class Region(models.Model):
    """
    The region of a city is represented as a number.
    """
    id = models.IntegerField(primary_key=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return 'Region ({})'.format(self.id)

    def __repr__(self):
        return str(self.id)


class HoursAbstract(models.Model):
    """
    The abstract class are inhereted by WorkingHours.
    """

    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        abstract = True

    def __repr__(self):
        return '{}-{}'.format(
            self.start.strftime('%H:%M'),
            self.end.strftime('%H:%M'),
        )


class WorkingHours(HoursAbstract):
    """"
    The WorkingHours class represent 'working_hours' field of Courier model.

    The format of 'working_hours' is 'HH:MM-HH:MM'
    Example: '09:00-12:00'
    """

    courier = models.ForeignKey(
        Courier, on_delete=models.CASCADE, related_name='working_hours',
    )
