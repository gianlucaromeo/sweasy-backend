# tests/test_auth.py
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from allauth.account.models import EmailAddress
from accounts.models import User
from catalog.models import Book, Category, Chapter


@override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
class RegistrationTests(APITestCase):
    REGISTER_URL = reverse("rest_register")
    LOGIN_URL = reverse("rest_login")

    @classmethod
    def setUpTestData(cls):
        cls.username = "john-doe"
        cls.email = "john@doe.com"
        cls.password = "top_secret"
        cls.payload = {
            "username": cls.username,
            "email": cls.email,
            "password1": cls.password,
            "password2": cls.password,
        }

    # helpers
    def register(self, data=None):
        return self.client.post(
            self.REGISTER_URL, 
            data or self.payload,
        )

    def verify_email(self, email=None):
        addr = EmailAddress.objects.get(email=email or self.email)
        addr.verified = True
        addr.save(update_fields=["verified"])

    # tests
    def test_register__creates_user_and_returns_detail(self):
        res = self.register()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(username=self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertIn("detail", res.data)

    def test_register__missing_required_fields(self):
        required_fields = ["username", "email", "password1", "password2"]
        for field in required_fields:
            with self.subTest(missing=field):
                data = dict(self.payload)
                data.pop(field)
                res = self.register(data)
                self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, res.data)
                self.assertEqual(User.objects.count(), 0)

    def test_register__username_must_be_unique(self):
        self.assertEqual(self.register().status_code, status.HTTP_201_CREATED)
        res = self.register()  # same payload again
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", res.data)
        self.assertEqual(User.objects.count(), 1)  # unchanged

    def test_register__email_must_be_unique(self):
        self.assertEqual(self.register().status_code, status.HTTP_201_CREATED)
        data = dict(self.payload, username="another-user")
        res = self.register(data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", res.data)
        self.assertNotIn("username", res.data)
        self.assertEqual(User.objects.count(), 1)

@override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
class LoginTests(APITestCase):
    REGISTER_URL = reverse("rest_register")
    LOGIN_URL = reverse("rest_login")

    @classmethod
    def setUpTestData(cls):
        cls.username = "john-doe"
        cls.email = "john@doe.com"
        cls.password = "top_secret"
        cls.payload = {
            "username": cls.username,
            "email": cls.email,
            "password1": cls.password,
            "password2": cls.password,
        }

    # helpers
    def register(self):
        return self.client.post(self.REGISTER_URL, self.payload)

    def verify_email(self):
        addr = EmailAddress.objects.get(email=self.email)
        addr.verified = True
        addr.save(update_fields=["verified"])

    # tests
    def test_login__fails_before_email_verification(self):
        self.assertEqual(self.register().status_code, status.HTTP_201_CREATED)
        res = self.client.post(
            self.LOGIN_URL, 
            { "email": self.email, "password": self.password },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)

    def test_login__succeeds_after_email_verification(self):
        self.assertEqual(self.register().status_code, status.HTTP_201_CREATED)
        self.verify_email()
        res = self.client.post(
            self.LOGIN_URL,
            { "email": self.email, "password": self.password },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # token or session key varies by setup; just assert payload contains 
        # something useful
        self.assertTrue(bool(res.data))


class CatalogPermissionTests(APITestCase):
    LIST_CATEGORIES_URL = reverse("category-list")
    CATEGORY_DETAIL_URL = reverse("category-detail", args=[1])
    LIST_BOOKS_URL = reverse("book-list")
    BOOK_DETAIL_URL = reverse("book-detail", args=[1])
    LIST_CHAPTERS_URL = reverse("chapter-list")
    CHAPTER_DETAIL_URL = reverse("chapter-detail", args=[1])

    def setUp(self):
        self.user = User.objects.create_user(
            username="alice", email="alice@test.com", password="pw123456"
        )
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True
        )
        
        self.category = Category.objects.create(
            name="Network",
            description="Learn about Protocols, Subnetting, and more."
        )
        
        self.book = Book.objects.create(
            category=self.category,
            number=1,
            title="IP Addressing",
            description="Learn about IP Addresses."
        )
        
        self.chapter = Chapter.objects.create(
            book=self.book,
            number=1,
            title="IP Addresses",
            description="Learn about IP Addresses.",
            content={
                "h1": "IP Addresses",
                "p": "IP Addresses are used to identify devices on a network.",
            }
        )
        
    #  categories
    def test_categories__anonymous_cannot_list(self):
        res = self.client.get(self.LIST_CATEGORIES_URL)
        self.assertIn(res.status_code, {status.HTTP_401_UNAUTHORIZED})

    def test_categories__authenticated_can_list(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.LIST_CATEGORIES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_categories__anonymous_cannot_view_detail(self):
        res = self.client.get(self.CATEGORY_DETAIL_URL, args=[self.category.id])
        self.assertIn(res.status_code, {status.HTTP_401_UNAUTHORIZED})
        
    def test_categories__authenticated_can_view_detail(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.CATEGORY_DETAIL_URL, args=[self.category.id])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
       
    #  books
    def test_books__anonymous_cannot_list(self):
        res = self.client.get(self.LIST_BOOKS_URL)
        self.assertIn(res.status_code, {status.HTTP_401_UNAUTHORIZED})
        
    def test_books__authenticated_can_list(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.LIST_BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_books__anonymous_cannot_view_detail(self):
        res = self.client.get(self.BOOK_DETAIL_URL, args=[self.book.id])
        self.assertIn(res.status_code, {status.HTTP_401_UNAUTHORIZED})
        
    def test_books__authenticated_can_view_detail(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.BOOK_DETAIL_URL, args=[self.book.id])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    #  chapters
    def test_chapters__anonymous_cannot_list(self):
        res = self.client.get(self.LIST_CHAPTERS_URL)
        self.assertIn(res.status_code, {status.HTTP_401_UNAUTHORIZED})
        
    def test_chapters__authenticated_can_list(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.LIST_CHAPTERS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_chapters__anonymous_cannot_view_detail(self):
        res = self.client.get(self.CHAPTER_DETAIL_URL, args=[self.chapter.id])
        self.assertIn(res.status_code, {status.HTTP_401_UNAUTHORIZED})
        
    def test_chapters__authenticated_can_view_detail(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.CHAPTER_DETAIL_URL, args=[self.chapter.id])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
