import json
from urllib.parse import urlparse
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from your_bank.models import Account, DebitCard, Deposit, DepositCondition, Subscription

def remove_field_from_user_sessions(user_id, field_name):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in sessions:
        data = session.get_decoded()
        if str(user_id) == str(data.get('_auth_user_id')):
            if field_name in data:
                del data[field_name]
                session.session_data = Session.objects.encode(data)
                session.save()


def go_pin(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next', '/login/pin-code/')
        return redirect(next_url)
    else:
        next_url = request.GET.get('next', '/login/')
        return redirect(next_url)
    
def bank_view(request):
    accounts = Account.objects.filter(user=request.user)
    
    debit_cards = []
    for account in accounts:
        cards = DebitCard.objects.filter(account=account)
        for card in cards:
            debit_cards.append({
                "balance": f"{account.balance} ₽",
                "type_card": card.subscription.name,
                "number_card": card.card_number[-4:]
            })

    user_id = request.user.id
    deposits_info = Deposit.get_all_deposits_info(user_id)
    print(deposits_info)  
    formatted_deposits_info = [
        {
            "balance": f"{info['balance']} ₽",
            "type_deposit": info["condition_name"],
            "interest_rate": f"{info['interest_rate']} %"
        }
        for info in deposits_info
    ]

    print(formatted_deposits_info)
    
    context = {
        "debit_cards": debit_cards,
        "deposits": formatted_deposits_info,
    }
    return render(request, 'your_bank.html', context)

@csrf_exempt
def update_deposite_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            deposite_name = data.get('deposite_name')
            data = DepositCondition.get_condition_by_name(deposite_name)
            example = {
                'procent': data['procent'],
                'period': data['period'],
                'close': 'да' if data['close'] else 'нет'
            }
            return JsonResponse(example)
        except Subscription.DoesNotExist:
            return JsonResponse({'error': 'Card not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def update_card_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            card_name = data.get('card_name')
            subscription = Subscription.objects.get(name=card_name)
            response_data = {
                'cost': str(subscription.monthly_cost),
                'limit': 'нет' 
            }
            return JsonResponse(response_data)
        except Subscription.DoesNotExist:
            return JsonResponse({'error': 'Card not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def new_deposite(request):
    referer = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        if request.user.is_authenticated:
            subscription = request.POST.get('subscription')
            user = request.user
    
            condition = DepositCondition.objects.get(name=subscription)
    
            Deposit.create_deposit(user, condition.id)
            
            return JsonResponse({'status': 'success', 'message': '/your_bank/'}, content_type="application/json")
        else:
            return JsonResponse({'status': 'success', 'message': '/login/'}, status=400, content_type="application/json")
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        
        if parsed_referer.netloc == current_domain:
            # DepositCondition.create_condition("Сберегательный", 3, 60, True)
            # DepositCondition.create_condition("Накопительный", 6, 3, False)

            deposites = DepositCondition.get_all_names()
            data = DepositCondition.get_condition_by_name(deposites[0])
            example = {
                'deposites': deposites,
                'procent': data['procent'],
                'period': data['period'],
                'close': 'да' if data['close'] else 'нет'
            }

            return render(request, 'new_deposite.html', example)
        else:
            return go_pin(request)
    else:
        return go_pin(request)
    
def new_debit_view(request):
    referer = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        if request.user.is_authenticated:
            subscription = request.POST.get('subscription')
            pin = request.POST.get('pin')
            if len(pin) != 3 or not pin.isdigit():
                return JsonResponse({'status': 'error', 'message': "Пин код из 3-х цифр", 'error_elemenet':'pin'})
            DebitCard.create_card(request.user, subscription, pin)
            return JsonResponse({'status': 'success', 'message': '/your_bank/'}, content_type="application/json")
        else:
            return JsonResponse({'status': 'error', 'message': '/login/'}, status=400, content_type="application/json")
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        
        if parsed_referer.netloc == current_domain:
            # Subscription.create_subscription(name="Polosun", monthly_cost=0)
            # Subscription.create_subscription(name="Cozumel", monthly_cost=190)
            # Subscription.create_subscription(name="Cacomistle", monthly_cost=290)
            debits = Subscription.get_all_subscriptions()
            cost = Subscription.get_monthly_cost_by_name(debits[0])
            example = {
                'debits': debits,
                'cost': cost
            }

            return render(request, 'new_debit.html', example)
        else:
            return go_pin(request)
    else:
        return go_pin(request)

def your_bank_view(request):
    remove_field_from_user_sessions(request.user.id, 'redirect_url')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        
        if parsed_referer.netloc == current_domain:
            return bank_view(request)
        else:
            return go_pin(request)
    else:
        return go_pin(request)