from django.test import TestCase
from django.urls import reverse, re_path
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from .models import Chat
from .consumers import ChatConsumer
from datetime import datetime
from channels.auth import AuthMiddlewareStack
from django.test import SimpleTestCase
from django.urls import resolve
from channels.routing import URLRouter
from chat_app.routing import websocket_urlpatterns

User = get_user_model()

# Test Model: Chat
class ChatModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpassword')
        self.receiver = User.objects.create_user(username='receiver', password='testpassword')
        self.chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message="Hello, how are you?",
            timestamp=datetime(2024, 11, 24, 10, 0),
        )

    def test_str_method(self):
        chat = self.chat
        expected_str = f"{self.sender} to {self.receiver} at {chat.timestamp}"
        self.assertEqual(str(chat), expected_str)

    def test_get_unread_count(self):
        unread_count = Chat.get_unread_count(self.receiver)
        self.assertEqual(unread_count, 1)

    def test_mark_as_read(self):
        self.chat.mark_as_read()
        self.assertTrue(self.chat.is_read)
        self.assertEqual(self.chat.last_read, self.chat.timestamp)

    def test_mark_multiple_messages_as_read(self):
        # Create multiple unread messages
        Chat.objects.create(sender=self.sender, receiver=self.receiver, message="Another message", is_read=False)
        Chat.objects.create(sender=self.receiver, receiver=self.sender, message="Yet another message", is_read=False)

        self.receiver.unread_count = 2  # Simulate unread count
        self.assertEqual(Chat.get_unread_count(self.receiver), 2)

        # Mark all messages as read
        Chat.objects.all().update(is_read=True)
        self.assertEqual(Chat.get_unread_count(self.receiver), 0)

    def test_unread_count_with_no_unread_messages(self):
        # Ensure that the receiver has no unread messages
        self.receiver.chat_set.update(is_read=True)  # Mark all messages as read, if any

         # Now check that the unread count is 0
        self.assertEqual(Chat.get_unread_count(self.receiver), 0)


# Test WebSocket: ChatConsumer
class WebSocketTest(TestCase):
    def setUp(self):
        # Create test users
        self.sender = User.objects.create_user(username='sender', password='testpassword')
        self.receiver = User.objects.create_user(username='receiver', password='testpassword')

    async def test_chat_connect(self):
        room_name = 'testroom'
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(URLRouter([re_path(r'ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer.as_asgi())])),
            f"ws/chat/{room_name}/"
        )

        # Log in before connecting WebSocket
        self.client.login(username='sender', password='testpassword')

        # Now connect
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_chat_message_send(self):
        room_name = 'testroom'
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(URLRouter([re_path(r'ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer.as_asgi())])),
            f"ws/chat/{room_name}/"
        )
        # Log in before connecting WebSocket
        self.client.login(username='sender', password='testpassword')

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        message = {'message': 'Hello, receiver!'}
        await communicator.send_json_to(message)

        response = await communicator.receive_json_from()
        self.assertEqual(response['message'], message['message'])

        await communicator.disconnect()

    async def test_chat_message_received(self):
        room_name = 'testroom'
        communicator1 = WebsocketCommunicator(
            AuthMiddlewareStack(URLRouter([re_path(r'ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer.as_asgi())])),
            f"ws/chat/{room_name}/"
        )
        communicator2 = WebsocketCommunicator(
            AuthMiddlewareStack(URLRouter([re_path(r'ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer.as_asgi())])),
            f"ws/chat/{room_name}/"
        )

        # Log in before connecting WebSocket
        self.client.login(username='sender', password='testpassword')

        connected1, subprotocol1 = await communicator1.connect()
        connected2, subprotocol2 = await communicator2.connect()
        self.assertTrue(connected1)
        self.assertTrue(connected2)

        message = {'message': 'Hello from sender!'}
        await communicator1.send_json_to(message)

        response = await communicator2.receive_json_from()
        self.assertEqual(response['message'], message['message'])

        await communicator1.disconnect()
        await communicator2.disconnect()

    async def test_invalid_room_connect(self):
        # Test connection to an invalid room
        room_name = 'invalidroom'
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(URLRouter([re_path(r'ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer.as_asgi())])),
            f"ws/chat/{room_name}/"
        )
        # Log in before connecting WebSocket
        self.client.login(username='sender', password='testpassword')

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()


# Test Views: Chat Room
class ChatRoomViewTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpassword')
        self.receiver = User.objects.create_user(username='receiver', password='testpassword')

    def test_chat_room_view_authenticated(self):
        # Test that a logged-in user can access the chat room
        self.client.login(username='sender', password='testpassword')
        response = self.client.get(reverse('chat_room', kwargs={'room_name': self.receiver.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Type a message...')
        self.assertContains(response, self.receiver.username)

    def test_chat_room_view_unauthenticated(self):
        # Test that an unauthenticated user cannot access the chat room
        response = self.client.get(reverse('chat_room', kwargs={'room_name': self.receiver.username}))
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_unread_message_counts(self):
        # Test unread message counts
        Chat.objects.create(sender=self.receiver, receiver=self.sender, message="Test message", is_read=False)
        self.client.login(username='sender', password='testpassword')
        response = self.client.get(reverse('chat_room', kwargs={'room_name': self.receiver.username}))
        self.assertEqual(response.context['unread_message_counts'][self.receiver.username], 1)

    def test_unread_message_count_for_multiple_messages(self):
        # Test with multiple unread messages
        Chat.objects.create(sender=self.receiver, receiver=self.sender, message="Message 1", is_read=False)
        Chat.objects.create(sender=self.receiver, receiver=self.sender, message="Message 2", is_read=False)
        self.client.login(username='sender', password='testpassword')
        response = self.client.get(reverse('chat_room', kwargs={'room_name': self.receiver.username}))
        self.assertEqual(response.context['unread_message_counts'][self.sender.username], 2)

    def test_chat_room_access_without_login(self):
        # Ensure non-logged in user is redirected
        response = self.client.get(reverse('chat_room', kwargs={'room_name': self.receiver.username}))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

class RoutingTestCase(SimpleTestCase):
    def test_routing_resolves_to_consumer(self):
        """
        Test that the WebSocket URL correctly resolves to the ChatConsumer.
        """
        room_name = "testroom"
        resolved_function = resolve(f"/ws/chat/{room_name}/")
        
        # Ensure the route resolves correctly
        self.assertEqual(resolved_function.func.view_class, ChatConsumer)

    def test_all_routes_registered(self):
        """
        Test that all WebSocket routes are registered correctly.
        """
        router = URLRouter(websocket_urlpatterns)
        self.assertEqual(len(websocket_urlpatterns), 1)
        self.assertIsInstance(websocket_urlpatterns[0], re_path)
        self.assertIn('room_name', websocket_urlpatterns[0].pattern.regex.pattern)

    def test_invalid_route(self):
        """
        Test that invalid WebSocket routes are not resolved.
        """
        with self.assertRaises(Exception):
            resolve("/ws/chat/")  # Missing `room_name`

        with self.assertRaises(Exception):
            resolve("/ws/invalid_path/")










