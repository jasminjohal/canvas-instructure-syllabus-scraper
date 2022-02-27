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
    rows = table.find_all('tr')
    print(table)


CS361_URL = 'https://oregonstate.instructure.com/courses/1877222/assignments/syllabus'
CS372_URL = 'https://oregonstate.instructure.com/courses/1830291/assignments/syllabus'
rows = scrape_canvas(CS361_URL)
print(rows)
