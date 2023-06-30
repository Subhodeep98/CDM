#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service


# In[2]:


def set_chrome_options(download_directory):
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_directory,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True,
        'plugins.always_open_pdf_externally': True,  # always open pdf externally
        'download.open_pdf_in_system_reader': False,  # don't open pdf in system reader
        'profile.default_content_settings.popups': 0,  # disable popups
    })
    return chrome_options


# In[3]:


download_directory = (r"C:\Users\Subho_98\Desktop\CDM Pipeline")
options = set_chrome_options(download_directory)


# In[ ]:


driver = webdriver.Chrome('C:\Chrome', options=set_chrome_options(download_directory))
driver.get('https://unepccc.org/cdm-ji-pipeline/')


# In[ ]:


cdmpipeline = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div[2]/div/p[2]/strong/a')
cdmpipeline.click()

stakeholder_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="input_1_1"]'))
index1 = 10
stakeholder_dropdown.select_by_index(index1)

country_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="input_1_2"]'))
index2 = 78
country_dropdown.select_by_index(index2)

submit = driver.find_element(By.XPATH, '//*[@id="gform_submit_button_1"]')
submit.click()


# In[ ]:


download = driver.find_element(By.XPATH, '//*[@id="gform_confirmation_message_1"]/a')
download.click()

