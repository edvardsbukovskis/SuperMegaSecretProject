import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import settings

# Create a new instance of the Chrome driver
chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--start-maximized")
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
username = settings.username
password = settings.password
username_field = "/html/body/div[8]/div[3]/aside/div[1]/div[2]/form/div[1]/input"
password_field = "/html/body/div[8]/div[3]/aside/div[1]/div[2]/form/div[2]/input"

# Open the Eklase website
driver.get("https://www.eklase.lv")

# Find the username and password input fields
username_input = driver.find_element(By.XPATH, username_field)
password_input = driver.find_element(By.XPATH, password_field)

# Enter the username and password
username_input.send_keys(username)
password_input.send_keys(password)

# Click on login button
driver.find_element(By.XPATH, "/html/body/div[8]/div[3]/aside/div[1]/div[2]/form/button").click()
time.sleep(1)

# Click on 'Žurnāls' button and on all žurnāli
driver.find_element(By.XPATH, "/html/body/div[6]/input[2]").click()
time.sleep(1)
driver.find_element(By.XPATH, "/html/body/div/div/div/div[3]/div[1]/div[1]/div/div/div[1]/div/div").click()

#Click on klases container
driver.find_element(By.XPATH, "/html/body/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div/div/div[2]").click()
time.sleep(1)


#Iterate through each klase starting from 5.a 
for i in range(29, 59):
    klase = driver.find_element(By.XPATH, f"/html/body/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div/div/div[3]/ul/li[{i}]/span").text
    driver.find_element(By.XPATH, f"/html/body/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div/div/div[3]/ul/li[{i}]/span").click()
    time.sleep(0.2)
    #Find the max number of priekšmeti for the given klase, get the html code of it and pass it to bs4
    prieksmeti_box_html = driver.find_element(By.XPATH, "/html/body/div/div/div/div[3]/div[1]/div[1]/div/div/div[3]/div/div/div[3]/ul")
    prieksmeti_box_html = prieksmeti_box_html.get_attribute('outerHTML')
    soup = BeautifulSoup(prieksmeti_box_html, 'html.parser')
    li_elements = soup.find_all('li', class_='multiselect__element')
    id_numbers =[]
    for li in li_elements:
        li_id = li.get('id')
        if li_id is not None:
            match = re.match(r'null-(\d+)', li_id)
            if match:
                id_numbers.append(int(match.group(1)))
        else:
            print("No id found")
    max_id_numbers = max(id_numbers) if id_numbers else None
    time.sleep(1)

    #Iterate through each priekšmets
    spinner_xpath = "//div[contains(@class, 'multiselect__spinner') and not(contains(@style, 'display: none;'))]"
    for i in range(1, max_id_numbers + 1):
        # Wait for the spinner to disappear before attempting to click the element
        WebDriverWait(driver, 40).until_not(
            EC.presence_of_element_located((By.XPATH, spinner_xpath))
        )

        # Click on priekšmeti container (This is needed because we are skipping some priekšmeti, so that it doesnt get stuck on the last priekšmets of the klase)
        prieksmeti_container_xpath = "/html/body/div/div/div/div[3]/div[1]/div[1]/div/div/div[3]/div/div/div[2]"
        WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, prieksmeti_container_xpath))).click()

        element_xpath = f"/html/body/div/div/div/div[3]/div[1]/div[1]/div/div/div[3]/div/div/div[3]/ul/li[{i}]"
        element = WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, element_xpath)))

        #Skip interešu izglītība or fakultatīvs
        if "(I)" in element.text or "(F)" in element.text or "Klases stunda" in element.text:
            continue

        print(klase, element.text)

        # Scroll the priekšmets into view
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

        # Additional wait to let any possible transition finish
        WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, element_xpath)))

        # Now try clicking the priekšmets
        element.click()

        # Wait for the spinner to disappear again before continuing
        WebDriverWait(driver, 40).until_not(
            EC.presence_of_element_located((By.XPATH, spinner_xpath))
        )
        
        #Check each(current) priekšmets for necessary information
        th_elements_locator = "//th[.//div[@class='Tests']]"

        #Count the elements once at the beginning so we know indexes
        element_count = driver.find_elements(By.XPATH, th_elements_locator)
        print("PD skaits kopā: ", len(element_count))

        for index in range(0, len(element_count)):
            # Re-find all elements and select the one at the current index
            th_elements_with_tests = driver.find_elements(By.XPATH, th_elements_locator)
            th_element = th_elements_with_tests[index]

            # Scroll to and click on the PD
            driver.execute_script("arguments[0].scrollIntoView(true);", th_element)
            WebDriverWait(driver, 40).until(EC.element_to_be_clickable(th_element)).click()
                
            # Click on "Uz uzdevumu tabulu"
            WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'LinkToTest') and contains(text(), 'Uz uzdevumu tabulu')]"))).click()
                
            # Do some logic to check if the PD has been created correctly
            
                
            # Tell the driver to go back from the PD uzdevumi page to the PD window
            driver.back()

            # Wait for the page to load and re-find the elements
            WebDriverWait(driver, 40).until(EC.presence_of_all_elements_located((By.XPATH, th_elements_locator)))

            # Click X to close the PD window and be back on priekšmeta stundu table
            WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div[3]/div[2]/div/div/div[1]/div[2]"))).click()
        

        # Click on priekšmeti container after finished working with current priekšmets
        prieksmeti_container_xpath = "/html/body/div/div/div/div[3]/div[1]/div[1]/div/div/div[3]/div/div/div[2]"
        WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, prieksmeti_container_xpath))).click()



    #Click on klases container
    driver.find_element(By.XPATH, "/html/body/div/div/div/div[3]/div[1]/div[1]/div/div/div[2]/div/div/div[2]").click()

time.sleep(5)
