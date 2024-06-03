from django.urls import path
from .views import *

urlpatterns = [
    path('', your_bank_view, name='your_bank'),
    path('new-debit-card/', new_debit_view, name='new_debit'),
    path('new-deposite/', new_deposite, name='new_deposite'),
    path('transfers/', transfers_view, name='transfers'),
    path('transfers-debit/', transfers_debit_view, name='transfers_debit'),
    path('transfers-own/', transfers_own_view, name='transfers_own'),

    path('update-card-info/', update_card_info, name='debit_info'),
    path('update-deposite-info/', update_deposite_info, name='deposite_info'),
    
]
