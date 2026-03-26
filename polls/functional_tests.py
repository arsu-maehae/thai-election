from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from polls.models import Candidate, Election
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class VotingFlowTest(LiveServerTestCase):
    """
    Functional test — จำลองผู้ใช้จริงเปิด browser แล้วโหวต
    ต้องติดตั้ง Chrome + ChromeDriver ก่อนรัน
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument('--headless')  # รันแบบไม่เปิด window
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

    def test_user_can_see_candidates_and_vote(self):
        # เปิดหน้าแรก
        self.browser.get(self.live_server_url)

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
        self.browser.get(self.live_server_url)
        vote_btn = self.browser.find_element(By.CSS_SELECTOR, 'button.vote-btn')
        vote_btn.click()

        # รอให้ redirect ไป /results/ เสร็จก่อน
        WebDriverWait(self.browser, 5).until(
            EC.url_contains('/results/')
        )

        # แล้วค่อยกลับหน้าแรก — session cookie ยังอยู่ใน browser
        self.browser.get(self.live_server_url)

        # รอให้หน้าโหลดเสร็จ
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        self.assertIn('ได้ลงคะแนนแล้ว', self.browser.page_source)