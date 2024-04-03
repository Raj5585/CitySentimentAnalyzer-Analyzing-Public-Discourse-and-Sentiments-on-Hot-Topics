from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium import webdriver


# keyword = input("Enter a city's name: ")

async def timesofindia(keyword):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get("https://timesofindia.indiatimes.com/")

    try:
        print(f"searching for {keyword}")
        searchbutton = '//*[@id="app"]/div/div[2]/div/div[3]/div/div/div/div[2]/div/span'
        inputbar = '//*[@id="searchField"]'
        latestbutton = '//*[@id="Last 24 Hours"]'
        titleofnews = '//div[contains(@class,"uwU81")]//div[@class="VXBf7"]//div/span'
        noresultfound = '//div[contains(@class,"hxbkY")]'

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
        checkresult = None
        try:
            checkresult = driver.find_element(By.XPATH,noresultfound)
        except:
            pass
        if not checkresult:
            print("ok ")
            try:
                titles = driver.find_elements(By.XPATH,titleofnews)
                lst = []
                for i in titles[:5]:
                    text = i.text
                    print(text)
                    list =text.split(':')
                    print(list)
                    if len(list) > 1:
                        if len(list[0]) >= len(list[1]):
                            lst.append(list[0])
                        else:
                            lst.append(list[1])
                    else:
                        lst.append(list[0])
                print(lst)
                return lst    
            except Exception as e:
                print("no news found ")
                print(e)
                return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def bbcnews():
    pass
