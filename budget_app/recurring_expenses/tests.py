from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from datetime import date, timedelta
from unittest.mock import patch
from decimal import *

from .forms import RecurringForm
from .models import Recurring
from main.models import Expense
from main.add_recurring_expenses import *

# Helper functions

def login(self):
    """ Logs in user created in setUp """
    return self.client.login(username='Georgie', password='12345678')

def recurring_form_data(self):
    """ Returns dummy data for RecurringForm"""
    return {
        'start_date': date.today(),
        'how_often': 'Weekly',
        'description': 'Internet',
        'category': 'Bills',
        'amount': 50,
        'currency': 'GBP',
        'who_for': 'Everyone',
        'who_paid': 'Georgie',
    }

def get_recurring_expense(self, description):
    return Recurring.objects.get(description=description)

# Tests

class RecurringUrlAndFormTests(TestCase):

    @classmethod
    def setUp(cls):
        User.objects.create_user('Georgie', 'email@email.com', '12345678')

    def test_login_required_to_access_scheduled_expenses_page(self):
        response = self.client.get(reverse('scheduled'))
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'scheduled.html')

    def test_payback_url_exists_at_desired_location_and_uses_correct_template(self):
        login(self)
        response = self.client.get(reverse('scheduled'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduled.html')

    def test_login_required_to_access_recurring_expense_form(self):
        response = self.client.get(reverse('recurring_form'))
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'recurring_form.html')

    def test_recurring_expense_form_url_exists_at_desired_location_and_uses_correct_template(self):
        login(self)
        response = self.client.get(reverse('recurring_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recurring_form.html')

    def test_recurring_form(self):
        form = RecurringForm(data=recurring_form_data(self))
        self.assertTrue(form.is_valid())

    def test_error_message_displayed_if_form_not_valid(self):
        form = RecurringForm(data={
            'start_date': '2019-01-40',
            'how_often': 'Weekly',
            'description': 'Internet',
            'category': 'Bills',
            'amount': 50,
            'currency': 'GBP',
            'who_for': 'Everyone',
            'who_paid': 'Georgie',
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors['start_date'], ['Enter a valid date.'])

    def test_submitting_recurring_expense_form_generates_success_message_and_redirects_to_scheduled_expenses_page(self):
        login(self)
        response = self.client.post(
            reverse('recurring_form'), recurring_form_data(self))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Recurring expense successfully added.")
        self.assertRedirects(response, reverse("scheduled"))

class ScheduledExpenses(TestCase):
    @classmethod
    def setUp(cls):
        User.objects.create_user('Georgie', 'email@email.com', '12345678')

        Recurring.objects.create(
            start_date='2019-01-01',
            next_date='2019-01-01',
            how_often='Weekly',
            description="Test bill",
            category="Bills",
            amount=100,
            currency="ILS",
            who_for="Everyone",
            who_paid="Georgie"
        )

    def test_recurring_expense_added_to_scheduled_expenses(self):
        recurring_expense = get_recurring_expense(self, "Test bill")
        login(self)
        response = self.client.get(reverse('scheduled'))
        self.assertEqual(
            response.context['scheduled_expenses'][0], recurring_expense)

    def test_delete_recurring_expense_url_exists_at_desired_location_and_uses_correct_template(self):
        recurring_expense = get_recurring_expense(self, "Test bill")
        login(self)
        response = self.client.get(
            reverse('recurring_delete', kwargs={'pk': recurring_expense.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,'recurring_expenses/recurring_delete_form.html')

    def test_login_required_to_delete_recurring_expense(self):
        recurring_expense = get_recurring_expense(self, "Test bill")
        response = self.client.get(
            reverse('recurring_delete', kwargs={'pk': recurring_expense.pk}))
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(
            response,'recurring_expenses/recurring_delete_form.html')

    def test_deleting_recurring_expense_generates_success_message_and_redirects_to_overview(self):
        recurring_expense = get_recurring_expense(self, "Test bill")
        login(self)
        response = self.client.post(
            reverse('recurring_delete', kwargs={'pk': recurring_expense.pk}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Recurring expense successfully deleted.")
        self.assertRedirects(response, reverse("scheduled"))

    def test_deleted_recurring_expense_not_found_in_scheduled_expenses(self):
        recurring_expense = get_recurring_expense(self, "Test bill")
        login(self)
        self.client.post(
            reverse('recurring_delete', kwargs={'pk': recurring_expense.pk}))
        response = self.client.get(reverse('scheduled'))
        self.assertEqual(len(response.context['scheduled_expenses']), 0)


class AddRecurringExpensesInPast(TestCase):
    @classmethod
    def setUp(cls):
        """ Create 3 recurring expenses starting in the past """
        Recurring.objects.create(
            start_date='2019-01-01',
            next_date='2019-01-01',
            how_often='Weekly',
            description="Test bill 1",
            category="Bills",
            amount=100,
            currency="GBP",
            who_for="Everyone",
            who_paid="Georgie"
        )
        Recurring.objects.create(
            start_date='2019-01-01',
            next_date='2019-01-01',
            how_often='Fortnightly',
            description="Test bill 2",
            category="Bills",
            amount=150,
            currency="GBP",
            who_for="Everyone",
            who_paid="Georgie"
        )
        Recurring.objects.create(
            start_date='2019-01-01',
            next_date='2019-01-01',
            how_often='Monthly',
            description="Test bill 3",
            category="Bills",
            amount=200,
            currency="GBP",
            who_for="Everyone",
            who_paid="Georgie"
        )

    def test_next_date_calculated_correctly_for_weekly_fortnightly_and_monthly_expenses(self):
        add_scheduled_expenses()
        response_1 = get_recurring_expense(self, 'Test bill 1')
        response_2 = get_recurring_expense(self, 'Test bill 2')
        response_3 = get_recurring_expense(self, 'Test bill 3')
        self.assertEqual(response_1.next_date, date(2019, 1, 8))
        self.assertEqual(response_2.next_date, date(2019, 1, 15))
        self.assertEqual(response_3.next_date, date(2019, 2, 1))

    def test_recurring_expense_added_to_Expense_if_next_date_is_in_the_past(self):
        bill_1 = get_recurring_expense(self, 'Test bill 1')
        add_scheduled_expenses()
        response = Expense.objects.get(description='Test bill 1')
        self.assertEqual(response.description, bill_1.description)

    def test_if_currency_is_GBP_converted_amount_equals_amount(self):
        bill_1 = get_recurring_expense(self, 'Test bill 1')
        add_recurring_expense(bill_1)
        response = Expense.objects.get(description='Test bill 1')
        self.assertEqual(response.converted_amount, bill_1.amount)

class AddRecurringExpensesFromToday(TestCase):
    def test_recurring_expense_added_to_Expense_if_next_date_is_today(self):
        bill = Recurring.objects.create(
            start_date=date.today(),
            next_date=date.today(),
            how_often='Weekly',
            description="Test bill 4",
            category="Bills",
            amount=100,
            currency="GBP",
            who_for="Everyone",
            who_paid="Georgie"
        )
        add_scheduled_expenses()
        response = Expense.objects.get(description='Test bill 4')
        self.assertEqual(response.description, bill.description)

class AddRecurringExpensesInILS(TestCase):
    @patch('main.add_recurring_expenses.currency_converter')
    def test_if_currency_is_not_GBP_converted_amount_is_calculated_correctly(self, mock_currency_converter):
        mock_currency_converter.return_value = Decimal(0.25)
        bill = Recurring.objects.create(
            start_date=date.today(),
            next_date=date.today(),
            how_often='Weekly',
            description="Test bill 5",
            category="Bills",
            amount=100,
            currency="ILS",
            who_for="Everyone",
            who_paid="Georgie"
        )
        add_recurring_expense(bill)
        response = Expense.objects.get(description='Test bill 5')
        self.assertEqual(response.converted_amount, Decimal(25.0))

class AddRecurringExpensesInFuture(TestCase):
    def test_recurring_expense_not_added_to_Expense_if_next_date_is_in_the_future(self):
        bill = Recurring.objects.create(
            start_date=date.today() + timedelta(days=1),
            next_date=date.today() + timedelta(days=1),
            how_often='Weekly',
            description="Test bill 6",
            category="Bills",
            amount=100,
            currency="GBP",
            who_for="Everyone",
            who_paid="Georgie"
        )
        add_scheduled_expenses()
        response = Expense.objects.all()
        self.assertEqual(len(response), 0)


