from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from polls.views import home_page
from polls.models import Candidate
from polls.models import Vote
from polls.models import Candidate, Vote, Election


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)


class CandidateModelTest(TestCase):
    def test_saving_and_retrieving_candidates(self):
        first_candidate = Candidate()
        first_candidate.name = 'Arsu Maehae'
        first_candidate.party = 'CP North Bangkok'
        first_candidate.save()

        saved_candidates = Candidate.objects.all()
        self.assertEqual(saved_candidates.count(), 1)
        self.assertEqual(saved_candidates[0].name, 'Arsu Maehae')

class DuplicateVoteTest(TestCase):
    def setUp(self):
        Election.objects.create(name='Election 2568', is_open=True) 
        self.candidate = Candidate.objects.create(
            name='Somchai', party='Green Party'
        )

    def test_cannot_vote_twice_in_same_session(self):
        # vote ครั้งแรก — ต้อง success
        response1 = self.client.post(f'/vote/{self.candidate.id}/')
        self.assertEqual(response1.status_code, 302)

        # vote ครั้งที่สอง — ต้อง redirect กลับพร้อม error
        response2 = self.client.post(f'/vote/{self.candidate.id}/')
        self.assertRedirects(response2, '/')

    def test_vote_count_stays_one_after_duplicate(self):
        self.client.post(f'/vote/{self.candidate.id}/')
        self.client.post(f'/vote/{self.candidate.id}/')
        vote_count = Vote.objects.filter(candidate=self.candidate).count()
        self.assertEqual(vote_count, 1)

class ElectionPeriodTest(TestCase):
    def test_cannot_vote_when_election_is_closed(self):
        Election.objects.create(name='Election 2568', is_open=False)
        candidate = Candidate.objects.create(name='Somchai', party='Green')
        response = self.client.post(f'/vote/{candidate.id}/')
        self.assertRedirects(response, '/')
        self.assertEqual(Vote.objects.count(), 0)

    def test_can_vote_when_election_is_open(self):
        Election.objects.create(name='Election 2568', is_open=True)
        candidate = Candidate.objects.create(name='Somchai', party='Green')
        response = self.client.post(f'/vote/{candidate.id}/')
        self.assertEqual(Vote.objects.count(), 1)



class FlashMessageTest(TestCase):
    def setUp(self):
        Election.objects.create(name='Election 2568', is_open=True)
        self.candidate = Candidate.objects.create(
            name='Somchai', party='Green Party'
        )

    def test_success_message_after_voting(self):
        response = self.client.post(
            f'/vote/{self.candidate.id}/', follow=True
        )
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertIn('Somchai', str(messages_list[0]))

    def test_error_message_when_election_closed(self):
        Election.objects.all().update(is_open=False)
        response = self.client.post(
            f'/vote/{self.candidate.id}/', follow=True
        )
        messages_list = list(response.context['messages'])
        self.assertTrue(any('ยังไม่เปิด' in str(m) for m in messages_list))

    def test_warning_message_on_duplicate_vote(self):
        self.client.post(f'/vote/{self.candidate.id}/')
        response = self.client.post(
            f'/vote/{self.candidate.id}/', follow=True
        )
        messages_list = list(response.context['messages'])
        self.assertTrue(any('โหวตซ้ำ' in str(m) for m in messages_list))


class ResultsPageTest(TestCase):
    def setUp(self):
        Election.objects.create(name='Election 2568', is_open=True)
        self.c1 = Candidate.objects.create(name='Somchai', party='Green')
        self.c2 = Candidate.objects.create(name='Malee', party='Blue')

    def test_results_shows_correct_vote_count(self):
        Vote.objects.create(candidate=self.c1)
        Vote.objects.create(candidate=self.c1)
        Vote.objects.create(candidate=self.c2)
        response = self.client.get('/results/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Somchai')
        self.assertContains(response, 'Malee')

    def test_results_shows_total_votes(self):
        Vote.objects.create(candidate=self.c1)
        Vote.objects.create(candidate=self.c2)
        response = self.client.get('/results/')
        self.assertContains(response, '2')

    def test_winner_appears_first(self):
        Vote.objects.create(candidate=self.c1)
        Vote.objects.create(candidate=self.c1)
        Vote.objects.create(candidate=self.c2)
        response = self.client.get('/results/')
        candidates = list(response.context['candidates'])
        self.assertEqual(candidates[0].name, 'Somchai')