from django.urls import path

from .views import submit_proposal

urlpatterns = [

    path(
        'submit-proposal/',
        submit_proposal,
        name='submit_proposal'
    ),
]