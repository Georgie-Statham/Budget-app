from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from datetime import date

from main.models import Expense

# Helper functions

def login(self):
    """ Logs in user created in setUp """
    return self.client.login(username='Georgie', password='12345678')

def overview_response(self):
    """ Gets detailed_month url for Jan 2019 """
    return self.client.get(reverse_lazy(
            'detailed_month',
            kwargs={'month': 'Jan', 'year': '2019'}
        )
    )


def edit_view_response(self, url_name):
    """ Gets expense update or delete url """
    expense = Expense.objects.get(description='Test 1')
    response = self.client.get(
        reverse(url_name, kwargs={
        'pk': expense.pk,
        'month': 'Jan',
        'year': '2019'
    }))
    return response


# Tests

class HistoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """ Creates a dummy user and three expense objects """
        User.objects.create_user(
            'Georgie', 'email@email.com', '12345678'
        )
        Expense.objects.create(
            date="2019-01-01",
            description="Test 1",
            category="Food",
            amount=50,
            converted_amount=10,
            currency="ILS",
            who_for="Everyone",
            who_paid="Georgie"
        )
        Expense.objects.create(
            date="2019-01-05",
            description="Test 2",
            category="Food",
            amount=100,
            converted_amount=20,
            currency="ILS",
            who_for="Everyone",
            who_paid="Georgie"
        )
        Expense.objects.create(
            date="2019-01-10",
            description="Test 3",
            category="Baby",
            amount=50,
            converted_amount=50,
            currency="GBP",
            who_for="Everyone",
            who_paid="Tristan"
        )

    def detailed_month_exists_at_url_determined_by_expense_date(self):
        login(self)
        response = overview_response(self)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detailed_month.html')

    def test_login_required_to_access_history_pages(self):
        response = overview_response(self)
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'detailed_month.html')

    def test_expenses_in_month(self):
        login(self)
        response = overview_response(self)
        self.assertEqual(response.context['months'], [('Jan', '2019')])


    def test_expenses_within_a_category_are_added_to_category_total(self):
        login(self)
        response = overview_response(self)
        category_totals_dict = response.context['category_totals_dict']
        self.assertEqual(category_totals_dict['Food'], 30)
        self.assertEqual(category_totals_dict['Baby'], 50)

    def test_expenses_for_everyone_are_summed_to_give_family_total(self):
        login(self)
        response = overview_response(self)
        self.assertEqual(
            response.context['family_total'], 80)

    def test_expenses_paid_for_are_attributed_to_correct_user_and_summed(self):
        login(self)
        response = overview_response(self)
        amount_paid_dict = response.context['amount_paid_dict']
        self.assertEqual(
            amount_paid_dict['Georgie'], 30)
        self.assertEqual(
            amount_paid_dict['Tristan'], 50)


# Test for individual expenses

class IndividualExpenses(TestCase):

    def setUp(self):
        """ Create a user and two individual expenses """
        User.objects.create_user(
            'Georgie', 'email@email.com', '12345678'
        )
        Expense.objects.create(
            date='2019-01-02',
            description="Test 4",
            category="Hobbies",
            amount=50,
            converted_amount=10,
            currency="ILS",
            who_for="Georgie",
            who_paid="Georgie"
        )
        Expense.objects.create(
            date='2019-01-20',
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
        response = self.client.get(reverse_lazy(
            'detailed_month',
            kwargs={'month': 'Jan', 'year': '2019'}
        ))
        individual_breakdown = response.context['individual_breakdown']
        self.assertEqual(individual_breakdown['Georgie']['total'], 30)
        self.assertEqual(individual_breakdown['Georgie']['Hobbies'], 10)

# Tests for generic update and delete views

class EditViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """ Crested a user and an expense object """
        User.objects.create_user('Georgie', 'georgie@email.com', '12345678')

        Expense.objects.create(
            date="2019-01-01",
            description="Test 1",
            category="Food",
            amount=50,
            converted_amount=10,
            currency="ILS",
            who_for="Everyone",
            who_paid="Georgie"
        )

    def test_update_expense_url_exists_at_desired_location_and_uses_correct_template(self):
        login(self)
        response = edit_view_response(self, 'expense_update')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/expense_update_form.html')

    def test_login_required_to_access_expense_update_form(self):
        response = edit_view_response(self, 'expense_update')
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(
            response, 'expense/expense_update_form.html')

    def test_updating_payment_generates_success_message_and_redirects_to_overview(self):
        expense = Expense.objects.get(description='Test 1')
        login(self)
        response = self.client.post(
            reverse('expense_update', kwargs={'pk': expense.pk,
            'month': 'Jan',
            'year': '2019'
        }), {
            'date': "2019-01-01",
            'description': 'Test 1',
            'category': 'Food',
            'amount': 60,
            'currency': 'ILS',
            'who_for': 'Everyone',
            'who_paid': 'Georgie'
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Expense successfully updated.")
        self.assertRedirects(response, reverse_lazy(
            "detailed_month", kwargs={
            'month': 'Jan',
            'year': '2019'
        }))

    def test_delete_expense_url_exists_at_desired_location_and_uses_correct_template(self):
        login(self)
        response = edit_view_response(self, 'expense_delete')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'main/expense_delete_form.html')

    def test_login_required_to_delete_expense(self):
        response = edit_view_response(self, 'expense_delete')
        self.assertNotEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response,'main/expense_delete_form.html')

    def test_deleting_payment_generates_success_message_and_redirects_to_overview(self):
        expense = Expense.objects.get(description='Test 1')
        login(self)
        response = self.client.post(
            reverse('expense_delete', kwargs={
            'pk': expense.pk,
            'month': 'Jan',
            'year': '2019'
        }))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Expense successfully deleted.")
        self.assertRedirects(response, reverse_lazy(
            "detailed_month", kwargs={
            'month': 'Jan',
            'year': '2019'
        }))
