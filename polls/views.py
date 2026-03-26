from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import Candidate, Vote

def home_page(request):
    candidates = Candidate.objects.all()
    return render(request, 'polls/home.html', {'candidates': candidates})

def vote(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    Vote.objects.create(candidate=candidate)
    return redirect('results')

def results(request):
    candidates = Candidate.objects.annotate(
        vote_count=Count('votes')
    ).order_by('-vote_count')
    return render(request, 'polls/results.html', {'candidates': candidates})