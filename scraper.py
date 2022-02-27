import requests
import time
import os
from bs4 import BeautifulSoup
import pandas as pd


def scrape_canvas(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find(id="syllabus")
    print(table)


rows = scrape_canvas(
    'https://oregonstate.instructure.com/courses/1877222/assignments/syllabus')
print(rows)
