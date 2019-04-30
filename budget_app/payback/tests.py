from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from datetime import date
import requests
import json
from decimal import *
from unittest.mock import Mock, patch
from itertools import cycle

from .forms import PaybackForm
from .models import Payback
from main.views import currency_converter
from main.models import Expense

# helper functions

def login(self):
    """ Logs in user created in setUp """
    return self.client.login(username='Georgie', password='12345678')

def payback_form_data(self):
    return {
        'date': date.today(),
        'who_from': 'Georgie',
        'who_to': 'Tristan',
        'amount': 50,
        'currency': 'GBP',
        'method': 'Bank_transfer'
    }

def create_payback(self):
    return Payback.objects.create(
        date=date.today(),
        amount=10,
        who_from="Claire",
        who_to="Tristan",
        currency="GBP",
        GBP=10,
        ILS=40,
        AUD=20,
        method='Cash'
    )

# tests

class PaybackTests(TestCase):

    @classmethod
    def setUp(cls):
        User.objects.create_user('Georgie', 'email@email.com', '12345678')

    def test_login_required_to_access_payback_page(self):
        response = self.client.get(reverse('overview'))
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'payback.html')

    def test_payback_url_exists_at_desired_location_and_uses_correct_template(self):
        login(self)
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payback.html')

    def test_login_required_to_access_payback_form(self):
        response = self.client.get(reverse('payback_form'))
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'payback_form.html')

    def test_payback_form_url_exists_at_desired_location_and_uses_correct_template(self):
        login(self)
        response = self.client.get(reverse('payback_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payback_form.html')

    def test_payback_form(self):
        form = PaybackForm(data=payback_form_data(self))
        self.assertTrue(form.is_valid())

    def test_error_message_displayed_if_form_not_valid(self):
        form = PaybackForm(data={
            'date': 'Tomorrow',
            'who_from': 'Georgie',
            'who_to': 'Tristan',
            'amount': 50,
            'currency': 'GBP',
            'method': 'Bank_transfer'
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors['date'], ['Enter a valid date.'])

    def test_submitting_payback_form_generates_success_message_and_redirects_to_payment_overview(self):
        login(self)
        response = self.client.post("/payback/payback_form", payback_form_data(self))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Payback successfully recorded.")
        self.assertRedirects(response, "/payback/overview")


class BalancesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """ Creates three users and three expense objects """

        User.objects.create_user('Claire', 'claire@email.com', '12345678')
        User.objects.create_user('Georgie', 'georgie@email.com', '12345678')
        User.objects.create_user('Tristan', 'tristan@email.com', '12345678')

        Expense.objects.create(
            date=date.today(),
            description="Test balance 2",
            category="Food",
            amount=10,
            converted_amount=10,
            currency="GBP",
            who_for="Everyone",
            who_paid="Claire"
        )
        Expense.objects.create(
            date=date.today(),
            description="Test balance 1",
            category="Food",
            amount=20,
            converted_amount=20,
            currency="GBP",
            who_for="Everyone",
            who_paid="Georgie"
        )
        Expense.objects.create(
            date=date.today(),
            description="Test balance 3",
            category="Food",
            amount=30,
            converted_amount=30,
            currency="GBP",
            who_for="Everyone",
            who_paid="Tristan"
        )

    @patch('payback.views.currency_converter')
    def test_balances_from_expenses(self, mock_currency_converter):
        mock_currency_converter.side_effect = cycle((
            Decimal(4.0),
            Decimal(2.0),
        ))
        login(self)
        response = self.client.get(reverse('overview'))
        balances = response.context['balances']
        self.assertEqual(
            balances['Claire'], (Decimal(-10), Decimal(-40), Decimal(-20)))
        self.assertEqual(
            balances['Georgie'], (Decimal(0), Decimal(0), Decimal(0)))
        self.assertEqual(
            balances['Tristan'], (Decimal(10), Decimal(40), Decimal(20)))

    @patch('payback.views.currency_converter')
    def test_balances_with_payback(self, mock_currency_converter):
        mock_currency_converter.side_effect = cycle((
            Decimal(4.0),
            Decimal(2.0),
        ))
        create_payback(self)
        login(self)
        response = self.client.get(reverse('overview'))
        balances = response.context['balances']
        self.assertEqual(
            balances['Claire'], (Decimal(0), Decimal(0), Decimal(0)))
        self.assertEqual(
            balances['Georgie'], (Decimal(0), Decimal(0), Decimal(0)))
        self.assertEqual(
            balances['Tristan'], (Decimal(0), Decimal(0), Decimal(0)))

# tests for generic update and delete views

class EditViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user('Georgie', 'georgie@email.com', '12345678')
        User.objects.create_user('Claire', 'claire@email.com', '12345678')
        User.objects.create_user('Tristan', 'tristan@email.com', '12345678')

    def test_update_payback_url_exists_at_desired_location_and_uses_correct_template(self):
        payback = create_payback(self)
        login(self)
        response = self.client.get(
            reverse('payback_update', kwargs={'pk': payback.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payback/payback_update_form.html')

    def test_login_required_to_access_payback_update_form(self):
        payback = create_payback(self)
        response = self.client.get(
            reverse('payback_update', kwargs={'pk': payback.pk}))
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(
            response, 'payback/payback_update_form.html')

    def test_updating_payment_generates_success_message_and_redirects_to_overview(self):
        payback = create_payback(self)
        login(self)
        response = self.client.post(
            reverse('payback_update', kwargs={'pk': payback.pk}), {
            'date': date.today(),
            'who_from': 'Georgie',
            'who_to': 'Tristan',
            'amount': 10,
            'currency': 'GBP',
            'method': 'Cash'
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Payback successfully updated.")
        self.assertRedirects(response, reverse("overview"))

    def test_delete_payback_url_exists_at_desired_location_and_uses_correct_template(self):
        payback = create_payback(self)
        login(self)
        response = self.client.get(
            reverse('payback_delete', kwargs={'pk': payback.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payback/payback_delete_form.html')

    def test_login_required_to_delete_payback(self):
        payback = create_payback(self)
        response = self.client.get(
            reverse('payback_delete', kwargs={'pk': payback.pk}))
        self.assertNotEqual(response.status_code, 200)

    def test_deleting_payment_generates_success_message_and_redirects_to_overview(self):
        payback = create_payback(self)
        login(self)
        response = self.client.post(
            reverse('payback_delete', kwargs={'pk': payback.pk}
        ))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Payback successfully deleted.")
        self.assertRedirects(response, reverse("overview"))






