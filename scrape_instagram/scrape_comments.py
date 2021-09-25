from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import pandas as pd
import os.path
import datetime
from dateutil.relativedelta import relativedelta

target_date_list = ['2020-01','2020-02','2020-03','2020-04','2020-05','2020-06','2020-07','2020-08','2020-09','2020-10','2020-11','2020-12']
with open('user_password.txt', 'r') as f:
    instagram_email = f.readline().split('=')[1] .strip(' \n')   
    instagram_password = f.readline().split('=')[1] .strip(' \n')

with open('successful_insta_handle.txt', 'r') as f:
    handle = f.readline().strip('@\n')

if not handle:
    print('1'+1)

url_csv_file = f"{handle}_url.csv" 
output_csv_file = f"{handle}_comments.csv" 
all_url_list = list(pd.read_csv(url_csv_file)['url'])

driver = webdriver.Chrome("chromedriver.exe")
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

time.sleep(10)

for target_date in target_date_list:
    posts_to_scrape_list = []
    data = {"username": [], "datetime": [], "comment": [], "likes": [], "url": []}
    bsearch_count = 3
    target_date = datetime.datetime.strptime(target_date, '%Y-%m')
    while bsearch_count:
        lower = -1
        upper = len(all_url_list)
        mid = (lower+upper)//2
        while lower+1 != upper:
            temp_url = all_url_list[mid]
            driver.get(temp_url)
            temp_date = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div[2]/div[1]/ul/div/li/div/div/div[2]/div/div/time').get_attribute('datetime')
            temp_date = datetime.datetime.strptime(temp_date[:7], '%Y-%m')
            if temp_date > target_date:
                lower = mid
            elif temp_date < target_date:
                upper = mid
            else:
                posts_to_scrape_list.append(temp_url)
                bsearch_count = 0
                break
            mid = (lower+upper)//2
            time.sleep(3)
        else:
            target_date_list.append((datetime.datetime.strptime(target_date_list[-1], '%Y-%m')+relativedelta(months=1)).strftime('%Y-%m'))
            target_date += relativedelta(months=1)
            bsearch_count -= 1

    posts_to_scrape_list += [all_url_list[mid-1], all_url_list[mid+1]]

    for i in range(3):
        if i != 0:
            temp_url = posts_to_scrape_list[i]
            driver.get(temp_url)
        time.sleep(5)
        try_click_plus_btn_count = 10
        while try_click_plus_btn_count:
            try:
                plus_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='dCJp8 afkep']")))
                plus_btn.click()
            except:
                try_click_plus_btn_count -= 1
        
        try_scrape_comments_count = 10
        card_index_before_error = None
        while try_scrape_comments_count:
            try:
                cards = driver.find_elements_by_class_name('Mr508')
                if card_index_before_error is not None:
                    cards = cards[card_index_before_error:]
                for j, card in enumerate(cards):
                    card_index_before_error = j
                    card = card.find_element_by_xpath('./div/li/div/div[1]/div[2]')
                    user_name = card.find_element_by_xpath('.//a').text
                    comments = card.find_element_by_xpath('./span').text
                    date_time = card.find_element_by_xpath('.//time').get_attribute('datetime')
                    likes = card.find_element_by_xpath('.//button').text
                    data["username"].append(user_name)
                    data["datetime"].append(date_time)
                    data["comment"].append(comments)
                    data["likes"].append(str(likes))
                    data["url"].append(temp_url)
                break
            except:
                try_scrape_comments_count -= 1
                time.sleep(3)
    # save the data
    if os.path.isfile(output_csv_file):
        df = pd.read_csv(output_csv_file).drop(['Unnamed: 0'], axis=1)
        pd.concat([df, pd.DataFrame(data)]).to_csv(output_csv_file)
    else:
        pd.DataFrame(data).to_csv(output_csv_file)

# close window
driver.close()

with open('successful_insta_handle.txt', 'r') as f:
    instagram_handle_list = f.readlines()

with open('successful_insta_handle.txt', 'w') as f:
    for insta_handle in instagram_handle_list[1:]:
        f.write(insta_handle)

