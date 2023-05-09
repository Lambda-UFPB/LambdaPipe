from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_experimental_option('detach', True)

driver = webdriver.Chrome(options=options)
driver.get("https://pharmit.csb.pitt.edu/search.html")
driver.implicitly_wait(0.5)
driver.maximize_window()

# Uploading Session
upload_session = driver.find_element(By.XPATH, '//*[@id="pharmit"]/div[2]/div[5]/div/div/input')
upload_session.send_keys("/home/kdunorat/Documentos/LambdaPipe/files/pharmit.json")

# Modificar o value dps
# Searching
search = driver.find_element(By.XPATH, '//*[@id="pharmitsearchbutton"]')
search.click()
# Saving
time.sleep(5)
save = driver.find_element(By.XPATH, '//*[@id="pharmit"]/div[1]/div[4]/div[3]/div/button[2]')
save.click()
