import time
import pandas as pd
import os
import glob
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HardwarezoneCrawler:
    def __init__(self) -> None:
        options = webdriver.ChromeOptions() 
        options.add_argument('log-level=3')
        options.add_argument("start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("enable-automation")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-browser-side-navigation")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    def get_options():
        options = webdriver.ChromeOptions() 
        options.add_argument('log-level=3')
        options.add_argument("start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("enable-automation")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-browser-side-navigation")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return options
        
    def get_url(self, aspect_item: str):
        self.driver.quit()
        options = webdriver.ChromeOptions() 
        options.add_argument('log-level=3')
        options.add_argument("start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("enable-automation")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-browser-side-navigation")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.driver.get("https://www.hardwarezone.com.sg/search/forum")

        # Wait for the search input field to be clickable
        search_navi = WebDriverWait(self.driver, 11).until(
            EC.element_to_be_clickable((By.XPATH, "//form/input[@class='text']"))
        )
        search_navi.send_keys(aspect_item)
        time.sleep(10)

        submit_btn = self.driver.find_element("xpath","//form/input[@type='submit']")
        webdriver.ActionChains(self.driver).move_to_element(submit_btn).click(submit_btn).perform()
        time.sleep(10)
        forum_btn = self.driver.find_element("xpath","//ul[@class='tabs-menu']/li[6]")
        webdriver.ActionChains(self.driver).move_to_element(forum_btn).click(forum_btn).perform()
        time.sleep(10)

        self.driver.execute_script ("window.scrollTo(0,document.body.scrollHeight);")

        # The first page of forums
        threads_list = []
        links_list = self.driver.find_elements("xpath","//a[@class='gs-title']")
        for link in links_list:
            if link.get_attribute('href'):
                threads_list.append(link.get_attribute('href'))
                
        # The rest pages of forums
        for i in range(2, 20):
            try:
                page_ele = self.driver.find_element("xpath", "//div[@aria-label='Page " + str(i) + "']")
                webdriver.ActionChains(self.driver).move_to_element(page_ele).click(page_ele).perform()
                time.sleep(10)
            except NoSuchElementException:
                print("Page element not found for page", i)
            
            links_list = self.driver.find_elements("xpath","//a[@class='gs-title']")
            for link in links_list:
                if link.get_attribute('href'):
                    threads_list.append(link.get_attribute('href'))

        # Navigate to Google
        try:
            google_navi_ele = self.driver.find_element("xpath","//div[@class='gcsc-more-maybe-branding-root']/a")
            google_search_url = google_navi_ele.get_attribute("href")
            self.driver.get(google_search_url)
        except NoSuchElementException:
            print("Page element not found for page")

        # The first page of google search results
        links_list = self.driver.find_elements("xpath","//div[@class='yuRUbf']/a")
        for link in links_list:
            if link.get_attribute("href"):
                threads_list.append(link.get_attribute("href"))

        self.driver.execute_script ("window.scrollTo(0,document.body.scrollHeight);")
        # The rest pages of google search results
        for i in range(2, 16):
            try:
                page_ele = self.driver.find_element("xpath","//a[@aria-label='Page " + str(i) + "']")
                webdriver.ActionChains(self.driver).move_to_element(page_ele).click(page_ele).perform()
                time.sleep(10)
                
                links_list = self.driver.find_elements("xpath","//div[@class='yuRUbf']/a")
                for link in links_list:
                    if link.get_attribute('href'):
                        threads_list.append(link.get_attribute('href'))
            except:
                print("We can not find the pages that required, end the loop")
                    
        threads_list = list(set(threads_list))
        aspects_list = [aspect_item for i in range(len(threads_list))]
        data_df = pd.DataFrame(list(zip(threads_list, aspects_list)), columns=['url', 'aspect'])
        data_df.to_csv("E:/Critical Inquiry/Code/Data Scraping/data/hwz_data_" + aspect_item + ".csv", index=False)
    
    def getReviews_content(self, csv_path: str, aspect_term: str):
        url_df = pd.read_csv(csv_path)
        url_df = url_df.drop(url_df[url_df['url'] == "https://forums.hardwarezone.com.sg/forums/eat-drink-man-woman.16/"].index)
        
        aspects_list = []
        urls_list = []
        titles_list = []
        contents_list = []
        authors_list = []
        timeStamps_list = []
        memberships_list = []

        for index, row in tqdm(url_df.iterrows()):
            if row.aspect != aspect_term:
                continue
            self.driver.quit()
            options = webdriver.ChromeOptions() 
            options.add_argument('log-level=3')
            options.add_argument("start-maximized")
            options.add_argument("--disable-gpu")
            options.add_argument("enable-automation")
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-browser-side-navigation")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            self.driver.get(row.url)
            try:
                thread_first_page = self.driver.find_element("xpath","//ul[@class='pageNav-main']/li/a")
                self.driver.get(thread_first_page.get_attribute("href"))
                # time.sleep(1)
            except:
                print(self.driver.find_element("xpath","//h1[@class='p-title-value']").text, "\t, this thread Only one pages")

            contents_web = self.driver.find_elements("xpath","//div[@class='bbWrapper']")
            for content in contents_web:
                contents_list.append(content.text)
                titles_list.append(self.driver.find_element("xpath","//h1[@class='p-title-value']").text)
                urls_list.append(row.url)
                aspects_list.append(row.aspect)

            authors_web = self.driver.find_elements("xpath","//a[@class='username ']")
            for author in authors_web:
                authors_list.append(author.text)

            timeStamps_web = self.driver.find_elements("xpath","//time[@class='u-dt']")
            for timeStamp in timeStamps_web:
                timeStamps_list.append(timeStamp.text)

            memberships_web = self.driver.find_elements("xpath","//h5[@class='userTitle message-userTitle']")
            for membership in memberships_web:
                memberships_list.append(membership.text)
                
            flag = True
            cnt = 0
            while flag and cnt <= 100:
                try:
                    forum_first_page = self.driver.find_element("xpath","//a[@class='pageNav-jump pageNav-jump--next']")
                    self.driver.get(forum_first_page.get_attribute("href"))
                    time.sleep(1)
                
                    contents_web = self.driver.find_elements("xpath","//div[@class='bbWrapper']")
                    for content in contents_web:
                        contents_list.append(content.text)
                        titles_list.append(self.driver.find_element("xpath","//h1[@class='p-title-value']").text)
                        urls_list.append(row.url)
                        aspects_list.append(row.aspect)

                    authors_web = self.driver.find_elements("xpath","//a[@class='username ']")
                    for author in authors_web:
                        authors_list.append(author.text)

                    timeStamps_web = self.driver.find_elements("xpath","//time[@class='u-dt']")
                    for timeStamp in timeStamps_web:
                        timeStamps_list.append(timeStamp.text)

                    memberships_web = self.driver.find_elements("xpath","//h5[@class='userTitle message-userTitle']")
                    for membership in memberships_web:
                        memberships_list.append(membership.text)
                except: 
                    flag = False
                    cnt = 0
                    print("Websites Name:\t", self.driver.find_element("xpath","//h1[@class='p-title-value']").text, ', We encounter a problem in this websites or we come the end the this thread')
                    time.sleep(1)
                    
        hardware_zone_df = pd.DataFrame(list(zip(urls_list, titles_list, contents_list,
                                                        authors_list, timeStamps_list, memberships_list, aspects_list)),
                                            columns=['url', 'title', 'content', 'author', 
                                                        'time_stamp', 'membership', "aspect"])
        hardware_zone_df.to_csv("E:/Critical Inquiry/Code/Data Scraping/data/hwz_thread_all_data_" + aspect_term + '.csv', index=False)
    
    def write_to_disk(self, aspects_list, urls_list, titles_list, contents_list, authors_list, timeStamps_list, memberships_list, aspect_term):
        hardware_zone_df = pd.DataFrame({
            'url': urls_list,
            'title': titles_list,
            'content': contents_list,
            'author': authors_list,
            'time_stamp': timeStamps_list,
            'membership': memberships_list,
            'aspect': aspects_list
        })
        # Write data to disk
        file_path = f"E:/Critical Inquiry/Code/Data Scraping/data/hwz_thread_all_data_{aspect_term}.csv"
        if os.path.exists(file_path):
            mode = 'a'
            header = False
        else:
            mode = 'w'
            header = True
        hardware_zone_df.to_csv(file_path, mode=mode, header=header, index=False)
    
    def search_items(self, aspect_items: list):
        for item in aspect_items:
            self.getAndSave_url(item)
        
        self.combine_data()
    
    def combine_url_data(self):
        all_data = glob.glob(os.path.join("E:/Critical Inquiry/Code/Data Scraping/data/", "hwz_data_*.csv"))
        df_from_each_file = (pd.read_csv(f, sep=',') for f in all_data)
        df_merged = pd.concat(df_from_each_file, ignore_index=True)
        df_merged.drop_duplicates()
        
        # Drop noise pages
        for index, row in tqdm(df_merged.iterrows()):
            cnt = 1
            self.driver.get(row.url)
            try:
                pages = self.driver.find_elements("xpath","//li[@class='pageNav-page ']/a")
                for page in pages: 
                    cnt = max(int(page.text), cnt)
            except:
                cnt = 1
                
            if cnt >= 100:
                df_merged.drop(index, inplace=True)
            time.sleep(1)
        
        df_merged.to_csv("E:/Critical Inquiry/Code/Data Scraping/data/hwz_url_data.csv", index=False)
        
    def combine_data(self):
        all_data = glob.glob(os.path.join("E:/Critical Inquiry/Code/Data Scraping/data/", "hwz_thread_all_data_*.csv"))
        df_from_each_file = (pd.read_csv(f, sep=',') for f in all_data)
        df_merged = pd.concat(df_from_each_file, ignore_index=True)
        df_merged.drop_duplicates(subset=['content'], inplace=True)
        
        df_merged.to_csv("E:/Critical Inquiry/Code/Data Scraping/data/hwz_all_data.csv", index=False)
        
aspect_items = ["lgbtq", "lgbt", "gay", "lesbian", "bisexual", "transgender", "queer", "pink dot", "pride month", "section 377A", "same-sex marriage"]
#aspect_items = ["lgbtq"]
crawler = HardwarezoneCrawler()
for aspect in aspect_items:
    crawler.get_url(aspect)
crawler.combine_url_data()
data_df = pd.read_csv("E:/Critical Inquiry/Code/Data Scraping/data/hwz_url_data.csv")
aspect_terms = dict(data_df["aspect"].value_counts()).keys()
print("All aspect terms:\t" + str(aspect_terms))
for aspect in aspect_terms:
    print("Aspect is :\t" + aspect)
    crawler.getReviews_content("E:/Critical Inquiry/Code/Data Scraping/data/hwz_url_data.csv", aspect)
    
crawler.combine_data()