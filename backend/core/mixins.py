from core.utils import success_response, error_response

class StandardResponseMixin:
    """
    Mixin para estandarizar respuestas de éxito y error en views DRF.
    """
    def success_response(self, data=None, message="Operación exitosa", code="success", http_status=200, errors=None):
        return success_response(data=data, message=message, code=code, http_status=http_status, errors=errors)

    def error_response(self, errors=None, message="Ocurrió un error", code="error", http_status=400, data=None):
        return error_response(errors=errors, message=message, code=code, http_status=http_status, data=data)

    def handle_exception(self, exc):
        """
        Sobrescribe el manejo de excepciones para devolver error_response.
        """
        return self.error_response(
            errors=str(exc),
            message="Ocurrió un error inesperado",
            code="unexpected_error",
            http_status=500
        )