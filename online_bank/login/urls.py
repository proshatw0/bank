from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='login'),
    path('new/', registration_view, name='registration'),
    path('pin-code/', pin_view, name='pin'),
    path('check-redirect/', check_redirect, name='check_redirect'),
    path('local-only/', local_view, name='local_only')
]
