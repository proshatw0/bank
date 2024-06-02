from django.urls import path
from .views import *

urlpatterns = [
    path('', your_bank_view, name='your_bank'),
    path('new-debit-card/', new_debit_view, name='new_debit'),
    path('new-deposite/', new_deposite, name='new_deposite'),
    path('update-card-info/', update_card_info, name='debit_info'),
    path('update-deposite-info/', update_deposite_info, name='deposite_info'),
    
]
