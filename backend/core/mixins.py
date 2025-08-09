from rest_framework.response import Response
from rest_framework import status

class StandardResponseMixin:
    """
    Mixin para estandarizar respuestas de éxito y error en views DRF.
    """
    def success_response(self, data=None, message="Operación exitosa", code="success", http_status=status.HTTP_200_OK, errors=None):
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

    def error_response(self, errors=None, message="Ocurrió un error", code="error", http_status=status.HTTP_400_BAD_REQUEST, data=None):
        """
        Devuelve una respuesta estándar para errores.
        """
        # Procesa y simplifica los errores
        processed_errors = self.extract_first_error_message(errors)
        
        # Acepta errors como string o lista
        if isinstance(processed_errors, str):
            processed_errors = [processed_errors]
            
        return Response({
            "data": data,
            "message": message,
            "status": "error",
            "code": code,
            "http_status": http_status,
            "errors": processed_errors
        }, status=http_status)

    def extract_first_error_message(self, errors):
        # Si es un dict, busca el primer mensaje
        if isinstance(errors, dict):
            for field, messages in errors.items():
                print(field)
                if isinstance(messages, list) and messages:
                    return str(messages[0])
                return str(messages)
        # Si es una lista, devuelve el primer elemento
        if isinstance(errors, list) and errors:
            return str(errors[0])
        # Si es un string, devuélvelo tal cual
        return str(errors)

    def handle_exception(self, exc):
        """
        Sobrescribe el manejo de excepciones para devolver error_response.
        """
        # Extraer solo el mensaje de error limpio
        error_message = getattr(exc, 'detail', str(exc))
        
        # Si el error tiene detail, procesarlo para obtener solo el string
        if hasattr(exc, 'detail'):
            error_message = self.extract_first_error_message(exc.detail)
        
        return self.error_response(
            errors=error_message,
            message="Ocurrió un error inesperado",
            code="unexpected_error",
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    def paginated_list_response(self, request, queryset, serializer_class, paginated_message, unpaginated_message, code, error_code):
        try:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = serializer_class(page, many=True)
                paginated = self.get_paginated_response(serializer.data).data
                return self.success_response(
                    data=paginated,
                    message=paginated_message,
                    code=code,
                    http_status=status.HTTP_200_OK
                )
            serializer = serializer_class(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message=unpaginated_message,
                code=code,
                http_status=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el listado",
                code=error_code,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def standard_create_response(self, request, *args, success_message="Creado exitosamente", code="created", error_message="Error al crear", error_code="create_error", http_status=status.HTTP_201_CREATED, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return self.success_response(
                data=response.data,
                message=success_message,
                code=code,
                http_status=http_status
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message=error_message,
                code=error_code,
                http_status=status.HTTP_400_BAD_REQUEST
            )