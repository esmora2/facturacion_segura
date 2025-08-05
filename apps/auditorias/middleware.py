"""Middleware personalizado para Django Silk profiling automático."""

from silk.profiling.profiler import silk_profile


class AutoSilkProfilingMiddleware:
    """
    Middleware que aplica profiling automático a todas las vistas API.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Aplicar profiling solo a endpoints API
        if request.path.startswith('/api/'):
            with silk_profile(name=f'API_{request.method}_{request.path}'):
                response = self.get_response(request)
        else:
            response = self.get_response(request)
        
        return response
