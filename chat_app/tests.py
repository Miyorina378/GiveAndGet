from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Chat
from django.utils import timezone

class ChatModelTest(TestCase):
    def setUp(self):
        # Create two users for the chat
        User = get_user_model()
        self.sender = User.objects.create_user(username='sender', password='testpassword')
        self.receiver = User.objects.create_user(username='receiver', password='testpassword')

        # Create a Chat instance
        self.chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message="Hello, how are you?",
            timestamp=timezone.now(),
        )

    def test_str_method(self):
        # Check the string representation of the chat
        expected_str = f"{self.sender.username} to {self.receiver.username} at {self.chat.timestamp}"
        self.assertEqual(str(self.chat), expected_str)
