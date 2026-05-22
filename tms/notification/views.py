from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from .forms import SendNotificationForm
from thesis.models import ThesisGroup, GroupMember
from users.models import Lecturer
from django.contrib import messages

@login_required
def send_notification(request, group_id):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    group = ThesisGroup.objects.get(
        id=group_id
    )

    if request.method == 'POST':

        form = SendNotificationForm(
            request.POST
        )

        if form.is_valid():

            message = form.cleaned_data[
                'message'
            ]

            send_type = form.cleaned_data[
                'send_type'
            ]

            if send_type == 'group':

                members = GroupMember.objects.filter(
                    group=group
                )

                for member in members:

                    Notification.objects.create(
                        user=member.student.user,
                        message=message
                    )

            else:

                student = form.cleaned_data[
                    'student'
                ]

                Notification.objects.create(
                    user=student.user,
                    message=message
                )

            messages.success(
                request,
                "Notification sent successfully"
            )

            return redirect(
                'lecturer_dashboard'
            )

    else:

        form = SendNotificationForm()

    context = {
        'form': form,
        'group': group
    }

    return render(
        request,
        'notification/send_notification.html',
        context
    )

@login_required
def student_notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'notifications': notifications
    }

    return render(
        request,
        'notification/student_notifications.html',
        context
    )