from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        code = getattr(exc, 'code', None)
        if isinstance(response.data, dict):
            error_messages = []
            for field, errors in response.data.items():
                if isinstance(errors, list):
                    if field == 'non_field_errors':
                        error_messages.extend(errors)
                    else:
                        for error in errors:
                            error_messages.append(f"{error}")
                else:
                    error_messages.append(str(errors))
            response.data = {
                'error_message': error_messages,
                'status': 'error'
            }
            if code:
                response.data['code'] = code
        else:
            response.data = {
                'error_message': [str(response.data)],
                'status': 'error'
            }
            if code:
                response.data['code'] = code
    return response

class CustomValidationError(APIException):
    """
    Error de validacion personalizada que puede ser utilizada en la app
    """
    status_code = 400
    default_detail = "Validation error"
    default_code = "custom_validation_error"

    def __init__(self, message, code=None):
        self.detail = message
        self.code = code or self.default_code

class BusinessLogicError(APIException):
    """
    Excepcion Personalizada para error de logica de negocio
    """
    status_code = 400
    default_detail = "Business logic error"
    default_code = "business_logic_error"

    def __init__(self, message, code=None):
        self.detail = message
        self.code = code or self.default_code