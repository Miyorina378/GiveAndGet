from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime
from .models import Chat  # เปลี่ยน yourapp เป็นชื่อแอปของคุณ
from django.contrib.auth.models import User


class ChatModelTest(TestCase):

    def setUp(self):
        # สร้างผู้ใช้สำหรับการทดสอบ
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        # สร้างข้อความทดสอบ
        self.chat1 = Chat.objects.create(sender=self.user1, receiver=self.user2, message="Hello!")
        self.chat2 = Chat.objects.create(sender=self.user2, receiver=self.user1, message="Hi!", is_read=True)

    def test_chat_creation(self):
        """ทดสอบการสร้างข้อความ"""
        self.assertEqual(Chat.objects.count(), 2)
        self.assertEqual(self.chat1.message, "Hello!")
        self.assertEqual(self.chat2.sender, self.user2)

    def test_get_unread_count(self):
        """ทดสอบการคำนวณจำนวนข้อความที่ยังไม่ได้อ่าน"""
        unread_count = Chat.get_unread_count(self.user2)
        self.assertEqual(unread_count, 1)  # user2 มี 1 ข้อความที่ยังไม่ได้อ่าน

    def test_mark_as_read(self):
        """ทดสอบการอัพเดตสถานะข้อความว่าอ่านแล้ว"""
        self.assertFalse(self.chat1.is_read)  # ก่อน mark_as_read ต้องยังไม่ได้อ่าน
        self.chat1.mark_as_read()
        self.assertTrue(self.chat1.is_read)  # หลัง mark_as_read ต้องเป็น True
        self.assertIsNotNone(self.chat1.last_read)  # last_read ต้องไม่เป็น None


    def test_str_method(self):
        # ทดสอบ method __str__
        chat_str = str(self.chat1)
        self.assertEqual(chat_str, f"{self.chat1.sender} to {self.chat1.receiver} at {self.chat1.timestamp}")



from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Chat
from products.models import Product
from datetime import datetime
from unittest.mock import patch
from django.http import JsonResponse

User = get_user_model()

class ChatViewsTest(TestCase):

    def setUp(self):
        # สร้างผู้ใช้ 2 คน
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        # สร้าง Chat สำหรับทดสอบ
        self.chat1 = Chat.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message='Hello, user2!',
            is_read=False
        )
        self.chat2 = Chat.objects.create(
            sender=self.user2,
            receiver=self.user1,
            message='Hello, user1!',
            is_read=True
        )

        self.chat_room_url = reverse('chat_room', args=['user2'])
        self.get_user_products_url = reverse('get_user_products', args=['user2'])

    def test_chat_room_view(self):
        # ทดสอบการเข้าถึงห้องแชท
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.chat_room_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat_app/chat.html')
        self.assertContains(response, 'Hello, user2!')
        self.assertContains(response, 'Hello, user1!')

    def test_search_chat_messages(self):
        # ทดสอบการค้นหาข้อความในห้องแชท
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.chat_room_url + '?search=Hello')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, user2!')
        self.assertContains(response, 'Hello, user1!')



