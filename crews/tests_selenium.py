import re
import time

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

from crews.models import Worker, Crew
from flights.models import Flight, Airplane


def advance_date(date, hours=0, minutes=0, seconds=0):
    return date + timezone.timedelta(hours=hours, minutes=minutes, seconds=seconds)


class SeleniumTests(StaticLiveServerTestCase):
    def create_flight(self, start, landing, crew):
        return Flight.objects.create(start=start,
                                     landing=landing,
                                     airplane=self.airplane,
                                     start_airport="start",
                                     landing_airport="finish",
                                     crew=crew)

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.katalon.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

        worker1 = Worker.objects.create(name="Jan", surname="Kowalski 1")
        worker2 = Worker.objects.create(name="Jan", surname="Kowalski 2")
        crew1 = Crew.objects.create(captain=worker1)
        crew2 = Crew.objects.create(captain=worker2)
        crew1.workers.add(worker1)
        crew2.workers.add(worker2)
        self.worker3 = Worker.objects.create(name="Jan", surname="Kowalski 3")

        self.airplane = Airplane.objects.create(registration_number="samolocik", capacity=40)
        self.flight1 = self.create_flight(timezone.now(), advance_date(timezone.now(), hours=2), crew=crew1)
        self.flight2 = self.create_flight(advance_date(timezone.now(), hours=1), advance_date(timezone.now(), hours=3), crew=crew2)

        u = User(username='admin')
        u.set_password('tajnehaslo')
        u.is_superuser = True
        u.is_staff = True
        u.save()

    def test_ticket(self):
        driver = self.driver
        driver.get(self.live_server_url)
        driver.find_element_by_xpath("//td[2]").click()
        driver.find_element_by_link_text("Zaloguj").click()
        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys("admin")
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys("tajnehaslo")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_id("id_name").click()
        driver.find_element_by_id("id_name").clear()
        driver.find_element_by_id("id_name").send_keys("Karol")
        driver.find_element_by_id("id_surname").click()
        driver.find_element_by_id("id_surname").clear()
        driver.find_element_by_id("id_surname").send_keys("Smolak")
        driver.find_element_by_id("id_count").click()
        driver.find_element_by_id("id_count").clear()
        driver.find_element_by_id("id_count").send_keys("1")
        driver.find_element_by_xpath("//input[@value='dodaj']").click()
        self.assertEqual("1", driver.find_element_by_xpath("//td[3]").text)

    def test_crew(self):
        driver = self.driver
        driver.get(self.live_server_url)
        driver.find_element_by_link_text(u"Załogi").click()
        driver.find_element_by_xpath("//input[@type='text']").click()
        driver.find_element_by_xpath("//input[@type='text']").clear()
        driver.find_element_by_xpath("//input[@type='text']").send_keys("admin")
        driver.find_element_by_xpath("//input[@type='password']").clear()
        driver.find_element_by_xpath("//input[@type='password']").send_keys("tajnehaslo")
        driver.find_element_by_id("loginbtn").click()
        driver.find_element_by_xpath("(//input[@type='text'])[2]").click()
        driver.find_element_by_xpath("(//input[@type='text'])[2]").clear()
        driver.find_element_by_xpath("(//input[@type='text'])[2]").send_keys(self.flight1.pk)
        driver.find_element_by_id("search").click()
        Select(driver.find_element_by_xpath("//select")).select_by_visible_text(str(self.worker3))
        driver.find_element_by_xpath("//select").click()
        driver.find_element_by_id("addworker").click()
        driver.find_element_by_xpath("(//input[@type='text'])[2]").click()
        driver.find_element_by_xpath("(//input[@type='text'])[2]").clear()
        driver.find_element_by_xpath("(//input[@type='text'])[2]").send_keys(self.flight2.pk)
        driver.find_element_by_id("search").click()
        driver.find_element_by_xpath("//select").click()
        driver.find_element_by_id("addworker").click()
        # Warning: waitForTextPresent may require manual changes
        for i in range(60):
            try:
                if re.search(r"^[\s\S]*$", driver.find_element_by_css_selector("BODY").text): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual(u"Członek załogi nie może być jednocześnie na dwóch lotach: 2 i 1", driver.find_element_by_id("errors").text)

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
