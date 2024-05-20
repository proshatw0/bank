from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='login'),
    path('new/', registration_view, name='registration'),
    path('pin-code/', pin_view, name='pin')
]
