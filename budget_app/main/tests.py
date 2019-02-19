from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from datetime import date, timedelta
import requests
from unittest.mock import Mock, patch
import json
from decimal import *

from .models import Expense
from .forms import ExpenseForm
from .views import get_exchange_rate

    # Helper functions

def login(self):
    """ Logs in user created in setUp """
    return self.client.login(username='Georgie', password='12345678')

def dummy_family_expenses(self):
    """ Returns list of converted amounts for three dummy expenses """
    expenses = [
        Expense.objects.get(description='Test 1'),
        Expense.objects.get(description='Test 2'),
        Expense.objects.get(description='Test 3')
    ]
    return [expense.converted_amount for expense in expenses]

def add_expense_data(self):
    return {
        'date': date.today(),
        'description': 'Shopping',
        'category': 'Food',
        'amount': 50,
        'currency': 'GBP',
        'who_for': 'Everyone',
        'who_paid': 'Georgie'
    }

def month_year(self, expense):
    (month, year) = (
            expense.date.strftime("%b"),
            expense.date.strftime("%Y")
        )
    month_year_bytes = (month + ', ' + year).encode('utf-8')
    return [(month, year), month_year_bytes]


# tests for home view

class FamilyExpensesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """ Creates a dummy user and three expense objects """
        User.objects.create_user(
            'Georgie', 'email@email.com', '12345678'
        )
        Expense.objects.create(
            date=date.today(),
            description="Test 1",
            category="Food",
            amount=50,
            converted_amount=10,
            currency="ILS",
            who_for="Everyone",
            who_paid="Georgie"
        )
        Expense.objects.create(
            date=date.today().replace(day=1),
            description="Test 2",
            category="Food",
            amount=100,
            converted_amount=20,
            currency="ILS",
            who_for="Everyone",
            who_paid="Georgie"
        )
        Expense.objects.create(
            date=date.today().replace(day=10),
            description="Test 3",
            category="Baby",
            amount=50,
            converted_amount=50,
            currency="GBP",
            who_for="Everyone",
            who_paid="Tristan"
        )

    # Class tests: home page

    def test_login_required_to_access_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'home.html')

    def test_home_url_exists_at_desired_location_and_uses_correct_template(self):
        login(self)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_expenses_within_a_category_are_added_to_category_total(self):
        login(self)
        expense_1, expense_2, expense_3 = dummy_family_expenses(self)
        response = self.client.get(reverse('home'))
        category_totals_dict = response.context['category_totals_dict']
        self.assertEqual(
            category_totals_dict['Food'], expense_1+expense_2)
        self.assertEqual(
            category_totals_dict['Baby'], expense_3)

    def test_expenses_for_everyone_are_summed_to_give_family_total(self):
        login(self)
        response = self.client.get(reverse('home'))
        self.assertEqual(
            response.context['family_total'], sum(dummy_family_expenses(self)))

    def test_expenses_paid_for_are_attributed_to_correct_user_and_summed(self):
        login(self)
        expense_1, expense_2, expense_3 = dummy_family_expenses(self)
        response = self.client.get(reverse('home'))
        amount_paid_dict = response.context['amount_paid_dict']
        self.assertEqual(
            amount_paid_dict['Georgie'], expense_1+expense_2)
        self.assertEqual(
            amount_paid_dict['Tristan'], expense_3)

    def test_month_added_to_drop_down_list(self):
        login(self)
        expense_1 = Expense.objects.get(description='Test 1')
        mon_year, mon_year_bytes =  month_year(self, expense_1)
        response = self.client.get(reverse('home'))
        self.assertEqual(
            [mon_year], response.context['months'])
        self.assertIn(mon_year_bytes, response.content)


# test for individual expenses

