import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import pandas as pd

ID = "id"
NAME = "name"
XPATH = "xpath"
LINK_TEXT = "link text"
PARTIAL_LINK_TEXT = "partial link text"
TAG_NAME = "tag name"
CLASS_NAME = "class name"
CSS_SELECTOR = "css selector"

# get excel file with street names
excel_data = pd.read_excel('comm_median_rentals_2022Q2.xlsx')
data = pd.DataFrame(excel_data.iloc[2:, [0, 2]].reset_index(drop=True))
data.columns = ['Street Name', 'Median Rent']
data = data[data['Median Rent'] != '.']    # Remove streets with no rent value
data['Median Rent'] = data['Median Rent'].astype(float)
# data = data[:10]
print(data)


driver = webdriver.Chrome()
driver.get('https://www.ura.gov.sg/maps/')

first_gotomap = '//*[@id="us-c-ip"]/div[1]/div[1]/div[4]/div[3]/div[2]/div[2]'
address_input = '//*[@id="us-s-txt"]'
first_result = '/html/body/div[6]/div[2]/div/a[1]'
planning_area_txt = '//*[@id="us-ip-poi-content"]/div[1]/div[3]'

all_results = []


def document_initialised(driver):
    return driver.execute_script("return initialised")


driver.get('https://www.ura.gov.sg/maps/')
driver.find_element(By.XPATH, first_gotomap).click()

for street in data['Street Name']:

    driver.find_element(By.XPATH, address_input).send_keys(street)

    # https://www.selenium.dev/selenium/docs/api/py/webdriver_support/selenium.webdriver.support.expected_conditions.html?highlight=expected
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, first_result))
    )
    element.click()

    time.sleep(1)

    error = True
    while error:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        select_area = soup.find('div', class_='us-ip-poi-a-note')
        print('select area:', select_area.string)
        if select_area.string != None:
            result = (select_area.string).rsplit(' ', 2)[0]
            # print(result)
            all_results.append(result)
            driver.find_element(By.XPATH, address_input).clear()
            error = False
        else:
            time.sleep(2)       # add more time if page still loading


print(all_results)
data['Planning Area'] = all_results
print(data)

# Group by planning area and obtain mean rent for each planning area
print('-------EXPORTING')

data.to_excel('results.xlsx')
rent_by_area = pd.DataFrame(data.groupby(['Planning Area']).mean())
print(rent_by_area)
rent_by_area.to_excel('median_rent_by_planning_area.xlsx')

print('-------COMPLETED')


time.sleep(10)
driver.quit()
