from datetime import date, timedelta
import json
from django.contrib.auth import logout
import random
import string
from django.utils import timezone
import re
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404

from login.forms import LoginForm, PinCode, RegistrationForm
from login.models import CustomUser
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
import requests

def check_redirect(request):
    redirect_url = request.session.get('redirect_url')
    return JsonResponse({'redirect_url': redirect_url})

def update_user_sessions(user_id, key, value):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in sessions:
        data = session.get_decoded()
        if str(user_id) == str(data.get('_auth_user_id')):
            data[key] = value
            session.session_data = Session.objects.encode(data)
            session.save()

def generate_unique_code(num):
    code = ''.join(random.choices(string.digits, k=num))
    return code

@csrf_exempt
def local_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if user_id:
            user = get_object_or_404(CustomUser, id=user_id)
            if user:
                user.telegram = True
                user.save()
            update_user_sessions(user_id, 'redirect_url', '/your_bank')
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'User ID not provided'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def registration_view(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next', '/your_bank/')
        return redirect(next_url)
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            if len(password) < 8:
                return JsonResponse({'success':False, 'error': "Простой пароль", 'error_elemenet':'password'})
            retry_password = form.cleaned_data['retry_password']
            if password != retry_password:
                return JsonResponse({'success':False, 'error': "Пароли не совпадают", 'error_elemenet':'password'})
            phone = form.cleaned_data['phone']
            if len(phone) > 15:
                return JsonResponse({'success':False, 'error': "Неверный номер телефона", 'error_elemenet':'phone'})
            email = form.cleaned_data['email']
            if len(email) > 50:
                return JsonResponse({'success':False, 'error': "Неверный Email", 'error_elemenet':'email'})
            pattern = re.compile(r'[^А-Яа-я\s]')
            name = form.cleaned_data['name']
            if pattern.search(name) or len(name) > 100:
                return JsonResponse({'success':False, 'error': "Неверное имя", 'error_elemenet':'name'})
            surname = form.cleaned_data['surname']
            if pattern.search(surname) or len(surname) > 100:
                return JsonResponse({'success':False, 'error': "Неверная фамилия", 'error_elemenet':'surname'})
            middle_name = form.cleaned_data['middle_name']
            if middle_name != "":
                if pattern.search(middle_name) or len(middle_name) > 100:
                    return JsonResponse({'success':False, 'error': "Неверное отчество", 'error_elemenet':'middle_name'})
            passport_serial = form.cleaned_data['passport_serial']
            if len(passport_serial) != 4 or not passport_serial.isdigit():
                return JsonResponse({'success':False, 'error': "Неверная серия паспорта", 'error_elemenet':'passport_serial'})
            passport_number = form.cleaned_data['passport_number']
            if len(passport_number) != 6 or not passport_number.isdigit():
                return JsonResponse({'success':False, 'error': "Неверный номер паспорта", 'error_elemenet':'passport_number'})
            passport_issue_date = form.cleaned_data['passport_issue_date']
            if (passport_issue_date > date.today()) or (passport_issue_date < date.today() - timedelta(days=110*365)):
                return JsonResponse({'success':False, 'error': "Неверная дата выдачи паспорта", 'error_elemenet':'passport_issue_date'})
            passport_issuer = form.cleaned_data['passport_issuer']
            if len(passport_issuer) > 100:
                return JsonResponse({'success':False, 'error': "Неверно указано кем выдан паспорт", 'error_elemenet':'passport_issuer'})
            birth_date = form.cleaned_data['birth_date']
            if (birth_date > date.today() - timedelta(days=14*365)) or (birth_date < date.today() - timedelta(days=110*365)):
                return JsonResponse({'success':False, 'error': "Неверная дата рождения", 'error_elemenet':'birth_date'})
            user = CustomUser.objects.create_user(name=name.capitalize(), surname=surname.capitalize(), middle_name=middle_name.capitalize(), phone=phone, passport_serial=passport_serial, passport_number=passport_number, birth_date=birth_date, passport_issue_date=passport_issue_date, passport_issuer=passport_issuer, password=password,email=email)
            if user == 'Этот номер телефона или почта уже зарегистрированы':
                return JsonResponse({'success':False, 'error': "Этот номер телефона или почта уже зарегистрированы", 'error_elemenet':'phone', 'or_error_elemenet':'email'})
            else:
                login(request, user)
                user.is_active = True
                CustomUser.objects.filter(pk=user.pk).update(last_login=timezone.now())
                user.save()
                return JsonResponse({'success':True, 'next_url': "/login/pin-code/"})
        else:
            pass
    else:
        form = RegistrationForm()
    
    return render(request, 'registration.html', {'form': form})

def pin_view(request):
    if not request.user.is_authenticated:
        next_url = request.GET.get('next', '/')
        return redirect(next_url)
    if request.method == 'POST':
        form = PinCode(request.POST)
        if form.is_valid():
            arr = [False, False, False, False]
            one = form.cleaned_data['one']
            if len(one) != 1 or not one.isdigit():
                arr[0] = True
            two = form.cleaned_data['two']
            if len(two) != 1 or not two.isdigit():
                arr[1] = True
            three = form.cleaned_data['three']
            if len(three) != 1 or not three.isdigit():
                arr[2] = True
            four = form.cleaned_data['four']
            if len(four) != 1 or not four.isdigit():
                arr[3] = True
            if True in arr:
                return JsonResponse({'success':False, 'one':arr[0], 'two':arr[1], 'three':arr[2], 'four':arr[3]})
            else:
                user = request.user
                if user.pin == None or user.pin != one + two + three + four:
                    request.user.input_attempts +=1
                    print(request.user.input_attempts)
                    request.user.save()
                    
                    if request.user.input_attempts == 5:
                        request.user.pin = None
                        request.user.input_attempts = 0
                        request.user.save()
                        logout(request)
                        return JsonResponse({'success':True, 'next_url': "/login"})
                    return JsonResponse({'success':False, 'one':True, 'two':True, 'three':True, 'four':True})
                else:
                    request.user.input_attempts = 0
                    request.user.pin = None
                    request.user.save()
                    return JsonResponse({'success':True, 'next_url': "/your_bank"})
    user_id = request.user.id
    headers = {
        'Content-Type': 'application/json'
    }
    if request.user.telegram == True:
        pin = generate_unique_code(4)
        request.user.pin = pin
        request.user.save()

        form = PinCode()
        form.text = "Введите код"
        data = {
        'number': pin,
        'user_id': user_id
        }
        response = requests.post('http://localhost:5000/send_message', json=data, headers=headers)

        if response.status_code == 200:
            return render(request, 'pin.html', {'form': form})
        else:
            return JsonResponse({'error': 'Failed to send message'}, status=500)
    else:
        pin = generate_unique_code(8)
        context = {
            'form': {
                'text': 'Введите код в телеграм-бот',
                'pin': pin
            }
        }
        data = {
        'number': pin,
        'user_id': user_id
        }
        response = requests.post('http://localhost:5000/send_message', json=data, headers=headers)

        if response.status_code == 200:
            return render(request, 'pin.html', context)
        else:
            return JsonResponse({'error': 'Failed to send message'}, status=500)

def login_view(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next', '/your_bank/')
        return redirect(next_url)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            if len(phone) > 15:
                return JsonResponse({'success':False, 'error': "Неверный номер телефона", 'error_elemenet':'phone'})
            password = form.cleaned_data['password']
            if len(password) < 8:
                return JsonResponse({'success':False, 'error': "Простой пароль", 'error_elemenet':'password'})

            user = authenticate(phone=phone, password=password)
            if user is not None:
                login(request, user)
                user.is_active = True
                CustomUser.objects.filter(pk=user.pk).update(last_login=timezone.now())
                user.save()
                return JsonResponse({'success':True, 'next_url': "pin-code/"})
            else:
                return JsonResponse({'success':False, 'error': "Неверный логин или пароль", 'error_elemenet':'password'})

        else:
            pass
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})
