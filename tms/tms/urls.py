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
from django.urls import path
from users.views import login_view, signup_view, logout_view, student_dashboard, supervisor_dashboard, lecturer_dashboard, home, complete_lecturer_profile, complete_student_profile, complete_supervisor_profile
urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name="login"),
    path('signup/', signup_view, name="signup"),
    path('logout/', logout_view, name='logout'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/dashboard/create', student_dashboard, name='student_dashboard.create'),
    path('student/dashboard/<int:id>/edit', student_dashboard, name='student_dashboard.edit'),
    path('supervisor/dashboard/', supervisor_dashboard, name='supervisor_dashboard'),
    path('lecturer/dashboard/', lecturer_dashboard, name='lecturer_dashboard'),
    path('student/profile/', complete_student_profile, name='complete_student_profile'),
    path('lecturer/profile/', complete_lecturer_profile, name='complete_lecturer_profile'),
    path('supervisor/profile/', complete_supervisor_profile, name='complete_supervisor_profile'),
    path('admin/', admin.site.urls),
]   
