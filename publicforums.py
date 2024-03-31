from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import time
import json
import praw
import os 

from News_sites.times_of_india import timesofindia 

keywords,cityname = timesofindia()
print(keywords, cityname)

 
usernamexpath= "//input[@name='text']"
next_buttonxpath = "//span[contains(text(),'Next')]"
passwordxpath = "//input[@name='password']"
loginxpath = "//span[contains(text(),'Log in')]"
base_url = "https://twitter.com/search?q="
commentpath = '//*[@data-testid="tweetText"]/span'

def store_data_json(datalist):
    file_path = "data/scrapped_data.json"
    if not os.path.exists(file_path):
        existing_data = []
    else:
        with open(file_path, "r") as file:
            existing_data = json.load(file)

        existing_data.append(datalist)

        with open(file_path, "w") as file:
            json.dump(existing_data, file, indent=4)

        print(f"Data have been stored in '{file_path}'.")



def scrape_twitter():
    driver = webdriver.Chrome()  
    driver.set_script_timeout(30)
    res=driver.get("https://twitter.com/i/flow/login") 
    time.sleep(5)

    with open('./data/credentials.json', 'r') as file:
        data = json.load(file)
        username = data["username"]
        password = data["password"]

    username_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH,usernamexpath))
    )
    username_input.send_keys(username)

    next_button = driver.find_element(By.XPATH,next_buttonxpath)
    next_button.click()
    time.sleep(5)

    password_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH,passwordxpath))
    )
    password_input.send_keys(password)

    log_in = driver.find_element(By.XPATH,loginxpath)
    log_in.click()
    time.sleep(5)

    list=[]
    for keyword in keywords:
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
            # print(len(profile_header))
            # if(len(profile_header)<1):
            #     tweetdata={}

        except:
            print("no article in this topic") 
            continue
        
        for headers in profile_header:
            # tweetdata={}
            # try:
            #     text=headers.find("div",{"data-testid":"User-Name"}).text
            #     lst=text.split("@")
            #     tweetdata["profile_name"]="@"+lst[1].split('·')[0]
            # except Exception as e:
            #     print(e)
            #     continue

            try:
                tweettime =headers.find("time").text
            except:
                continue

            try:
                sentence=headers.find("div",{"data-testid":"tweetText"}).text
                trun_caption= sentence[:450]
                title =trun_caption
            except:
                continue

            try:
                link_css_selector = 'div > div > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(1) > div > div:nth-of-type(1) > div > div > div:nth-of-type(2) > div >div:nth-of-type(3) > a'
                child_element = headers.select_one(link_css_selector)
                href_value=child_element.get('href')
                if href_value:
                    link  = f"https://twitter.com{href_value}"
            except:
                continue    

            if (tweettime[-1:]=="s" or tweettime[-1:]=="m"  or tweettime[-1:]=="h"):
                driver.get(link)
                time.sleep(5)
                cmntlist =[comment.text for comment in driver.find_elements(By.XPATH,commentpath)]
                
                date_element=soup.find_all("time")
                date_text=None
                if date_element:
                    date_elements = date_element[0]
                    date_text = date_elements.get("datetime")
                    ddate=date_text.split('T')
                    date=ddate[0]

            list.append({"keyword":keyword,"cityname":cityname, "title":title, "link":link, "comments":cmntlist, "source":"Twitter", "date":date})            
            store_data_json({"keyword":keyword,"cityname":cityname, "title":title, "link":link, "comments":cmntlist, "source":"Twitter", "date":date})            
    print(json.dumps(list, indent=4, ensure_ascii=False))



def scrape_Reddit():   
    with open('./data/credentials.json', 'r') as file:
        data = json.load(file)
        reddit_client_id = data["reddit_client_id"]
        reddit_client_secret = data["reddit_client_secret"]

    user_agent = "scraper by /u/ramailo"
    reddit = praw.Reddit(
    client_id=reddit_client_id,
    client_secret=reddit_client_secret,
    user_agent=user_agent )

    for topic in keywords:
        submissions = reddit.subreddit("news").search(topic, sort="new", limit=3)
        dataList = []
        try:
            for submission in submissions:
                print(f"Searching for articles on topic: {topic}")
                title = submission.title
                link = submission.url
                date = submission.created_utc

                submission.comments.replace_more(limit=None)
                comments = submission.comments.list()
                cmntlist = []
                print("Comments:")
                for comment in comments:
                    if isinstance(comment, praw.models.MoreComments):
                        continue
                    cmntlist.append(comment.body)

                store_data_json({ "keyword":topic,"cityname":cityname, "title":title, "link":link, "comments":cmntlist, "source":"Reddit"})
                dataList.append({ "keyword":topic,"cityname":cityname, "title":title, "link":link, "comments":cmntlist, "source":"Reddit"})
        except Exception as e:
            print(e)
    print(json.dumps(dataList, indent=4,ensure_ascii=False))

scrape_twitter()
scrape_Reddit()