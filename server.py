from flask import Flask
from scraper import scrape_canvas
import json

app = Flask(__name__)


@app.route("/")
def hello_world():
    CS361_URL = 'https://oregonstate.instructure.com/courses/1877222/assignments/syllabus'
    # CS372_URL = 'https://oregonstate.instructure.com/courses/1830291/assignments/syllabus'
    syllabus = scrape_canvas(CS361_URL)
    stringified_syllabus = json.dumps(syllabus)
    return stringified_syllabus
