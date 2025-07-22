from core.utils import success_response, error_response

class StandardResponseMixin:
    """
    Mixin para estandarizar respuestas de éxito y error en views DRF.
    """
    def success_response(self, data=None, message="Operación exitosa", code="success", http_status=200, errors=None):
        return success_response(data=data, message=message, code=code, http_status=http_status, errors=errors)

    def error_response(self, errors=None, message="Ocurrió un error", code="error", http_status=400, data=None):
        simple_error = self.extract_first_error_message(errors)
        return error_response(
            errors=simple_error,
            message=message,
            code=code,
            http_status=http_status,
            data=data
        )

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
        return self.error_response(
            errors="Esta tratando de realizar una operación no Autorizada, contacte al adminitrador.",
            message="Ocurrió un error inesperado",
            code="unexpected_error",
            http_status=500
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
                    http_status=200
                )
            serializer = serializer_class(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message=unpaginated_message,
                code=code,
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el listado",
                code=error_code,
                http_status=500
            )

    def standard_create_response(self, request, *args, success_message="Creado exitosamente", code="created", error_message="Error al crear", error_code="create_error", http_status=201, **kwargs):
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
                http_status=400
            )