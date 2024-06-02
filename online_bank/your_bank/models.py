import random
from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone

from login.models import CustomUser

class Account(models.Model):
    account_number = models.CharField(max_length=20, primary_key=True, verbose_name='Номер счета')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Баланс')

    def __str__(self):
        return f"Account {self.account_number} for user {self.user.phone}"
    
    @classmethod
    def generate_unique_account_number(cls):
        while True:
            account_number = ''.join(random.choices('0123456789', k=20))
            if not cls.objects.filter(account_number=account_number).exists():
                return account_number

    @classmethod
    def create_account(cls, user):
        account_number = cls.generate_unique_account_number()
        account = cls.objects.create(account_number=account_number, user=user)
        account.save()
        return account
    
    def get_balance(self):
        try:
            return self.balance
        except:
            return None
        
    def deposit(self, amount):
        self.balance += amount
        self.save()
    
    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        else:
            return False
        
    def close_account(self):
        self.delete()

class Organization(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True, verbose_name='Номер счета')
    name = models.CharField(max_length=100, verbose_name='Название организации')

    def __str__(self):
        return self.name

class Subscription(models.Model):
    name = models.CharField(max_length=100, primary_key=True, verbose_name='Название')
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ежемесячная стоимость')

    def __str__(self):
        return f"{self.name} - {self.monthly_cost}"
    
    @classmethod
    def create_subscription(cls, name, monthly_cost):
        subscription = cls.objects.create(name=name, monthly_cost=monthly_cost)
        return subscription
    
    @classmethod
    def get_all_subscriptions(cls):
        return list(cls.objects.order_by('-pk').values_list('name', flat=True))

    @classmethod
    def get_monthly_cost_by_name(cls, name):
        try:
            subscription = cls.objects.get(name=name)
            return subscription.monthly_cost
        except cls.DoesNotExist:
            return None
    
    def delete_subscription(self):
        self.delete()

    
class DebitCard(models.Model):
    card_number = models.CharField(max_length=16, primary_key=True, verbose_name='Номер карты')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Номер счета')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, verbose_name='Условия')
    frozen = models.BooleanField(default=False, verbose_name='Заморожена')
    expiration_date = models.CharField(max_length=5, verbose_name='Срок действия (MM/YY)')
    cvv = models.CharField(max_length=3, verbose_name='CVV код')
    pin_code = models.CharField(max_length=4, verbose_name='PIN код')

    def __str__(self):
        return f"Card {self.card_number} linked to account {self.account.account_number}"
    
    @classmethod
    def generate_unique_card_number(cls):
        while True:
            card_number = ''.join(random.choices('0123456789', k=16))
            if not cls.objects.filter(card_number=card_number).exists():
                return card_number
    
    @classmethod
    def generate_expiration_date(cls):
        now = datetime.now()
        future_date = now + timedelta(days=365 * 5)
        return future_date.strftime('%m/%y')
    
    @classmethod
    def generate_cvv(cls):
        return ''.join(random.choices('0123456789', k=3))
    
    @classmethod
    def create_card(cls, user, subscription, pin_code):
        card_number = cls.generate_unique_card_number()
        expiration_date = cls.generate_expiration_date()
        cvv = cls.generate_cvv()
        new_card = cls(
            card_number=card_number,
            account=Account.create_account(user),
            subscription=Subscription.objects.get(name=subscription),
            expiration_date=expiration_date,
            cvv=cvv,
            pin_code=pin_code
        )
        new_card.save()
        return new_card
    
    def freeze(self):
        try:
            self.frozen = True
            self.save()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        
    def unfreeze(self):
        try:
            self.frozen = False
            self.save()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def get_balance(self):
        return self.account.get_balance()
        
    def deposit(self, amount):
        self.account.deposit(amount)
        self.save()
    
    def withdraw(self, amount):
        return self.account.withdraw(amount)

    def close_card(self):
        self.delete()

class DepositCondition(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название условия')
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Процентная ставка')
    period_in_months = models.IntegerField(verbose_name='Период в месяцах действия')
    early_closure_allowed = models.BooleanField(default=False, verbose_name='Возможно ли закрыть досрочно')

    def __str__(self):
        return f"{self.name} - {self.interest_rate}% на {self.period_in_months} месяцев"
    
    @classmethod
    def create_condition(cls, name, interest_rate, period_in_months, early_closure_allowed):
        condition = cls(
            name=name,
            interest_rate=interest_rate,
            period_in_months=period_in_months,
            early_closure_allowed=early_closure_allowed
        )
        condition.save()
        return condition
    
    @classmethod
    def get_all_names(cls):
        return list(cls.objects.values_list('name', flat=True))
    
    @classmethod
    def get_condition_by_name(cls, name):
        try:
            condition = cls.objects.get(name=name)
            return {
                'procent': condition.interest_rate,
                'period': condition.period_in_months,
                'close': condition.early_closure_allowed
            }
        except cls.DoesNotExist:
            return None

class Deposit(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE, verbose_name='Номер счета')
    opening_date = models.DateField(default=timezone.now, verbose_name='Дата открытия')
    condition = models.ForeignKey('DepositCondition', on_delete=models.CASCADE, verbose_name='Условия депозита')

    def __str__(self):
        return f"Deposit for account {self.account.account_number} under condition {self.condition.name}"

    @classmethod
    def create_deposit(cls, user, condition_id):
        condition = DepositCondition.objects.get(id=condition_id)
        new_deposit = cls(
            account=Account.create_account(user),
            condition=condition
        )
        new_deposit.save()
        return new_deposit

    def get_balance(self):
        return self.account.get_balance()

    def deposit(self, amount):
        self.account.deposit(amount)
        self.save()

    def withdraw(self, amount):
        if not self.condition.early_closure_allowed:
            maturity_date = self.opening_date + timedelta(days=30 * self.condition.period_in_months)
            if timezone.now().date() < maturity_date:
                raise ValueError("Withdrawal is not allowed before the maturity date.")
        return self.account.withdraw(amount)

    def close_deposit(self):
        if not self.condition.early_closure_allowed:
            maturity_date = self.opening_date + timedelta(days=30 * self.condition.period_in_months)
            if timezone.now().date() < maturity_date:
                raise ValueError("Closing deposit is not allowed before the maturity date.")
        self.delete()

    def get_deposit_info(self):
        return {
            "condition_name": self.condition.name,
            "interest_rate": self.condition.interest_rate,
            "balance": self.get_balance(),
        }

    @classmethod
    def get_all_deposits_info(cls, user_id):
        deposits = cls.objects.filter(account__user_id=user_id)
        return [deposit.get_deposit_info() for deposit in deposits]