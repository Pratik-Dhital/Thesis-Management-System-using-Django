"""
URL configuration for tms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import login_view, logout_view, student_dashboard,lecturer_dashboard, home, complete_lecturer_profile, complete_student_profile, admin_dashboard, create_user, manage_users, assign_role, manage_faculty, manage_department
urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name='logout'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/dashboard/create', student_dashboard, name='student_dashboard.create'),
    path('student/dashboard/<int:id>/edit', student_dashboard, name='student_dashboard.edit'),
    path('lecturer/dashboard/', lecturer_dashboard, name='lecturer_dashboard'),
    path('student/profile/', complete_student_profile, name='complete_student_profile'),
    path('lecturer/profile/', complete_lecturer_profile, name='complete_lecturer_profile'),
    path('thesis/', include('thesis.urls')),
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/create-user/', create_user, name='create_user'),
    path('admin-panel/manage-users/', manage_users, name='manage_users'),
    path('admin-panel/assign-role/<int:user_id>/', assign_role, name='assign_role'),
    path('admin-panel/manage-faculty/',manage_faculty, name='manage_faculty'),
    path('admin-panel/manage-department/', manage_department,name='manage_department'),
    path('admin/', admin.site.urls),
]   

