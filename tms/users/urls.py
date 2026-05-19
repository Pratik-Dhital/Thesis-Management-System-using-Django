from django.urls import path
from .views import login_view, logout_view, student_dashboard,lecturer_dashboard, complete_lecturer_profile, complete_student_profile, admin_dashboard, create_user, manage_users, assign_role, manage_faculty, manage_department, home

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name='logout'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('lecturer/dashboard/', lecturer_dashboard, name='lecturer_dashboard'),
    path('student/profile/', complete_student_profile, name='complete_student_profile'),
    path('lecturer/profile/', complete_lecturer_profile, name='complete_lecturer_profile'),
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/create-user/', create_user, name='create_user'),
    path('admin-panel/manage-users/', manage_users, name='manage_users'),
    path('admin-panel/assign-role/<int:user_id>/', assign_role, name='assign_role'),
    path('admin-panel/manage-faculty/',manage_faculty, name='manage_faculty'),
    path('admin-panel/manage-department/', manage_department,name='manage_department'),
]