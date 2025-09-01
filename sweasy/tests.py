from django.test import TestCase
from accounts.models import User
from django.urls import reverse
from rest_framework import status

class TestAuth(TestCase):
    def setUp(self):
        self.test_username = 'john-doe'
        self.test_email = 'john@doe.com'
        self.test_password = 'top_secret'

        self.test_user_data = {
            'username': self.test_username,
            'email': self.test_email,
            'password1': self.test_password,
            'password2': self.test_password
        }
        
    def tearDown(self):
        User.objects.all().delete()
        
    def create_test_user(self):
        User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )
        
    def test_can_create_user(self):
        response = self.client.post(
            reverse('rest_register'),
            self.test_user_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        
        user = User.objects.get(username=self.test_username)
        self.assertEqual(user.email, self.test_email)
        self.assertTrue(user.check_password(self.test_password))
        
        email_verification_message = 'If this email was not registered before, a confirmation email will be sent to this address.'
        self.assertEqual(response.data['detail'], email_verification_message)
        
    def test_cannot_create_user_if_username_is_missing(self):
        self.test_user_data.pop('username')
        response = self.client.post(
            reverse('rest_register'),
            self.test_user_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data['username'][0], 'This field is required.')
    
    def test_cannot_create_user_if_email_is_missing(self):
        self.test_user_data.pop('email')
        response = self.client.post(
            reverse('rest_register'),
            self.test_user_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data['email'][0], 'This field is required.')

    def test_cannot_create_user_if_password_is_missing(self):
        self.test_user_data.pop('password1')
        response = self.client.post(
            reverse('rest_register'),
            self.test_user_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data['password1'][0], 'This field is required.')

    def test_cannot_create_user_if_password_confirmation_is_missing(self):
        self.test_user_data.pop('password2')
        response = self.client.post(
            reverse('rest_register'),
            self.test_user_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data['password2'][0], 'This field is required.')

    def test_cannot_create_user_if_username_already_exists(self):
        self.create_test_user()
        
        assert User.objects.count() == 1

        response = self.client.post(
            reverse('rest_register'),
            self.test_user_data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        only_username_error_message = 'If this username was not registered before, a confirmation email will be sent to this address.'
        self.assertEqual(response.data['username'][0], only_username_error_message)
        self.assertEqual(User.objects.count(), 1)
        
    def test_cannot_create_user_if_email_already_exists(self):
        self.create_test_user()
        
        assert User.objects.count() == 1
        
        data = {
            'username': 'another-username',
            'email': self.test_email,
            'password1': self.test_password,
            'password2': self.test_password
        }
        
        response = self.client.post(
            reverse('rest_register'),
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        only_email_error_message = 'If this email was not registered before, a confirmation email will be sent to this address.'
        self.assertEqual(response.data['email'][0], only_email_error_message)

        self.assertNotIn('username', response.data)
        
        self.assertEqual(User.objects.count(), 1)
        
    def test_cannot_login_after_registration_without_email_verification(self):
        self.create_test_user()
        
        assert User.objects.count() == 1
        
        response = self.client.post(
            reverse('rest_login'),
            {
                'email': self.test_email,
                'password': self.test_password
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['non_field_errors'][0], 'E-mail is not verified.')