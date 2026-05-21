from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login as auth_login,
    logout
)
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)
from .models import Student, Lecturer
from .forms import StudentProfileForm, LecturerProfileForm
from .decorators import student_required, lecturer_required
from thesis.models import (
    GroupMember,
    ThesisGroup,
    Proposal,
    Defense
)
from notification.models import Notification
from academics.models import Faculty, Department


User = get_user_model()

# LOGIN
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

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')

# HOME
def home(request):
    return render(request, "home.html" )

# DASHBOARDS
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
    return render(request,'student/dashboard.html',context)

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
    # COUNTS
    pending_reviews = Proposal.objects.filter(
        group__supervisor=lecturer,
        status__name='Pending'
    ).count()

    scheduled_defenses = Defense.objects.filter(
        thesis__supervisor=lecturer
    ).count()
    supervised_students = students.count()
    context = {
        'lecturer_groups': lecturer_groups,
        'students': students,
        'pending_reviews': pending_reviews,
        'scheduled_defenses': scheduled_defenses,
        'supervised_students': supervised_students
    }
    return render(request,"lecturer/dashboard.html",context)

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
    return render(request,'student/complete_profile.html',context)

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
    return render(request,'lecturer/complete_profile.html',context)

def admin_required(user):
    return user.is_superuser

@user_passes_test(admin_required)
def admin_dashboard(request):
    return render(request,'admin_panel/dashboard.html')

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
    return render(request,'admin_panel/create_user.html')

@user_passes_test(admin_required)
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(
            request,
            "User deleted successfully"
        )
        return redirect('manage_users')
    context = {
        'user_obj': user
    }
    return render(request,'admin_panel/delete_user.html',context)

@user_passes_test(admin_required)
def manage_users(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request,'admin_panel/manage_users.html',context)

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
    return render(request,'admin_panel/assign_roles.html',context)

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
    return render(request,'admin_panel/manage_faculty.html',context)

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
    return render(request,'admin_panel/manage_departments.html',context)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    context = {
        'notifications': notifications
    }
    return render(request,'notifications.html',context)