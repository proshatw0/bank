from decimal import Decimal
import json
from urllib.parse import urlparse
from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout

from login.models import CustomUser
from your_bank.models import Account, DebitCard, Deposit, DepositCondition, Subscription, Transaction

def logout_view(request):
    logout(request)
    return redirect('/login/')

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
    formatted_deposits_info = [
        {
            "balance": f"{info['balance']} ₽",
            "type_deposit": info["condition_name"],
            "interest_rate": f"{info['interest_rate']} %"
        }
        for info in deposits_info
    ]

    context = {
        "name": request.user.name,
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
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        
        if parsed_referer.netloc == current_domain:
            if request.method == 'POST':
                if request.user.is_authenticated:
                    subscription = request.POST.get('subscription')
                    user = request.user
                    condition = DepositCondition.objects.get(name=subscription)
                    Deposit.create_deposit(user, condition.id)
                    return JsonResponse({'status': 'success', 'message': '/your_bank/'}, content_type="application/json")
                else:
                    return JsonResponse({'status': 'success', 'message': '/login/'}, status=400, content_type="application/json")
            # DepositCondition.create_condition("Сберегательный", 3, 60, True)
            # DepositCondition.create_condition("Накопительный", 6, 3, False)

            deposites = DepositCondition.get_all_names()
            data = DepositCondition.get_condition_by_name(deposites[0])
            example = {
                "name": request.user.name,
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
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        
        if parsed_referer.netloc == current_domain:

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
            # Subscription.create_subscription(name="Polosun", monthly_cost=0)
            # Subscription.create_subscription(name="Cozumel", monthly_cost=190)
            # Subscription.create_subscription(name="Cacomistle", monthly_cost=290)
            debits = Subscription.get_all_subscriptions()
            cost = Subscription.get_monthly_cost_by_name(debits[0])
            example = {
                "name": request.user.name,
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
    
def transfers_view(request):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        if parsed_referer.netloc == current_domain:
            if request.method == 'POST':
                if request.user.is_authenticated:
                    data = json.loads(request.body)
                    phone_number = data.get('phone_number')
                    if len(phone_number) != 10 or not phone_number.isdigit():
                        return JsonResponse({'status': 'error'}, json_dumps_params={'ensure_ascii': False})
                    try:
                        user = CustomUser.objects.get(phone=phone_number)
                    except ObjectDoesNotExist:
                        return JsonResponse({'status': 'error'}, json_dumps_params={'ensure_ascii': False})
                    return JsonResponse({'status': 'success', 'message': f'/your_bank/transfers-telephone/{phone_number}'}, content_type="application/json")

            example = {
                "name": request.user.name,
            }

            return render(request, 'transfers.html', example)
        else:
            return go_pin(request)
    else:
        return go_pin(request)

def find_account_by_subscription_and_last_four_digits(user, subscription_array):
    if not subscription_array:
        raise ValidationError("Subscription array is empty")
    
    if DebitCard.objects.filter(subscription__name=subscription_array[0]).exists():
        user_cards = DebitCard.objects.filter(account__user=user)
        matching_cards = user_cards.filter(card_number__endswith=subscription_array[1])
        
        matching_account_numbers = [card.account.account_number for card in matching_cards]
        return matching_account_numbers
    
    else:
        user_deposits = Deposit.objects.filter(account__user=user)
        matching_deposits = user_deposits.filter(account__account_number__endswith=subscription_array[1])
        
        matching_account_numbers = [deposit.account.account_number for deposit in matching_deposits]
        return matching_account_numbers
    
def transfers_debit_view(request):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        if parsed_referer.netloc == current_domain:
            if request.method == 'POST':
                if request.user.is_authenticated:
                    number_card = request.POST.get('number_card')
                    subscription = request.POST.get('subscription')
                    cost = request.POST.get('cost')

                    if len(number_card) != 16 or not number_card.isdigit():
                        return JsonResponse({'status': 'error', 'message': "Номер карты должен состоять из 16 цифр", 'error_element': 'number_card'}, json_dumps_params={'ensure_ascii': False})
                    subscription_part = subscription.split(' - ')[0].strip()
                    subscription_array = subscription_part.split(' ')
                    result = find_account_by_subscription_and_last_four_digits(request.user, subscription_array)
                    try:
                        cost_decimal = Decimal(cost)
                    except:
                        return JsonResponse({'status': 'error', 'message': 'Неверный формат суммы. Не более 10 знаков целой части и 2 дробной.'}, json_dumps_params={'ensure_ascii': False})

                    transaction = Transaction.create_transaction(
                        user=request.user,
                        from_account_number=result[0],
                        to_account_number=DebitCard.get_account_number_by_card_number(number_card),
                        amount=cost_decimal,
                        description='Transaction description here'
                    )
                    if not isinstance(transaction, str):
                        reques = {
                            "accountInfo": subscription_array[0],
                            "amountInfo": f"{Account.get_balance_by_account_number(result[0])+cost_decimal} ₽ -> {Account.get_balance_by_account_number(result[0])} ₽",
                            "transactionAmount": f"- {cost_decimal} ₽",
                            "cardNumber": number_card,
                        }
                        return JsonResponse({'status': 'success', 'message': reques}, content_type="application/json")
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Произошла ошибка при создании транзакции'}, content_type="application/json", json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse({'status': 'success', 'message': '/login/'}, status=400, content_type="application/json")
            debit_cards = DebitCard.objects.filter(account__user_id=request.user.id)
            card_info = [{
                'name': f"{card.subscription.name}",
                'number': card.card_number[-4:],
                'balance': f"{card.get_balance()} ₽"
            } for card in debit_cards]
        
            deposits = Deposit.objects.filter(account__user_id=request.user.id)
            deposit_info = []

            for deposit in deposits:
                if deposit.condition.early_closure_allowed:
                    deposit_info.append({
                        'name': f"{deposit.condition.name}",
                        'number': deposit.account.account_number[-4:],
                        'balance': f"{deposit.get_balance()} ₽"
                    })
                else:
                    maturity_date = deposit.opening_date + timedelta(days=30 * deposit.condition.period_in_months)
                    if timezone.now().date() >= maturity_date:
                        deposit_info.append({
                            'name': f"{deposit.condition.name}",
                            'number': deposit.account.account_number[-4:],
                            'balance': f"{deposit.get_balance()} ₽"
                        })
            example = {
                "card_info": card_info,
                "deposits": deposit_info,
                "name": request.user.name,
            }

            return render(request, 'transfers_debit.html', example)
        else:
            return go_pin(request)
    else:
        return go_pin(request)
    

def transfers_own_view(request):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        if parsed_referer.netloc == current_domain:
            if request.method == 'POST':
                if request.user.is_authenticated:
                    subscription1 = request.POST.get('subscription1')
                    subscription2 = request.POST.get('subscription2')
                    cost = request.POST.get('cost')

                    subscription_part1 = subscription1.split(' - ')[0].strip()
                    subscription_array1 = subscription_part1.split(' ')
                    subscription_part2 = subscription2.split(' - ')[0].strip()
                    subscription_array2 = subscription_part2.split(' ')
                    result1 = find_account_by_subscription_and_last_four_digits(request.user, subscription_array1)
                    result2 = find_account_by_subscription_and_last_four_digits(request.user, subscription_array2)
                    
                    try:
                        cost_decimal = Decimal(cost)
                    except:
                        return JsonResponse({'status': 'error', 'message': 'Неверный формат суммы. Не более 10 знаков целой части и 2 дробной.'}, json_dumps_params={'ensure_ascii': False})

                    transaction = Transaction.create_transaction_own(
                        request.user, result1[0], result2[0], cost_decimal, "Transfer description"
                    )

                    if not isinstance(transaction, str):
                        reques = {
                            "accountInfo": subscription_array1[0],
                            "amountInfo": f"{Account.get_balance_by_account_number(result1[0])+cost_decimal} ₽ -> {Account.get_balance_by_account_number(result1[0])} ₽",
                            "transactionAmount": f"- {cost_decimal} ₽",

                        }
                        return JsonResponse({'status': 'success', 'message': reques}, content_type="application/json")
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Произошла ошибка при создании транзакции'}, content_type="application/json", json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse({'status': 'success', 'message': '/login/'}, status=400, content_type="application/json")
            debit_cards = DebitCard.objects.filter(account__user_id=request.user.id)
            card_info = [{
                'name': f"{card.subscription.name}",
                'number': card.card_number[-4:],
                'balance': f"{card.get_balance()} ₽"
            } for card in debit_cards]
        
            deposits = Deposit.objects.filter(account__user_id=request.user.id)
            deposit_info = []

            for deposit in deposits:
                if deposit.condition.early_closure_allowed:
                    deposit_info.append({
                        'name': f"{deposit.condition.name}",
                        'number': deposit.account.account_number[-4:],
                        'balance': f"{deposit.get_balance()} ₽"
                    })
                else:
                    maturity_date = deposit.opening_date + timedelta(days=30 * deposit.condition.period_in_months)
                    if timezone.now().date() >= maturity_date:
                        deposit_info.append({
                            'name': f"{deposit.condition.name}",
                            'number': deposit.account.account_number[-4:],
                            'balance': f"{deposit.get_balance()} ₽"
                        })
            example = {
                "card_info": card_info,
                "deposits": deposit_info,
                "name": request.user.name,
            }

            return render(request, 'transfers_own.html', example)
        else:
            return go_pin(request)
    else:
        return go_pin(request)
    

def transfers_telephone_view(request, phone_number):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        if parsed_referer.netloc == current_domain:
            if request.method == 'POST':
                if request.user.is_authenticated:
                    data = json.loads(request.body)
                    phone_number = data.get('phone')
                    subscription = data.get('subscription')
                    cost = data.get('cost')
                    print(phone_number, subscription, cost)

                    subscription_part = subscription.split(' - ')[0].strip()
                    subscription_array = subscription_part.split(' ')
                    result = find_account_by_subscription_and_last_four_digits(request.user, subscription_array)
                    try:
                        cost_decimal = Decimal(cost)
                    except:
                        return JsonResponse({'status': 'error', 'message': 'Неверный формат суммы. Не более 10 знаков целой части и 2 дробной.'}, json_dumps_params={'ensure_ascii': False})
                    user = CustomUser.objects.get(phone=phone_number)
                    to_account_number = Account.objects.filter(user=user).first().account_number
                    if not to_account_number:
                        return JsonResponse({'status': 'error', 'message': 'У получателя нет счетов'}, json_dumps_params={'ensure_ascii': False})
                    print(to_account_number)
                    transaction = Transaction.create_transaction(
                        user=request.user,
                        from_account_number=result[0],
                        to_account_number=to_account_number,
                        amount=cost_decimal,
                        description='Transaction description here'
                    )
                    name = user.get_short_name()
                    if not isinstance(transaction, str):
                        reques = {
                            "accountInfo": subscription_array[0],
                            "amountInfo": f"{Account.get_balance_by_account_number(result[0])+cost_decimal} ₽ -> {Account.get_balance_by_account_number(result[0])} ₽",
                            "bankLogo": name,
                            "transactionAmount": f"- {cost_decimal} ₽",
                            "cardNumber": f"+7 {phone_number}",
                        }
                        return JsonResponse({'status': 'success', 'message': reques}, content_type="application/json")
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Произошла ошибка при создании транзакции'}, content_type="application/json", json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse({'status': 'success', 'message': '/login/'}, status=400, content_type="application/json")
           
            debit_cards = DebitCard.objects.filter(account__user_id=request.user.id)
            card_info = [{
                'name': f"{card.subscription.name}",
                'number': card.card_number[-4:],
                'balance': f"{card.get_balance()} ₽"
            } for card in debit_cards]
        
            deposits = Deposit.objects.filter(account__user_id=request.user.id)
            deposit_info = []

            for deposit in deposits:
                if deposit.condition.early_closure_allowed:
                    deposit_info.append({
                        'name': f"{deposit.condition.name}",
                        'number': deposit.account.account_number[-4:],
                        'balance': f"{deposit.get_balance()} ₽"
                    })
                else:
                    maturity_date = deposit.opening_date + timedelta(days=30 * deposit.condition.period_in_months)
                    if timezone.now().date() >= maturity_date:
                        deposit_info.append({
                            'name': f"{deposit.condition.name}",
                            'number': deposit.account.account_number[-4:],
                            'balance': f"{deposit.get_balance()} ₽"
                        })
            user = CustomUser.objects.get(phone=phone_number)
            name = user.get_short_name()
            example = {
                "recipient": {"phone": phone_number,
                              "name": name},
                "card_info": card_info,
                "deposits": deposit_info,
                "name": request.user.name,
            }

            return render(request, 'transfers_telephone.html', example)
        else:
            return go_pin(request)
    else:
        return go_pin(request)
    
def get_card_info(request):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        if parsed_referer.netloc == current_domain:
            if request.method == 'POST':
                if request.user.is_authenticated:
                    data = json.loads(request.body)
                    type_card = data.get('type_card')
                    number_card = data.get('number_card')
                    result = find_account_by_subscription_and_last_four_digits(request.user, [type_card, number_card])
                    card = DebitCard.objects.get(account=result[0])
                    if card.account.user != request.user:
                        return
                    info = {
                        "type": card.subscription.name,
                        "balance": card.account.balance,
                        "number": card.card_number,
                        "date": card.expiration_date,
                        "cvv": card.cvv,
                        "is_frozen": card.frozen
                    }
                    return JsonResponse({'status': 'success', 'message': info}, content_type="application/json")
        else:
            return go_pin(request)
    else:
        return go_pin(request)      

def operations_view(request):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        parsed_referer = urlparse(referer)
        current_domain = request.get_host()
        if parsed_referer.netloc == current_domain:
            if request.method == 'POST':
                if request.user.is_authenticated:
                    user = request.user
                    transactions_data = []
                    print(123)

                    transactions = Transaction.objects.filter(from_account__user=user)

                    for transaction in transactions:
                        card = DebitCard.objects.filter(account=transaction.from_account).first()
                        deposit = Deposit.objects.filter(account=transaction.from_account).first()

                        if card:
                            transaction_info = {
                                'name': card.card_number,
                                'subscription': card.subscription.name,
                                'amount': transaction.amount
                            }
                        elif deposit:
                            transaction_info = {
                                'name': deposit.account.account_number,
                                'subscription_name': deposit.condition.name,
                                'amount': transaction.amount
                            }

                        transactions_data.append(transaction_info)
                    print(transactions_data)
                    return JsonResponse(transactions_data, safe=False)
        
            return render(request, 'operations.html')
        else:
            return go_pin(request)
    else:
        return go_pin(request) 