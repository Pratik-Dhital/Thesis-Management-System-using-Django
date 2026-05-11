from django.shortcuts import render, redirect
from .models import *
from django.http import HttpResponse
from django.contrib.auth import get_user_model
# Create your views here.

def login(request):
    return render(request, "login.html")
 
User = get_user_model()

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        user.save()
        return redirect('login')
    return render(request, "signup.html")