from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

class CheckUserIsActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.is_active:
                logout(request)
                return redirect(f"{reverse('login')}?inactive=1")
        response = self.get_response(request)
        return response
