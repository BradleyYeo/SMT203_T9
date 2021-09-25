# Scrape Instagram Comments

## Open 10_insta_handle and put your 10 celebrities instagram handle in this format

@adele\
@alexshibutani\
@amberheard\
@annakendrick47\
@anthonyramosofficial

## Open user_password and write your instagram email and password

# Using Task Scheduler to automatically run python files

## read scrape_insta_url_instructions and set up auto run for scrape_url.py

scape_url.py will read the first instagram handle in 10_insta_handle.txt and collect the first 500~700 post urls that celebrity and their bio
after successful run, the celebrity's instagram handle will be removed from 10_insta_handle.txt and successful_isnta_handle.txt will be updated with that celebrity's instagram handle

## read scrape_insta_comments_instructions and set up auto run for scrape_comments.py

scrape_comments.py will read the first instagram handle in successful_isnta_handle.txt and get all the comments of 3 random post in each month of that celebrity
each run of scrape_comments.py will only target 1 celebrity but it will run for 1hr+ :")
after successful run, the celebrity's instagram handle will be removed from successful_isnta_handle.txt
