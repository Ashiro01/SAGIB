# auditoria_app/middleware.py

import threading

# Usamos un almacenamiento local de hilo (thread-local) para guardar la petición
# de forma segura en entornos multiproceso.
_request_storage = threading.local()

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_storage.request = request
        response = self.get_response(request)
        # Limpiar después de que la petición se complete
        del _request_storage.request
        return response

def get_current_request():
    """Devuelve el objeto request actual o None si no está disponible."""
    return getattr(_request_storage, 'request', None)