from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_experimental_option('detach', True)

driver = webdriver.Chrome(options=options)
driver.get("https://pharmit.csb.pitt.edu/search.html")
driver.implicitly_wait(0.5)

# Upload Ligand
ligand = driver.find_element(By.XPATH, '//*[@id="pharmit"]/div[2]/div[3]/div[3]/div[2]/input')
ligand.send_keys("/home/kdunorat/Documentos/LambdaPipe/files/7KR1-pocket3-remdesivir-cid76325302.pdbqt")

# Upload Receptor
time.sleep(3)
receptor = driver.find_element(By.XPATH, '//*[@id="pharmit"]/div[2]/div[3]/div[3]/div[1]/input')
receptor.send_keys("/home/kdunorat/Documentos/LambdaPipe/files/7KR1.pdbqt")

# Modificar o value dps
# Searching
search = driver.find_element(By.XPATH, '//*[@id="pharmitsearchbutton"]')
search.click()

# Saving
time.sleep(5)
driver.find_element(By.XPATH, '//*[@id="pharmit"]/div[1]/div[4]/div[3]/div/button[2]').click()

