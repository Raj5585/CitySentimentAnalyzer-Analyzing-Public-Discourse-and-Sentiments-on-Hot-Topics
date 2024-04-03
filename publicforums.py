from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import time
import json
import asyncpraw
from asyncpraw.models import MoreComments

import os 

# from News_sites.times_of_india import timesofindia
# import app 

# keywords,cityname = app.async_function


class PublicForum:
    def __init__(self) -> None:
        self.usernamexpath= "//input[@name='text']"
        self.next_buttonxpath = "//span[contains(text(),'Next')]"
        self.passwordxpath = "//input[@name='password']"
        self.loginxpath = "//span[contains(text(),'Log in')]"
        self.base_url = "https://twitter.com/search?q="
        self.commentpath = '//*[@data-testid="tweetText"]/span'

    async def store_data_json(self,datalist):
        file_path = "./data/scrapped_data.json"
        if not os.path.exists(file_path):
            existing_data = []
        else:
            with open(file_path, "r") as file:
                existing_data = json.load(file)

            existing_data.append(datalist)

            with open(file_path, "w") as file:
                json.dump(existing_data, file, indent=4)

            print(f"Data have been stored in '{file_path}'.")

    def store_data_json_replace(self,datalist):
        file_path = "data/extracted_data.json"
        with open(file_path, "w") as file:
            json.dump(datalist, file, indent=4)
        
        print(f"Data have been stored in '{file_path}'.")



    async def scrape_twitter(self, keywords,cityname):
        # Create ChromeOptions
        options = webdriver.ChromeOptions()

        # Set headless mode
        options.headless = True

        # Initialize Chrome WebDriver with headless options
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
 
        driver.set_script_timeout(30)
        res=driver.get("https://twitter.com/i/flow/login") 
        time.sleep(5)

        with open('./data/credentials.json', 'r') as file:
            data = json.load(file)
            username = data["username"]
            password = data["password"]

        username_input = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH,self.usernamexpath))
        )
        username_input.send_keys(username)

        next_button = driver.find_element(By.XPATH,self.next_buttonxpath)
        next_button.click()
        time.sleep(5)

        password_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH,self.passwordxpath))
        )
        password_input.send_keys(password)

        log_in = driver.find_element(By.XPATH,self.loginxpath)
        log_in.click()
        time.sleep(5)

        list=[]
        for keyword in keywords:
            if len(keywords) == 0:
                break
            print(keyword)
            search_url = f'{self.base_url}{keyword}&src=typed_query'
            driver.get(search_url)
            time.sleep(15)
            resp=driver.page_source
            # print("\n"+keyword,end=":\n")
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
                    cmntlist =[comment.text for comment in driver.find_elements(By.XPATH,self.commentpath)]
                    
                    date_element=soup.find_all("time")
                    date_text=None
                    if date_element:
                        date_elements = date_element[0]
                        date_text = date_elements.get("datetime")
                        ddate=date_text.split('T')
                        date=ddate[0]

                    list.append({"keyword":keyword,"cityname":cityname, "title":title, "link":link, "comments":cmntlist, "source":"Twitter", "date":date})
        print(json.dumps(list, indent=4, ensure_ascii=False))
        return list            
        #         store_data_json({"keyword":keyword,"cityname":cityname, "title":title, "link":link, "comments":cmntlist, "source":"Twitter", "date":date})            
        #     store_data_json_replace(list)



    async def scrape_Reddit(self,keywords, cityname):   
        with open('./data/credentials.json', 'r') as file:
            data = json.load(file)
            reddit_client_id = data["reddit_client_id"]
            reddit_client_secret = data["reddit_client_secret"]

        user_agent = "scraper by /u/ramailo"
        reddit = asyncpraw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent=user_agent )

        dataList = []
        for topic in keywords:
            if len(keywords) == 0:
                break
        # Search for submissions asynchronously
            subreddit = await reddit.subreddit("news")
            async for submission in subreddit.search(topic, sort="new", limit=3):
                print(f"Searching for articles on topic: {topic}")
                title = submission.title
                link = submission.url
                print(link)

                submission.comment_sort = "new"
                await submission.load()
                comments = submission.comments.list()           

            
                cmntlist = []
                
                for comment in comments:
                    if isinstance(comment, asyncpraw.models.MoreComments):
                        continue
                    cmntlist.append(comment.body)
                
                # Append data to dataList
                dataList.append({
                    "keyword": topic,
                    "cityname": cityname,
                    "title": title,
                    "link": link,
                    "comments": cmntlist,
                    "source": "Reddit"
                })
        print(json.dumps(dataList, indent=4,ensure_ascii=False))
        return dataList

        # for topic in keywords:
        #     if len(keywords) == 0:
        #         break
        #     submissions = await reddit.subreddit("news").search(topic, sort="new", limit=3)
        #     dataList = []
        #     try:
        #         for submission in submissions:
        #             print(f"Searching for articles on topic: {topic}")
        #             title = submission.title
        #             link = submission.url
        #             # date = submission.created_utc

        #             submission.comments.replace_more(limit=None)
        #             comments = submission.comments.list()
        #             cmntlist = []
        #             print("Comments:")
        #             for comment in comments:
        #                 if isinstance(comment, asyncpraw.models.MoreComments):
        #                     continue
        #                 cmntlist.append(comment.body)
        #             dataList.append({ "keyword":topic,"cityname":cityname, "title":title, "link":link, "comments":cmntlist, "source":"Reddit"})
        #             # store_data_json({ "keyword":topic,"cityname":cityname, "title":title, "link":link, "comments":cmntlist, "source":"Reddit"})
        #         # store_data_json_replace(dataList)
        #         # store_data_json(dataList)
        #     except Exception as e:
        #         print(e)
        # print(json.dumps(dataList, indent=4,ensure_ascii=False))
        # return dataList
    
    async def main(self,keywords,cityname):
        lst1 = await self.scrape_twitter(keywords,cityname)
        lst2 = await self.scrape_Reddit(keywords,cityname)
        lst3 =  lst1 +  lst2
        self.store_data_json_replace(lst3)




# if __name__ == "main":