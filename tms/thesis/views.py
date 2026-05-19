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

# Create Group
@login_required
def create_group(request):

    current_student = get_object_or_404(
        Student,
        user=request.user
    )

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

    supervisors = Lecturer.objects.filter(
        is_supervisor=True
    )

    config = GroupConfiguration.objects.first()

    max_students = 4

    if config:
        max_students = config.max_students_per_group

    students = Student.objects.filter(
        department=current_student.department
    ).exclude(
        id=current_student.id
    ).exclude(
        groupmember__isnull=False
    )

    if request.method == 'POST':

        try:

            name = request.POST.get(
                'name'
            )

            supervisor_id = request.POST.get(
                'supervisor'
            )

            member_ids = request.POST.getlist(
                'members'
            )

            supervisor = Lecturer.objects.get(
                id=supervisor_id
            )

            group = ThesisGroup.objects.create(
                name=name,
                supervisor=supervisor
            )

            # add current student automatically
            GroupMember.objects.create(
                group=group,
                student=current_student
            )

            # add selected members
            for member_id in member_ids:

                student = Student.objects.get(
                    id=member_id
                )

                # prevent duplicate insert
                if not GroupMember.objects.filter(
                    group=group,
                    student=student
                ).exists():

                    GroupMember.objects.create(
                        group=group,
                        student=student
                    )

            messages.success(
                request,
                "Group created successfully."
            )

            return redirect(
                'student_dashboard'
            )

        except Exception as e:

            messages.error(
                request,
                f"Error creating group: {str(e)}"
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

# SUBMIT PROPOSAL
@login_required
def submit_proposal(request):

    student = Student.objects.get(
        user=request.user
    )

    group = ThesisGroup.objects.filter(
        groupmember__student=student
    ).first()

    if not group:

        messages.error(
            request,
            "You must create a group first."
        )

        return redirect(
            'create_group'
        )

    # latest proposal
    latest_proposal = Proposal.objects.filter(
        group=group
    ).order_by(
        '-version'
    ).first()

    defense = Defense.objects.filter(
        thesis__proposal__group=group
    ).first()

    # deadline check
    if defense:

        if timezone.now() > defense.submission_deadline:

            messages.error(
                request,
                "Submission deadline exceeded."
            )

            return redirect(
                'student_dashboard'
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

            # versioning
            if latest_proposal:
                proposal.version = latest_proposal.version + 1
            else:
                proposal.version = 1

            proposal.save()

            messages.success(
                request,
                "Proposal submitted successfully."
            )

            return redirect(
                'student_dashboard'
            )

    else:

        form = ProposalForm()

    context = {
        'form': form,
        'latest_proposal': latest_proposal,
        'defense': defense
    }

    return render(
        request,
        'thesis/submit_proposal.html',
        context
    )

# LECTURER PROPOSALS
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

# REVIEW PROPOSAL
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
        group__supervisor__user=request.user
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

        thesis = None

        # create thesis automatically
        if selected_status.name.lower() in ['approved', 'under review']:

            thesis, created = Thesis.objects.get_or_create(
                proposal=proposal,
                defaults={
                    'title': proposal.title,
                    'supervisor': lecturer,
                    'lecturer': lecturer,
                    'status': selected_status,
                }
            )

            thesis.status = selected_status
            thesis.save()

            # copy proposal document
            if proposal.document:

                ThesisDocument.objects.get_or_create(
                    thesis=thesis,
                    file=proposal.document
                )

            # create thesis progress
            ThesisProgress.objects.get_or_create(
                thesis=thesis,
                title="Proposal Reviewed",
                defaults={
                    'description': f"Proposal status updated to {selected_status.name}"
                }
            )

        # notify students
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

# SUPERVISOR REVIEW
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

# UPLOAD THESIS DOCUMENT
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

# SCHEDULE DEFENSE
@login_required
@lecturer_required
def schedule_defense(request, group_id):

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

    group = get_object_or_404(
        ThesisGroup,
        id=group_id,
        supervisor=lecturer
    )

    thesis = Thesis.objects.filter(
        proposal__group=group
    ).first()

    if not thesis:

        messages.error(
            request,
            "No thesis found for this group."
        )

        return redirect(
            'lecturer_group_detail',
            group.id
        )

    if request.method == 'POST':

        form = DefenseForm(
            request.POST
        )

        if form.is_valid():

            existing_defense = Defense.objects.filter(
                thesis=thesis
            ).first()

            if existing_defense:

                existing_defense.date = form.cleaned_data['date']
                existing_defense.time = form.cleaned_data['time']
                existing_defense.venue = form.cleaned_data['venue']
                existing_defense.submission_deadline = form.cleaned_data['submission_deadline']
                existing_defense.scheduled_by = lecturer

                existing_defense.save()

                defense = existing_defense

            else:

                defense = form.save(
                    commit=False
                )

                defense.thesis = thesis
                defense.scheduled_by = lecturer

                defense.save()

            # =========================
            # SEND NOTIFICATION
            # =========================
            members = GroupMember.objects.filter(
                group=group
            )

            for member in members:

                Notification.objects.create(
                    user=member.student.user,
                    message=f"""
    Defense Scheduled
    Group: {group.name}
    Date: {defense.date}
    Time: {defense.time}
    Venue: {defense.venue}
    Submission Deadline: {defense.submission_deadline}
    """
                )
        
            Notification.objects.create(
                user=member.student.user,
                message=f"""
    Defense Scheduled

    Date: {defense.date}
    Time: {defense.time}
    Venue: {defense.venue}
    Submission Deadline: {defense.submission_deadline}
    """
            )

            # create progress entry
            ThesisProgress.objects.create(
                thesis=thesis,
                title="Defense Scheduled",
                description=f"""
Defense scheduled on
{defense.date}
at
{defense.time}
"""
            )

            messages.success(
                request,
                "Defense scheduled successfully."
            )

            return redirect(
                'lecturer_group_detail',
                group.id
            )

    else:

        form = DefenseForm()

    context = {
        'form': form,
        'group': group,
        'thesis': thesis
    }

    return render(
        request,
        'thesis/schedule_defense.html',
        context
    )

# LECTURER GROUPS
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


# LECTURER GROUP DETAIL
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

    thesis = Thesis.objects.filter(
        proposal__group=group
    ).first()

    progress = []

    documents = []

    defense = None

    if thesis:

        progress = ThesisProgress.objects.filter(
            thesis=thesis
        ).order_by('-created_at')

        documents = ThesisDocument.objects.filter(
            thesis=thesis
        ).order_by('-uploaded_at')

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
        'defense': defense,
    }

    return render(
        request,
        'thesis/lecturer_group_detail.html',
        context
    )

# NOTIFICATION CENTER
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

        # SEND TO GROUP
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

        # SEND TO INDIVIDUAL STUDENT 
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

# LECTURER COMMENT ON PROPOSAL
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

@login_required
def proposal_history(request):

    student = Student.objects.get(
        user=request.user
    )

    member = GroupMember.objects.filter(
        student=student
    ).first()

    if not member:

        messages.error(
            request,
            "No group found."
        )

        return redirect(
            'student_dashboard'
        )

    proposals = Proposal.objects.filter(
        group=member.group
    ).order_by('-submitted_at')

    context = {
        'proposals': proposals
    }

    return render(
        request,
        'thesis/proposal_history.html',
        context
    )