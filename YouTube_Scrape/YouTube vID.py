import urllib.request
import re
import pandas as pd
import csv

file = pd.read_excel('List of Celebrities.xlsx')
videoid_lst = []

for i in file['Name']:

    search_keyword = i.replace(' ', '')
    html = urllib.request.urlopen('https://www.youtube.com/results?search_query=' + search_keyword +'&sp=CAMSBAgFEAE%253D')
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    videoid_lst.append(video_ids[0:3])
print(videoid_lst)

with open('celebrityYT1.csv', 'w') as f:
    writer = csv.writer(f)
    for vid_id in videoid_lst:
        writer.writerow(vid_id)
