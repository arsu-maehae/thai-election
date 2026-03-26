from django.test import LiveServerTestCase
from polls.models import Candidate, Election, Voter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class VotingFlowTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        cls.browser = webdriver.Chrome(options=options)
        cls.browser.implicitly_wait(3)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        Election.objects.create(name='Election 2568', is_open=True)
        Candidate.objects.create(name='Somchai Jaidee', party='Green Party')
        Candidate.objects.create(name='Malee Rakdee', party='Blue Party')
        # เพิ่ม Voter สำหรับ login
        Voter.objects.create(national_id='1234567890123', name='ผู้ทดสอบ')

    def _login(self):
        """Helper — เปิดหน้า login แล้วกรอกรหัสประชาชน"""
        self.browser.get(f'{self.live_server_url}/login/')
        id_input = self.browser.find_element(By.NAME, 'national_id')
        id_input.clear()
        id_input.send_keys('1234567890123')
        id_input.submit()
        # รอให้ redirect ไปหน้าแรก
        WebDriverWait(self.browser, 5).until(
            EC.url_to_be(f'{self.live_server_url}/')
        )

    def test_user_can_see_candidates_and_vote(self):
        self._login()

        # เห็นรายชื่อผู้สมัคร
        self.assertIn('Somchai', self.browser.page_source)
        self.assertIn('Malee', self.browser.page_source)

        # กดโหวต
        vote_btn = self.browser.find_element(By.CSS_SELECTOR, 'button.vote-btn')
        vote_btn.click()

        # ถูก redirect ไปหน้า results
        WebDriverWait(self.browser, 5).until(
            EC.url_contains('/results/')
        )
        self.assertIn('ผลการเลือกตั้ง', self.browser.page_source)

    def test_user_cannot_vote_twice(self):
        self._login()

        # โหวตครั้งแรก
        vote_btn = self.browser.find_element(By.CSS_SELECTOR, 'button.vote-btn')
        vote_btn.click()

        # รอ redirect ไป /results/
        WebDriverWait(self.browser, 5).until(
            EC.url_contains('/results/')
        )

        # กลับหน้าแรก
        self.browser.get(f'{self.live_server_url}/')
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # ควรเห็น warning แทน form โหวต
        self.assertIn('ได้ลงคะแนนแล้ว', self.browser.page_source)