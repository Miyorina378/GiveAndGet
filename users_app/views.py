from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from users_app.forms import RegisterForm
from django.contrib import messages
import json


# Create your views here.
def register(request: HttpRequest):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = RegisterForm()
    form = RegisterForm()
    context = {'form': form}
    return render(request, 'users_app/register.html', context)

@login_required
def dashboard(request):
    username = request.user.username
    return render(request, "users_app/dashboard.html", {'username': username})

@login_required
def chat(request):
    return render(request, 'chat_app/chat.html')

@login_required
def update_username(request):
    if request.method == "POST":
        data = json.loads(request.body)
        new_username = data.get("username")
        if new_username:
            request.user.username = new_username
            request.user.save()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)

@login_required
def update_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        new_email = data.get("email")
        if new_email:
            request.user.email = new_email
            request.user.save()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)



@login_required
def update_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        new_profile_picture = request.FILES['profile_picture']
        request.user.profile_picture = new_profile_picture
        request.user.save()
        messages.success(request, 'Profile picture updated successfully!')
        return redirect('profile')  
    messages.error(request, 'Please provide a valid profile picture.')
    return redirect('profile') 
