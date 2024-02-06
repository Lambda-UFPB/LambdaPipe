from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.chrome.service import Service
from json_handler import JsonHandler
import time
import os


class PharmitControl:

    def __init__(self):
        options = Options()
        options.add_experimental_option('detach', True)
        self.db_tuple = ('molport', 'mcule', 'ultimate', 'nsc', 'pubchem', 'wuxi-lab',
                         'zinc')
        self.proceed = False
        chrome_driver_path = '/home/kdunorat/projetos/LambdaPipe/chromedriver/chromedriver'
        service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.minimize_count = 0

    def _open_tab(self, count,  db):
        if count <= 4:
            main_tab = self.driver.current_window_handle

            self.driver.execute_script(f"window.open('about:blank','{db}');")
            self.driver.switch_to.window(f"{db}")
            self.driver.get("https://pharmit.csb.pitt.edu/search.html")
            time.sleep(3)
            if count == 0:
                self._close_tab(main_tab)
        else:
            pass

    def _close_tab(self, tab):
        self.driver.switch_to.window(tab)
        self.driver.close()

    def _upload_complex(self):
        # Get page
        self.driver.get("https://pharmit.csb.pitt.edu/search.html")
        self.driver.implicitly_wait(3)
        # Upload ligand
        ligand = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[3]/div[2]/input')
        ligand.send_keys(f"{os.getcwd()}/files/7KR1-pocket3-remdesivir-cid76325302.pdbqt")
        # Upload receptor
        time.sleep(3)
        receptor = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[3]/div[1]/input')
        receptor.send_keys(f"{os.getcwd()}/files/7KR1.pdbqt")

    def _get_json(self):
        # Download first json
        time.sleep(3)
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[5]/div/button').click()

    def _change_db(self, count, db):
        time.sleep(3)
        if count >= 5:
            self.driver.switch_to.window(f"{self.db_tuple[count - 5]}")
        database = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[1]/button[1]')
        self.driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", database, db)

    @staticmethod
    def _create_json():
        time.sleep(3)
        jsh = JsonHandler()
        modified_json_path = jsh.create_json()
        return modified_json_path

    def _upload_json(self, count, db, modified_json_path):
        # Create second json
        if count <= 4:
            # Upload session
            self.driver.switch_to.window(f"{db}")
            load_session = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[5]/div/div/input')
            load_session.send_keys(modified_json_path)
            time.sleep(3)
        else:
            pass

    def _search(self):
        # Click on the search button
        search = self.driver.find_element(By.XPATH, '//*[@id="pharmitsearchbutton"]')
        time.sleep(2)
        search.click()

    def _search_loop(self, count):
        for n in range(count - count, 5):
            self.driver.switch_to.window(f"{self.db_tuple[n]}")
            while True:
                minimize_button = self.driver.find_element(By.XPATH,
                                                           '//*[@id="pharmit"]/div[1]/div[4]/div[3]/div/button[1]')
                try:
                    no_results = self.driver.find_element(By.CLASS_NAME, "dataTables_empty")
                    if no_results.text == 'No results found':
                        print(no_results.text)
                        break
                except NoSuchElementException:
                    pass

                if minimize_button.is_enabled():
                    self.proceed = True
                    break
                else:
                    time.sleep(1)
            if self.proceed:
                self.proceed = False
                self._download(minimize_button)

    def _download(self, minimize_button):
        # Minimize
        time.sleep(3)
        minimize_button.click()
        try:
            self.driver.switch_to.alert.dismiss()
        except NoAlertPresentException:
            pass
        save_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[3]/div[3]/div[2]/button')
        # Saving
        while True:
            if save_button.is_enabled():
                time.sleep(1)
                save_button.click()
                self.minimize_count += 1
                break
            time.sleep(1)

    def run(self):
        #self._upload_complex()
        #self._get_json()
        modified_json_path = PharmitControl._create_json()
        for count, db in enumerate(self.db_tuple):
            self._open_tab(count, db)
            self._upload_json(count, db, '/home/kdunorat/Área de Trabalho/pharmit.json')
            self._change_db(count, db)
            self._search()
            if count == 4 or count == 9:
                self._search_loop(count)
        time.sleep(5)
        self.driver.quit()
        return self.minimize_count

if __name__ == '__main__':
    pc = PharmitControl()
    minimize_count = pc.run()