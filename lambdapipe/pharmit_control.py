from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException, NoAlertPresentException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils import *
from exceptions import InvalidInputError


class PharmitControl:

    def __init__(self, receptor_path: str, ligand_path: str, output_folder_path: str):
        self.output_folder_path = output_folder_path
        self.receptor_path = receptor_path
        self.ligand_path = ligand_path
        self.total_hits = 0
        options = Options()
        options.add_argument("--window-size=800,600")
        options.add_argument("--window-position=1000,0")
        self.db_list = [['chembl', 'chemdiv', 'enamine', 'molport', 'mcule'],
                        ['ultimate', 'nsc', 'pubchem', 'wuxi-lab', 'zinc']]

        chrome_options = options
        possible_chrome_binary_locations = get_chrome_binary_path()
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
            load_receptor = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[3]/div[1]/input')
            load_receptor.send_keys(self.receptor_path)
            time.sleep(3)
            # Upload ligand
            load_ligand = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[3]/div[2]/input')
            load_ligand.send_keys(self.ligand_path)
        except WebDriverException:
            raise InvalidInputError("Error uploading files. Please check the path and file name and try again.")

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
            print(search_count)
            if search_count == len(db_half):
                break
            for n, db in enumerate(db_half):
                if db in searched_dbs:
                    print("JÁ FEZ")
                    continue
                time.sleep(3)
                self.driver.switch_to.window(f"{self.db_list[0][n]}")
                minimize_button = self.driver.find_element(By.XPATH,
                                                           '//*[@id="pharmit"]/div[1]/div[4]/div[3]/div/button[1]')
                if self._check_no_results(db):
                    self.db_list[run].remove(db)
                if minimize_button.is_enabled():
                    self._minimize(minimize_button, db)
                    search_count += 1
                    searched_dbs.append(db)

    def _check_no_results(self, db):
        try:
            no_results = self.driver.find_element(By.CLASS_NAME, "dataTables_empty")
            if no_results.text == 'No results found':
                print("NÃO FEZ")
                print(f"{no_results.text} in {db}")
                return True
        except NoSuchElementException:
            return False

    def _minimize(self, minimize_button, db):
        number_of_hits = self._get_screening_stats()
        write_stats(f"\n{db}: {number_of_hits}", self.output_folder_path)
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
            print("COMEÇOU O DOWNLOAD LOOP 1")
            if proceed:
                break
            for n, db in enumerate(db_half):
                print("COMEÇOU O DOWNLOAD LOOP 2")
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
            new_download_list = get_download_list('minimized_results*')
            all_downloads = len(new_download_list) - len(old_download_list)
            if all_downloads >= counter:
                break
            else:
                time.sleep(2)
        return True

    def _run_fast(self, modified_json_path):
        for index, db in enumerate(self.db_list[0]):
            self._open_tab(index, db)
            self._upload_json(db, modified_json_path)
            self._change_db(0, index, db)
            self._search()
        self._search_loop(0, self.db_list[0])
        self._download_loop(self.db_list[0])

    def _run_slow(self, modified_json_path):
        for run, db_half in enumerate(self.db_list):
            for count, db in enumerate(db_half):
                if run == 0:
                    self._open_tab(count, db)
                    self._upload_json(db, modified_json_path)
                self._change_db(run, count, db)
                self._search()
            self._search_loop(run, db_half)
            self._download_loop(db_half)

    def run_pharmit_search(self, modified_json_path, fast=False):
        old_download_list = get_download_list('minimized_results*')
        if fast:
            self.db_list[1].remove('pubchem')
            self.db_list = [self.db_list[0] + self.db_list[1]]
            self._run_fast(modified_json_path)
        else:
            self._run_slow(modified_json_path)

        if PharmitControl.check_finished_download(self.minimize_count, old_download_list):
            self.driver.quit()
            write_stats(f"\nTotal hits: {self.total_hits}", self.output_folder_path)

            return self.minimize_count


if __name__ == '__main__':
    modified_json_path = '/home/kdunorat/lambdapipe_results/testeateofimfast/new_session3.json'
    output_path = '/home/kdunorat/lambdapipe_results/testeateofimfast'
    receptor_path = '/home/kdunorat/Projetos/LambdaPipe/files/7KR1.pdbqt'
    ligand_path = '/home/kdunorat/Projetos/LambdaPipe/files/7KR1-pocket3-remdesivir-cid76325302.pdbqt'
    phc = PharmitControl(receptor_path, ligand_path, output_path)
    phc.upload_complex()
    minimize_c = phc.run_pharmit_search(modified_json_path, fast=False)
