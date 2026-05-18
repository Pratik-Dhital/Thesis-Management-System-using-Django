from django.urls import path

from notification import views

from .views import (
    create_group,
    lecturer_comment_proposal,
    schedule_defense,
    submit_proposal,
    lecturer_proposals,
    review_proposal,
    pending_proposals,
    lecturer_groups,
    lecturer_group_detail,
    notification_center,
    supervisor_review,
)

urlpatterns = [
    path('create-group/', create_group, name='create_group'),
    path('submit-proposal/',submit_proposal,name='submit_proposal'),
    path('lecturer/proposals/', lecturer_proposals, name='lecturer_proposals'),
    path('lecturer/review/<int:proposal_id>/', review_proposal, name='review_proposal'),
    path('lecturer/pending/', pending_proposals, name='pending_proposals'),
    path('lecturer/groups/', lecturer_groups, name='lecturer_groups'),
    path('lecturer/group/<int:group_id>/', lecturer_group_detail, name='lecturer_group_detail'),
    path('notification-center/', notification_center, name='notification_center'),
    path('lecturer/comment/<int:proposal_id>/',lecturer_comment_proposal,name='lecturer_comment_proposal'),
    path('supervisor/review/<int:proposal_id>/',supervisor_review,name='supervisor_review'),
    path('schedule-defense/<int:group_id>/',schedule_defense,name='schedule_defense'),
]

