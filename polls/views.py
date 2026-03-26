from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import Candidate, Election, Vote
from django.contrib import messages

def home_page(request):
    candidates = Candidate.objects.all()
    election_open = Election.is_voting_open()
    already_voted = request.session.get('has_voted', False)
    return render(request, 'polls/home.html', {
        'candidates': candidates,
        'election_open': election_open,
        'already_voted': already_voted,
    })

def vote(request, candidate_id):
    if not Election.is_voting_open():
        messages.error(request, 'ขณะนี้ยังไม่เปิดรับการลงคะแนน')
        return redirect('home')

    if request.session.get('has_voted'):
        messages.warning(request, 'คุณได้ลงคะแนนแล้ว ไม่สามารถโหวตซ้ำได้')
        return redirect('home')

    candidate = get_object_or_404(Candidate, id=candidate_id)
    Vote.objects.create(candidate=candidate)
    request.session['has_voted'] = True
    messages.success(request, f'ลงคะแนนให้ {candidate.name} เรียบร้อยแล้ว!')
    return redirect('results')

def results(request):
    candidates = Candidate.objects.annotate(
        vote_count=Count('votes')
    ).order_by('-vote_count')
    total_votes = Vote.objects.count()
    return render(request, 'polls/results.html', {
        'candidates': candidates,
        'total_votes': total_votes,
    })