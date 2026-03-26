from django.contrib import admin
from .models import Candidate, Vote, Election

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'party', 'vote_count']
    search_fields = ['name', 'party']

    def vote_count(self, obj):
        return obj.votes.count()
    vote_count.short_description = 'คะแนน'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'created_at']
    list_filter = ['candidate']
    readonly_fields = ['created_at']

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_open', 'start_time', 'end_time']