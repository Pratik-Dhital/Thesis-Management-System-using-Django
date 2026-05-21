from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def generate_approval_letter(thesis):

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=letter
    )

    y = 750

    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawString(
        180,
        y,
        "THESIS APPROVAL LETTER"
    )

    y -= 60

    pdf.setFont(
        "Helvetica",
        12
    )

    group = thesis.proposal.group

    pdf.drawString(
        50,
        y,
        f"Group Name: {group.name}"
    )

    y -= 30

    pdf.drawString(
        50,
        y,
        f"Thesis Title: {thesis.title}"
    )

    y -= 30

    pdf.drawString(
        50,
        y,
        f"Supervisor: {thesis.supervisor.full_name}"
    )

    y -= 40

    pdf.drawString(
        50,
        y,
        "Group Members:"
    )

    y -= 30

    members = group.groupmember_set.all()

    for index, member in enumerate(members, start=1):

        pdf.drawString(
            80,
            y,
            f"{index}. {member.student.full_name}"
        )

        y -= 25

    y -= 30

    pdf.drawString(
        50,
        y,
        f"Status: {thesis.status.name}"
    )

    y -= 30

    pdf.drawString(
        50,
        y,
        f"Date: {thesis.created_at.date()}"
    )

    y -= 80

    pdf.drawString(
        50,
        y,
        "Supervisor Signature:"
    )

    y -= 50

    pdf.line(
        50,
        y,
        250,
        y
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        thesis.supervisor.full_name
    )

    pdf.save()

    buffer.seek(0)

    return buffer