from django.db import IntegrityError, models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self,phone, email, name, surname, middle_name, passport_serial, passport_number, passport_issue_date, passport_issuer, birth_date, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(name=name, surname=surname, middle_name=middle_name, phone=phone, passport_series=passport_serial, passport_number=passport_number, birth_date=birth_date, passport_issue_date=passport_issue_date, passport_issuer=passport_issuer,  email=email, **extra_fields)
        user.set_password(password)
        try:
            user.save(using=self._db)
        except IntegrityError:
            return('Этот номер телефона или почта уже зарегистрированы')
        return user
    
    def create_superuser(self, phone=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if phone is None:
            phone = input('Enter phone: ')
        if email is None:
            email = input('Enter email: ')
        if password is None:
            password = input('Enter password: ')
        if extra_fields.get('name') is None:
            extra_fields['name'] = input('Enter name: ')
        if extra_fields.get('surname') is None:
            extra_fields['surname'] = input('Enter surname: ')
        if extra_fields.get('middle_name') is None:
            extra_fields['middle_name'] = input('Enter middle name: ')
        if extra_fields.get('passport_serial') is None:
            extra_fields['passport_serial'] = input('Enter passport seriel: ')
        if extra_fields.get('passport_number') is None:
            extra_fields['passport_number'] = input('Enter passport number: ')
        if extra_fields.get('birth_date') is None:
            extra_fields['birth_date'] = input('Enter birth date (YYYY-MM-DD): ')
        if extra_fields.get('passport_issue_date') is None:
            extra_fields['passport_issue_date'] = input('Enter passport issue date (YYYY-MM-DD): ')
        if extra_fields.get('passport_issuer') is None:
            extra_fields['passport_issuer'] = input('Enter passport issuer: ')
        if extra_fields.get('pin') is None:
            extra_fields['pin'] = input('Enter PIN code: ')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, email=email, password=password, **extra_fields)
    
    def get_all_cards(self):
        from your_bank.models import DebitCard
        return DebitCard.objects.filter(account__user=self)

    def get_all_deposits(self):
        from your_bank.models import Deposit
        return Deposit.objects.filter(account__user=self)

    def get_all_assets(self):
        cards = self.get_all_cards()
        deposits = self.get_all_deposits()
        return list(cards) + list(deposits)

    
    def user_exists(self, phone, password):
        user = self.get(phone=phone)
        if user.check_password(password):
            return user
        return None


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False, verbose_name='Имя')
    surname = models.CharField(max_length=100, blank=False, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Отчество')
    
    phone = models.CharField(max_length=10, unique=True, blank=False, verbose_name='Телефон')
    email = models.CharField(max_length=50, unique=True, blank=False, verbose_name='Электронная почта')
    password = models.CharField(max_length=128, blank=False, verbose_name='Пароль')
    pin = models.CharField(max_length=4, blank=False, null=True, verbose_name='ПИН-КОД')
    telegram = models.BooleanField(default=False, verbose_name='Telegram')
    input_attempts = models.IntegerField(default=0, verbose_name='Количество вводов')

    passport_series = models.CharField(max_length=4, blank=False, verbose_name='Серия паспорта')
    passport_number = models.CharField(max_length=6, blank=False, verbose_name='Номер паспорта')
    birth_date = models.DateField(blank=False, null=False, verbose_name='Дата рождения')
    passport_issue_date = models.DateField(blank=False, null=False, verbose_name='Дата выдачи паспорта')
    passport_issuer = models.CharField(max_length=100, blank=False, verbose_name='Кем выдан паспорт')
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.phone
    
    def get_short_name(self):
        initial_name = f"{self.name[0]}." if self.name else ""
        initial_middle_name = f"{self.middle_name[0]}." if self.middle_name else ""
        return f"{self.surname} {initial_name}{initial_middle_name}"

