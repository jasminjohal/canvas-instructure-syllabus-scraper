from ast import Return
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from setuptools import setup
import validators
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


def is_valid_url(url):
    """Accept a URL and returns True if the URL is a valid Canvas syllabus URL;
    False otherwise."""
    valid_url = valid_canvas_url = True
    if not validators.url(url):
        valid_url = False
    if ("instructure" not in url or "canvas" not in url) and "syllabus" not in url:
        valid_canvas_url = False
    return valid_url and valid_canvas_url


def setup_driver():
    """Return an instance of ChromeDriver"""
    options = webdriver.ChromeOptions()
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", None)
    options.add_argument("--headless")
    # disable console warnings/errors
    options.add_argument("--log-level=3")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get(
        "CHROMEDRIVER_PATH"), options=options)

    return driver


def get_raw_html(driver, url):
    """Return the raw scraped contents of the passed URL"""

    # visit url
    soup = None
    driver.get(url)

    try:
        # force browser to wait <=10 seconds for content to load
        elem = WebDriverWait(driver, 10).until(
            # tr with class 'detail_list' only appears in syllabusTableBody
            EC.presence_of_element_located((By.CLASS_NAME, "detail_list"))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
    except TimeoutException as e:
        print("Timed out - could not locate syllabus content.")
    finally:
        driver.quit()

    return soup


def is_canvas_page(soup):
    """Return True if the HTML content corresponds to a Canvas syllabus page;
    False otherwise"""
    if not soup:
        return False

    # check if the page has a header contained specifically in Canvas course pages
    header = soup.find_all("a", {'class': 'mobile-header-title expandable'})
    if not header:
        return False
    return True


def get_course_name(soup):
    """Extract and return the full name of the course from the scraped HTML page"""
    header = soup.find_all("a", {'class': 'mobile-header-title expandable'})[0]
    course_name = header.find('div').text
    return course_name


def get_syllabus_rows(soup):
    """Accepts the raw HTML content of the syllabus page and returns a list of rows in the syllabus table"""
    table = soup.find(id="syllabus")
    remove_extraneous_rows(table)
    rows = table.find_all('tr')
    return rows


def remove_extraneous_rows(table):
    """Remove all rows in HTML table that contain duplicate tasks, screenreader content, and calendar icons"""
    # removes duplicate (1 student), (3 students) rows
    for tr in table.find_all("tr", {'class': 'special_date'}):
        tr.decompose()
    for span in table.find_all("span", {'class': 'screenreader-only'}):
        span.decompose()
    for icon in table.find_all("i", {'class': 'icon-assignment'}):
        icon.decompose()


def contains_date(row):
    """Return True if the row has a populated date field; return False otherwise"""
    # date is contained in a class name (e.g. "events_2020_09_27")
    for row_class in row['class']:
        if "events_" in row_class:
            return True

    return False


def extract_date(row):
    """Parse and return the date from the passed row data if it has a date"""
    # check if the task has a due date; some tasks do not
    if contains_date(row):
        # date is contained in a class name (e.g. "events_2020_09_27")
        task_date = row['class'][3].split('_')
        year = task_date[1]
        month = task_date[2]
        day = task_date[3]
        task_date = f'{month}/{day}/{year}'
        # "09/27/2020" -> "Sun Sep 27, 2020"
        task_date = datetime.strptime(
            task_date, '%m/%d/%Y').strftime('%a %b %#d, %Y')  # THIS IS ONLY VALID FOR WINDOWS!
    else:
        task_date = ''

    return task_date


def extract_task_name(row):
    """Parse and return the task name from the passed row data"""
    return row.find_all('td', {'class': 'name'})[
        0].text.strip().replace('\n', '')


def extract_time(row):
    """Parse and return the time from the passed row data"""
    return row.find_all('td', {'class': 'dates'})[
        0].text.strip().replace('\n', '')


def create_df(tasks, dates, times):
    """Return a dataframe with Tasks, Dates, and Times columns"""
    return pd.DataFrame({
        'Tasks': tasks,
        'Dates': dates,
        'Times': times
    })


def convert_syllabus_to_df(syllabus):
    """Return a pandas dataframe after parsing every row in the syllabus HTML"""
    dates = []
    tasks = []
    times = []

    # get the task date, name, and time information from each row in syllabus
    # but ignore first row because it contains column names
    for row in syllabus[1:]:
        task_date = extract_date(row)
        task_name = extract_task_name(row)
        task_time = extract_time(row)

        dates.append(task_date)
        tasks.append(task_name)
        times.append(task_time)

    syllabus_df = create_df(tasks, dates, times)
    return syllabus_df


def rename_columns(df, tms):
    """Return a dataframe with renamed column names depending on the passed task management system"""
    if tms == 'todoist':
        df = df.rename(columns={"Dates": "DATE", "Tasks": "CONTENT"})
    elif tms == 'asana':
        # place time in description since Asana does not support due time
        df = df.rename(columns={"Dates": "Due Date",
                       "Tasks": "Name", "Times": "Description"})
    return df


def add_columns(df, tms):
    """Add requisite columns to passed dataframe depending on task management system"""
    if tms == 'todoist':
        df['TYPE'] = "task"
        df['PRIORITY'] = 4
        df['INDENT'] = ""
        df['AUTHOR'] = ""
        df['RESPONSIBLE'] = ""
        df['DATE_LANG'] = "en"
        df['TIMEZONE'] = ""
    elif tms == 'asana':
        df['Assignee'] = ""
        df['Collaborators'] = ""
        df['Start Date'] = ""
        df['Type'] = ""
        df['Section/Column'] = ""


def format_date_column(df, tms):
    if tms == 'todoist':
        # concatenate the time to the date for 'DATE' column
        df['Times'] = df['Times'].str.replace(
            'due by ', '', regex=True).str.strip()
        df['DATE'] = df['DATE'] + " @ " + df['Times']
    elif tms == 'asana':
        # convert date to format that Asana expects (e.g. 'Mon Sep 27, 2021' -> '9/27/21')
        df['Due Date'] = pd.to_datetime(df['Due Date'], format='%a %b %d, %Y')


def reorder_columns(df, tms):
    """Return a dataframe with reordered columns depending on the passed task management system"""
    if tms == 'todoist':
        df = df[['TYPE', 'CONTENT', 'PRIORITY', 'INDENT', 'AUTHOR',
                 'RESPONSIBLE', 'DATE', 'DATE_LANG', 'TIMEZONE']]
    elif tms == 'asana':
        df = df[['Name', 'Description', 'Assignee', 'Collaborators',
                 'Due Date', 'Start Date', 'Type', 'Section/Column']]
    return df


def process_df_for_tms(df, tms):
    """Return modified version of df in accordance with task management system specifications"""
    df = rename_columns(df, tms)
    add_columns(df, tms)
    format_date_column(df, tms)
    df = reorder_columns(df, tms)
    return df


if __name__ == "__main__":
    CS361_URL = 'https://oregonstate.instructure.com/courses/1877222/assignments/syllabus'
    CS372_URL = 'https://oregonstate.instructure.com/courses/1830291/assignments/syllabus'

    driver = setup_driver()
    html = get_raw_html(driver, CS361_URL)
    course_name = get_course_name(html)
    syllabus = get_syllabus_rows(html)
    df = convert_syllabus_to_df(syllabus)
    todoist_df = process_df_for_tms(df, 'todoist')
    print(todoist_df)
