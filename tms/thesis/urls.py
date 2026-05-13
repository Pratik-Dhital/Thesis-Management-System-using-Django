from django.urls import path

from .views import (
    submit_proposal,
    create_group,
    lecturer_proposals,
    review_proposal,
)

urlpatterns = [

    path(
        'create-group/',
        create_group,
        name='create_group'
    ),

    path(
        'submit-proposal/',
        submit_proposal,
        name='submit_proposal'
    ),

    path(
        'lecturer/proposals/',
        lecturer_proposals,
        name='lecturer_proposals'
    ),

    path(
        'lecturer/review/<int:proposal_id>/',
        review_proposal,
        name='review_proposal'
    ),
]