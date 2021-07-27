import subprocess
import sys
import os
import time
from datetime import datetime
from Config import HOME_FOLDER, DRIVER_NAME, DRIVER_TYPE, DRIVER_PATH, jobToCheck, languageOfWebPage  # Path of the drivers

# We will assume that pip will be use to install module in case the needed package are not installed
try:
    from selenium import webdriver  # import webdriver
    from selenium.webdriver.common.keys import Keys  # To import Keyx in the keyboard like RETURN, F1, ALT, etc
except:
     subprocess.check_call([sys.executable, "-m", 'pip', "install", 'selenium'])
     from selenium import webdriver  # import webdriver
     from selenium.webdriver.common.keys import Keys  # To import Keyx in the keyboard like RETURN, F1, ALT, etc

try:
    import pandas as pd # used to create csv file at the end
    import numpy as np  # used to create a dataframe which will be used as input to create csv file
except:
     subprocess.check_call([sys.executable, "-m", 'pip', "install", 'pandas'])
     import pandas as pd # used to create csv file at the end
     import numpy as np  # used to create a dataframe which will be used as input to create csv file



def SeleniumWebdriver(driver_path:str = '.' ,driver_type:str ='chrome'):
    """ 
    This function will return the driver path for selenium
    This function takes as input the driver_folder and 
    the drive type (chrome, firefox, edge, safari)
    """
    if driver_type.lower() == 'chrome':
        driver = webdriver.Chrome(executable_path=driver_path) # configure the webdriver
    elif driver_type.lower() == 'edge':
        driver = webdriver.Edge(executable_path=driver_path) # configure the webdriver
    elif driver_type.lower() == 'firefox':
        driver = webdriver.Firefox(executable_path=driver_path) # configure the webdriver 
    elif driver_type.lower() == 'safari':
        driver = webdriver.Safari(executable_path=driver_path) # configure the webdriver 
    else:
        driver = None
        
    return driver


def linksPage(page_number:int, job_tile:str, lang:str):
    """ This function will return a list of link page from the site welcomeToTheJungle
        It take the number of page and the job title in the serach
    """
    job_tile = job_tile.replace(" ", "%")
    link_page = f"https://www.welcometothejungle.com/{lang}/jobs?query={job_tile}&page={page_number}"

    return link_page

def webScrapingSinglePage (page_number:int, searchJob:str, driverPath:str, driverType:str, lang:str):
    """ This function will return a dataframe of results for one webpage
    """

    search_page = linksPage(page_number, searchJob, lang)
    driver = SeleniumWebdriver(driverPath,driverType )
    driver.get(search_page) # Browser will be opened
    
    # To check if we have jungle in the webpage title
    assert "Jungle" in driver.title

    # Find the button to click to accept the cookies
    button =  driver.find_element_by_id("axeptio_btn_acceptAll")
    #Click on the button
    button.click()

    bodyElem = driver.find_element_by_tag_name("body")

    # Scroll until the end of page to load all page elements
    for i in range(15):
        # Scroll down to bottom
        bodyElem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
        bodyElem.send_keys(Keys.ARROW_UP)
        bodyElem.send_keys(Keys.ARROW_UP)
        # Wait to load page
        time.sleep(0.2)

    # All element for class sc-1kkiv1h-8 iwJoCg and tag img
    logo_elements= driver.find_elements_by_css_selector('.sc-1kkiv1h-8.iwJoCg')
    logoLinkList = [logo.get_attribute("src") for logo in logo_elements]

    # Find Company names   
    company_elements = driver.find_elements_by_css_selector('.ais-Highlight.sc-1s0dgt4-13.guUpAr')
    company_list = [company.find_elements_by_css_selector('.ais-Highlight-nonHighlighted')[0].text for company in company_elements]

    # Find Job types  
    Job_elements = driver.find_elements_by_css_selector('.sc-1qc42fc-4.dLcIHx')
    job_type_list = []
    Job_update_list = []
    job_location_list = []

    for job in Job_elements :
        jobTypeInfo = False
        jobUpdateInfo = False
        jobLocationInfo =  False
        for jobItem in job.find_elements_by_tag_name("li") :
            jobItemType = jobItem.find_elements_by_tag_name("span")[0].find_elements_by_tag_name('i')[0].get_attribute("name")
            if (jobItemType == "write"):
                job_type_list.append(jobItem.find_elements_by_tag_name("span")[1].text)
                jobTypeInfo = True
            elif (jobItemType == "location" or jobItemType == "remote"):
                job_location_list.append(jobItem.find_elements_by_tag_name("span")[1].text)
                jobLocationInfo =  True
            elif (jobItemType == "date"):
                Job_update_list.append(jobItem.find_elements_by_tag_name("span")[1].text)
                jobUpdateInfo = True
        
        if (not jobTypeInfo):
            job_type_list.append("")
        if (not jobUpdateInfo):
            Job_update_list.append("")
        if (not jobLocationInfo):
            job_location_list.append("")


    result_df = pd.DataFrame(np.array([company_list, 
                                       job_type_list, 
                                       Job_update_list, 
                                       job_location_list,
                                       logoLinkList]).transpose(),
                             columns=["Company", "Contract_type", "Last_update", "Location", "Logo_link"])
    

    # Checking the next page
    nextPageItem = driver.find_element_by_css_selector('.ais-Pagination-item.ais-Pagination-item--nextPage')
    try:
        nextPageItem.find_element_by_tag_name('a').get_attribute("aria-label") # we have a next page only if tag_name('a') exists
        nextPage = True
    except:
        nextPage = False
        

    
    #To quit driver
    driver.quit()

    # return the dataframe and a boolean representing if there is a nextpage or not
    return result_df, nextPage

pageNumber = 1
nextPage = True

while (nextPage):
    (df, nextPage) = webScrapingSinglePage (page_number = pageNumber, searchJob = jobToCheck, driverPath = DRIVER_PATH, driverType = DRIVER_TYPE, lang = languageOfWebPage)
    myDatetime = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    if (pageNumber == 1):
        csvFileName = f"{jobToCheck}_WTTJ_{languageOfWebPage}_{myDatetime}.csv"
        df.to_csv(path_or_buf = csvFileName, index = False, encoding = 'utf-8-sig', mode = 'a', )
    else :
        df.to_csv(path_or_buf = csvFileName, index = False, encoding = 'utf-8-sig', mode = 'a', header = False)
    
    pageNumber += 1





