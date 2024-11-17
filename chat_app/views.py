from django.shortcuts import render, get_object_or_404, redirect
from .forms import ChatForm, UserSearchForm
from .models import Chat
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.decorators import login_required

User = get_user_model()

@login_required
def chat_room(request, user_id=None):
    # Get the user to chat with
    user_to_chat = None
    if user_id:
        user_to_chat = get_object_or_404(User, pk=user_id)

    # Fetch messages between the current user and the target user (if any)
    messages = Chat.objects.filter(
        (Q(sender=request.user) & Q(receiver=user_to_chat)) |
        (Q(sender=user_to_chat) & Q(receiver=request.user))
    ).order_by('timestamp') if user_to_chat else []

    # Handle the search functionality
    search_form = UserSearchForm(request.GET)
    search_results = []

    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('username')
        if search_query:
            # Search for users whose usernames match the search query (case-insensitive)
            search_results = User.objects.filter(username__icontains=search_query).exclude(username=request.user.username)

    # Handle the POST request to send a message
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            # Create a new message
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.receiver = user_to_chat
            new_message.save()
            return redirect('chat_room', user_id=user_id)  # Redirect back to the same chat room (changed 'chat' to 'chat_room')
    else:
        form = ChatForm()

    # Render the chat template with search results, messages, and the search form
    return render(request, 'chat_app/chat.html', {
        'messages': messages,
        'user_to_chat': user_to_chat,
        'form': form,
        'search_form': search_form,
        'search_results': search_results,
    })




