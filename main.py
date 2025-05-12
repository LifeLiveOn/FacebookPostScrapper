import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import re


from func import *

POST_URL = 'https://www.facebook.com'

#set up drivers
options = Options()
driver = webdriver.Chrome(options=options)
driver.get(POST_URL)
time.sleep(2)

#load cookies
with open("facebook.json", "r") as f:
    cookies = json.load(f)
    for cookie in cookies:
        # Avoid issues with sameSite or expiry formats
        cookie.pop('sameSite', None)
        cookie.pop('expiry', None)
        driver.add_cookie(cookie)

POST_URL = 'https://www.facebook.com/webtretho.vietnam/posts/pfbid02KDJ1xZJuVCU8sRQBAQiVqDFrFv5KRsWzw2jF5P5ePNh2H7hsWGF1eBMpWLk8yqyKl'


# Now reload the page, logged in
driver.get(POST_URL)
# comment_container = driver.find_element(By.XPATH, "//div[contains(@class, 'x1gslohp')]")
wait = WebDriverWait(driver, 10)
comment_container = wait.until(EC.presence_of_element_located(
    (By.XPATH, "//div[contains(@class, 'x1gslohp')]")
))


scrollable_div = find_scrollable_parent(driver, comment_container)
switch_to_all_comments(wait)

if scrollable_div:
    random_scrolls = random.randint(300, 450)
    for _ in range(50):
        driver.execute_script(f"arguments[0].scrollBy(0, {random_scrolls});", scrollable_div)
        time.sleep(1.5)
else:
    print("No scrollable parent found")

expand_see_more_buttons(driver, comment_container)

data = process_all_comments(driver, comment_container, POST_URL)
# # Get all comments
# comments = comment_container.find_elements(By.XPATH, ".//div[contains(@class, 'x1y1aw1k')]")

output_file = f"comments_facebookPost{POST_URL[-5:]}.csv"
clean_and_save_comments(data, output_file)