class IndividualExpenses(TestCase):

    def setUp(self):
        """ Create a user and two individual expenses """
        User.objects.create_user(
            'Georgie', 'email@email.com', '12345678'
        )
        Expense.objects.create(
            date=date.today(),
            description="Test 4",
            category="Hobbies",
            amount=50,
            converted_amount=10,
            currency="ILS",
            who_for="Georgie",
            who_paid="Georgie"
        )
        Expense.objects.create(
            date=date.today().replace(day=1),
            description="Test 5",
            category="Travel",
            amount=100,
            converted_amount=20,
            currency="ILS",
            who_for="Georgie",
            who_paid="Georgie"
        )

    def test_individual_expenses_added_to_correct_user_and_summed(self):
        login(self)
        expense_4 = Expense.objects.get(description="Test 4")
        expense_5 = Expense.objects.get(description="Test 5")
        response = self.client.get(reverse('home'))
        individual_expenses_dict = response.context['individual_expenses_dict']
        self.assertEqual(
            individual_expenses_dict['Georgie'],
            expense_4.converted_amount + expense_5.converted_amount
        )

# tests for add_expenses view

class AddExpenses(TestCase):

    @classmethod
    def setUp(cls):
        User.objects.create_user(
            'Georgie', 'email@email.com', '12345678'
        )

    def test_add_expense_url_exists_at_desired_location_and_uses_correct_template(self):
        login(self)
        response = self.client.get(reverse('add_expense'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_expense.html')

    def test_login_required_to_access_add_expense_page(self):
        response = self.client.get(reverse('add_expense'))
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'add_expense.html')

    def test_add_expense_form(self):
        form = ExpenseForm(data=add_expense_data(self))
        self.assertTrue(form.is_valid())

    def test_error_message_displayed_if_form_not_valid(self):
        form = ExpenseForm(data={
            'date': 'Tomorrow',
            'description': 'Shopping',
            'category': 'Food',
            'amount': 50,
            'currency': 'GBP',
            'who_for': 'Everyone',
            'who_paid': 'Georgie'
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors['date'], ['Enter a valid date.'])

    def test_submitting_form_generates_success_message_and_redirect_to_home(self):
        login(self)
        response = self.client.post("/add_expense/", add_expense_data(self))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Expense successfully added.")
        self.assertRedirects(response, "/")

    def test_if_currency_is_GBP_converted_amount_equal_to_amount(self):
        login(self)
        self.client.post("/add_expense/", add_expense_data(self)
        )
        response = Expense.objects.get(description='Shopping')
        self.assertEqual(response.converted_amount, response.amount)

    @patch('main.views.requests.get')
    def test_get_exchange_rate(self, mock_get):
        date = 2019-2-15
        rate_data = {
            "base":"EUR",
            "date":"2019-02-15",
            "rates":{"GBP":1.0,"ILS":4.0}
        }
        mock_get.return_value = Mock(content=json.dumps(rate_data))
        response = get_exchange_rate(date)
        self.assertEqual(response, 0.25)

    @patch('main.views.get_exchange_rate')
    def test_if_currency_is_ILS_amount_is_converted_to_pounds(self, mock_get_exchange_rate):
        mock_get_exchange_rate.return_value = Mock()
        mock_get_exchange_rate.return_value = Decimal(0.25)
        login(self)
        self.client.post("/add_expense/", {
                'date': date.today(),
                'description': 'Shopping',
                'category': 'Food',
                'amount': 50,
                'currency': 'ILS',
                'who_for': 'Everyone',
                'who_paid': 'Georgie'
            }
        )
        response = Expense.objects.get(description='Shopping')
        self.assertTrue(mock_get_exchange_rate.called)
        self.assertEqual(
            response.converted_amount, response.amount*Decimal(0.25))

    def test_expenses_from_past_month_added_to_dropdown_but_not_home_page(self):
        login(self)
        past_expense = Expense.objects.create(
            date=date(2018, 12, 31),
            description="Expense from past month",
            category="Food",
            amount=50,
            converted_amount=10,
            currency="ILS",
            who_for="Everyone",
            who_paid="Georgie"
        )
        mon_year, mon_year_bytes =  month_year(self, past_expense)
        response = self.client.get(reverse('home'))
        self.assertEqual(
            [mon_year], response.context['months'])
        self.assertIn(mon_year_bytes, response.content)
        self.assertEqual(response.context['family_total'], 0)


    def test_date_in_future_raises_error(self):
        login(self)
        form = ExpenseForm(data={
            'date': date.today() + timedelta(days=1),
            'description': 'Shopping',
            'category': 'Food',
            'amount': 50,
            'currency': 'GBP',
            'who_for': 'Everyone',
            'who_paid': 'Georgie'
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors['date'], ["Date can't be in the future."])





