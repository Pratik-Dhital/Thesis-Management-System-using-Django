from django.shortcuts import render, redirect
from .models import Student, Lecturer, Supervisor
from django.http import HttpResponse
from django.contrib.auth import (
    get_user_model,
    authenticate,
    logout,
    login as auth_login
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required


User = get_user_model()


# ================= LOGIN =================

def login_view(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            auth_login(request, user)

            if user.role == 'student':
                return redirect("student_dashboard")

            elif user.role == 'lecturer':
                return redirect('lecturer_dashboard')

            elif user.role == 'supervisor':
                return redirect('supervisor_dashboard')

        else:
            messages.error(
                request,
                "Invalid email or password"
            )

    return render(request, "login.html")


# ================= SIGNUP =================

def signup_view(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')

        # Check duplicate email
        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already exists"
            )

            return redirect('signup')

        # Create user
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            role=role
        )

        user.set_password(password)
        user.save()

        # Create profile based on role

        if role == "student":

            Student.objects.create(
                user=user,
                full_name=f"{first_name} {last_name}"
            )

        elif role == "lecturer":

            Lecturer.objects.create(
                user=user,
                full_name=f"{first_name} {last_name}"
            )

        elif role == "supervisor":

            Supervisor.objects.create(
                user=user,
                full_name=f"{first_name} {last_name}"
            )

        messages.success(
            request,
            "Account created successfully"
        )

        return redirect('login')

    return render(request, "signup.html")


# ================= LOGOUT =================

def logout_view(request):

    logout(request)

    return redirect('login')


# ================= HOME =================

def home(request):
    return render(request, "home.html" )


# ================= DASHBOARDS =================

@login_required
def student_dashboard(request):

    return HttpResponse("Student Dashboard")


@login_required
def lecturer_dashboard(request):

    return HttpResponse("Lecturer Dashboard")


@login_required
def supervisor_dashboard(request):

    return HttpResponse("Supervisor Dashboard")