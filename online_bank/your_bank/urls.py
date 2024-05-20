from django.urls import path
from .views import *

urlpatterns = [
    path('', your_bank_view, name='your_bank'),
]
