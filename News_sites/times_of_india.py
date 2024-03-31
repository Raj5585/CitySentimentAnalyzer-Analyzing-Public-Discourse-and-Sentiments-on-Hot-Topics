from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium import webdriver


keyword = input("Enter a city's name: ")

def timesofindia():
    driver = webdriver.Chrome()
    driver.get("https://timesofindia.indiatimes.com/")

    try:
        print(f"searching for {keyword}")
        searchbutton = '//*[@id="app"]/div/div[2]/div/div[3]/div/div/div/div[2]/div/span'
        inputbar = '//*[@id="searchField"]'
        latestbutton = '//*[@id="Last 24 Hours"]'
        titleofnews = '//div[contains(@class,"uwU81")]//div[@class="VXBf7"]//div/span'

        search = driver.find_element(By.XPATH,searchbutton)
        search.click()
        input_field = driver.find_element(By.XPATH,inputbar)
        input_field.send_keys(keyword)
        input_field.send_keys(Keys.RETURN)
        time.sleep(15)
        searchlatest = driver.find_element(By.XPATH,latestbutton)
        searchlatest.click()
        print("Clicked")
        time.sleep(5)
        titles = driver.find_elements(By.XPATH,titleofnews)
        lst = []
        for i in titles[:5]:
            text = i.text
            list =text.split(':')
            if(len(list)>=2):
                for stipped_lst in list:
                    if(len(stipped_lst[0])>stipped_lst(lst[1])):
                        lst.append(stipped_lst[0])
                    else:
                        lst.append(stipped_lst[1])
            else:
                 lst.append(list[0])
            
        return lst, keyword     
    except Exception as e:
        print(f"Error: {e}")

def bbcnews():
    pass
