from rest_framework.views import exception_handler
from core.utils import error_response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        code = getattr(exc, 'code', None)
        http_status = response.status_code
        # Extrae los mensajes de error
        error_messages = []
        if isinstance(response.data, dict):
            for field, errors in response.data.items():
                if isinstance(errors, list):
                    error_messages.extend(errors)
                else:
                    error_messages.append(str(errors))
        else:
            error_messages = [str(response.data)]
        # Usa el helper para la respuesta
        return error_response(
            errors=error_messages,
            message="Ocurrió un error",
            code=code or "error",
            http_status=http_status,
            data=None
        )
    return response
    