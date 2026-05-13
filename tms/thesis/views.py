from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProposalForm
from .models import *
from users.models import Student, Lecturer
from users.decorators import lecturer_required
from django.contrib import messages
# Create your views here.

@login_required
def create_group(request):

    supervisors = Lecturer.objects.filter(
        is_supervisor=True
    )

    current_student = Student.objects.get(
    user=request.user
    )

    students = Student.objects.filter(
        department=current_student.department
    ).exclude(
        groupmember__isnull=False
    )

    if request.method == 'POST':

        name = request.POST.get('name')
        supervisor_id = request.POST.get('supervisor')

        supervisor = Lecturer.objects.get(
            id=supervisor_id
        )

        group = ThesisGroup.objects.create(
            name=name,
            supervisor=supervisor
        )

        member_ids = request.POST.getlist('members')

        for member_id in member_ids:

            student = Student.objects.get(
                id=member_id
            )

            GroupMember.objects.create(
                group=group,
                student=student
            )

        return redirect('student_dashboard')

    context = {
        'supervisors': supervisors,
        'students': students
    }

    return render(
        request,
        'thesis/create_group.html',
        context
    )

# ================= SUBMIT PROPOSAL =================
@login_required
def submit_proposal(request):

    student = Student.objects.get(
        user=request.user
    )

    # find student's group
    member = GroupMember.objects.filter(
        student=student
    ).first()

    if not member:
        return redirect('create_group')

    group = member.group

    if request.method == 'POST':

        form = ProposalForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            proposal = form.save(
                commit=False
            )

            proposal.group = group

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

@login_required
@lecturer_required
def lecturer_proposals(request):

    proposals = Proposal.objects.filter(
        status__name='Pending'
    )

    context = {
        'proposals': proposals
    }

    return render(
        request,
        'thesis/lecturer_proposals.html',
        context
    )

@login_required
@lecturer_required
def review_proposal(request, proposal_id):

    proposal = Proposal.objects.get(
        id=proposal_id
    )

    if request.method == 'POST':

        action = request.POST.get('action')
        comment = request.POST.get('comment')

        proposal.lecturer_comment = comment

        if action == 'approve':

            proposal.status = ThesisStatus.objects.get(
                name='Lecturer Approved'
            )

        elif action == 'reject':

            proposal.status = ThesisStatus.objects.get(
                name='Lecturer Rejected'
            )

        proposal.save()

        messages.success(
            request,
            "Proposal reviewed successfully"
        )

        return redirect(
            'lecturer_proposals'
        )

    context = {
        'proposal': proposal
    }

    return render(
        request,
        'thesis/review_proposal.html',
        context
    )

