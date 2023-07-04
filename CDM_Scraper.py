#!/usr/bin/env python
# coding: utf-8

# In[12]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException


# In[2]:


import pandas as pd
import os
import time
import hashlib
import glob


# In[3]:


#setting the download directory path
download_directory = (r"C:\Users\Subho_98\Desktop\CDM Scraper")


# In[4]:


#creating a function to easy access of chrome_options.
def set_chrome_options(download_directory):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
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


# In[5]:


#function created to find any duplicate find. If found it will be deleted.
def find_duplicate_files(folder_path, delete_duplicates=False):
    if not os.path.exists(folder_path):
        raise ValueError("Invalid folder path: " + folder_path)

    files = {}
    duplicates = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'rb') as file:
                    file_hash = hashlib.md5(file.read()).hexdigest()
                    if file_hash in files:
                        duplicates.append((filename, files[file_hash]))
                        if delete_duplicates:
                            os.remove(file_path)
                    else:
                        files[file_hash] = filename
            except IOError as e:
                print("Error accessing file:", file_path, "-", str(e))
            except Exception as e:
                print("Error processing file:", file_path, "-", str(e))

    return duplicates


# In[6]:


#creating a data frame with a column of all the file names which have been downloaded.
def create_old_df(download_directory):
    Old_df = pd.DataFrame()
    for root, dirs, files in os.walk(download_directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            new_data1 = {'Old_Name': file_name}
            Old_df = Old_df.append(new_data1, ignore_index=True)
    return Old_df


# In[7]:


#adding prefix to the files downloaded for an easier recognition.
def add_prefix_to_files_in_folder(folder_path, prefix):
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            new_filename = prefix + filename
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            os.rename(old_file_path, new_file_path)
            
def add_prefix_to_files_in_folders():
    for x in range(len(df)):
        folder_path = os.path.join(download_directory, str(df.iloc[x, 3]))
        prefix = 'CDM_' + str(df.iloc[x, 3]) + '_'
        add_prefix_to_files_in_folder(folder_path, prefix)


# In[8]:


#creating a data frame with a column of all thwe renamed names of files which were downloaded after adding the prefix in it.
def create_new_df(download_directory):
    New_df = pd.DataFrame()
    for root, dirs, files in os.walk(download_directory):
        for file in files:
            file_path = os.path.join(root, file)
            renamed_name = os.path.basename(file_path)
            new_data2 = {'New_Name': renamed_name}
            New_df = New_df.append(new_data2, ignore_index=True)
    return New_df


# In[9]:


#creating a meta data after merging all the small data frames into one.
def process_data(download_directory, Old_df, New_df, result):
    result1 = pd.merge(Old_df, result, left_index=True, right_index=True)
    Final = pd.merge(New_df, result1, left_index=True, right_index=True)

    Final['Pro_Id'] = Final['New_Name'].str.extract(r'CDM_(\d+)_')

    last_column = Final.columns[-1]
    Final = Final[[last_column] + Final.columns[:-1].tolist()]

    excel_path = os.path.join(download_directory, 'CDM_Meta.xlsx')
    Final.to_excel(excel_path, index=False)


# In[10]:


files = r"C:\Users\Subho_98\Desktop\CDM Project ID.xlsx"
df = pd.read_excel(files, header=0)
df


# In[19]:


def main():
    project_id = df["Ref_id"]
    result = pd.DataFrame()
    for ids in project_id:
        folder_path = os.path.join(download_directory,str(ids))
        os.makedirs(folder_path, exist_ok=True)

        driver = webdriver.Chrome('C:\Chrome', options=set_chrome_options(folder_path))
        driver.get('https://cdm.unfccc.int/Projects/projsearch.html')
        input_field = driver.find_element(By.XPATH, '//*[@id="Ref"]') 
        input_field.send_keys(ids)
        input_field.send_keys(Keys.ENTER)

        item = driver.find_element(By.XPATH, '//*[@id="projectsTable"]/table/tbody/tr[4]/td[2]/a')
        item.click()
        element_present = EC.presence_of_element_located((By.XPATH, "//a[@href]"))

        WebDriverWait(driver, 5).until(element_present)

        elems = driver.find_elements(by=By.XPATH, value="//a[@href]")

        for elem in elems:
            try:
                link = elem.get_attribute("href")
                if 'https://cdm.unfccc.int/UserManagement/FileStorage/' in link:
                    driver.get(link)
                    result['Registry'] = "CDM"
                    new_data={'Doc_Type' : elem.text}
                    result = result.append(new_data, ignore_index=True)
                    time.sleep(2)
            except StaleElementReferenceException:
                pass
                    time.sleep(2)

    duplicate_files = find_duplicate_files(folder_path)
    if duplicate_files:
        print("Duplicate files found:")

    old_df = create_old_df(download_directory)

    add_prefix_to_files_in_folders()

    new_df = create_new_df(download_directory)

    process_data(download_directory, old_df, new_df, result)
    
    
if __name__ == "__main__":
    main()  

