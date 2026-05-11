from django.contrib import admin
from .models import ThesisStatus, Thesis, ThesisDocument, ThesisGroup, Proposal, GroupMember,Review, Defense
# Register your models here.

admin.site.register(ThesisStatus)
admin.site.register(Thesis)
admin.site.register(ThesisDocument)
admin.site.register(ThesisGroup)
admin.site.register(Proposal)
admin.site.register(GroupMember)
admin.site.register(Review)
admin.site.register(Defense)
