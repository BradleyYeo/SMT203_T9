from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import pandas as pd
import os.path
import datetime
from dateutil.relativedelta import relativedelta
import re

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

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

df_set_url = []
if os.path.isfile(output_csv_file):
    df = pd.read_csv(output_csv_file).drop(['Unnamed: 0'], axis=1)
    df_set_url = set(df.url)

driver = webdriver.Chrome("chromedriver.exe")
#open the webpage
driver.get("http://www.instagram.com")

try:
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
        bsearch_count = 10
        target_date = datetime.datetime.strptime(target_date, '%Y-%m')
        while bsearch_count:
            lower = -1
            upper = len(all_url_list)
            mid = (lower+upper)//2
            while lower+1 != upper:
                temp_url = all_url_list[mid]
                driver.get(temp_url)
                temp_date = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "time[class='_1o9PC Nzb55']"))).get_attribute('datetime')
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
                if target_date_list[-1] == '2020-12':
                    target_date_list.append((datetime.datetime.strptime(target_date_list[0], '%Y-%m')+relativedelta(months=-1)).strftime('%Y-%m'))
                else:
                    target_date_list.append((datetime.datetime.strptime(target_date_list[-1], '%Y-%m')+relativedelta(months=-1)).strftime('%Y-%m'))
                bsearch_count = 0

        while len(posts_to_scrape_list) < 3:
            index_left = mid-1
            index_right = mid+1
            left_url = all_url_list[index_left]
            right_url = all_url_list[index_right]
            if left_url in df_set_url:
                index_left -= 1
                left_url = all_url_list[index_left]
            if right_url in df_set_url:
                index_right += 1
                right_url = all_url_list[index_right]
            posts_to_scrape_list.append(left_url) 
            posts_to_scrape_list.append(right_url)

        for i in range(3):
            data = {"username": [], "datetime": [], "comment": [], "likes": [], "url": []}
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
            
            page_source = driver.page_source
            list_ps = page_source.split('Mr508')[1:-1]
            for card in list_ps:
                username_index1 = card.find('span')
                username_index2 = card.find('span', 4+username_index1)
                user_name = striphtml(card[username_index1-1:username_index2+5])

                comment_index1 = card.find('span', 4+username_index2)
                comment_index2 = card.find('span', 4+comment_index1)
                comments = striphtml(card[comment_index1-1:comment_index2+5])

                datetime_index = card.find('datetime', 8+comment_index2)
                date_time = card[datetime_index+10:datetime_index+34]

                like_index1 = card.find('<button class="FH9sR">', 22+datetime_index)
                if like_index1 != -1:
                    like_index2 = card.find('</button>', 9+like_index1)
                    likes = card[like_index1+22:like_index2]

                data["username"].append(user_name)
                data["datetime"].append(date_time)
                data["comment"].append(comments)
                if like_index1 != -1:
                    data["likes"].append(str(likes))
                else:
                    data["likes"].append('Reply')
                data["url"].append(temp_url)
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
except:
    driver.close()
    with open('successful_insta_handle.txt', 'r') as f:
        instagram_handle_list = f.readlines()

    if len(pd.read_csv(output_csv_file)['url']) > 300*3*12:
        instagram_handle_list.pop(0)
    else:
        instagram_handle_list = instagram_handle_list[1:]+[instagram_handle_list[0]]
    
    with open('successful_insta_handle.txt', 'w') as f:
        for insta_handle in instagram_handle_list[1:]+[instagram_handle_list[0]]:
            f.write(insta_handle)
