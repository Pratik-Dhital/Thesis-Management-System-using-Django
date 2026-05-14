from django.urls import path
from .views import *

urlpatterns = [

    path(
        'send/',
        send_notification,
        name='send_notification'
    ),

    path(
        'student/',
        student_notifications,
        name='student_notifications'
    ),
]