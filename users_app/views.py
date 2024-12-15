from django.contrib.auth import login, get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from users_app.forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Report, GGUser
from django.utils.timezone import now
import json
from django.shortcuts import get_object_or_404
from .forms import ProfilePictureForm
from .forms import UserProfileForm

User = get_user_model()

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
    if request.method == 'POST':
        data = json.loads(request.body)
        new_username = data.get('username')
        user = request.user
        user.username = new_username
        user.save()
        request.session['username'] = new_username

        return JsonResponse({"message": "Username updated successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def update_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_email = data.get('email')
        user = request.user
        user.email = new_email
        user.save()

        # Update the session with the new username
        request.session['username'] = new_email

        return JsonResponse({"message": "Email updated successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def update_profile_picture(request):
    if request.method == "POST" and request.FILES.get("profile_picture"):
        # Update profile picture with the new file
        request.user.profile_picture = request.FILES["profile_picture"]
        request.user.save()
        messages.success(request, "Profile picture updated successfully!")
        return redirect("dashboard")  # หรือหน้าอื่นๆ ตามที่คุณต้องการ
    return redirect("dashboard")

import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from django.core.files.storage import default_storage

@login_required
def edit_profile(request):
    user = request.user
    old_image = user.profile_picture  # เก็บไฟล์รูปภาพเดิมไว้

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # ตรวจสอบและลบรูปภาพเดิมหากมีการอัพโหลดรูปภาพใหม่
            if 'profile_picture' in request.FILES:
                new_image = request.FILES['profile_picture']
                if old_image and old_image != new_image and os.path.isfile(old_image.path):  # ถ้ามีไฟล์เก่าและไฟล์นั้นมีอยู่จริง
                    os.remove(old_image.path)  # ลบไฟล์เก่า

            form.save()  # บันทึกข้อมูลใหม่
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'users_app/edit_profile.html', {'form': form})
