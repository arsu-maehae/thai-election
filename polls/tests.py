from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from polls.views import home_page
from polls.models import Candidate


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