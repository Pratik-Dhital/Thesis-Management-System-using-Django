from django.shortcuts import render

# Create your views here.
from django.shortcuts import (
    render,
    redirect
)

from django.contrib.auth.decorators import login_required

from .forms import ProposalForm

from .models import (
    Proposal,
    ThesisStatus
)

from users.models import Student


# ================= SUBMIT PROPOSAL =================

@login_required
def submit_proposal(request):

    student = Student.objects.get(
        user=request.user
    )

    if request.method == 'POST':

        form = ProposalForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            proposal = form.save(
                commit=False
            )

            proposal.student = student

            proposal.status = ThesisStatus.objects.get(
                name='Pending'
            )

            proposal.save()

            return redirect(
                'student_dashboard'
            )

    else:

        form = ProposalForm()

    context = {
        'form': form
    }

    return render(
        request,
        'thesis/submit_proposal.html',
        context
    )