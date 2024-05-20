from datetime import date, timedelta
from django.utils import timezone
import re
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser


from login.forms import LoginForm, PinCode, RegistrationForm
from login.models import CustomUser
from django.contrib.auth import authenticate, login

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
                return JsonResponse({'success':False, 'error': "Этот номер телефона или почта уже зарегистрированы", 'error_elemenet':'phone'})
            else:
                return JsonResponse({'success':True, 'next_url': "pin-code/"})
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
                if user.pin == None:
                    user.pin = one + two + three + four
                    user.save()
                else:
                    if user.pin != one + two + three + four:
                        return JsonResponse({'success':False, 'one':True, 'two':True, 'three':True, 'four':True})
                return JsonResponse({'success':True, 'next_url': "/your_bank"})



    form = PinCode()
    if request.user.pin == None:
        form.text = "Придумайте код"
    elif request.user.pin != None:
        form.text = "Введите код"
    
    return render(request, 'pin.html', {'form': form})

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
