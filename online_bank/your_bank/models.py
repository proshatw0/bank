import random
from django.db import models

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
    
    def delete_subscription(self):
        self.delete()
    
class DebitCard(models.Model):
    card_number = models.CharField(max_length=16, primary_key=True, verbose_name='Номер карты')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Номер счета')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, verbose_name='Условия')
    frozen = models.BooleanField(default=False, verbose_name='Заморожена')

    def __str__(self):
        return f"Card {self.card_number} linked to account {self.account.account_number}"
    
    @classmethod
    def generate_unique_card_number(cls):
        while True:
            card_number = ''.join(random.choices('0123456789', k=16))
            if not cls.objects.filter(card_number=card_number).exists():
                return card_number

    @classmethod
    def create_card(cls, user, subscription):
        card_number = cls.generate_unique_card_number()
        new_card = cls(card_number=card_number, account=Account.create_account(user), subscription=subscription)
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

class Deposit(models.Model):
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Процентная ставка')
    is_savings = models.BooleanField(default=False, verbose_name='Вид вклада')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Номер счета')

    def __str__(self):
        return f"Deposit with interest rate {self.interest_rate}% for account {self.account.account_number}"
    
    @classmethod
    def create_deposit(cls, user, interest_rate, is_savings):
        new_deposit = cls(interest_rate=interest_rate, account=Account.create_account(user), is_savings=is_savings)
        new_deposit.save()
        return new_deposit
    
    def get_balance(self):
        return self.account.get_balance()
        
    def deposit(self, amount):
        self.account.deposit(amount)
        self.save()
    
    def withdraw(self, amount):
        return self.account.withdraw(amount)
    
    def close_deposit(self):
        self.delete()