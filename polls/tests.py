from django.test import TestCase
from django.urls import resolve
from polls.views import home_page
from polls.models import Candidate, Vote, Election, Voter


def create_voter_and_login(client):
    voter = Voter.objects.create(national_id='1234567890123', name='ผู้ทดสอบ')
    client.post('/login/', {'national_id': '1234567890123'})
    return voter


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_200(self):
        create_voter_and_login(self.client)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class CandidateModelTest(TestCase):
    def test_saving_and_retrieving_candidates(self):
        candidate = Candidate()
        candidate.name = 'Arsu Maehae'
        candidate.party = 'CP North Bangkok'
        candidate.save()
        saved_candidates = Candidate.objects.all()
        self.assertEqual(saved_candidates.count(), 1)
        self.assertEqual(saved_candidates[0].name, 'Arsu Maehae')


class DuplicateVoteTest(TestCase):
    def setUp(self):
        Election.objects.create(name='Election 2568', is_open=True)
        self.candidate = Candidate.objects.create(name='Somchai', party='Green Party')
        self.voter = create_voter_and_login(self.client)

    def test_cannot_vote_twice_in_same_session(self):
        self.client.post(f'/vote/{self.candidate.id}/')
        response2 = self.client.post(f'/vote/{self.candidate.id}/')
        self.assertRedirects(response2, '/')

    def test_vote_count_stays_one_after_duplicate(self):
        self.client.post(f'/vote/{self.candidate.id}/')
        self.client.post(f'/vote/{self.candidate.id}/')
        self.assertEqual(Vote.objects.filter(candidate=self.candidate).count(), 1)


class ElectionPeriodTest(TestCase):
    def setUp(self):
        self.candidate = Candidate.objects.create(name='Somchai', party='Green Party')
        create_voter_and_login(self.client)

    def test_cannot_vote_when_election_is_closed(self):
        Election.objects.create(name='Election 2568', is_open=False)
        response = self.client.post(f'/vote/{self.candidate.id}/')
        self.assertRedirects(response, '/')
        self.assertEqual(Vote.objects.count(), 0)

    def test_can_vote_when_election_is_open(self):
        Election.objects.create(name='Election 2568', is_open=True)
        self.client.post(f'/vote/{self.candidate.id}/')
        self.assertEqual(Vote.objects.count(), 1)


class FlashMessageTest(TestCase):
    def setUp(self):
        Election.objects.create(name='Election 2568', is_open=True)
        self.candidate = Candidate.objects.create(name='Somchai', party='Green Party')
        create_voter_and_login(self.client)

    def test_success_message_after_voting(self):
        response = self.client.post(f'/vote/{self.candidate.id}/', follow=True)
        messages_list = list(response.context['messages'])
        self.assertTrue(any('Somchai' in str(m) for m in messages_list))

    def test_error_message_when_election_closed(self):
        Election.objects.all().update(is_open=False)
        response = self.client.post(f'/vote/{self.candidate.id}/', follow=True)
        messages_list = list(response.context['messages'])
        self.assertTrue(any('ยังไม่เปิด' in str(m) for m in messages_list))

    def test_warning_message_on_duplicate_vote(self):
        self.client.post(f'/vote/{self.candidate.id}/')
        response = self.client.post(f'/vote/{self.candidate.id}/', follow=True)
        messages_list = list(response.context['messages'])
        self.assertTrue(any('โหวตซ้ำ' in str(m) for m in messages_list))


class ResultsPageTest(TestCase):
    def setUp(self):
        Election.objects.create(name='Election 2568', is_open=True)
        self.c1 = Candidate.objects.create(name='Somchai', party='Green')
        self.c2 = Candidate.objects.create(name='Malee', party='Blue')
        create_voter_and_login(self.client)

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


class VoterAuthTest(TestCase):
    def setUp(self):
        Election.objects.create(name='การเลือกตั้ง 2569', is_open=True)
        Candidate.objects.create(name='สมชาย', party='พรรคเขียว')

    def test_cannot_access_home_without_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/')

    def test_can_login_with_valid_national_id(self):
        Voter.objects.create(national_id='1234567890123', name='สมหมาย ใจดี')
        response = self.client.post('/login/', {'national_id': '1234567890123'})
        self.assertRedirects(response, '/')

    def test_cannot_login_with_invalid_national_id(self):
        response = self.client.post('/login/', {'national_id': '0000000000000'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ไม่พบรหัสประชาชน')

    def test_national_id_must_be_13_digits(self):
        response = self.client.post('/login/', {'national_id': '12345'})
        self.assertContains(response, 'รหัสประชาชนต้องมี 13 หลัก')



class PageTitleTest(TestCase):
    """เช็ค title ทุกหน้าว่าถูกต้อง"""

    def setUp(self):
        Election.objects.create(name='Election 2568', is_open=True)
        Candidate.objects.create(name='Somchai', party='Green')
        create_voter_and_login(self.client)

    def test_login_page_title(self):
        # logout ก่อนเพื่อเข้าหน้า login
        self.client.get('/logout/')
        response = self.client.get('/login/')
        self.assertContains(response, '<title>เข้าสู่ระบบ')

    def test_home_page_title(self):
        response = self.client.get('/')
        self.assertContains(response, '<title>ลงคะแนนเสียง')

    def test_results_page_title(self):
        response = self.client.get('/results/')
        self.assertContains(response, '<title>ผลการเลือกตั้ง')


class LogoutTest(TestCase):
    """เช็คว่า logout ล้าง session จริง"""

    def setUp(self):
        create_voter_and_login(self.client)

    def test_logout_clears_session(self):
        # ก่อน logout เข้าหน้าแรกได้
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # logout
        self.client.get('/logout/')

        # หลัง logout เข้าหน้าแรกไม่ได้
        response = self.client.get('/')
        self.assertRedirects(response, '/login/')

    def test_logout_redirects_to_login(self):
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/login/')


class LoginRedirectTest(TestCase):
    """เช็คว่าทุก URL ที่ต้อง login จะ redirect ไป /login/"""

    def test_home_redirects_when_not_logged_in(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/')

    def test_vote_redirects_when_not_logged_in(self):
        candidate = Candidate.objects.create(name='Somchai', party='Green')
        response = self.client.post(f'/vote/{candidate.id}/')
        self.assertRedirects(response, '/login/')

    def test_results_accessible_without_login(self):
        # results ดูได้โดยไม่ต้อง login
        response = self.client.get('/results/')
        self.assertEqual(response.status_code, 200)


class VoterModelTest(TestCase):
    """เช็ค Voter model methods"""

    def test_is_valid_id_with_13_digits(self):
        self.assertTrue(Voter.is_valid_id('1234567890123'))

    def test_is_valid_id_rejects_short(self):
        self.assertFalse(Voter.is_valid_id('12345'))

    def test_is_valid_id_rejects_letters(self):
        self.assertFalse(Voter.is_valid_id('123456789012a'))

    def test_voter_str(self):
        voter = Voter(national_id='1234567890123', name='สมหมาย')
        self.assertIn('สมหมาย', str(voter))
        self.assertIn('1234567890123', str(voter))


class AlreadyLoggedInTest(TestCase):
    """เช็คว่า login ซ้ำถูก redirect กลับหน้าแรก"""

    def test_logged_in_user_cannot_access_login_page(self):
        create_voter_and_login(self.client)
        response = self.client.get('/login/')
        self.assertRedirects(response, '/')