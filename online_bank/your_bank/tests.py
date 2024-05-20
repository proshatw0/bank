from django.test import TestCase
from login.models import CustomUser
from .models import Account, Subscription, DebitCard, Deposit

class ModelTests(TestCase):

    def setUp(self):
        # Создание пользователя для тестов
        self.user = CustomUser.objects.create_user(
            name='John',
            surname='Doe',
            middle_name='Middle',
            phone='1234567890',
            passport_serial='1234',
            passport_number='567890',
            birth_date='1990-01-01',
            passport_issue_date='2010-01-01',
            passport_issuer='Issuer',
            password='testpassword',
            email='test@example.com'
        )

    def test_generate_unique_account_number(self):
        account_number = Account.generate_unique_account_number()
        self.assertEqual(len(account_number), 20)
        self.assertFalse(Account.objects.filter(account_number=account_number).exists())

    def test_create_account(self):
        account = Account.create_account(self.user)
        self.assertIsNotNone(account.account_number)
        self.assertEqual(account.user, self.user)
        self.assertEqual(account.balance, 0)

    def test_get_balance(self):
        account = Account.create_account(self.user)
        self.assertEqual(account.get_balance(), 0)

    def test_deposit(self):
        account = Account.create_account(self.user)
        account.deposit(100)
        self.assertEqual(account.get_balance(), 100)

    def test_withdraw(self):
        account = Account.create_account(self.user)
        account.deposit(100)
        result = account.withdraw(50)
        self.assertTrue(result)
        self.assertEqual(account.get_balance(), 50)
        result = account.withdraw(100)
        self.assertFalse(result)
        self.assertEqual(account.get_balance(), 50)

    def test_close_account(self):
        account = Account.create_account(self.user)
        account_number = account.account_number
        account.close_account()
        self.assertFalse(Account.objects.filter(account_number=account_number).exists())

    def test_create_subscription(self):
        subscription = Subscription.create_subscription(name="Basic Plan", monthly_cost=9.99)
        self.assertIsNotNone(subscription.name)
        self.assertEqual(subscription.monthly_cost, 9.99)

    def test_delete_subscription(self):
        subscription = Subscription.create_subscription(name="Basic Plan", monthly_cost=9.99)
        subscription.delete_subscription()
        self.assertFalse(Subscription.objects.filter(name="Basic Plan").exists())

    def test_generate_unique_card_number(self):
        card_number = DebitCard.generate_unique_card_number()
        self.assertEqual(len(card_number), 16)
        self.assertFalse(DebitCard.objects.filter(card_number=card_number).exists())

    def test_create_card(self):
        subscription = Subscription.create_subscription(name="Basic Plan", monthly_cost=9.99)
        card = DebitCard.create_card(user=self.user, subscription=subscription)
        self.assertIsNotNone(card.card_number)
        self.assertEqual(card.account.user, self.user)
        self.assertEqual(card.subscription, subscription)

    def test_close_card(self):
        subscription = Subscription.create_subscription(name="Basic Plan", monthly_cost=9.99)
        card = DebitCard.create_card(user=self.user, subscription=subscription)
        card_number = card.card_number
        card.close_card()
        self.assertFalse(DebitCard.objects.filter(card_number=card_number).exists())

    def test_create_deposit(self):
        deposit = Deposit.create_deposit(user=self.user, interest_rate=2.5, is_savings=True)
        self.assertEqual(deposit.interest_rate, 2.5)
        self.assertTrue(deposit.is_savings)
        self.assertEqual(deposit.account.user, self.user)

    def test_get_deposit_balance(self):
        deposit = Deposit.create_deposit(user=self.user, interest_rate=2.5, is_savings=True)
        self.assertEqual(deposit.get_balance(), 0)

    def test_deposit_to_deposit(self):
        deposit = Deposit.create_deposit(user=self.user, interest_rate=2.5, is_savings=True)
        deposit.deposit(100)
        self.assertEqual(deposit.get_balance(), 100)

    def test_withdraw_from_deposit(self):
        deposit = Deposit.create_deposit(user=self.user, interest_rate=2.5, is_savings=True)
        deposit.deposit(100)
        result = deposit.withdraw(50)
        self.assertTrue(result)
        self.assertEqual(deposit.get_balance(), 50)
        result = deposit.withdraw(100)
        self.assertFalse(result)
        self.assertEqual(deposit.get_balance(), 50)

    def test_close_deposit(self):
        deposit = Deposit.create_deposit(user=self.user, interest_rate=2.5, is_savings=True)
        deposit_id = deposit.id
        deposit.close_deposit()
        self.assertFalse(Deposit.objects.filter(id=deposit_id).exists())
