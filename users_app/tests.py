from django.test import TestCase, Client
from django.urls import reverse
from users_app.models import GGUser
from users_app.forms import RegisterForm
from django.contrib.admin.sites import site
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
import json


# Test models
class GGUserModelTest(TestCase):
    def setUp(self):
        self.user = GGUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.status, "offline")

    def test_user_id_auto_increment(self):
        user2 = GGUser.objects.create_user(username="testuser2", password="password123")
        self.assertEqual(user2.user_id, self.user.user_id + 1)

    def test_user_str(self):
        self.assertEqual(str(self.user), "testuser - offline")


# Test forms
class RegisterFormTest(TestCase):
    def test_valid_register_form(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_register_form(self):
        form_data = {
            "username": "",
            "email": "invalid@example.com",
            "password1": "password123",
            "password2": "differentpassword",
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())


# Test views
class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = GGUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
        )
        self.client.login(username="testuser", password="password123")

    def test_register_view(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users_app/register.html")

    def test_dashboard_view(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users_app/dashboard.html")

    def test_update_username(self):
        response = self.client.post(
            reverse("update_username"),
            data=json.dumps({"username": "updateduser"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_update_email(self):
        response = self.client.post(
            reverse("update_email"),
            data=json.dumps({"email": "updated@example.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@example.com")

    def test_update_profile_picture(self):
        mock_image = BytesIO()
        mock_image.write(b"test image data")
        mock_image.seek(0)
        image = SimpleUploadedFile("test_image.jpg", mock_image.read(), content_type="image/jpeg")

        response = self.client.post(reverse("update_profile_picture"), {"profile_picture": image})
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_picture.name.startswith("media/profile_pics/"))

    ### yes
    def test_update_profile_picture_no_file(self):
        response = self.client.post(reverse("update_profile_picture"), {})
        self.assertRedirects(response, reverse("dashboard"))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Please provide a valid profile picture.")

# Test admin
class AdminSiteTest(TestCase):
    def test_admin_registered_models(self):
        self.assertTrue(site.is_registered(GGUser))
