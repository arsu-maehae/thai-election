from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from polls.views import home_page
from polls.models import Candidate
from polls.models import Vote


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