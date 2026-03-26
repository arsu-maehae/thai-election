from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from .models import Candidate, Vote, Election, Voter
from .forms import VoterLoginForm


def voter_login(request):
    if request.session.get('voter_id'):
        return redirect('home')

    form = VoterLoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        national_id = form.cleaned_data['national_id']
        try:
            voter = Voter.objects.get(national_id=national_id)
            request.session['voter_id'] = voter.id
            request.session['voter_name'] = voter.name
            messages.success(request, f'ยินดีต้อนรับ {voter.name}')
            return redirect('home')
        except Voter.DoesNotExist:
            form.add_error('national_id', 'ไม่พบรหัสประชาชนในระบบ')

    return render(request, 'polls/login.html', {'form': form})


def voter_logout(request):
    request.session.flush()
    return redirect('login')


def home_page(request):
    if not request.session.get('voter_id'):
        return redirect('login')

    candidates = Candidate.objects.all()
    election_open = Election.is_voting_open()
    already_voted = request.session.get('has_voted', False)
    voter_name = request.session.get('voter_name', '')

    return render(request, 'polls/home.html', {
        'candidates': candidates,
        'election_open': election_open,
        'already_voted': already_voted,
        'voter_name': voter_name,
    })


def vote(request, candidate_id):
    if not request.session.get('voter_id'):
        return redirect('login')

    if not Election.is_voting_open():
        messages.error(request, 'ขณะนี้ยังไม่เปิดรับการลงคะแนน')
        return redirect('home')

    if request.session.get('has_voted'):
        messages.warning(request, 'คุณได้ลงคะแนนแล้ว ไม่สามารถโหวตซ้ำได้')
        return redirect('home')

    # เช็คจาก Voter model ด้วย (double check)
    voter = get_object_or_404(Voter, id=request.session['voter_id'])
    if voter.has_voted:
        messages.warning(request, 'คุณได้ลงคะแนนแล้ว ไม่สามารถโหวตซ้ำได้')
        return redirect('home')

    candidate = get_object_or_404(Candidate, id=candidate_id)
    Vote.objects.create(candidate=candidate)

    voter.has_voted = True
    voter.save()
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