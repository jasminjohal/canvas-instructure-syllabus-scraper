import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd


def scrape_canvas(url):
    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    driver.quit()
    table = soup.find(id="syllabus")

    # strip out extraneous trailing info, screenreader content, and calendar icons
    for div in table.find_all("div", {'class': 'special_date_title'}):
        div.decompose()
    for span in table.find_all("span", {'class': 'screenreader-only'}):
        span.decompose()
    for icon in table.find_all("i", {'class': 'icon-assignment'}):
        icon.decompose()

    last_date = None
    dates = []
    tasks = []
    times = []

    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')

        # some rows only have 2 columns if multiple assignments are due on a given day
        if len(cells) == 3:
            td_count = 1
        elif len(cells) == 2:
            td_count = 2
            dates.append(last_date)

        for cell in cells:
            cur_text = cell.text.strip().replace('\n', '')
            # date column (contains due date)
            if td_count == 1:
                dates.append(cur_text)
                last_date = cur_text
            # details column (contains task name)
            elif td_count == 2:
                tasks.append(cur_text)
            # due column (contains due by time)
            elif td_count == 3:
                times.append(cur_text)
            td_count += 1

    syllabus_df = pd.DataFrame(
        {'Tasks': tasks, 'Dates': dates, 'Times': times})
    print(syllabus_df)


if __name__ == "__main__":
    CS361_URL = 'https://oregonstate.instructure.com/courses/1877222/assignments/syllabus'
    CS372_URL = 'https://oregonstate.instructure.com/courses/1830291/assignments/syllabus'
    rows = scrape_canvas(CS361_URL)
