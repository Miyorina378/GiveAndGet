from django.test import TestCase, Client
from django.urls import reverse
from users_app.models import GGUser
from users_app.forms import RegisterForm
from django.contrib.admin.sites import site
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
import json
from unittest.mock import patch
import mimetypes
from PIL import Image
import io


# ตั้งค่า MIME type สำหรับระบบ Windows
mimetypes.init(files=[])  # ใช้ไฟล์ MIME ว่างเพื่อไม่ให้โหลด /etc/mime.types
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/png", ".png")


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
        self.user = GGUser.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        self.login_url = reverse('dashboard')
        self.register_url = reverse('register')
        self.edit_profile_url = reverse('edit_profile')

    def test_register_view_GET(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users_app/register.html')

    def test_register_view_POST(self):
        data = {
            'username': 'newuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'email': 'new@example.com'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(GGUser.objects.filter(username='newuser').exists())

    def test_dashboard_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users_app/dashboard.html')

    def test_dashboard_view_redirect_unauthenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_update_username(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('update_username'),
                                    json.dumps({'username': 'updateduser'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_update_email(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('update_email'),
                                    json.dumps({'email': 'updated@example.com'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_update_profile_picture(self):
        self.client.login(username='testuser', password='testpassword')
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('update_profile_picture'), {'profile_picture': image})
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_POST(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'username': 'newusername',
            'email': 'newemail@example.com'
        }
        response = self.client.post(reverse('edit_profile'), data)
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        self.user.refresh_from_db()  # โหลดข้อมูลใหม่จากฐานข้อมูล
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.user.email, 'newemail@example.com')


    def test_chat_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('chat'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat_app/chat.html')
    
    def test_update_username_invalid_request(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('update_username'))  # ส่ง GET แทน POST
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Invalid request"})

    def test_update_email_invalid_request(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('update_email'))  # ส่ง GET แทน POST
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Invalid request"})

    def test_update_profile_picture_no_file(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('update_profile_picture'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_edit_profile_GET(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users_app/edit_profile.html')

    def generate_image_file(self, filename="test_image.jpg"):
        """Helper function to generate a valid image file."""
        image = Image.new("RGB", (100, 100), color="red")
        file = io.BytesIO()
        image.save(file, format="JPEG")
        file.name = filename
        file.seek(0)
        return file

    def test_edit_profile_POST_delete_old_image(self):
        self.client.login(username='testuser', password='testpassword')

        # จำลองไฟล์รูปภาพเก่าที่มีอยู่
        old_image = SimpleUploadedFile("old_image.jpg", b"old_content", content_type="image/jpeg")
        self.user.profile_picture = old_image
        self.user.save()

        # สร้างไฟล์รูปภาพใหม่
        new_image = self.generate_image_file("new_image.jpg")
        data = {'profile_picture': new_image, 'username': 'newusername', 'email': 'newemail@example.com'}
    
        with patch('os.path.isfile', return_value=True), patch('os.remove') as mock_remove:
            response = self.client.post(reverse('edit_profile'), data)

            self.user.refresh_from_db()  # โหลดข้อมูลใหม่จากฐานข้อมูล
            self.assertEqual(response.status_code, 302)  # Redirect to dashboard
            self.assertEqual(self.user.username, 'newusername')
            self.assertEqual(self.user.email, 'newemail@example.com')

            # ตรวจสอบว่าชื่อไฟล์มีคำว่า "new_image" และอยู่ใน directory "profile_pics"
            self.assertIn("new_image", self.user.profile_picture.name)
            self.assertIn("profile_pics/", self.user.profile_picture.name)

            # ตรวจสอบว่ามีการลบไฟล์รูปภาพเก่าหรือไม่
            mock_remove.assert_called_once()






# Test admin
class AdminSiteTest(TestCase):
    def test_admin_registered_models(self):
        self.assertTrue(site.is_registered(GGUser))
