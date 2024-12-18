from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Chat
from products.models import Product
from django.db.models import Q, Count
from django.http import JsonResponse
import json



User = get_user_model()



def get_unread_message_counts(user):
    # Calculate unread messages count between user and each sender
    return Chat.objects.filter(receiver=user, is_read=False) \
        .values('sender') \
        .annotate(unread_count=Count('id')) \
        .order_by('sender')

@login_required
def chat_room(request, room_name):
    
    seller = get_object_or_404(User, username=room_name)
    products = Product.objects.filter(user=seller)
    
    search_query = request.GET.get('search', '')

    # Fetch all users who have interacted with the current user in the chat
    users = User.objects.exclude(id=request.user.id)

    # Get the chat history for the room
    chats = Chat.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    # If there is a search query, filter messages that match the search
    if search_query:
        chats = chats.filter(message__icontains=search_query)

    chats = chats.order_by('timestamp')

    # Update unread messages to read for the current user
    unread_messages = chats.filter(receiver=request.user, is_read=False)
    unread_messages.update(is_read=True)

    # Get unread message counts for each sender
    unread_message_counts = get_unread_message_counts(request.user)

    # Convert unread message counts to a dictionary for use in the template
    unread_message_counts_dict = {str(item['sender']): item['unread_count'] for item in unread_message_counts}

    # Get the most recent message from each user with whom the current user has chatted
    user_last_messages = []
    for user in users:
        last_message = Chat.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        # Only include users who have exchanged messages with the current user
        if last_message:
            user_last_messages.append({
                'user': user,
                'last_message': last_message,
                'unread_count': unread_message_counts_dict.get(user.username, 0),
            })

    return render(request, 'chat_app/chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query,
        'unread_message_counts': unread_message_counts_dict,
        'products': products,
        'seller': seller,
        'room_name': room_name,
    })

@login_required
def get_user_products(request, room_name):
    # Fetch the user based on the room_name (which is the seller's username)
    seller = get_object_or_404(User, username=room_name)
    
    # Fetch the products posted by this seller
    products = Product.objects.filter(user=seller)

    # Check if products are found
    if products.exists():
        # Prepare the product data to send back as a JSON response
        product_data = [{"id": product.id, "name": product.name, "price": str(product.price)} for product in products]
        return JsonResponse({"success": True, "products": product_data})
    else:
        return JsonResponse({"success": False, "message": "No products available for this user."})

