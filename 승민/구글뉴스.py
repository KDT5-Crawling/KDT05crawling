from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
search = '자동화'
driver.get(f'https://news.google.com/search?q={search}&hl=ko&gl=KR&ceid=KR%3Ako')

# driver.implicitly_wait(3)

search_box = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/main/div[2]/c-wiz/c-wiz[9]/c-wiz/article/div[1]/div[2]/div/a')
search_box.send_keys('자동화')
search_box.submit()     # 검색 버튼 누름

time.sleep(10)
search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
print(len(search_results))

# Extract and print the title and URL of each search result
for result in search_results:
    title_element = result.find_element(By.CSS_SELECTOR, "h3")
    title = title_element.text.strip()
    print(f"{title}")

driver.quit()