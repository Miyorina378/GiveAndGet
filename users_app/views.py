from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from users_app.forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Report
import json
from django.shortcuts import get_object_or_404

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
        new_profile_picture = request.FILES["profile_picture"]
        request.user.profile_picture = new_profile_picture
        request.user.save() 
        messages.success(request, "Profile picture updated successfully!")
        return redirect("dashboard")
    messages.error(request, "Please provide a valid profile picture.")
    return redirect("dashboard")

@login_required
def report_user(request, username):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'You must be logged in to submit a report.'})

    # Retrieve the reported user from the database
    reported_user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        # Extract the form data
        reason = request.POST.get('reason')
        report_description = request.POST.get('report_description')

        # Log the received data for debugging
        print(f"Received POST request: Reason - {reason}, Description - {report_description}")

        # Ensure reason and description are provided
        if reason and report_description:
            # Create the report
            report = Report.objects.create(
                reporter=request.user,
                reported_user=reported_user,
                reason=reason,
                report_description=report_description
            )
            print(f"Created report: {report}")
            return JsonResponse({'success': True, 'message': 'Report submitted successfully!'})
        else:
            return JsonResponse({'success': False, 'message': 'Missing required fields.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method. Only POST is allowed.'})





















