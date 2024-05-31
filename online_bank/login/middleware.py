from django.http import HttpResponseForbidden

class LocalhostOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/local-only/') and not self.is_local(request):
            return HttpResponseForbidden("This URL is accessible only from localhost.")
        response = self.get_response(request)
        return response

    def is_local(self, request):
        return request.META['REMOTE_ADDR'] in ('127.0.0.1', '::1')