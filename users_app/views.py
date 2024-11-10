from django.contrib.auth import login
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from users_app.forms import RegisterForm
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