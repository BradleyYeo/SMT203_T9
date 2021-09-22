from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import pandas as pd
import json
import os.path
import datetime

# update the 5 variable below
instagram_email = "emocado46@gmail.com"
instagram_password = "Happy_2013"
url_txt_file = "lilireinhart_url.txt" # name of the text file with all the url links
output_json_file = "lilireinhart_comments.json" # name of the output file u want to store for comments data
                                                # IMPORTANT don't create an empty json file before running this script just
                                                # let the script create the file for you
num_post_to_scrape = 200 # number of post u want scrape

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

is_exception = False

with open(url_txt_file, 'r') as f:
    all_url_list = f.read().split(',')
    all_url_set = set(all_url_list)

if os.path.isfile(output_json_file):
    df = pd.read_json(output_json_file)
    df_url_set = set(df['url'])
    all_url_set = all_url_set.difference(df_url_set)
    all_url_list = list(all_url_set)
    print(len(all_url_list))    
    count = len(df['url'])
    # last_url = df.tail(1)['url'].iloc[0]
    # last_url = df['url'].iloc[count-1]
    # url_index = all_url_list.index(last_url)
    # print(url_index)
else:
    # url_index = 0
    count = 0
    
data = {"username": {}, "datetime": {}, "comment": {}, "likes": {}, "url": {}}
break_count = 5
try:
    for i, url in enumerate(all_url_list[:num_post_to_scrape], start=1):
        driver.get(url)
        time.sleep(10)
        try_count = 3
        while try_count:
            try:
                plus_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='dCJp8 afkep']")))
                plus_btn.click()
                break_count = 5
                break
            except:
                print('click blocked,', 'try_count,', try_count)
                try_count -= 1
                if not try_count:
                    break_count -= 1
        if not break_count:
            break

        try_count2 = 3
        while try_count2:
            try:
                cards = driver.find_elements_by_class_name('Mr508')
                for card in cards:
                    card = card.find_element_by_xpath('./div/li/div/div[1]/div[2]')
                    # //*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div[2]/div[1]/ul/ul[1]
                    # //*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div[2]/div[1]/ul/ul[1]/div/li/div/div[1]/div[2]/span
                    user_name = card.find_element_by_xpath('.//a').text
                    comments = card.find_element_by_xpath('./span').text
                    date_time = card.find_element_by_xpath('.//time').get_attribute('datetime')
                    likes = card.find_element_by_xpath('.//button').text
                    str_count = str(count)
                    data["username"][str_count] = user_name
                    data["datetime"][str_count] = date_time
                    data["comment"][str_count] = comments
                    data["likes"][str_count] = str(likes)
                    data["url"][str_count] = url
                    count += 1
                # print(len(data['username']), data['username'][str(count-1)], data['comment'][str(count-1)], data['likes'][str(count-1)])
                print(f'{i} post scraped')
                break
            except:
                print('try_count2 exception', try_count2)
                try_count2 -= 1

except:
    is_exception = True
    last_index = str(max(map(int, data['url'].keys())))
    # scraped_post_count = all_url_list.index(data['url'][last_index])-url_index
    scraped_post_count = len(set(data['url'].values()))
    debug_msg = f'something went wrong! run the script again\n This run managed to scrape {scraped_post_count} posts. Please update the "num_post_to_scrape" accordingly'
    print(debug_msg)

# close window
driver.close()

# save the data
if os.path.isfile(output_json_file):
    with open(output_json_file, 'r') as f:
        temp_dict = json.loads(f.read())
    for key in temp_dict:
        data[key].update(temp_dict[key])
with open(output_json_file, 'w') as out_f:
    json.dump(data, out_f)

if not is_exception and break_count:
    debug_msg = 'Successful! Run this script again tmr!' 
    print(debug_msg)
elif not break_count:
    debug_msg = 'Unsuccessful... Instagram might have blocked your account or IP address' 
    print(debug_msg)

with open('debug_info.txt', 'a') as f:
    f.write(f'srcape_comments.py: {debug_msg} {datetime.datetime.now().strftime("%d %b %Y %H:%M:%S")}\n')