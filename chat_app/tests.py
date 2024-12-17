from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime
from .models import Chat  # เปลี่ยน yourapp เป็นชื่อแอปของคุณ

class ChatModelTest(TestCase):

    def setUp(self):
        # สร้างผู้ใช้ 2 คน
        self.user1 = get_user_model().objects.create_user(username='user1', password='password123')
        self.user2 = get_user_model().objects.create_user(username='user2', password='password123')

        # สร้างข้อความ (Chat)
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
        self.chat3 = Chat.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message='Are you there?',
            is_read=False
        )

    def test_chat_creation(self):
        # ทดสอบว่าแชทถูกสร้างขึ้นมาอย่างถูกต้อง
        self.assertEqual(self.chat1.sender.username, 'user1')
        self.assertEqual(self.chat1.receiver.username, 'user2')
        self.assertEqual(self.chat1.message, 'Hello, user2!')
        self.assertEqual(self.chat1.is_read, False)
        self.assertIsNotNone(self.chat1.timestamp)

    def test_get_unread_count(self):
        # ทดสอบการคำนวณจำนวนข้อความที่ยังไม่ได้อ่าน
        unread_count_user1 = Chat.get_unread_count(self.user1)
        unread_count_user2 = Chat.get_unread_count(self.user2)

        # user1 ได้รับ 2 ข้อความที่ยังไม่ได้อ่าน (chat1, chat3)
        self.assertEqual(unread_count_user1, 2)

    def test_mark_as_read(self):
        # ทดสอบการอัปเดตสถานะเป็น "อ่านแล้ว"
        self.chat1.mark_as_read()

        # ตรวจสอบว่า is_read ถูกตั้งเป็น True
        self.assertTrue(self.chat1.is_read)
        self.assertEqual(self.chat1.last_read, self.chat1.timestamp)

    def test_str_method(self):
        # ทดสอบ method __str__
        chat_str = str(self.chat1)
        self.assertEqual(chat_str, f"{self.chat1.sender} to {self.chat1.receiver} at {self.chat1.timestamp}")

    def test_unread_count_exclude_sender(self):
        # ทดสอบว่า get_unread_count ไม่รวมข้อความที่ผู้ใช้ส่งเอง
        self.chat4 = Chat.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message='Test message',
            is_read=False
        )
        unread_count_user1 = Chat.get_unread_count(self.user1)
        self.assertEqual(unread_count_user1, 2)  # user1 ได้รับ 2 ข้อความที่ยังไม่ได้อ่าน (chat3, chat1)

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

    def test_update_unread_messages(self):
        # ทดสอบการอัปเดตสถานะข้อความที่ยังไม่ได้อ่าน
        self.client.login(username='user1', password='password123')
        self.client.get(self.chat_room_url)

        # ตรวจสอบว่า ข้อความที่ยังไม่ได้อ่านของ user1 ถูกอัปเดตเป็น "อ่านแล้ว"
        self.chat1.refresh_from_db()
        self.assertTrue(self.chat1.is_read)

