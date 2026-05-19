from django.shortcuts import render, redirect
from thesis.models import GroupMember
from .models import Student, Lecturer
from django.contrib.auth import (get_user_model,authenticate,logout,login as auth_login)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import (StudentProfileForm, LecturerProfileForm)
from notification.models import Notification
from academics.models import Faculty, Department
from django.contrib.auth.decorators import user_passes_test
from users.decorators import student_required, lecturer_required
from thesis.models import ThesisGroup
from users.models import Student
from thesis.models import ThesisGroup
from users.models import Student, Lecturer
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

            elif user.role == 'admin':
                return redirect('admin_dashboard')

        else:
            messages.error(
                request,
                "Invalid email or password"
            )

    return render(request, "login.html")


# ================= SIGNUP =================

# def signup_view(request):

#     if request.method == 'POST':

#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         role = request.POST.get('role')
#         password = request.POST.get('password')

#         # Check duplicate email
#         if User.objects.filter(email=email).exists():

#             messages.error(
#                 request,
#                 "Email already exists"
#             )

#             return redirect('signup')

#         # Create user
#         user = User.objects.create(
#             first_name=first_name,
#             last_name=last_name,
#             username=username,
#             email=email,
#             role=role
#         )

#         user.set_password(password)
#         user.save()

#         # Create profile based on role

#         if role == "student":

#             Student.objects.create(
#                 user=user,
#                 full_name=f"{first_name} {last_name}",
#             )

#         elif role == "lecturer":

#             Lecturer.objects.create(
#                 user=user,
#                 full_name=f"{first_name} {last_name}"
#             )

#         elif role == "supervisor":

#             Supervisor.objects.create(
#                 user=user,
#                 full_name=f"{first_name} {last_name}"
#             )

#         messages.success(
#             request,
#             "Account created successfully"
#         )

#         return redirect('login')

#     return render(request, "signup.html")


# ================= LOGOUT =================

def logout_view(request):

    logout(request)

    return redirect('login')


# ================= HOME =================

def home(request):
    return render(request, "home.html" )

# ================= DASHBOARDS =================

@login_required
@student_required
def student_dashboard(request):

    student = Student.objects.get(
        user=request.user
    )

    has_group = GroupMember.objects.filter(
        student=student
    ).exists()

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    latest_notification = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at').first()

    context = {
        'has_group': has_group,
        'notifications': notifications,
        'latest_notification': latest_notification
    }

    return render(
        request,
        'student/dashboard.html',
        context
    )

@login_required
@lecturer_required
def lecturer_dashboard(request):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    # PROFILE CHECK
    if (
        not lecturer.designation or
        not lecturer.faculty or
        not lecturer.department
    ):

        return redirect(
            'complete_lecturer_profile'
        )

    # GROUPS UNDER THIS LECTURER
    lecturer_groups = ThesisGroup.objects.filter(
        supervisor=lecturer
    )

    # STUDENTS UNDER THIS LECTURER
    students = Student.objects.filter(
        groupmember__group__supervisor=lecturer
    ).distinct()

    context = {

        'lecturer_groups': lecturer_groups,

        'students': students

    }

    return render(
        request,
        "lecturer/dashboard.html",
        context
    )

# @login_required
# def supervisor_dashboard(request):

#     supervisor = Supervisor.objects.get(
#         user=request.user
#     )

#     if (
#         not supervisor.designation or
#         not supervisor.qualification or
#         not supervisor.faculty or
#         not supervisor.department
#     ):

#         return redirect(
#             'complete_supervisor_profile'
#         )

#     return render(
#         request,
#         "supervisor/dashboard.html"
#     )

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

def admin_required(user):
    return user.is_superuser

@user_passes_test(admin_required)
def admin_dashboard(request):

    return render(
        request,
        'admin_panel/dashboard.html'
    )

@user_passes_test(admin_required)
def create_user(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email
        )

        user.set_password(password)
        user.save()

        messages.success(
            request,
            "User created successfully"
        )

        return redirect('manage_users')

    return render(
        request,
        'admin_panel/create_user.html'
    )

@user_passes_test(admin_required)
def manage_users(request):

    users = User.objects.all()

    context = {
        'users': users
    }

    return render(
        request,
        'admin_panel/manage_users.html',
        context
    )

@user_passes_test(admin_required)
def assign_role(request, user_id):

    user = User.objects.get(id=user_id)

    if request.method == 'POST':

        role = request.POST.get('role')

        user.role = role
        user.save()

        # create profile automatically

        if role == 'student':

            Student.objects.get_or_create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}"
            )

        elif role == 'lecturer':

            Lecturer.objects.get_or_create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}"
            )

        messages.success(
            request,
            "Role assigned successfully"
        )

        return redirect('manage_users')

    context = {
        'user_obj': user
    }

    return render(
        request,
        'admin_panel/assign_roles.html',
        context
    )

@user_passes_test(admin_required)
def manage_faculty(request):

    if request.method == 'POST':

        name = request.POST.get('name')

        Faculty.objects.create(
            name=name
        )

        return redirect('manage_faculty')

    faculties = Faculty.objects.all()

    context = {
        'faculties': faculties
    }

    return render(
        request,
        'admin_panel/manage_faculty.html',
        context
    )
@user_passes_test(admin_required)
def manage_department(request):

    if request.method == 'POST':

        faculty_id = request.POST.get('faculty')
        name = request.POST.get('name')

        faculty = Faculty.objects.get(id=faculty_id)

        Department.objects.create(
            faculty=faculty,
            name=name
        )

        return redirect('manage_department')

    faculties = Faculty.objects.all()
    departments = Department.objects.all()

    context = {
        'faculties': faculties,
        'departments': departments
    }

    return render(
        request,
        'admin_panel/manage_departments.html',
        context
    )

@login_required
def notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'notifications': notifications
    }

    return render(
        request,
        'notifications.html',
        context
    )

# @login_required
# def complete_supervisor_profile(request):

#     supervisor = Supervisor.objects.get(
#         user=request.user
#     )

#     form = SupervisorProfileForm(
#         instance=supervisor
#     )

#     if request.method == 'POST':

#         form = SupervisorProfileForm(
#             request.POST,
#             instance=supervisor
#         )

#         if form.is_valid():

#             form.save()

#             return redirect(
#                 'supervisor_dashboard'
#             )

#     context = {
#         'form': form
#     }

#     return render(
#         request,
#         'supervisor/complete_profile.html',
#         context
#     )