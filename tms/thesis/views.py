from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProposalForm
from .models import *
from users.models import Student, Lecturer
from users.decorators import lecturer_required
from django.contrib import messages
from django.utils import timezone
from notification.models import Notification
from .forms import ThesisDocumentForm
from .forms import DefenseForm
# Create your views here.

@login_required
def create_group(request):

    supervisors = Lecturer.objects.filter(
        is_supervisor=True
    )

    current_student = Student.objects.get(
        user=request.user
    )

    config = GroupConfiguration.objects.first()

    max_students = 1

    if config:
        max_students = config.max_students_per_group

    existing_group = GroupMember.objects.filter(
        student=current_student
    ).first()

    if existing_group:

        messages.warning(
            request,
            "You are already in a group."
        )

        return redirect(
            'student_dashboard'
        )

    students = Student.objects.filter(
        department=current_student.department
    ).exclude(
        groupmember__isnull=False
    )

    if request.method == 'POST':

        name = request.POST.get('name')

        supervisor_id = request.POST.get(
            'supervisor'
        )

        member_ids = request.POST.getlist(
            'members'
        )

        total_members = len(member_ids)

        if total_members > max_students:

            messages.error(
                request,
                f"Maximum allowed students is {max_students}"
            )

            return redirect(
                'create_group'
            )

        supervisor = Lecturer.objects.get(
            id=supervisor_id
        )

        group = ThesisGroup.objects.create(
            name=name,
            supervisor=supervisor
        )

        for member_id in member_ids:

            student = Student.objects.get(
                id=member_id
            )

            GroupMember.objects.create(
                group=group,
                student=student
            )

        messages.success(
            request,
            "Group created successfully"
        )

        return redirect(
            'student_dashboard'
        )

    context = {
        'supervisors': supervisors,
        'students': students,
        'max_students': max_students
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

    group = ThesisGroup.objects.filter(
        groupmember__student=student
    ).first()

    if not group:
        return redirect('create_group')

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
def pending_proposals(request):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    proposals = Proposal.objects.filter(
        status_name = 'pending'
    )

    context = {
        'proposals': proposals
    }

    return render(
        request,
        'thesis/pending_proposals.html',
        context
    )

@login_required
@lecturer_required
def review_proposal(request, proposal_id):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    proposal = Proposal.objects.get(
        id=proposal_id
    )

    statuses = ThesisStatus.objects.all()

    if request.method == 'POST':

        status_id = request.POST.get('status')

        comment = request.POST.get('comment')

        selected_status = ThesisStatus.objects.get(
            id=status_id
        )

        proposal.status = selected_status

        proposal.lecturer_comment = comment

        proposal.reviewed_by_lecturer = lecturer

        proposal.reviewed_at = timezone.now()

        proposal.save()

        members = GroupMember.objects.filter(
            group=proposal.group
        )

        for member in members:

            Notification.objects.create(
                user=member.student.user,
                message=f"""
Proposal '{proposal.title}'
status updated to:
{selected_status.name}
"""
            )

        messages.success(
            request,
            "Proposal reviewed successfully"
        )

        return redirect(
            'lecturer_proposals'
        )

    context = {
        'proposal': proposal,
        'statuses': statuses
    }

    return render(
        request,
        'thesis/review_proposal.html',
        context
    )

@login_required
def supervisor_pending_proposals(request):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    proposals = Proposal.objects.filter(
        status_name='Lecturer Approved',
        group__supervisor=lecturer
    )

    context = {
        'proposals': proposals
    }

    return render(
        request,
        'thesis/supervisor_pending.html',
        context
    )

@login_required
def supervisor_review(request, proposal_id):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    proposal = Proposal.objects.get(
        id=proposal_id
    )

    statuses = ThesisStatus.objects.all()

    if request.method == 'POST':

        status_id = request.POST.get('status')

        comment = request.POST.get('comment')

        selected_status = ThesisStatus.objects.get(
            id=status_id
        )

        proposal.status = selected_status

        proposal.supervisor_comment = comment

        proposal.save()

        if selected_status.name == "Supervisor Approved":

            thesis = Thesis.objects.create(
                thesis=thesis,
                
                title=proposal.title,

                proposal=proposal,

                lecturer=proposal.reviewed_by_lecturer,

                supervisor=proposal.group.supervisor,

                status=selected_status
            )

        return redirect(
            'supervisor_pending'
        )

    context = {
        'proposal': proposal,
        'statuses': statuses
    }

    return render(
        request,
        'thesis/supervisor_review.html',
        context
    )

@login_required
def upload_thesis_document(request, thesis_id):

    thesis = Thesis.objects.get(
        id=thesis_id
    )

    if request.method == 'POST':

        form = ThesisDocumentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            document = form.save(
                commit=False
            )

            document.thesis = thesis

            document.save()

            return redirect(
                'student_dashboard'
            )

    else:

        form = ThesisDocumentForm()

    context = {
        'form': form
    }

    return render(
        request,
        'thesis/upload_document.html',
        context
    )

@login_required
def schedule_defense(request, thesis_id):

    thesis = Thesis.objects.get(
        id=thesis_id
    )

    if request.method == 'POST':

        form = DefenseForm(
            request.POST
        )

        if form.is_valid():

            defense = form.save(
                commit=False
            )

            defense.thesis = thesis

            defense.save()

            return redirect(
                'lecturer_dashboard'
            )

    else:

        form = DefenseForm()

    context = {
        'form': form
    }

    return render(
        request,
        'thesis/schedule_defense.html',
        context
    )

@login_required
@lecturer_required
def lecturer_groups(request):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    groups = ThesisGroup.objects.all()

    context = {
        'groups': groups
    }

    return render(
        request,
        'thesis/lecturer_groups.html',
        context
    )

@login_required
@lecturer_required
def lecturer_group_detail(request, group_id):

    lecturer = Lecturer.objects.get(
        user=request.user
    )

    group = ThesisGroup.objects.get(
        id=group_id
    )

    members = GroupMember.objects.filter(
        group=group
    )

    proposal = Proposal.objects.filter(
        group=group
    ).first()

    thesis = None

    progress = None

    documents = None

    defense = None

    if proposal:

        thesis = Thesis.objects.filter(
            proposal=proposal
        ).first()

    if thesis:

        progress = ThesisProgress.objects.filter(
            thesis=thesis
        ).order_by('-created_at')

        documents = ThesisDocument.objects.filter(
            thesis=thesis
        )

        defense = Defense.objects.filter(
            thesis=thesis
        ).first()

    context = {
        'group': group,
        'members': members,
        'proposal': proposal,
        'thesis': thesis,
        'progress': progress,
        'documents': documents,
        'defense': defense
    }

    return render(
        request,
        'thesis/lecturer_group_detail.html',
        context
    )