from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .forms import ProposalForm, ThesisDocumentForm, DefenseForm
from .models import (
    ThesisGroup,
    GroupMember,
    Proposal,
    Thesis,
    ThesisStatus,
    ThesisDocument,
    ThesisProgress,
    Defense,
    GroupConfiguration
)

from users.models import Student, Lecturer
from users.decorators import lecturer_required
from notification.models import Notification


# ============================================
# CREATE GROUP
# ============================================
@login_required
def create_group(request):
    supervisors = Lecturer.objects.filter(
        is_supervisor=True
    )

    current_student = Student.objects.get(
        user=request.user
    )

    config = GroupConfiguration.objects.first()
    max_students = 4

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
        name = request.POST.get(
            'name'
        )

        supervisor_id = request.POST.get(
            'supervisor'
        )

        member_ids = request.POST.getlist(
            'members'
        )

        # Include current student automatically
        selected_members = list(
            member_ids
        )

        if str(current_student.id) not in selected_members:
            selected_members.append(
                str(current_student.id)
            )

        total_members = len(
            selected_members
        )

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

        for member_id in selected_members:
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


# ============================================
# SUBMIT PROPOSAL
# ============================================
@login_required
def submit_proposal(request):
    student = Student.objects.get(
        user=request.user
    )

    group = ThesisGroup.objects.filter(
        groupmember__student=student
    ).first()

    if not group:
        return redirect(
            'create_group'
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


# ============================================
# LECTURER PROPOSALS
# ============================================
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
    proposals = Proposal.objects.filter(
        status__name='Pending'
    )

    context = {
        'proposals': proposals
    }

    return render(
        request,
        'thesis/pending_proposals.html',
        context
    )


# ============================================
# REVIEW PROPOSAL
# ============================================
@login_required
@lecturer_required
def review_proposal(request, proposal_id):
    lecturer = Lecturer.objects.get(
        user=request.user
    )

    if not lecturer.is_supervisor:
        messages.error(
            request,
            "Only supervisors can review proposals."
        )
        return redirect(
            'lecturer_proposals'
        )

    proposal = get_object_or_404(
        Proposal,
        id=proposal_id,
        group__supervisor=lecturer
    )

    statuses = ThesisStatus.objects.all()

    if request.method == 'POST':
        status_id = request.POST.get(
            'status'
        )

        comment = request.POST.get(
            'comment'
        )

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


# ============================================
# SUPERVISOR REVIEW
# ============================================
@login_required
@lecturer_required
def supervisor_review(request, proposal_id):
    lecturer = Lecturer.objects.get(
        user=request.user
    )

    if not lecturer.is_supervisor:
        messages.error(
            request,
            "Only supervisors can review proposals."
        )
        return redirect(
            'lecturer_dashboard'
        )

    proposal = get_object_or_404(
        Proposal,
        id=proposal_id,
        group__supervisor=lecturer
    )

    statuses = ThesisStatus.objects.all()

    if request.method == 'POST':
        status_id = request.POST.get(
            'status'
        )

        comment = request.POST.get(
            'comment'
        )

        selected_status = ThesisStatus.objects.get(
            id=status_id
        )

        proposal.status = selected_status
        proposal.supervisor_comment = comment
        proposal.save()

        if selected_status.name == "Approved":
            Thesis.objects.get_or_create(
                proposal=proposal,
                defaults={
                    'title': proposal.title,
                    'lecturer': proposal.reviewed_by_lecturer,
                    'supervisor': proposal.group.supervisor,
                    'status': selected_status
                }
            )

        members = GroupMember.objects.filter(
            group=proposal.group
        )

        for member in members:
            Notification.objects.create(
                user=member.student.user,
                message=f"""
Proposal '{proposal.title}'
updated to:
{selected_status.name}
""",
                sent_by=request.user
            )

        messages.success(
            request,
            "Proposal reviewed successfully."
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


# ============================================
# UPLOAD THESIS DOCUMENT
# ============================================
@login_required
def upload_thesis_document(request, thesis_id):
    thesis = get_object_or_404(
        Thesis,
        id=thesis_id
    )

    if request.user.role == 'student':
        student = Student.objects.get(
            user=request.user
        )

        is_member = GroupMember.objects.filter(
            group=thesis.proposal.group,
            student=student
        ).exists()

        if not is_member:
            messages.error(
                request,
                "You are not allowed to upload documents."
            )
            return redirect(
                'student_dashboard'
            )

    elif request.user.role == 'lecturer':
        lecturer = Lecturer.objects.get(
            user=request.user
        )

        if thesis.supervisor != lecturer:
            messages.error(
                request,
                "You are not assigned to this thesis."
            )
            return redirect(
                'lecturer_dashboard'
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

            messages.success(
                request,
                "Document uploaded successfully."
            )

            return redirect(
                'lecturer_group_detail',
                group_id=thesis.proposal.group.id
            )
    else:
        form = ThesisDocumentForm()

    context = {
        'form': form,
        'thesis': thesis
    }

    return render(
        request,
        'thesis/upload_document.html',
        context
    )

# ============================================
# SCHEDULE DEFENSE
# ============================================
@login_required
def schedule_defense(request, thesis_id):
    lecturer = Lecturer.objects.get(
        user=request.user
    )

    if not lecturer.is_supervisor:
        messages.error(
            request,
            "Only supervisors can schedule defenses."
        )

        return redirect(
            'lecturer_dashboard'
        )

    thesis = get_object_or_404(
        Thesis,
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

            messages.success(
                request,
                "Defense scheduled successfully."
            )

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


# ============================================
# LECTURER GROUPS
# ============================================
@login_required
@lecturer_required
def lecturer_groups(request):
    lecturer = Lecturer.objects.get(
        user=request.user
    )

    groups = ThesisGroup.objects.filter(
        supervisor=lecturer
    )

    context = {
        'groups': groups
    }

    return render(
        request,
        'thesis/lecturer_groups.html',
        context
    )


# ============================================
# LECTURER GROUP DETAIL
# ============================================
@login_required
@lecturer_required
def lecturer_group_detail(request, group_id):
    lecturer = Lecturer.objects.get(
        user=request.user
    )

    group = get_object_or_404(
        ThesisGroup,
        id=group_id,
        supervisor=lecturer
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
        ).order_by(
            '-created_at'
        )

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


# ============================================
# NOTIFICATION CENTER
# ============================================
@login_required
@lecturer_required
def notification_center(request):
    lecturer = Lecturer.objects.get(
        user=request.user
    )

    groups = ThesisGroup.objects.filter(
        supervisor=lecturer
    )

    students = Student.objects.filter(
        groupmember__group__supervisor=lecturer
    ).distinct()

    if request.method == "POST":
        send_type = request.POST.get(
            'send_type'
        )

        message = request.POST.get(
            'message'
        )

        # ================= SEND TO GROUP =================
        if send_type == "group":
            group_id = request.POST.get(
                'group_id'
            )

            group = ThesisGroup.objects.get(
                id=group_id
            )

            members = GroupMember.objects.filter(
                group=group
            )

            for member in members:
                Notification.objects.create(
                    user=member.student.user,
                    message=message
                )

        # ================= SEND TO INDIVIDUAL STUDENT =================
        else:
            student_id = request.POST.get(
                'student_id'
            )

            student = Student.objects.get(
                id=student_id
            )

            Notification.objects.create(
                user=student.user,
                message=message
            )

        messages.success(
            request,
            "Notification sent successfully."
        )

        return redirect(
            'notification_center'
        )

    context = {
        'groups': groups,
        'students': students
    }

    return render(
        request,
        'thesis/notification_center.html',
        context
    )


# ============================================
# LECTURER COMMENT ON PROPOSAL
# ============================================
@login_required
@lecturer_required
def lecturer_comment_proposal(request, proposal_id):
    lecturer = Lecturer.objects.get(
        user=request.user
    )

    proposal = get_object_or_404(
        Proposal,
        id=proposal_id
    )

    if request.method == 'POST':
        comment = request.POST.get(
            'comment'
        )

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
Lecturer commented on proposal:
{proposal.title}
""",
                sent_by=request.user
            )

        messages.success(
            request,
            "Comment added successfully."
        )

        return redirect(
            'lecturer_proposals'
        )

    context = {
        'proposal': proposal
    }

    return render(
        request,
        'thesis/lecturer_comment.html',
        context
    )