from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
from timesofindia import timesofindia

usernamexpath= "//input[@name='text']"
next_buttonxpath = "//span[contains(text(),'Next')]"
passwordxpath = "//input[@name='password']"
loginxpath = "//span[contains(text(),'Log in')]"
base_url = "https://twitter.com/search?q="
commentpath = '//*[@data-testid="tweetText"]/span'


def scrape_twitter():
    lst = timesofindia()
    driver = webdriver.Chrome()  
    driver.set_script_timeout(30)
    res=driver.get("https://twitter.com/i/flow/login") 
    time.sleep(5)

    with open('./credentials.json', 'r') as file:
        data = json.load(file)
        username = data["username"]
        password = data["password"]



    username_input = driver.find_element(By.XPATH,usernamexpath)
    username_input.send_keys(username)

    next_button = driver.find_element(By.XPATH,next_buttonxpath)
    next_button.click()
    time.sleep(5)

    password_input = driver.find_element(By.XPATH,passwordxpath)
    password_input.send_keys(password)

    log_in = driver.find_element(By.XPATH,loginxpath)
    log_in.click()

    time.sleep(5)
 

    list=[]
    for keyword in lst:
        print(keyword)
        search_url = f'{base_url}{keyword}&src=typed_query'
        driver.get(search_url)
        time.sleep(15)
        resp=driver.page_source
        print("\n"+keyword,end=":\n")
        soup=BeautifulSoup(resp,'html.parser')
        article_section = soup.find("section",{"class":"css-175oi2r"})

        try:
            profile_header = article_section.find_all("article",{"data-testid":"tweet"})
            print(len(profile_header))
            if(len(profile_header)<1):
                tweetdata={}

        except:
            print("no article in this topic") 
            continue
        
        for headers in profile_header:
            print("inside")
            tweetdata={}
            try:
                text=headers.find("div",{"data-testid":"User-Name"}).text
                lst=text.split("@")
                tweetdata["profile_name"]="@"+lst[1].split('·')[0]
            except Exception as e:
                print(e)
                continue

            try:
                tweetdata["tweet_time"]=headers.find("time").text
            except:
                continue

            try:
                sentence=headers.find("div",{"data-testid":"tweetText"}).text
                trun_caption= sentence[:450]
                tweetdata["caption"]=trun_caption
            except:
                continue

            try:
                link_css_selector = 'div > div > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(1) > div > div:nth-of-type(1) > div > div > div:nth-of-type(2) > div >div:nth-of-type(3) > a'
                child_element = headers.select_one(link_css_selector)
                href_value=child_element.get('href')
                if href_value:
                    tweetdata["post_link"]  = f"https://twitter.com{href_value}"
            except:
                continue    

            ttime=tweetdata["tweet_time"]
            if (ttime[-1:]=="s" or ttime[-1:]=="m"  or ttime[-1:]=="h"):
                driver.get(tweetdata["post_link"])
                time.sleep(5)
                comments =[comment.text for comment in driver.find_elements(By.XPATH,commentpath)]
                tweetdata['comments'] = comments
                date_element=soup.find_all("time")

                date_text=None
                if date_element:
                    date_elements = date_element[0]
                    date_text = date_elements.get("datetime")
                    ddate=date_text.split('T')
                    tweetdata["date"]=ddate[0]
                    print("**************************************")
               
            tweetdata["keyword"]=keyword
            tweetdata["source"]='X(twitter)'
            list.append(tweetdata)             
    print(json.dumps(list, indent=4, ensure_ascii=False))

    file_path = "data.json"
    with open(file_path, "w") as json_file:
        json.dump(list, json_file, indent=4)

    print(f"Data have been stored in '{file_path}'.")


def scrape_Reddit():
    pass

scrape_twitter()