from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException, NoAlertPresentException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
import re
import time
import utils


class PharmitControl:

    def __init__(self, receptor_path: str, ligand_path: str, output_folder_path: str):
        self.output_folder_path = output_folder_path
        self.receptor_path = receptor_path
        self.ligand_path = ligand_path
        self.total_hits = 0
        options = Options()
        options.add_experimental_option('detach', True)
        self.db_list = [['chembl', 'chemdiv', 'enamine', 'molport', 'mcule'],
                        ['ultimate', 'nsc', 'pubchem', 'wuxi-lab', 'zinc']]
        chrome_options = Options()
        possible_chrome_binary_locations = utils.get_chrome_binary_path()
        for chrome_location in possible_chrome_binary_locations:
            try:
                chrome_options.binary_location = chrome_location
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except WebDriverException:
                continue
        self.minimize_count = 0

    def _open_tab(self, count,  db):
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

    def upload_complex(self):
        # Get page
        self.driver.get("https://pharmit.csb.pitt.edu/search.html")
        self.driver.implicitly_wait(3)
        # MODIFICAR ISSO AQUI
        try:
            # Upload receptor
            receptor = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[3]/div[1]/input')
            receptor.send_keys(self.receptor_path)
            time.sleep(3)
            # Upload ligand
            ligand = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[3]/div[2]/input')
            ligand.send_keys(self.ligand_path)
        except WebDriverException:
            print("Error uploading files. Please check the paths and try again.")

    def get_json(self):
        # Download first json
        time.sleep(3)
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[5]/div/button').click()

    def _change_db(self, run, count, db):
        time.sleep(3)
        if run == 1:
            self.driver.switch_to.window(f"{self.db_list[0][count]}")
        else:
            self.driver.switch_to.window(f"{db}")
        database = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[1]/button[1]')
        self.driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", database, db)

    def _upload_json(self, db, modified_json_path):
        # Upload session
        self.driver.switch_to.window(f"{db}")
        load_session = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[5]/div/div/input')
        load_session.send_keys(modified_json_path)
        time.sleep(3)

    def _search(self):
        # Click on the search button
        search = self.driver.find_element(By.XPATH, '//*[@id="pharmitsearchbutton"]')
        while True:
            try:
                search.click()
                break
            except WebDriverException:
                pass

    def _search_loop(self, run: int, db_half: list):
        search_count = 0
        searched_dbs = []
        while True:
            print(f"Search count: {search_count}")
            if search_count == 5:
                break
            for n, db in enumerate(db_half):
                if db in searched_dbs:
                    continue
                self.driver.switch_to.window(f"{self.db_list[0][n]}")
                minimize_button = self.driver.find_element(By.XPATH,
                                                           '//*[@id="pharmit"]/div[1]/div[4]/div[3]/div/button[1]')
                if self._check_no_results(db):
                    self.db_list[run].remove(db)
                # if search_count == 4:
                    # self._waiting_last_db(db, minimize_button)
                if minimize_button.is_enabled():
                    self._minimize(minimize_button, db)
                    search_count += 1
                    searched_dbs.append(db)

    def _waiting_last_db(self, minimize_button):
        while True:
            try:
                WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable(minimize_button))
                break
            except TimeoutException:
                pass

    def _check_no_results(self, db):
        try:
            no_results = self.driver.find_element(By.CLASS_NAME, "dataTables_empty")
            if no_results.text == 'No results found':
                print(f"{no_results.text} in {db}")
                return True
        except NoSuchElementException:
            return False

    def _minimize(self, minimize_button, db):
        print(f"Minimizing {db}")
        number_of_hits = self._get_screening_stats()
        utils.write_stats(f"\n{db}: {number_of_hits}", self.output_folder_path)
        while True:
            try:
                minimize_button.click()
                break
            except WebDriverException:
                pass

        try:
            self.driver.switch_to.alert.dismiss()
        except NoAlertPresentException:
            pass

    def _get_screening_stats(self):
        element = self.driver.find_element(By.ID, "DataTables_Table_0_info")
        number_screening_text = element.text
        match = re.search(r'(\d[\d,]*)\s*hits', number_screening_text)
        if match:
            number_of_hits = match.group(1)
            number_of_hits_int = number_of_hits.replace(',', '')
            number_of_hits_int = int(number_of_hits_int)
        else:
            number_of_hits = "0"
            number_of_hits_int = 0

        self.total_hits += number_of_hits_int

        return number_of_hits

    def _download_loop(self, db_half: list):
        proceed = False
        downloaded_dbs = []
        while True:
            if proceed:
                break
            for n, db in enumerate(db_half):
                if len(downloaded_dbs) == len(db_half):
                    proceed = True
                    break
                if db in downloaded_dbs:
                    continue
                self.driver.switch_to.window(f"{self.db_list[0][n]}")
                time.sleep(5)
                save_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[3]/div[3]/div[2]/button')
                if save_button.is_enabled():
                    self.download(save_button, db)
                    downloaded_dbs.append(db)

    def download(self, save_button, db):
        print(f"Downloading {db}")
        time.sleep(1)
        while True:
            try:
                save_button.click()
                break
            except WebDriverException:
                pass
        self.minimize_count += 1

    @staticmethod
    def check_finished_download(counter, old_download_list):
        while True:
            new_download_list = utils.get_download_list('minimized_results*')
            all_downloads = len(new_download_list) - len(old_download_list)
            if all_downloads == counter:
                break
            else:
                time.sleep(2)
        return

    def run_pharmit_search(self, modified_json_path):
        old_download_list = utils.get_download_list('minimized_results*')
        for run, db_half in enumerate(self.db_list):
            for count, db in enumerate(db_half):
                if run == 0:
                    self._open_tab(count, db)
                    self._upload_json(db, modified_json_path)
                self._change_db(run, count, db)
                self._search()
            self._search_loop(run, db_half)
            self._download_loop(db_half)

        if PharmitControl.check_finished_download(self.minimize_count, old_download_list):
            self.driver.quit()
            utils.write_stats(f"\nTotal hits: {self.total_hits}", self.output_folder_path)

            return self.minimize_count
