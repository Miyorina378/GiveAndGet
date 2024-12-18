from django.contrib.auth import get_user_model
from .models import Chat  
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from users_app.models import GGUser
from main.asgi import application  


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

class ChatConsumerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = GGUser.objects.create_user(username="user1", password="password123")
        cls.user2 = GGUser.objects.create_user(username="user2", password="password123")

    async def test_websocket_communication(self):
        # Authenticate user1
        communicator = WebsocketCommunicator(
            application, f"/ws/chat/{self.user2.username}/"
        )
        communicator.scope['user'] = self.user1  # Simulate logged-in user
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send a message
        message = "Hello, user2!"
        await communicator.send_json_to({
            "message": message
        })

        # Receive the broadcasted message
        response = await communicator.receive_json_from()
        self.assertEqual(response["message"], message)
        self.assertEqual(response["sender"], self.user1.username)

        # Verify the message is saved in the database
        chat = await sync_to_async(Chat.objects.get)(
            sender=self.user1, receiver=self.user2, message=message
        )
        self.assertIsNotNone(chat)

        # Close the WebSocket
        await communicator.disconnect()
    

    async def test_invalid_user_connection(self):
        # Simulate an anonymous user connection
        communicator = WebsocketCommunicator(
            application, f"/ws/chat/user2/"
        )
        communicator.scope['user'] = AnonymousUser()  # Simulate an anonymous user
        connected, _ = await communicator.connect()

        # Assert that the connection was accepted
        self.assertTrue(connected)

        await communicator.disconnect()


from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from products.models import Product

User = get_user_model()


class GetUserProductsViewTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.seller = User.objects.create_user(username="seller1", password="password123")
        self.other_user = User.objects.create_user(username="user2", password="password123")
        
        # Create test products for the seller
        self.product1 = Product.objects.create(user=self.seller, name="Product 1", price=100.00, stock = 10)
        self.product2 = Product.objects.create(user=self.seller, name="Product 2", price=200.00, stock = 10)
        
        # Client for making requests
        self.client = Client()

    def test_get_products_for_valid_seller_with_products(self):
        # Login as a valid user
        self.client.login(username="user2", password="password123")
        
        # Request the seller's products
        response = self.client.get(reverse("get_user_products", args=["seller1"]))
        
        # Assert response is successful
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Assert success and product data in response
        self.assertTrue(response_data["success"])
        self.assertEqual(len(response_data["products"]), 2)
        self.assertEqual(response_data["products"][0]["name"], "Product 1")
        self.assertEqual(response_data["products"][1]["name"], "Product 2")

    def test_get_products_for_valid_seller_with_no_products(self):
        # Create a seller with no products
        new_seller = User.objects.create_user(username="empty_seller", password="password123")
        
        # Login as a valid user
        self.client.login(username="user2", password="password123")
        
        # Request the new seller's products
        response = self.client.get(reverse("get_user_products", args=["empty_seller"]))
        
        # Assert response is successful
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Assert success is False and proper message is returned
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["message"], "No products available for this user.")

    def test_get_products_for_invalid_seller(self):
        # Login as a valid user
        self.client.login(username="user2", password="password123")
        
        # Request products for a non-existent seller
        response = self.client.get(reverse("get_user_products", args=["non_existent_user"]))
        
        # Assert a 404 response
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_access(self):
        # Request products without logging in
        response = self.client.get(reverse("get_user_products", args=["seller1"]))
        
        # Assert redirection to the login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))

