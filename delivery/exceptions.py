"""
The utils.
"""

from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from rich import print, inspect


def validate_exception_handler(exc, context):
    """
    It's exception handler is used for creating awesome structure

    of errors that happens in validation time.
    """

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # check that a ValidationError exception is raised
    if isinstance(exc, ValidationError):
        # Wrap all response data (errors messages) into dict
        # with key 'validation_error
        response.data = {
            'validation_error': {'couriers': response.data},
        }

    return response
