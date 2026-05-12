from django.shortcuts import render, redirect
from .models import Student, Lecturer, Supervisor
from django.http import HttpResponse
from django.contrib.auth import (get_user_model,authenticate,logout,login as auth_login)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import (
    StudentProfileForm,
    LecturerProfileForm,
    SupervisorProfileForm
)

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
                full_name=f"{first_name} {last_name}",
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

    student = Student.objects.get(
        user=request.user
    )

    if (
        not student.roll_no or
        not student.faculty or
        not student.department or
        not student.academic_level
    ):

        return redirect(
            'complete_student_profile'
        )

    return render(
        request,
        "student/dashboard.html"
    )

@login_required
def lecturer_dashboard(request):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    if (
        not lecturer.designation or
        not lecturer.faculty or
        not lecturer.department
    ):

        return redirect(
            'complete_lecturer_profile'
        )

    return render(
        request,
        "lecturer/dashboard.html"
    )

@login_required
def supervisor_dashboard(request):

    supervisor = Supervisor.objects.get(
        user=request.user
    )

    if (
        not supervisor.designation or
        not supervisor.qualification or
        not supervisor.faculty or
        not supervisor.department
    ):

        return redirect(
            'complete_supervisor_profile'
        )

    return render(
        request,
        "supervisor/dashboard.html"
    )

@login_required
def complete_student_profile(request):

    student = Student.objects.get(
        user=request.user
    )

    form = StudentProfileForm(
        instance=student
    )

    if request.method == 'POST':

        form = StudentProfileForm(
            request.POST,
            instance=student
        )

        if form.is_valid():

            form.save()

            return redirect(
                'student_dashboard'
            )

    context = {
        'form': form
    }

    return render(
        request,
        'student/complete_profile.html',
        context
    )

@login_required
def complete_lecturer_profile(request):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    form = LecturerProfileForm(
        instance=lecturer
    )

    if request.method == 'POST':

        form = LecturerProfileForm(
            request.POST,
            instance=lecturer
        )

        if form.is_valid():

            form.save()

            return redirect(
                'lecturer_dashboard'
            )

    context = {
        'form': form
    }

    return render(
        request,
        'lecturer/complete_profile.html',
        context
    )

@login_required
def complete_supervisor_profile(request):

    supervisor = Supervisor.objects.get(
        user=request.user
    )

    form = SupervisorProfileForm(
        instance=supervisor
    )

    if request.method == 'POST':

        form = SupervisorProfileForm(
            request.POST,
            instance=supervisor
        )

        if form.is_valid():

            form.save()

            return redirect(
                'supervisor_dashboard'
            )

    context = {
        'form': form
    }

    return render(
        request,
        'supervisor/complete_profile.html',
        context
    )