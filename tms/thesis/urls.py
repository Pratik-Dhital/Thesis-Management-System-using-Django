from django.urls import path
from thesis import views
from .views import lecturer_group_detail, submit_proposal, create_group, lecturer_proposals, review_proposal, pending_proposals, lecturer_groups, lecturer_group_detail, supervisor_pending_proposals, supervisor_review, upload_thesis_document, supervisor_pending_proposals, supervisor_review, upload_thesis_document, schedule_defense

urlpatterns = [
    path('create-group/', create_group, name='create_group'),
    path('submit-proposal/',submit_proposal,name='submit_proposal'),
    path('lecturer/proposals/', lecturer_proposals, name='lecturer_proposals'),
    path('lecturer/review/<int:proposal_id>/', review_proposal, name='review_proposal'),
    path('lecturer/pending/', pending_proposals, name='pending_proposals'),
    path('supervisor/proposals/', views.supervisor_pending_proposals, name='supervisor_pending'),
    path('supervisor/review/<int:proposal_id>/',views.supervisor_review,name='supervisor_review'),
    path('upload-document/<int:thesis_id>/',views.upload_thesis_document,name='upload_document'),
    path('schedule-defense/<int:thesis_id>/', views.schedule_defense, name='schedule_defense'),
    path('lecturer/groups/', lecturer_groups, name='lecturer_groups'),
    path('lecturer/group/<int:group_id>/', lecturer_group_detail, name='lecturer_group_detail'),
]