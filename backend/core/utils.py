from rest_framework.response import Response
from rest_framework import status

def success_response(data=None, message="Operación exitosa", code="success", http_status=status.HTTP_200_OK, errors=None):
    """
    Devuelve una respuesta estándar para éxitos.
    """
    return Response({
        "data": data,
        "message": message,
        "status": "success",
        "code": code,
        "http_status": http_status,
        "errors": errors
    }, status=http_status)

def error_response(errors=None, message="Ocurrió un error", code="error", http_status=status.HTTP_400_BAD_REQUEST, data=None):
    """
    Devuelve una respuesta estándar para errores personalizados.
    """
    # Acepta errors como string o lista
    if isinstance(errors, str):
        errors = [errors]
    return Response({
        "data": data,
        "message": message,
        "status": "error",
        "code": code,
        "http_status": http_status,
        "errors": errors
    }, status=http_status)