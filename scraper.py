from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import validators
import pandas as pd
from datetime import datetime


def check_if_url_is_valid(url):
    """Accept a URL and returns True if the URL is a valid Canvas syllabus URL;
    False otherwise."""
    valid_url = valid_canvas_url = True
    if not validators.url(url):
        valid_url = False
    if ("instructure" not in url or "canvas" not in url) and "syllabus" not in url:
        valid_canvas_url = False
    return valid_url and valid_canvas_url


def get_syllabus_content(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")  # disable console warnings/errors
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    soup = None
    # force browser to wait <=10 seconds for content to load
    try:
        elem = WebDriverWait(driver, 10).until(
            # tr with class 'detail_list' only appears in syllabusTableBody
            EC.presence_of_element_located(
                (By.CLASS_NAME, "detail_list"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
    except TimeoutException as e:
        print("Timed out - could not locate syllabus content.")
    finally:
        driver.quit()

    return soup


def validate_content(soup):
    """Return True if the HTML content corresponds to a Canvas syllabus page;
    False otherwise"""
    if not soup:
        return False

    header = soup.find_all("a", {'class': 'mobile-header-title expandable'})
    if not header:
        return False
    return True


def get_course_name(soup):
    header = soup.find_all("a", {'class': 'mobile-header-title expandable'})[0]
    course_name = header.find('div').text
    return course_name


def convert_syllabus_to_df(soup):
    table = soup.find(id="syllabus")

    # strip out duplicate tasks, screenreader content, and calendar icons
    for tr in table.find_all("tr", {'class': 'special_date'}):
        # removes duplicate (1 student), (3 students) rows
        tr.decompose()
    for span in table.find_all("span", {'class': 'screenreader-only'}):
        span.decompose()
    for icon in table.find_all("i", {'class': 'icon-assignment'}):
        icon.decompose()

    dates = []
    tasks = []
    times = []

    rows = table.find_all('tr')
    for row in rows[1:]:  # first row contains column names
        # date is contained in class name (e.g. "events_2021_12_03")
        classes = row['class']
        found_date = False
        for row_class in classes:
            if "events_" in row_class:
                found_date = True

        if found_date:
            task_date = classes[3].split('_')
            year = task_date[1]
            month = task_date[2]
            day = task_date[3]
            task_date = f'{month}/{day}/{year}'
            # "09/27/2020" -> "Sun Sep 27, 2020"
            task_date = datetime.strptime(
                task_date, '%m/%d/%Y').strftime('%a %b %#d, %Y')  # THIS IS ONLY VALID FOR WINDOWS!
        # some tasks do not have due dates
        else:
            task_date = ''

        task_name = row.find_all('td', {'class': 'name'})[
            0].text.strip().replace('\n', '')
        task_time = row.find_all('td', {'class': 'dates'})[
            0].text.strip().replace('\n', '')

        dates.append(task_date)
        tasks.append(task_name)
        times.append(task_time)

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


def process_df_for_asana(df):
    # remove non-ASCII characters
    # df.replace({r'[^\x00-\x7F]+': ' '}, regex=True, inplace=True)

    # rename column names
    # place time in description since Asana does not support due time
    df = df.rename(columns={"Dates": "Due Date",
                            "Tasks": "Name", "Times": "Description"})

    # requisite columns for Asana import
    df['Assignee'] = ""
    df['Collaborators'] = ""
    df['Start Date'] = ""
    df['Type'] = ""
    df['Section/Column'] = ""

    # convert date to format that Asana expects (e.g. 'Mon Sep 27, 2021' -> '9/27/21')
    df['Due Date'] = pd.to_datetime(df['Due Date'], format='%a %b %d, %Y')

    # reorder columns and output to csv
    df = df[['Name', 'Description', 'Assignee', 'Collaborators',
             'Due Date', 'Start Date', 'Type', 'Section/Column']]

    return df


if __name__ == "__main__":
    CS361_URL = 'https://oregonstate.instructure.com/courses/1877222/assignments/syllabus'
    CS372_URL = 'https://oregonstate.instructure.com/courses/1830291/assignments/syllabus'
    html = get_syllabus_content(CS361_URL)
    course_name = get_course_name(html)
    df = convert_syllabus_to_df(html)
    todoist_df = process_df_for_todoist(df)
    todoist_df.to_csv('test.csv')
    print(todoist_df)
