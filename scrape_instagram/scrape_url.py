from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# This script will scrape all the instagram post url of a particular celebrity and
# output a text file containing all the links

SCROLL_PAUSE_TIME = 7
with open('user_password.txt', 'r') as f:
    instagram_email = f.readline().split('=')[1].strip(' \n')    
    instagram_password = f.readline().split('=')[1].strip(' \n')

#get the first instagram handle in the text file 
with open('10_insta_handle.txt', 'r') as f:
    instagram_handle = f.readline().strip('@\n')

# if no more celebrities to scrape '1'+1 will throw an error so the below code wont run
if not instagram_handle:
    print('1'+1)

#specify the path to chromedriver.exe (download and save on your computer)
driver = webdriver.Chrome(ChromeDriverManager().install())
#open the webpage
driver.get("http://www.instagram.com")

#target username
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

#enter username and password
username.clear()
username.send_keys(instagram_email)
password.clear()
password.send_keys(instagram_password)

#target the login button and click it
button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

instagram_url = f'https://www.instagram.com/{instagram_handle}/'
time.sleep(10)
driver.get(instagram_url)
list_url = []
instagram_bio = ''

# get instagram bio
bio_container = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[2]')))
all_children_by_xpath = bio_container.find_elements_by_xpath(".//*")
for ele in all_children_by_xpath:
    if ele.text:
        instagram_bio += ele.text


# get the first 9 post (do once before entering while loop)
time.sleep(SCROLL_PAUSE_TIME)
try_count = 3
while try_count:
    try:
        section = driver.find_element_by_css_selector('article[class="ySN3v"]').find_element_by_xpath('./div[1]/div')
        break
    except:
        time.sleep(2)
        try_count -= 1
    
try:
    for i in range(1, 4):
        for j in range(1, 4):
            temp_url = section.find_element_by_xpath(f'./div[{i}]/div[{j}]/a').get_attribute("href")
            list_url.append(temp_url)
except:
    pass

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

# continue scrolling down till no more post or time limit reached
start_time = time.time()
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)
    section = driver.find_element_by_css_selector('article[class="ySN3v"]').find_element_by_xpath('./div[1]/div')
    try:
        for i in range(1, 20):
            for j in range(1, 4):
                if temp_url not in list_url:
                    temp_url = section.find_element_by_xpath(f'./div[{i}]/div[{j}]/a').get_attribute("href")
                    list_url.append(temp_url)
    except:
        pass

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height or time.time()-start_time > 600:
        break
    last_height = new_height


# close window
driver.close()

# remove the instagram handle from text file after finishing scraping
with open('10_insta_handle.txt', 'r') as f:
    instagram_handle_list = f.readlines()

with open('10_insta_handle.txt', 'w') as f:
    for handle in instagram_handle_list[1:]:
        f.write(handle)

# add the succefully scraped instagram handle to another text file for scape_comments.py to ready 
with open('successful_insta_handle.txt', 'a') as f:
    f.write(f'{instagram_handle_list[0]}\n')

# upload to csv
df = pd.DataFrame({'name': [instagram_handle]*len(list_url), 'url': list_url, 'bio': [instagram_bio]*len(list_url)})
df.to_csv(f'{instagram_handle}_url.csv')
