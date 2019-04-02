from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from datetime import date
import requests
import json
from decimal import *

from .forms import PaybackForm
from .models import Payback
from main.views import get_exchange_rate

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

# tests

class Payback(TestCase):

    @classmethod
    def setUp(cls):
        User.objects.create_user(
            'Georgie', 'email@email.com', '12345678'
        )

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
        print(form)
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

    def test_submitting_form_generates_success_message_and_redirects_to_payment_overview(self):
        login(self)
        response = self.client.post("/payback/payback_form", payback_form_data(self))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Payback successfully recorded.")
        self.assertRedirects(response, "/payback/overview")

