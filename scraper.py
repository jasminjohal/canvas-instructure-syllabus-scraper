import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd


def get_syllabus_content(url):
    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    driver.quit()
    return soup


def convert_syllabus_to_df(soup):
    if not soup:
        return

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
    return syllabus_df


def process_df_for_todoist(df):
    # remove non-ASCII characters
    # df.replace({r'[^\x00-\x7F]+': ' '}, regex=True, inplace=True)

    df = df.rename(columns={"Dates": "DATE", "Tasks": "CONTENT"})

    # requisite columns for Todoist import
    df['TYPE'] = "task"
    df['PRIORITY'] = 4
    df['INDENT'] = ""
    df['AUTHOR'] = ""
    df['RESPONSIBLE'] = ""
    df['DATE_LANG'] = "en"
    df['TIMEZONE'] = ""

    # get time from 'Due' column and concatenate to 'DATE'
    df['Times'] = df['Times'].str.replace(
        'due by ', '', regex=True).str.strip()
    df['DATE'] = df['DATE'] + " @ " + df['Times']

    # reorder columns and output to csv
    df = df[['TYPE', 'CONTENT', 'PRIORITY', 'INDENT', 'AUTHOR',
             'RESPONSIBLE', 'DATE', 'DATE_LANG', 'TIMEZONE']]
    return df


if __name__ == "__main__":
    CS361_URL = 'https://oregonstate.instructure.com/courses/1877222/assignments/syllabus'
    CS372_URL = 'https://oregonstate.instructure.com/courses/1830291/assignments/syllabus'
    html = get_syllabus_content(CS372_URL)
    df = convert_syllabus_to_df(html)
    todoist_df = process_df_for_todoist(df)
    print(todoist_df)
