from django.urls import path

from .views import (
    create_group,
    submit_proposal,
    lecturer_proposals,
    review_proposal,
    pending_proposals,
    lecturer_groups,
    lecturer_group_detail,
    notification_center,
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
]
